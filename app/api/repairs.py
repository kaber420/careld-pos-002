from datetime import datetime, timedelta
from typing import List, Optional
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User, UserRole
from app.models.repair import Repair, RepairStatus, RepairItem, Priority, RepairLog
from app.models.device import Device, DeviceStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.schemas.repair import (
    RepairCreate,
    RepairUpdate,
    RepairResponse,
    RepairItemCreate,
    RepairItemResponse,
    RepairComplete,
    RepairCompleteResponse,
)
from app.core.dependencies import get_current_user, require_role
from app.services.repair_service import RepairService
from app.services.inventory_service import InventoryService

router = APIRouter()


def generate_repair_number(session: Session) -> str:
    """Generar número único de reparación"""
    today = datetime.now().strftime("%Y%m%d")
    last_repair = session.exec(
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


@router.post("/", response_model=RepairResponse, status_code=status.HTTP_201_CREATED)
def create_repair(
    repair_data: RepairCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Crear nueva orden de reparación"""
    # Verificar que el dispositivo existe
    device = session.get(Device, repair_data.device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # Verificar técnico si está asignado
    if repair_data.technician_id:
        technician = session.get(User, repair_data.technician_id)
        if not technician or technician.role not in [UserRole.TECHNICIAN, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid technician ID"
            )

    # Generar número de reparación
    repair_number = generate_repair_number(session)

    # Generar token de portal
    portal_token = secrets.token_urlsafe(32)
    portal_expires = datetime.utcnow() + timedelta(days=30)  # Token válido por 30 días

    # Crear reparación sin validar repair_number (se asigna manualmente)
    repair = Repair(
        description=repair_data.description,
        diagnosis=repair_data.diagnosis,
        notes=repair_data.notes,
        estimated_cost=repair_data.estimated_cost,
        final_cost=repair_data.final_cost,
        priority=repair_data.priority,
        warranty_days=repair_data.warranty_days,
        device_id=repair_data.device_id,
        technician_id=repair_data.technician_id,
        partner_id=repair_data.partner_id,
        repair_number=repair_number,
        portal_token=portal_token,
        portal_token_expires=portal_expires
    )

    # Actualizar estado del dispositivo
    device.status = DeviceStatus.IN_REPAIR

    session.add(repair)
    session.add(device)
    
    # Crear log inicial
    initial_log = RepairLog(
        repair_id=repair.id,
        from_status=RepairStatus.PENDING,
        to_status=RepairStatus.PENDING,
        description="Equipo ingresado al sistema",
        technician_id=current_user.id
    )
    session.add(initial_log)
    
    session.commit()
    session.refresh(repair)
    return repair


@router.get("/", response_model=List[RepairResponse])
def read_repairs(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[RepairStatus] = Query(None, alias="status"),
    device_id: Optional[int] = Query(None),
    technician_id: Optional[int] = Query(None),
    priority: Optional[Priority] = Query(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Listar reparaciones con filtros"""
    query = select(Repair)

    if status_filter:
        query = query.where(Repair.status == status_filter)
    if device_id:
        query = query.where(Repair.device_id == device_id)
    if technician_id:
        query = query.where(Repair.technician_id == technician_id)
    if priority:
        query = query.where(Repair.priority == priority)

    query = query.order_by(Repair.created_at.desc())
    repairs = session.exec(query.offset(skip).limit(limit)).all()
    return repairs


@router.get("/{repair_id}", response_model=RepairResponse)
def read_repair(
    repair_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener reparación por ID"""
    repair = session.get(Repair, repair_id)
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair not found"
        )
    return repair


@router.put("/{repair_id}", response_model=RepairResponse)
def update_repair(
    repair_id: int,
    repair_data: RepairUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Actualizar reparación"""
    repair = session.get(Repair, repair_id)
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair not found"
        )

    update_data = repair_data.model_dump(exclude_unset=True)

    # Manejar cambios de estado
    if "status" in update_data:
        new_status = update_data["status"]
        old_status = repair.status
        
        if new_status != old_status:
            # Crear log de cambio de estado
            status_names = {
                RepairStatus.PENDING: "Pendiente",
                RepairStatus.DIAGNOSING: "En Diagnóstico",
                RepairStatus.WAITING_APPROVAL: "Esperando Aprobación",
                RepairStatus.IN_PROGRESS: "En Reparación",
                RepairStatus.WAITING_PARTS: "Esperando Repuestos",
                RepairStatus.COMPLETED: "Reparación Completada",
                RepairStatus.DELIVERED: "Entregado",
                RepairStatus.CANCELLED: "Cancelado"
            }
            
            log_msg = f"Cambio de estado: {status_names.get(old_status, old_status)} -> {status_names.get(new_status, new_status)}"
            
            status_log = RepairLog(
                repair_id=repair.id,
                from_status=old_status,
                to_status=new_status,
                description=log_msg,
                technician_id=current_user.id
            )
            session.add(status_log)

        if new_status == RepairStatus.IN_PROGRESS and not repair.started_at:
            repair.started_at = datetime.utcnow()
        
        # Sincronización con el dispositivo
        device = session.get(Device, repair.device_id)
        if device:
            if new_status == RepairStatus.IN_PROGRESS:
                device.status = DeviceStatus.IN_REPAIR
            elif new_status == RepairStatus.WAITING_PARTS:
                device.status = DeviceStatus.WAITING_PARTS
            elif new_status == RepairStatus.DIAGNOSING:
                device.status = DeviceStatus.IN_REPAIR
            elif new_status == RepairStatus.COMPLETED:
                repair.completed_at = datetime.utcnow()
                device.status = DeviceStatus.READY
            elif new_status == RepairStatus.DELIVERED:
                repair.delivered_at = datetime.utcnow()
                device.status = DeviceStatus.DELIVERED
            elif new_status == RepairStatus.PENDING:
                device.status = DeviceStatus.REGISTERED
            session.add(device)

    for field, value in update_data.items():
        if field == "partner_id":
             # Validar que el socio existe si se proporciona
             if value is not None:
                 partner = session.get(User, value)
                 if not partner or partner.role != UserRole.PARTNER:
                     raise HTTPException(
                         status_code=status.HTTP_400_BAD_REQUEST,
                         detail="Invalid partner ID or user is not a partner"
                     )
             setattr(repair, field, value)
        elif value is not None:
            setattr(repair, field, value)

    session.add(repair)
    session.commit()
    session.refresh(repair)
    return repair


@router.delete("/{repair_id}")
def delete_repair(
    repair_id: int,
    current_user: User = Depends(require_role("admin", "technician")),
    session: Session = Depends(get_session)
):
    """Eliminar reparación"""
    repair = session.get(Repair, repair_id)
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair not found"
        )

    session.delete(repair)
    session.commit()
    return {"message": "Repair deleted successfully"}


# --- Repair Items ---

@router.post("/{repair_id}/items", response_model=RepairItemResponse)
def add_repair_item(
    repair_id: int,
    item_data: RepairItemCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Agregar item/repuesto a una reparación"""
    repair = session.get(Repair, repair_id)
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair not found"
        )

    service = RepairService(session)
    try:
        repair_item = service.add_repair_item(
            repair_id=repair_id,
            inventory_item_id=item_data.inventory_item_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            notes=item_data.notes
        )
        return repair_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{repair_id}/items", response_model=List[RepairItemResponse])
def get_repair_items(
    repair_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener items de una reparación"""
    items = session.exec(
        select(RepairItem).where(RepairItem.repair_id == repair_id)
    ).all()
    return items


@router.delete("/{repair_id}/items/{item_id}")
def remove_repair_item(
    repair_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Eliminar item de una reparación y devolver stock al inventario"""
    item = session.get(RepairItem, item_id)
    if not item or item.repair_id != repair_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in this repair"
        )

    inventory_service = InventoryService(session)
    inventory_service.adjust_stock(
        item_id=item.inventory_item_id,
        quantity=item.quantity,
        reason=f"Devuelto de reparación {repair_id}"
    )

    session.delete(item)
    session.commit()
    return {"message": "Item removed successfully"}


# --- Completar reparación con cobro ---

@router.post("/{repair_id}/complete", response_model=RepairCompleteResponse)
def complete_repair(
    repair_id: int,
    complete_data: RepairComplete,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Completar una reparación con cobro unificado.
    Calcula: total = costo_mano_obra + sum(refacciones)
    """
    repair = session.get(Repair, repair_id)
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair not found"
        )

    if repair.status in [RepairStatus.COMPLETED, RepairStatus.DELIVERED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Repair already completed"
        )

    if repair.status == RepairStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot complete a cancelled repair"
        )

    items = session.exec(
        select(RepairItem).where(RepairItem.repair_id == repair_id)
    ).all()
    items_total = sum(item.unit_price * item.quantity for item in items)

    final_total = complete_data.labor_cost + items_total
    repair.final_cost = final_total
    repair.status = RepairStatus.COMPLETED
    repair.completed_at = datetime.utcnow()

    device = session.get(Device, repair.device_id)
    if device:
        device.status = DeviceStatus.READY
        session.add(device)

    payment_registered = False
    if final_total > 0:
        payment = Payment(
            repair_id=repair_id,
            amount=final_total,
            payment_method=complete_data.payment_method,
            reference=complete_data.reference,
            notes=complete_data.notes,
            status=PaymentStatus.COMPLETED,
            processed_at=datetime.utcnow()
        )
        session.add(payment)
        payment_registered = True

    session.add(repair)
    session.commit()
    session.refresh(repair)

    return RepairCompleteResponse(
        repair=repair,
        items_total=items_total,
        labor_cost=complete_data.labor_cost,
        final_total=final_total,
        payment_registered=payment_registered
    )


# --- Portal de Cliente ---

@router.get("/portal/{token}", response_model=RepairResponse)
def get_repair_by_portal_token(
    token: str,
    session: Session = Depends(get_session)
):
    """Obtener reparación por token de portal (acceso público para clientes)"""
    from sqlalchemy.orm import selectinload
    repair = session.exec(
        select(Repair)
        .where(Repair.portal_token == token)
        .options(selectinload(Repair.device))
    ).first()
    
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired portal token"
        )
    
    # Verificar que el token no haya expirado
    if repair.portal_token_expires and repair.portal_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Portal token has expired"
        )
        
    return repair


@router.get("/portal/{token}/history", response_model=List[dict])
def get_repair_history_by_portal_token(
    token: str,
    session: Session = Depends(get_session)
):
    """Obtener el historial de cambios de estado por token de portal"""
    repair = session.exec(
        select(Repair).where(Repair.portal_token == token)
    ).first()
    
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired portal token"
        )
        
    logs = session.exec(
        select(RepairLog)
        .where(RepairLog.repair_id == repair.id)
        .order_by(RepairLog.created_at.asc())
    ).all()
    
    return logs


@router.get("/number/{repair_number}", response_model=RepairResponse)
def get_repair_by_number(
    repair_number: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener reparación por número de orden (requiere autenticación)"""
    repair = session.exec(
        select(Repair).where(Repair.repair_number == repair_number)
    ).first()
    
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair not found"
        )
    return repair


@router.put("/portal/{token}/approve", response_model=RepairResponse)
def approve_repair_via_portal(
    token: str,
    session: Session = Depends(get_session)
):
    """Aprobar presupuesto a través del portal del cliente"""
    repair = session.exec(
        select(Repair).where(Repair.portal_token == token)
    ).first()
    
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired portal token"
        )
    
    # Verificar que el token no haya expirado
    if repair.portal_token_expires and repair.portal_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Portal token has expired"
        )
    
    # Solo permitir aprobación si hay un presupuesto definido
    if repair.final_cost is None and repair.estimated_cost is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No cost estimate available for approval"
        )
    
    repair.client_approved = True
    session.add(repair)
    session.commit()
    session.refresh(repair)
    return repair


@router.put("/portal/{token}/reject", response_model=RepairResponse)
def reject_repair_via_portal(
    token: str,
    session: Session = Depends(get_session)
):
    """Rechazar presupuesto a través del portal del cliente"""
    repair = session.exec(
        select(Repair).where(Repair.portal_token == token)
    ).first()
    
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired portal token"
        )
    
    # Verificar que el token no haya expirado
    if repair.portal_token_expires and repair.portal_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Portal token has expired"
        )
    
    repair.client_approved = False
    session.add(repair)
    session.commit()
    session.refresh(repair)
    return repair


@router.get("/partner/my-devices", response_model=List[RepairResponse])
def get_partner_repairs(
    current_user: User = Depends(require_role(UserRole.PARTNER)),
    session: Session = Depends(get_session)
):
    """Listar reparaciones vinculadas al socio comercial autenticado"""
    repairs = session.exec(
        select(Repair)
        .where(Repair.partner_id == current_user.id)
        .order_by(Repair.created_at.desc())
    ).all()
    return repairs

