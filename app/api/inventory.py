from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User
from app.models.inventory import InventoryItem, Category
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    StockAdjustment,
)
from app.core.dependencies import get_current_user, require_role
from app.services.inventory_service import InventoryService

router = APIRouter()


# --- Búsqueda de refacciones para reparaciones ---

@router.get("/search", response_model=List[InventoryItemResponse])
def search_parts(
    q: Optional[str] = Query(None, description="Buscar por nombre o SKU"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Buscar refacciones disponibles para agregar a reparaciones.
    Retorna solo items con stock > 0.
    """
    query = select(InventoryItem).where(
        (InventoryItem.is_active == True) &
        (InventoryItem.stock_quantity > 0)
    )

    if q:
        query = query.where(
            (InventoryItem.name.ilike(f"%{q}%")) |
            (InventoryItem.sku.ilike(f"%{q}%"))
        )

    items = session.exec(query.order_by(InventoryItem.name).limit(limit)).all()
    return items


# --- Categorías ---

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(require_role("admin", "inventory_manager")),
    session: Session = Depends(get_session)
):
    """Crear categoría de inventario"""
    existing = session.exec(
        select(Category).where(Category.name == category_data.name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists"
        )

    category = Category.model_validate(category_data)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.get("/categories", response_model=List[CategoryResponse])
def read_categories(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Listar categorías"""
    categories = session.exec(select(Category)).all()
    return categories


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(require_role("admin", "inventory_manager")),
    session: Session = Depends(get_session)
):
    """Actualizar categoría"""
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


# --- Items de Inventario ---

@router.post("/", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    item_data: InventoryItemCreate,
    current_user: User = Depends(require_role("admin", "inventory_manager")),
    session: Session = Depends(get_session)
):
    """Crear nuevo item de inventario"""
    # Verificar SKU único
    existing = session.exec(
        select(InventoryItem).where(InventoryItem.sku == item_data.sku)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists"
        )

    # Verificar categoría si está presente
    if item_data.category_id:
        category = session.get(Category, item_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    item = InventoryItem.model_validate(item_data)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("/", response_model=List[InventoryItemResponse])
def read_inventory_items(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = Query(None),
    low_stock: bool = Query(False, description="Mostrar solo items con stock bajo"),
    search: Optional[str] = Query(None, description="Buscar por nombre o SKU"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Listar items de inventario"""
    query = select(InventoryItem).where(InventoryItem.is_active == True)

    if category_id:
        query = query.where(InventoryItem.category_id == category_id)

    if low_stock:
        query = query.where(InventoryItem.stock_quantity <= InventoryItem.min_stock)

    if search:
        query = query.where(
            (InventoryItem.name.ilike(f"%{search}%")) |
            (InventoryItem.sku.ilike(f"%{search}%"))
        )

    items = session.exec(query.offset(skip).limit(limit)).all()
    return items


@router.get("/{item_id}", response_model=InventoryItemResponse)
def read_inventory_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener item por ID"""
    item = session.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item


@router.put("/{item_id}", response_model=InventoryItemResponse)
def update_inventory_item(
    item_id: int,
    item_data: InventoryItemUpdate,
    current_user: User = Depends(require_role("admin", "inventory_manager")),
    session: Session = Depends(get_session)
):
    """Actualizar item de inventario"""
    item = session.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    update_data = item_data.model_dump(exclude_unset=True)

    if "sku" in update_data:
        existing = session.exec(
            select(InventoryItem).where(
                (InventoryItem.sku == update_data["sku"]) &
                (InventoryItem.id != item_id)
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU already exists"
            )

    for field, value in update_data.items():
        setattr(item, field, value)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.post("/{item_id}/stock", response_model=InventoryItemResponse)
def adjust_stock(
    item_id: int,
    adjustment: StockAdjustment,
    current_user: User = Depends(require_role("admin", "inventory_manager")),
    session: Session = Depends(get_session)
):
    """Ajustar stock de un item y registrar el movimiento"""
    inventory_service = InventoryService(session)
    try:
        item = inventory_service.adjust_stock(
            item_id=item_id,
            quantity=adjustment.quantity,
            reason=adjustment.reason,
            movement_type=adjustment.type,
            user_id=current_user.id
        )
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        return item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{item_id}")
def delete_inventory_item(
    item_id: int,
    current_user: User = Depends(require_role("admin", "inventory_manager")),
    session: Session = Depends(get_session)
):
    """Eliminar item de inventario (soft delete)"""
    item = session.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    item.is_active = False
    session.add(item)
    session.commit()
    return {"message": "Item deactivated successfully"}
