from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.inventory import InventoryItem, InventoryMovement
    from app.models.user import User
    from app.models.repair import Repair


class CategoryBase(SQLModel):
    """Categoría de producto"""
    name: str = Field(max_length=50, unique=True, index=True)
    description: Optional[str] = Field(default=None, max_length=200)


class CategoryCreate(CategoryBase):
    """Schema para crear categoría"""
    pass


class CategoryUpdate(SQLModel):
    """Schema para actualizar categoría"""
    name: Optional[str] = None
    description: Optional[str] = None


class Category(CategoryBase, table=True):
    """Modelo de categoría en la base de datos"""
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relación con items
    items: list["InventoryItem"] = Relationship(back_populates="category", sa_relationship_kwargs={"lazy": "selectin"})  # type: ignore


class MovementType(str, Enum):
    """Tipos de movimiento de inventario"""
    PURCHASE = "purchase"      # Entrada por compra
    REPAIR = "repair"          # Salida por reparación
    WITHDRAWAL = "withdrawal"  # Salida general (ej: uso interno)
    ADJUSTMENT = "adjustment"  # Ajuste manual (inventario físico)
    LOSS = "loss"              # Pérdida/Robo
    DAMAGED = "damaged"        # Producto dañado/defectuoso


class InventoryMovement(SQLModel, table=True):
    """Modelo para registrar historial de movimientos de inventario"""
    __tablename__ = "inventory_movements"

    id: Optional[int] = Field(default=None, primary_key=True)
    inventory_item_id: int = Field(foreign_key="inventory_items.id", index=True)
    quantity: int = Field(...)  # Positivo = entrada, Negativo = salida
    type: MovementType = Field(default=MovementType.ADJUSTMENT)
    reason: Optional[str] = Field(default=None, max_length=255)
    
    # Referencias (opcionales)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    repair_id: Optional[int] = Field(default=None, foreign_key="repairs.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relaciones
    item: Optional["InventoryItem"] = Relationship(back_populates="movements")  # type: ignore
    user: Optional["User"] = Relationship()  # type: ignore
    repair: Optional["Repair"] = Relationship()  # type: ignore


class InventoryItemBase(SQLModel):
    """Campos base de item de inventario"""
    name: str = Field(max_length=100, index=True)
    sku: str = Field(max_length=50, unique=True, index=True)  # Stock Keeping Unit
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    description: Optional[str] = Field(default=None)
    unit_price: float = Field(ge=0)  # Precio de venta
    cost_price: float = Field(default=0, ge=0)  # Precio de costo
    stock_quantity: int = Field(default=0, ge=0)
    min_stock: int = Field(default=5, ge=0)  # Stock mínimo para alerta
    location: Optional[str] = Field(default=None, max_length=50)  # Ubicación física
    supplier: Optional[str] = Field(default=None, max_length=100)


class InventoryItemCreate(InventoryItemBase):
    """Schema para crear item de inventario"""
    pass


class InventoryItemUpdate(SQLModel):
    """Schema para actualizar item"""
    name: Optional[str] = None
    sku: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    unit_price: Optional[float] = None
    cost_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    min_stock: Optional[int] = None
    location: Optional[str] = None
    supplier: Optional[str] = None
    is_active: Optional[bool] = None


class InventoryItem(InventoryItemBase, table=True):
    """Modelo de item de inventario en la base de datos"""
    __tablename__ = "inventory_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relaciones
    category: Optional["Category"] = Relationship(back_populates="items")  # type: ignore
    repair_items: list["RepairItem"] = Relationship(back_populates="inventory_item", sa_relationship_kwargs={"lazy": "selectin"})  # type: ignore
    movements: list["InventoryMovement"] = Relationship(back_populates="item", sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"})  # type: ignore
