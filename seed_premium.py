import os
import sys

# Añadir el directorio actual al path para importar 'app'
sys.path.append(os.getcwd())

from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.database import engine, create_db_and_tables
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.device import Device, DeviceType
from app.models.repair import Repair, RepairStatus, RepairLog

def seed():
    print("🌱 Iniciando siembra de datos de prueba...")
    
    # Asegurar que las tablas existan
    create_db_and_tables()
    
    with Session(engine) as session:
        # 1. Crear Usuarios si no existen
        admin = session.exec(select(User).where(User.username == "admin")).first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                full_name="Administrador del Sistema",
                role=UserRole.ADMIN,
                hashed_password=User.hash_password("admin123")
            )
            session.add(admin)
            print("✅ Usuario Admin creado.")

        partner = session.exec(select(User).where(User.username == "socio_premium")).first()
        if not partner:
            partner = User(
                username="socio_premium",
                email="socio@tecnicos.com",
                full_name="Socio Premium Tech",
                role=UserRole.PARTNER,
                hashed_password=User.hash_password("socio123")
            )
            session.add(partner)
            print("✅ Usuario Partner creado.")
        
        # Guardar para obtener IDs
        session.commit()
        session.refresh(admin)
        session.refresh(partner)

        # 2. Crear Cliente
        customer = session.exec(select(Customer).where(Customer.phone == "555123456")).first()
        if not customer:
            customer = Customer(
                name="Juan Perez",
                phone="555123456",
                email="juan@gmail.com",
                address="Calle Principal 123"
            )
            session.add(customer)
            print("✅ Cliente Juan Perez creado.")
        
        session.commit()
        session.refresh(customer)

        # 3. Crear Dispositivos
        d1 = Device(
            brand="Apple",
            model="iPhone 15 Pro",
            serial_number="SN-IPH15-001",
            type=DeviceType.SMARTPHONE,
            customer_id=customer.id
        )
        d2 = Device(
            brand="Apple",
            model="MacBook Air M2",
            serial_number="SN-MACB-9988",
            type=DeviceType.LAPTOP,
            customer_id=customer.id # También para Juan
        )
        session.add(d1)
        session.add(d2)
        session.commit()
        session.refresh(d1)
        session.refresh(d2)

        # 4. Crear Reparaciones
        r1 = Repair(
            repair_number="REP-20260320-0001",
            description="Cambio de pantalla por golpe",
            device_id=d1.id,
            technician_id=admin.id,
            status=RepairStatus.DIAGNOSING,
            estimated_cost=250.0,
            portal_token="tok_juan_123",
            portal_token_expires=datetime.utcnow() + timedelta(days=30)
        )
        
        r2 = Repair(
            repair_number="REP-PARTNER-0001",
            description="Mantenimiento preventivo",
            device_id=d2.id,
            technician_id=admin.id,
            partner_id=partner.id, # Vinculado al socio
            status=RepairStatus.COMPLETED,
            final_cost=150.0,
            portal_token="tok_socio_456",
            portal_token_expires=datetime.utcnow() + timedelta(days=30)
        )
        
        session.add(r1)
        session.add(r2)
        session.commit()
        session.refresh(r1)
        session.refresh(r2)

        # 5. Crear Logs de Historial
        logs = [
            RepairLog(repair_id=r1.id, from_status=RepairStatus.PENDING, to_status=RepairStatus.PENDING, description="Equipo ingresado al taller", technician_id=admin.id),
            RepairLog(repair_id=r1.id, from_status=RepairStatus.PENDING, to_status=RepairStatus.DIAGNOSING, description="El técnico inició el diagnóstico detallado", technician_id=admin.id),
            
            RepairLog(repair_id=r2.id, from_status=RepairStatus.PENDING, to_status=RepairStatus.PENDING, description="Equipo recibido de socio comercial", technician_id=admin.id),
            RepairLog(repair_id=r2.id, from_status=RepairStatus.PENDING, to_status=RepairStatus.IN_PROGRESS, description="Reparación en curso", technician_id=admin.id),
            RepairLog(repair_id=r2.id, from_status=RepairStatus.IN_PROGRESS, to_status=RepairStatus.COMPLETED, description="Equipo listo para entrega", technician_id=admin.id),
        ]
        
        for l in logs:
            session.add(l)
            
        session.commit()
        print("🚀 Datos de prueba sembrados correctamente.")
        print("\nPara probar el portal de cliente:")
        print(f"http://localhost:5173/portal/tok_juan_123")
        print("\nPara probar el dashboard de socio (inicia sesión como socio_premium / socio123):")
        print(f"http://localhost:5173/partner-dashboard")

if __name__ == "__main__":
    seed()
