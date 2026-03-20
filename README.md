# CareldPOS

Sistema de punto de venta y gestión para taller de reparación de dispositivos inteligentes.

## 🚀 Características

- **Autenticación JWT** con roles (admin, technician, receptionist, inventory_manager)
- **Gestión de clientes** - CRUD completo
- **Gestión de dispositivos** - Registro por cliente
- **Órdenes de reparación** - Seguimiento de estados, prioridades, técnicos asignados
- **Inventario** - Control de repuestos, categorías, alertas de stock bajo
- **Pagos** - Múltiples métodos, estados, resumen por reparación

## 📁 Estructura del Proyecto

```
fastapi_auth_app/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada
│   ├── config.py            # Configuración
│   ├── database.py          # Conexión BD
│   ├── models/              # Modelos SQLModel
│   │   ├── user.py          # Usuarios y roles
│   │   ├── customer.py      # Clientes
│   │   ├── device.py        # Dispositivos
│   │   ├── repair.py        # Órdenes de reparación
│   │   ├── inventory.py     # Inventario
│   │   └── payment.py       # Pagos
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # Routers/Endpoints
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── customers.py
│   │   ├── devices.py
│   │   ├── repairs.py
│   │   ├── inventory.py
│   │   └── payments.py
│   ├── services/            # Lógica de negocio
│   │   ├── auth.py
│   │   ├── repair_service.py
│   │   ├── inventory_service.py
│   │   └── payment_service.py
│   └── core/                # Utilidades core
│       ├── security.py      # JWT, hashing
│       └── dependencies.py  # Dependencies FastAPI
├── tests/
├── static/
├── .env
├── .env.example
└── requirements.txt
```

## 🛠️ Instalación

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Copiar configuración
cp .env.example .env
```

## ▶️ Ejecutar

```bash
source venv/bin/activate
python run.py
```

Accede a:
- **API Docs**: http://localhost:8100/docs
- **ReDoc**: http://localhost:8100/redoc
- **Root**: http://localhost:8100

## 📚 Endpoints

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Registrar usuario |
| POST | `/api/v1/auth/login` | Login (obtener token) |
| POST | `/api/v1/auth/refresh` | Refrescar token |

### Usuarios
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Perfil actual |
| PUT | `/api/v1/users/me` | Actualizar perfil |
| GET | `/api/v1/users/` | Listar usuarios (admin) |
| GET | `/api/v1/users/{id}` | Ver usuario (admin) |
| PATCH | `/api/v1/users/{id}` | Editar usuario (admin) |
| DELETE | `/api/v1/users/{id}` | Eliminar usuario (admin) |

### Clientes
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/customers/` | Crear cliente |
| GET | `/api/v1/customers/` | Listar clientes |
| GET | `/api/v1/customers/{id}` | Ver cliente |
| PUT | `/api/v1/customers/{id}` | Actualizar cliente |
| DELETE | `/api/v1/customers/{id}` | Eliminar cliente |

### Dispositivos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/devices/` | Registrar dispositivo |
| GET | `/api/v1/devices/` | Listar dispositivos |
| GET | `/api/v1/devices/{id}` | Ver dispositivo |
| PUT | `/api/v1/devices/{id}` | Actualizar dispositivo |
| DELETE | `/api/v1/devices/{id}` | Eliminar dispositivo |

### Reparaciones
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/repairs/` | Crear orden |
| GET | `/api/v1/repairs/` | Listar reparaciones |
| GET | `/api/v1/repairs/{id}` | Ver reparación |
| PUT | `/api/v1/repairs/{id}` | Actualizar reparación |
| DELETE | `/api/v1/repairs/{id}` | Eliminar reparación |
| POST | `/api/v1/repairs/{id}/items` | Agregar repuesto |
| GET | `/api/v1/repairs/{id}/items` | Ver items |

### Inventario
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/inventory/` | Crear item |
| GET | `/api/v1/inventory/` | Listar items |
| POST | `/api/v1/inventory/categories` | Crear categoría |
| GET | `/api/v1/inventory/categories` | Listar categorías |
| POST | `/api/v1/inventory/{id}/stock` | Ajustar stock |

### Pagos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/payments/` | Registrar pago |
| GET | `/api/v1/payments/` | Listar pagos |
| POST | `/api/v1/payments/{id}/complete` | Completar pago |
| GET | `/api/v1/payments/repair/{id}/summary` | Resumen pagos |

## 🔐 Roles

- **admin** - Acceso total al sistema
- **technician** - Gestionar reparaciones asignadas
- **receptionist** - Registro de clientes y dispositivos
- **inventory_manager** - Gestión de inventario

## 📝 Ejemplos de Uso

### Registrar usuario
```bash
curl -X POST "http://localhost:8100/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@taller.com",
    "full_name": "Administrador",
    "password": "admin123",
    "role": "admin"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8100/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Crear cliente (con token)
```bash
curl -X POST "http://localhost:8100/api/v1/customers/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <tu_token>" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan@email.com",
    "phone": "555-1234"
  }'
```

## 🔧 Configuración

Editar `.env`:

```env
SECRET_KEY=tu-clave-secreta-min-32-caracteres
DATABASE_URL=sqlite:///./data/repair_shop.db
PORT=8100
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🧪 Tests

```bash
pytest
```

## 📄 Licencia

AGPL-3.0

