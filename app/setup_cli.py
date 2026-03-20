import os
import secrets
import string
from typing import Dict, Any

def generate_secret_key(length: int = 50) -> str:
    """Generar una clave secreta aleatoria y segura"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def run_setup():
    """Ejecutar el proceso de configuración interactiva"""
    print("\n" + "="*40)
    print("🛠️  Configuración de CareldPOS")
    print("="*40 + "\n")
    
    # Cargar valores actuales si existen
    current_config = {}
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    current_config[key] = value.strip('"').strip("'")

    # Definir preguntas y valores por defecto
    questions = [
        ("APP_NAME", "Nombre de la aplicación", current_config.get("APP_NAME", "CareldPOS")),
        ("PORT", "Puerto del servidor", current_config.get("PORT", "8100")),
        ("DATABASE_URL", "URL de la base de datos", current_config.get("DATABASE_URL", "sqlite:///./data/repair_shop.db")),
        ("DEBUG", "Modo Debug (true/false)", current_config.get("DEBUG", "true")),
    ]

    new_config = {}
    for key, label, default in questions:
        value = input(f"{label} [{default}]: ").strip()
        new_config[key] = value if value else default

    # Generar SECRET_KEY si no existe o si el usuario quiere una nueva
    existing_secret = current_config.get("SECRET_KEY")
    generate_new = False
    if not existing_secret or existing_secret == "your-secret-key-change-in-production":
        generate_new = True
    else:
        ans = input(f"¿Generar nueva SECRET_KEY? (s/N): ").lower()
        if ans == 's':
            generate_new = True

    if generate_new:
        new_config["SECRET_KEY"] = generate_secret_key()
        print("✅ Nueva SECRET_KEY generada.")
    else:
        new_config["SECRET_KEY"] = existing_secret

    # Otras configuraciones fijas o heredadas
    new_config["ALGORITHM"] = current_config.get("ALGORITHM", "HS256")
    new_config["ACCESS_TOKEN_EXPIRE_MINUTES"] = current_config.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    new_config["REFRESH_TOKEN_EXPIRE_DAYS"] = current_config.get("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    new_config["CORS_ORIGINS"] = current_config.get("CORS_ORIGINS", '["*"]')

    # Guardar en .env
    with open(".env", "w") as f:
        f.write("# Configuración generada automáticamente\n")
        for key, value in new_config.items():
            f.write(f'{key}="{value}"\n')

    # Asegurar que el directorio de datos existe
    if new_config["DATABASE_URL"].startswith("sqlite:///"):
        db_path = new_config["DATABASE_URL"].replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"✅ Directorio de base de datos creado: {db_dir}")

    print("\n" + "="*40)
    print("✨ Configuración completada con éxito.")
    print("📝 Se ha actualizado el archivo .env")
    print("="*40 + "\n")

if __name__ == "__main__":
    run_setup()
