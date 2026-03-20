from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.inventory import MovementType


class CategoryBase(BaseModel):
    """Schema base de categoría"""
    name: str = Field(max_length=50)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema para crear categoría"""
    pass


class CategoryUpdate(BaseModel):
    """Schema para actualizar categoría"""
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    """Schema de respuesta de categoría"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class InventoryItemBase(BaseModel):
    """Schema base de item de inventario"""
    name: str
    sku: str
    category_id: Optional[int] = None
    description: Optional[str] = None
    unit_price: float = Field(ge=0)
    cost_price: float = Field(default=0, ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    min_stock: int = Field(default=5, ge=0)
    location: Optional[str] = None
    supplier: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    """Schema para crear item de inventario"""
    pass


class InventoryItemUpdate(BaseModel):
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


class InventoryItemResponse(InventoryItemBase):
    """Schema de respuesta de item"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class StockAdjustment(BaseModel):
    """Schema para ajustar el stock de inventario"""
    quantity: int = Field(description="Cantidad a ajustar (positivo para agregar, negativo para remover)")
    type: MovementType = Field(default=MovementType.ADJUSTMENT, description="Tipo de movimiento")
    reason: Optional[str] = Field(default=None, description="Motivo del ajuste")


class InventoryMovementResponse(BaseModel):
    """Schema de respuesta para historial de movimientos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    inventory_item_id: int
    quantity: int
    type: MovementType
    reason: Optional[str]
    user_id: Optional[int]
    repair_id: Optional[int]
    created_at: datetime
