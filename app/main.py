from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.database import create_db_and_tables
import os
import app.models # Asegurar registro de modelos
from app.api import (
    auth_router,
    users_router,
    customers_router,
    devices_router,
    repairs_router,
    inventory_router,
    payments_router,
    uploads_router,
    sales_router,
    settings_router,
    partners_router,
    partners_admin_router,
)
from app.api.settings import seed_settings
from app.database import SessionLocal

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema POS para taller de reparación de dispositivos",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.on_event("startup")
def on_startup():
    """Crear tablas de BD al iniciar"""
    create_db_and_tables()
    
    # Sembrar configuraciones por defecto
    with SessionLocal() as session:
        print("🌱 Iniciando siembra de configuraciones...") # Added print statement
        seed_settings(session)
    
    # Crear directorio de uploads si no existe
    os.makedirs("data/uploads", exist_ok=True)
    
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} iniciado en puerto {settings.PORT}")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Incluir routers (ANTES del mount de static files)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Usuarios"])
app.include_router(customers_router, prefix="/api/v1/customers", tags=["Clientes"])
app.include_router(devices_router, prefix="/api/v1/devices", tags=["Dispositivos"])
app.include_router(repairs_router, prefix="/api/v1/repairs", tags=["Reparaciones"])
app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventario"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["Pagos"])
app.include_router(sales_router, prefix="/api/v1/sales", tags=["Ventas"])
app.include_router(uploads_router, prefix="/api/v1/uploads", tags=["Archivos"])
app.include_router(settings_router, prefix="/api/v1/settings", tags=["Configuración"])
app.include_router(partners_router, prefix="/api/v1", tags=["Socio"])
app.include_router(partners_admin_router, prefix="/api/v1", tags=["Admin - Socios"])


@app.get("/health", tags=["Health"])
def health_check():
    """Verificar estado de la aplicación"""
    return {"status": "healthy", "version": settings.APP_VERSION}


# Montar archivos estáticos del frontend (después del build)
STATIC_DIR = "frontend/dist"
if os.path.exists(STATIC_DIR) and os.path.isdir(STATIC_DIR):
    # Montar el directorio static del build
    app.mount("/static", StaticFiles(directory=f"{STATIC_DIR}/static"), name="static")
    # Servir index.html para la raíz
    @app.get("/")
    async def serve_frontend():
        return FileResponse(f"{STATIC_DIR}/index.html")

    # SPA catch-all route - servir index.html para todas las rutas del frontend
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # No servir para rutas de API o docs
        if (full_path.startswith("api/") or
            full_path in ["docs", "redoc", "openapi.json"] or
            full_path.startswith("static/")):
            return {"detail": "Not found"}
        return FileResponse(f"{STATIC_DIR}/index.html")
else:
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
    except RuntimeError:
        pass  # Directorio no existe aún
