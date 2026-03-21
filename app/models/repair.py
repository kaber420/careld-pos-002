from datetime import datetime, timedelta
from enum import Enum
import secrets
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.device import Device
    from app.models.user import User
    from app.models.repair import RepairItem
    from app.models.payment import Payment


class RepairStatus(str, Enum):
    """Estados de una reparación"""
    PENDING = "pending"              # Pendiente de revisión
    DIAGNOSING = "diagnosing"        # En diagnóstico
    WAITING_APPROVAL = "waiting_approval"  # Esperando aprobación del cliente
    IN_PROGRESS = "in_progress"      # En reparación
    WAITING_PARTS = "waiting_parts"  # Esperando repuestos
    COMPLETED = "completed"          # Reparación completada
    DELIVERED = "delivered"          # Entregado al cliente
    CANCELLED = "cancelled"          # Cancelada


class Priority(str, Enum):
    """Prioridad de reparación"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class RepairBase(SQLModel):
    """Campos base de reparación"""
    description: str = Field(max_length=500)  # Descripción del problema
    diagnosis: Optional[str] = Field(default=None)  # Diagnóstico técnico
    notes: Optional[str] = Field(default=None)  # Notas internas
    estimated_cost: Optional[float] = Field(default=None, ge=0)
    final_cost: Optional[float] = Field(default=None, ge=0)
    priority: Priority = Field(default=Priority.NORMAL)
    warranty_days: int = Field(default=30, ge=0, le=365)  # Días de garantía


class RepairCreate(RepairBase):
    """Schema para crear reparación"""
    device_id: int
    technician_id: Optional[int] = None


class RepairUpdate(SQLModel):
    """Schema para actualizar reparación"""
    description: Optional[str] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    estimated_cost: Optional[float] = None
    final_cost: Optional[float] = None
    priority: Optional[Priority] = None
    status: Optional[RepairStatus] = None
    technician_id: Optional[int] = None
    warranty_days: Optional[int] = None
    delivered_at: Optional[datetime] = None


class Repair(RepairBase, table=True):
    """Modelo de reparación en la base de datos"""
    __tablename__ = "repairs"

    id: Optional[int] = Field(default=None, primary_key=True)
    repair_number: str = Field(unique=True, index=True)  # Número único de orden
    device_id: int = Field(foreign_key="devices.id", index=True)
    technician_id: Optional[int] = Field(default=None, foreign_key="users.id")
    status: RepairStatus = Field(default=RepairStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    client_approved: Optional[bool] = Field(default=None)  # None=pending, True=approved, False=rejected

    # Portal access
    portal_token: Optional[str] = Field(default=None, unique=True, index=True)
    portal_token_expires: Optional[datetime] = Field(default=None)
    partner_id: Optional[int] = Field(default=None, foreign_key="users.id")

    # Relaciones
    device: Optional["Device"] = Relationship(back_populates="repairs", sa_relationship_kwargs={"lazy": "selectin"})
    technician: Optional["User"] = Relationship(
        back_populates="repairs_assigned",
        sa_relationship_kwargs={"foreign_keys": "[Repair.technician_id]"}
    )
    items: list["RepairItem"] = Relationship(back_populates="repair", sa_relationship_kwargs={"lazy": "selectin"})
    payments: list["Payment"] = Relationship(back_populates="repair", sa_relationship_kwargs={"lazy": "selectin"})
    logs: list["RepairLog"] = Relationship(back_populates="repair", sa_relationship_kwargs={"lazy": "selectin"})


class RepairItemBase(SQLModel):
    """Item de reparación (repuestos usados)"""
    quantity: int = Field(default=1, ge=1)
    unit_price: float = Field(ge=0)
    notes: Optional[str] = Field(default=None)


class RepairItemCreate(RepairItemBase):
    """Schema para crear item de reparación"""
    repair_id: int
    inventory_item_id: int


class RepairItemUpdate(SQLModel):
    """Schema para actualizar item"""
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    notes: Optional[str] = None


class RepairItem(RepairItemBase, table=True):
    """Items usados en una reparación"""
    __tablename__ = "repair_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    repair_id: int = Field(foreign_key="repairs.id", index=True)
    inventory_item_id: int = Field(foreign_key="inventory_items.id")
    technician_id: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relaciones
    repair: Optional["Repair"] = Relationship(back_populates="items")  # type: ignore
    inventory_item: Optional["InventoryItem"] = Relationship()  # type: ignore


class RepairLog(SQLModel, table=True):
    """Historial detallado para la línea de tiempo"""
    __tablename__ = "repair_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    repair_id: int = Field(foreign_key="repairs.id", index=True)
    from_status: RepairStatus
    to_status: RepairStatus
    description: str
    technician_id: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relaciones
    repair: Optional["Repair"] = Relationship(back_populates="logs")
    technician: Optional["User"] = Relationship()
