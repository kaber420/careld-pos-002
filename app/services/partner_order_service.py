from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from app.models.partner_order import PartnerOrder, PartnerOrderItem, PartnerOrderStatus
from app.models.inventory import InventoryItem, MovementType
from app.services.inventory_service import InventoryService
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

class PartnerOrderService:
    """Servicio de gestión de pedidos de socios"""

    def __init__(self, session: Session):
        self.session = session
        self.inventory_service = InventoryService(session)

    def create_order(
        self,
        partner_id: int,
        items_data: List[dict],
        notes: Optional[str] = None
    ) -> PartnerOrder:
        """Crear un nuevo pedido para un socio"""
        
        total = 0.0
        order_items_to_create = []

        for item_data in items_data:
            inventory_item_id = item_data["inventory_item_id"]
            quantity = item_data["quantity"]
            
            # Verificar existencia del item
            inventory_item = self.inventory_service.get_item_by_id(inventory_item_id)
            if not inventory_item:
                raise ValueError(f"El producto con ID {inventory_item_id} no existe")
            
            # En pedidos de socios, no necesariamente reducimos stock de inmediato (es para recoger)
            # Pero validamos que haya suficiente para la "promesa"
            if inventory_item.stock_quantity < quantity:
                raise ValueError(f"Stock insuficiente para {inventory_item.name}. Disponible: {inventory_item.stock_quantity}")
            
            unit_price = inventory_item.unit_price # Precio actual de venta
            subtotal = unit_price * quantity
            total += subtotal
            
            order_items_to_create.append({
                "inventory_item_id": inventory_item_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": subtotal
            })

        # Generar número de pedido
        order_number = self._generate_order_number()
        
        order = PartnerOrder(
            order_number=order_number,
            partner_id=partner_id,
            total=total,
            notes=notes,
            status=PartnerOrderStatus.PENDING
        )
        self.session.add(order)
        self.session.flush()

        # Crear los items del pedido
        for item_data in order_items_to_create:
            order_item = PartnerOrderItem(
                order_id=order.id,
                inventory_item_id=item_data["inventory_item_id"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                subtotal=item_data["subtotal"]
            )
            self.session.add(order_item)

        self.session.commit()
        self.session.refresh(order)
        return order

    def get_order_by_id(self, order_id: int) -> Optional[PartnerOrder]:
        """Obtener pedido por ID"""
        return self.session.get(PartnerOrder, order_id)

    def get_partner_orders(self, partner_id: int, skip: int = 0, limit: int = 100) -> List[PartnerOrder]:
        """Obtener pedidos de un socio específico"""
        return self.session.exec(
            select(PartnerOrder)
            .where(PartnerOrder.partner_id == partner_id)
            .options(
                selectinload(PartnerOrder.items).selectinload(PartnerOrderItem.inventory_item),
                selectinload(PartnerOrder.partner)
            )
            .order_by(PartnerOrder.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def list_all_orders(self, skip: int = 0, limit: int = 100) -> List[PartnerOrder]:
        """Listar todos los pedidos (para admin/staff)"""
        return self.session.exec(
            select(PartnerOrder)
            .options(
                selectinload(PartnerOrder.items).selectinload(PartnerOrderItem.inventory_item),
                selectinload(PartnerOrder.partner)
            )
            .order_by(PartnerOrder.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def update_order_status(self, order_id: int, status: PartnerOrderStatus, user_id: int) -> PartnerOrder:
        """Actualizar el estado de un pedido"""
        order = self.get_order_by_id(order_id)
        if not order:
            raise ValueError("Pedido no encontrado")
        
        old_status = order.status
        order.status = status
        order.updated_at = datetime.utcnow()
        
        # Si el pedido se marca como completado, reducimos el stock definitivamente
        if status == PartnerOrderStatus.COMPLETED and old_status != PartnerOrderStatus.COMPLETED:
            for item in order.items:
                self.inventory_service.adjust_stock(
                    item_id=item.inventory_item_id,
                    quantity=-item.quantity,
                    reason=f"Pedido de socio {order.order_number} entregado",
                    movement_type=MovementType.WITHDRAWAL,
                    user_id=user_id
                )
        
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    def _generate_order_number(self) -> str:
        """Generar número único de pedido (SOC-YYYYMMDD-XXXX)"""
        today = datetime.now().strftime("%Y%m%d")
        last_order = self.session.exec(
            select(PartnerOrder)
            .where(PartnerOrder.order_number.like(f"SOC-{today}-%"))
            .order_by(PartnerOrder.order_number.desc())
            .limit(1)
        ).first()

        if last_order:
            last_num = int(last_order.order_number.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"SOC-{today}-{new_num:04d}"
