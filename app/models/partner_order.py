from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from app.models.user import UserRole, UserBase
from app.models.inventory import InventoryItemBase

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.inventory import InventoryItem

class PartnerOrderStatus(str, Enum):
    """Estados del pedido de un socio"""
    PENDING = "pending"      # Recién creado, esperando confirmación del staff
    CONFIRMED = "confirmed"  # Confirmado y listo para recoger
    CANCELLED = "cancelled"  # Cancelado por el socio o el staff
    COMPLETED = "completed"  # Recogido y pagado

# --- BASE SCHEMAS (Fields only, no table) ---

class PartnerOrderBase(SQLModel):
    """Campos base de un pedido de socio"""
    total: float = Field(default=0, ge=0)
    notes: Optional[str] = Field(default=None)
    status: PartnerOrderStatus = Field(default=PartnerOrderStatus.PENDING)

class PartnerOrderItemBase(SQLModel):
    """Campos base de un item de pedido"""
    inventory_item_id: int = Field(foreign_key="inventory_items.id")
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    subtotal: float = Field(ge=0)

# --- TABLE MODELS (Database) ---

class PartnerOrder(PartnerOrderBase, table=True):
    """Modelo de pedido de socio en la base de datos"""
    __tablename__ = "partner_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    partner_id: int = Field(foreign_key="users.id", index=True)
    order_number: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relaciones
    partner: Optional["User"] = Relationship()
    items: List["PartnerOrderItem"] = Relationship(
        back_populates="order", 
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"}
    )

class PartnerOrderItem(PartnerOrderItemBase, table=True):
    """Modelo de item de pedido de socio"""
    __tablename__ = "partner_order_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="partner_orders.id", index=True)

    # Relaciones
    order: Optional["PartnerOrder"] = Relationship(back_populates="items")
    inventory_item: Optional["InventoryItem"] = Relationship()

# --- READ SCHEMAS (API Serialization) ---

class PartnerOrderItemRead(PartnerOrderItemBase):
    """Schema para leer un item con su refacción"""
    id: int
    inventory_item: Optional[InventoryItemBase] = None

class PartnerOrderRead(PartnerOrderBase):
    """Schema para leer un pedido completo"""
    id: int
    order_number: str
    partner_id: int
    created_at: datetime
    updated_at: datetime
    partner: Optional[UserBase] = None
    items: List[PartnerOrderItemRead] = []

# --- CREATE SCHEMAS (Input) ---

class PartnerOrderItemCreate(SQLModel):
    """Schema para un item del pedido al crear"""
    inventory_item_id: int
    quantity: int = Field(ge=1)

class PartnerOrderCreate(SQLModel):
    """Schema para crear un pedido"""
    notes: Optional[str] = None
    items: List[PartnerOrderItemCreate]

# Reconstruir modelos para resolver referencias de tipos en Pydantic v2
PartnerOrderItemRead.model_rebuild()
PartnerOrderRead.model_rebuild()
