#!/bin/bash

# Script de configuración automatizada para CareldPOS
# Este script prepara el entorno de desarrollo (Python y Frontend)

set -e # Salir en caso de error

# Colores para la terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}   🚀 Configuración de CareldPOS      ${NC}"
echo -e "${BLUE}======================================${NC}"

# 1. Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 no está instalado.${NC}"
    exit 1
fi

# 2. Entorno Virtual de Python
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creando entorno virtual (venv)...${NC}"
    python3 -m venv venv
else
    echo -e "${GREEN}Entorno virtual 'venv' detectado.${NC}"
fi

# 3. Instalar dependencias de Python
echo -e "${YELLOW}Instalando dependencias de Python...${NC}"
source venv/bin/activate
pip install -e .
echo -e "${GREEN}Dependencias de Python instaladas correctamente.${NC}"

# 4. Verificar Node.js y pnpm
echo -e "${YELLOW}Verificando entorno de Frontend...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Aviso: Node.js no está instalado. El frontend no se podrá compilar.${NC}"
else
    if ! command -v pnpm &> /dev/null; then
        echo -e "${YELLOW}pnpm no detectado. Intentando usar npm...${NC}"
        PACKAGE_MANAGER="npm"
    else
        PACKAGE_MANAGER="pnpm"
    fi

    echo -e "${GREEN}Usando ${PACKAGE_MANAGER} para el frontend.${NC}"
    
    # 5. Instalar dependencias del Frontend
    echo -e "${YELLOW}Instalando dependencias del Frontend en 'frontend/'...${NC}"
    cd frontend
    $PACKAGE_MANAGER install
    cd ..
    echo -e "${GREEN}Dependencias del Frontend instaladas.${NC}"

    # 6. Build opcional
    read -p "¿Deseas compilar el frontend ahora? (s/N): " build_choice
    if [[ "$build_choice" =~ ^[Ss]$ ]]; then
        cd frontend
        $PACKAGE_MANAGER run build
        cd ..
        echo -e "${GREEN}Frontend compilado en 'frontend/dist'.${NC}"
    fi
fi

# 7. Configuración opcional (--setup)
read -p "¿Deseas correr la configuración interactiva de la aplicación? (s/N): " setup_choice
if [[ "$setup_choice" =~ ^[Ss]$ ]]; then
    ./venv/bin/python3 run.py --setup
fi

echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}✨ ¡Configuración completada con éxito!${NC}"
echo -e "Puedes iniciar la app con: ${YELLOW}careldpos${NC}"
echo -e "${BLUE}======================================${NC}"
