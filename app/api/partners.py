from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User, UserRole
from app.models.inventory import InventoryItem
from app.models.partner_order import PartnerOrder, PartnerOrderCreate, PartnerOrderStatus, PartnerOrderRead
from app.models.repair import Repair
from app.models.device import Device
from app.schemas.repair import RepairResponse
from app.schemas.device import DeviceResponse
from app.core.dependencies import get_current_user, require_role
from app.services.partner_order_service import PartnerOrderService
from sqlalchemy.orm import selectinload

# Router para socios (Partner Portal)
router = APIRouter(prefix="/partners", tags=["Socio"])

@router.get("/inventory", response_model=List[InventoryItem])
def get_partner_inventory(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Listar inventario disponible para socios"""
    # Solo socios y admins pueden ver esto
    if current_user.role not in [UserRole.PARTNER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta sección")
        
    return session.exec(
        select(InventoryItem).where(InventoryItem.is_active == True)
    ).all()

@router.post("/orders", response_model=PartnerOrderRead, status_code=status.HTTP_201_CREATED)
def create_partner_order(
    order_data: PartnerOrderCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Crear un pedido de refacciones (solo socios)"""
    if current_user.role != UserRole.PARTNER:
        raise HTTPException(status_code=403, detail="Solo los socios pueden realizar pedidos")
        
    service = PartnerOrderService(session)
    try:
        items_data = [item.model_dump() for item in order_data.items]
        return service.create_order(
            partner_id=current_user.id,
            items_data=items_data,
            notes=order_data.notes
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders", response_model=List[PartnerOrderRead])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Ver mis pedidos (como socio)"""
    if current_user.role != UserRole.PARTNER:
        raise HTTPException(status_code=403, detail="Acceso denegado")
        
    service = PartnerOrderService(session)
    return service.get_partner_orders(partner_id=current_user.id)

@router.get("/repairs", response_model=List[RepairResponse])
def get_my_repairs(
    current_user: User = Depends(require_role(UserRole.PARTNER)),
    session: Session = Depends(get_session)
):
    """Listar reparaciones vinculadas al socio comercial autenticado"""
    repairs = session.exec(
        select(Repair)
        .where(Repair.partner_id == current_user.id)
        .options(selectinload(Repair.device))
        .order_by(Repair.created_at.desc())
    ).all()
    return repairs

@router.get("/devices", response_model=List[DeviceResponse])
def get_my_devices(
    current_user: User = Depends(require_role(UserRole.PARTNER)),
    session: Session = Depends(get_session)
):
    """Listar dispositivos vinculados a las reparaciones del socio"""
    # Buscamos dispositivos que tengan al menos una reparación del socio
    query = (
        select(Device)
        .join(Repair)
        .where(Repair.partner_id == current_user.id)
        .options(selectinload(Device.customer))
        .distinct()
    )
    devices = session.exec(query).all()
    return devices

# Router para administrar pedidos de socios (Staff Portal)
admin_router = APIRouter(prefix="/admin/partners", tags=["Admin - Socios"])

@admin_router.get("/orders", response_model=List[PartnerOrderRead])
def list_all_partner_orders(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECEPTIONIST)),
    session: Session = Depends(get_session)
):
    """Listar todos los pedidos de socios (Staff)"""
    service = PartnerOrderService(session)
    return service.list_all_orders()

@admin_router.patch("/orders/{order_id}/status", response_model=PartnerOrderRead)
def update_partner_order_status(
    order_id: int,
    status: PartnerOrderStatus,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECEPTIONIST)),
    session: Session = Depends(get_session)
):
    """Actualizar estado de un pedido de socio"""
    service = PartnerOrderService(session)
    try:
        return service.update_order_status(order_id, status, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
