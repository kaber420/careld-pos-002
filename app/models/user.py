from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.repair import Repair

from app.core.security import SecurityManager


class UserRole(str, Enum):
    """Roles de usuario en el sistema"""
    ADMIN = "admin"           # Acceso total
    TECHNICIAN = "technician" # Puede gestionar reparaciones
    RECEPTIONIST = "receptionist"  # Solo registro y atención
    INVENTORY_MANAGER = "inventory_manager"  # Gestión de inventario
    PARTNER = "partner" # Socio comercial / Mayorista


class UserBase(SQLModel):
    """Campos base de usuario"""
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    email: str = Field(unique=True, index=True)
    full_name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.RECEPTIONIST)
    phone: Optional[str] = Field(default=None, max_length=20)


class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str = Field(min_length=6, max_length=100)


class UserUpdate(SQLModel):
    """Schema para actualizar usuario"""
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase, table=True):
    """Modelo de usuario en la base de datos"""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relación con reparaciones asignadas
    repairs_assigned: list["Repair"] = Relationship(
        back_populates="technician",
        sa_relationship_kwargs={"foreign_keys": "[Repair.technician_id]", "lazy": "selectin"}
    )  # type: ignore

    def verify_password(self, password: str) -> bool:
        """Verificar contraseña"""
        return SecurityManager.verify_password(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashear contraseña"""
        return SecurityManager.hash_password(password)


class Token(SQLModel):
    """Respuesta de token"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(SQLModel):
    """Datos del token"""
    username: Optional[str] = None
    exp: Optional[int] = None
