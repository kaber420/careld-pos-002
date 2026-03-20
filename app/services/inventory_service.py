from typing import List, Optional
from sqlmodel import Session, select
from app.models.inventory import InventoryItem, Category, InventoryMovement, MovementType


class InventoryService:
    """Servicio de gestión de inventario"""

    def __init__(self, session: Session):
        self.session = session

    def get_item_by_id(self, item_id: int) -> Optional[InventoryItem]:
        """Obtener item por ID"""
        return self.session.get(InventoryItem, item_id)

    def get_item_by_sku(self, sku: str) -> Optional[InventoryItem]:
        """Obtener item por SKU"""
        return self.session.exec(
            select(InventoryItem).where(InventoryItem.sku == sku)
        ).first()

    def get_low_stock_items(self) -> List[InventoryItem]:
        """Obtener items con stock bajo"""
        return self.session.exec(
            select(InventoryItem).where(
                (InventoryItem.stock_quantity <= InventoryItem.min_stock) &
                (InventoryItem.is_active == True)
            )
        ).all()

    def get_items_by_category(self, category_id: int) -> List[InventoryItem]:
        """Obtener items por categoría"""
        return self.session.exec(
            select(InventoryItem).where(
                (InventoryItem.category_id == category_id) &
                (InventoryItem.is_active == True)
            )
        ).all()

    def search_items(self, search_term: str) -> List[InventoryItem]:
        """Buscar items por nombre o SKU"""
        return self.session.exec(
            select(InventoryItem).where(
                (
                    (InventoryItem.name.ilike(f"%{search_term}%")) |
                    (InventoryItem.sku.ilike(f"%{search_term}%"))
                ) &
                (InventoryItem.is_active == True)
            )
        ).all()

    def adjust_stock(
        self,
        item_id: int,
        quantity: int,
        reason: Optional[str] = None,
        movement_type: MovementType = MovementType.ADJUSTMENT,
        user_id: Optional[int] = None,
        repair_id: Optional[int] = None
    ) -> Optional[InventoryItem]:
        """
        Ajustar stock de un item y registrar el movimiento.
        quantity positivo = agregar stock
        quantity negativo = remover stock
        """
        item = self.session.get(InventoryItem, item_id)
        if not item:
            return None

        new_quantity = item.stock_quantity + quantity
        if new_quantity < 0:
            raise ValueError("Insufficient stock")

        item.stock_quantity = new_quantity
        self.session.add(item)
        
        # Registrar el movimiento
        movement = InventoryMovement(
            inventory_item_id=item.id,
            quantity=quantity,
            type=movement_type,
            reason=reason,
            user_id=user_id,
            repair_id=repair_id
        )
        self.session.add(movement)

        self.session.commit()
        self.session.refresh(item)
        return item

    def create_category(
        self,
        name: str,
        description: Optional[str] = None
    ) -> Category:
        """Crear categoría"""
        # Verificar si ya existe
        existing = self.session.exec(
            select(Category).where(Category.name == name)
        ).first()
        if existing:
            raise ValueError("Category already exists")

        category = Category(name=name, description=description)
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def get_all_categories(self) -> List[Category]:
        """Obtener todas las categorías"""
        return self.session.exec(select(Category)).all()

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Obtener categoría por ID"""
        return self.session.get(Category, category_id)

    def create_item(
        self,
        name: str,
        sku: str,
        unit_price: float,
        cost_price: float = 0,
        stock_quantity: int = 0,
        min_stock: int = 5,
        category_id: Optional[int] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        supplier: Optional[str] = None
    ) -> InventoryItem:
        """Crear nuevo item de inventario"""
        # Verificar SKU único
        existing = self.get_item_by_sku(sku)
        if existing:
            raise ValueError("SKU already exists")

        # Verificar categoría si está presente
        if category_id:
            category = self.get_category_by_id(category_id)
            if not category:
                raise ValueError("Category not found")

        item = InventoryItem(
            name=name,
            sku=sku,
            unit_price=unit_price,
            cost_price=cost_price,
            stock_quantity=stock_quantity,
            min_stock=min_stock,
            category_id=category_id,
            description=description,
            location=location,
            supplier=supplier
        )

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def get_inventory_value(self) -> float:
        """Calcular valor total del inventario (precio de costo * stock)"""
        items = self.session.exec(
            select(InventoryItem).where(InventoryItem.is_active == True)
        ).all()
        return sum(item.cost_price * item.stock_quantity for item in items)

    def get_stock_alerts(self) -> List[dict]:
        """Obtener alertas de stock bajo"""
        low_stock_items = self.get_low_stock_items()
        alerts = []

        for item in low_stock_items:
            alerts.append({
                "item_id": item.id,
                "name": item.name,
                "sku": item.sku,
                "current_stock": item.stock_quantity,
                "min_stock": item.min_stock,
                "shortage": item.min_stock - item.stock_quantity,
                "supplier": item.supplier,
            })

        return alerts
