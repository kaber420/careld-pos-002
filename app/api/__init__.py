from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.customers import router as customers_router
from app.api.devices import router as devices_router
from app.api.repairs import router as repairs_router
from app.api.inventory import router as inventory_router
from app.api.payments import router as payments_router
from app.api.uploads import router as uploads_router
from app.api.sales import router as sales_router
from app.api.settings import router as settings_router
from app.api.partners import router as partners_router, admin_router as partners_admin_router

__all__ = [
    "auth_router",
    "users_router",
    "customers_router",
    "devices_router",
    "repairs_router",
    "inventory_router",
    "payments_router",
    "uploads_router",
    "sales_router",
    "settings_router",
    "partners_router",
    "partners_admin_router",
]
