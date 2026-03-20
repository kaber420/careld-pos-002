from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from app.models.repair import Repair, RepairStatus, RepairItem, Priority
from app.models.device import Device, DeviceStatus
from app.models.inventory import InventoryItem


class RepairService:
    """Servicio de gestión de reparaciones"""

    def __init__(self, session: Session):
        self.session = session

    def create_repair(
        self,
        device_id: int,
        description: str,
        technician_id: Optional[int] = None,
        priority: Priority = Priority.NORMAL,
        estimated_cost: Optional[float] = None
    ) -> Repair:
        """Crear nueva reparación"""
        # Generar número de reparación
        repair_number = self._generate_repair_number()

        repair = Repair(
            repair_number=repair_number,
            device_id=device_id,
            description=description,
            technician_id=technician_id,
            priority=priority,
            estimated_cost=estimated_cost,
            status=RepairStatus.PENDING
        )

        # Actualizar estado del dispositivo
        device = self.session.get(Device, device_id)
        if device:
            device.status = DeviceStatus.IN_REPAIR
            self.session.add(device)

        self.session.add(repair)
        self.session.commit()
        self.session.refresh(repair)
        return repair

    def get_repair_by_id(self, repair_id: int) -> Optional[Repair]:
        """Obtener reparación por ID"""
        return self.session.get(Repair, repair_id)

    def get_repairs_by_status(
        self,
        status: RepairStatus,
        limit: int = 100
    ) -> List[Repair]:
        """Obtener reparaciones por estado"""
        return self.session.exec(
            select(Repair)
            .where(Repair.status == status)
            .order_by(Repair.created_at.desc())
            .limit(limit)
        ).all()

    def get_repairs_by_technician(
        self,
        technician_id: int,
        status_filter: Optional[RepairStatus] = None
    ) -> List[Repair]:
        """Obtener reparaciones asignadas a un técnico"""
        query = select(Repair).where(Repair.technician_id == technician_id)

        if status_filter:
            query = query.where(Repair.status == status_filter)

        return self.session.exec(query.order_by(Repair.created_at.desc())).all()

    def update_repair_status(
        self,
        repair_id: int,
        status: RepairStatus
    ) -> Optional[Repair]:
        """Actualizar estado de reparación"""
        repair = self.session.get(Repair, repair_id)
        if not repair:
            return None

        repair.status = status
        repair.updated_at = datetime.utcnow()

        # Manejar timestamps según el estado
        if status == RepairStatus.IN_PROGRESS and not repair.started_at:
            repair.started_at = datetime.utcnow()
        elif status == RepairStatus.COMPLETED and not repair.completed_at:
            repair.completed_at = datetime.utcnow()
            # Actualizar dispositivo
            device = self.session.get(Device, repair.device_id)
            if device:
                device.status = DeviceStatus.READY
                self.session.add(device)
        elif status == RepairStatus.DELIVERED:
            repair.delivered_at = datetime.utcnow()
            device = self.session.get(Device, repair.device_id)
            if device:
                device.status = DeviceStatus.DELIVERED
                self.session.add(device)

        self.session.add(repair)
        self.session.commit()
        self.session.refresh(repair)
        return repair

    def assign_technician(
        self,
        repair_id: int,
        technician_id: int
    ) -> Optional[Repair]:
        """Asignar técnico a reparación"""
        repair = self.session.get(Repair, repair_id)
        if not repair:
            return None

        repair.technician_id = technician_id
        if repair.status == RepairStatus.PENDING:
            repair.status = RepairStatus.DIAGNOSING

        repair.updated_at = datetime.utcnow()
        self.session.add(repair)
        self.session.commit()
        self.session.refresh(repair)
        return repair

    def add_repair_item(
        self,
        repair_id: int,
        inventory_item_id: int,
        quantity: int = 1,
        unit_price: Optional[float] = None,
        notes: Optional[str] = None
    ) -> RepairItem:
        """Agregar item/repuesto a reparación"""
        # Obtener item de inventario para precio por defecto
        inventory_item = self.session.get(InventoryItem, inventory_item_id)
        if not inventory_item:
            raise ValueError("Inventory item not found")

        if unit_price is None:
            unit_price = inventory_item.unit_price

        # Reducir stock y registrar movimiento
        if inventory_item.stock_quantity < quantity:
            raise ValueError("Insufficient stock")

        inventory_item.stock_quantity -= quantity
        self.session.add(inventory_item)

        from app.models.inventory import InventoryMovement, MovementType
        movement = InventoryMovement(
            inventory_item_id=inventory_item.id,
            quantity=-quantity,
            type=MovementType.REPAIR,
            reason=f"Repuesto para reparación {repair_id}",
            repair_id=repair_id
        )
        self.session.add(movement)

        repair_item = RepairItem(
            repair_id=repair_id,
            inventory_item_id=inventory_item_id,
            quantity=quantity,
            unit_price=unit_price,
            notes=notes
        )

        self.session.add(repair_item)
        self.session.commit()
        self.session.refresh(repair_item)
        return repair_item

    def get_repair_items(self, repair_id: int) -> List[RepairItem]:
        """Obtener items de una reparación"""
        return self.session.exec(
            select(RepairItem).where(RepairItem.repair_id == repair_id)
        ).all()

    def calculate_total(self, repair_id: int) -> float:
        """Calcular total de items de reparación"""
        items = self.get_repair_items(repair_id)
        return sum(item.unit_price * item.quantity for item in items)

    def _generate_repair_number(self) -> str:
        """Generar número único de reparación"""
        today = datetime.now().strftime("%Y%m%d")
        last_repair = self.session.exec(
            select(Repair)
            .where(Repair.repair_number.like(f"REP-{today}-%"))
            .order_by(Repair.repair_number.desc())
            .limit(1)
        ).first()

        if last_repair:
            last_num = int(last_repair.repair_number.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"REP-{today}-{new_num:04d}"

    def get_pending_repairs_count(self) -> int:
        """Obtener cantidad de reparaciones pendientes"""
        return self.session.exec(
            select(Repair).where(Repair.status == RepairStatus.PENDING)
        ).count()

    def get_repairs_in_progress_count(self) -> int:
        """Obtener cantidad de reparaciones en progreso"""
        return self.session.exec(
            select(Repair).where(Repair.status == RepairStatus.IN_PROGRESS)
        ).count()
