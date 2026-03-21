from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.repair import RepairStatus, Priority
from app.models.payment import PaymentMethod


class RepairItemBase(BaseModel):
    """Schema base de item de reparación"""
    quantity: int = Field(default=1, ge=1)
    unit_price: float = Field(ge=0)
    notes: Optional[str] = None


class RepairItemCreate(BaseModel):
    """Schema para crear item - repair_id viene de la URL"""
    inventory_item_id: int
    quantity: int = Field(default=1, ge=1)
    unit_price: float = Field(ge=0)
    notes: Optional[str] = None
    technician_id: Optional[int] = None


class RepairItemUpdate(BaseModel):
    """Schema para actualizar item"""
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    notes: Optional[str] = None


class RepairItemResponse(RepairItemBase):
    """Schema de respuesta de item"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    repair_id: int
    inventory_item_id: int
    technician_id: Optional[int] = None
    created_at: datetime


class RepairBase(BaseModel):
    """Schema base de reparación"""
    description: str = Field(max_length=500)
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    estimated_cost: Optional[float] = Field(default=None, ge=0)
    final_cost: Optional[float] = Field(default=None, ge=0)
    priority: Priority = Priority.NORMAL
    warranty_days: int = Field(default=30, ge=0, le=365)


class RepairCreate(RepairBase):
    """Schema para crear reparación"""
    device_id: int
    technician_id: Optional[int] = None
    partner_id: Optional[int] = None


class RepairUpdate(BaseModel):
    """Schema para actualizar reparación"""
    description: Optional[str] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    estimated_cost: Optional[float] = None
    final_cost: Optional[float] = None
    priority: Optional[Priority] = None
    status: Optional[RepairStatus] = None
    technician_id: Optional[int] = None
    partner_id: Optional[int] = None
    warranty_days: Optional[int] = None


from app.schemas.device import DeviceResponse


class RepairResponse(RepairBase):
    """Schema de respuesta de reparación"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    repair_number: str
    device_id: int
    device: Optional[DeviceResponse] = None
    technician_id: Optional[int]
    partner_id: Optional[int] = None
    status: RepairStatus
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class RepairComplete(BaseModel):
    """Schema para completar una reparación con cobro"""
    labor_cost: float = Field(default=0, ge=0, description="Costo de mano de obra")
    payment_method: PaymentMethod = PaymentMethod.CASH
    reference: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None


class RepairCompleteResponse(BaseModel):
    """Schema de respuesta al completar reparación"""
    model_config = ConfigDict(from_attributes=True)

    repair: RepairResponse
    items_total: float
    labor_cost: float
    final_total: float
    payment_registered: bool
