# Plan de Proyecto: POS Integral y Sistema de Impresión de Tickets

**Objetivo:** Evolucionar la interfaz actual del sistema hacia un Punto de Venta (POS) completo que gestione ventas directas, cobro de reparaciones y un sistema automatizado de generación e impresión de tickets térmicos para talleres.

---

## 1. Módulo POS Integral (Ventas y Entregas)

El POS dejará de ser únicamente informativo para convertirse en una caja registradora funcional.

### Funcionalidades Clave
1. **Venta de Accesorios y Refacciones:**
   - Interfaz con un "Carrito de Compras" en el panel derecho.
   - Panel izquierdo con catálogo de productos visuales (accesorios, cargadores, fundas) y buscador rápido.
   - Posibilidad de vender refacciones a otros técnicos con "Precio de Técnico" (aplicando descuentos).
2. **Cobro y Entrega de Dispositivos:**
   - Poder buscar una Orden de Reparación que ya está "Lista para entregar".
   - Al seleccionarla, el saldo pendiente se agrega automáticamente al carrito del POS.
   - Al procesar el pago, el estado del dispositivo cambia a "Entregado".
3. **Gestión de Pagos:**
   - Selección de métodos de pago (Efectivo, Tarjeta, Transferencia).
   - Cálculo de cambio exacto.

### Cambios Técnicos Necesarios
- **Backend:** Crear modelos de base de datos para `Sale` (Venta) y `SaleItem` (Artículos de venta), ya que actualmente el sistema parece girar únicamente en torno a `Repair`.
- **Frontend:** Rediseñar `POS.svelte` para tener un diseño clásico de caja registradora.

---

## 2. Sistema de Impresión de Tickets (Órdenes y Ventas)

Implementar un diseño orientado a **Impresoras Térmicas (58mm o 80mm)**, utilizando CSS de impresión (`@media print`) para evitar que el usuario deba instalar software pesado.

### A. Tickets de Venta / Recibos
- Se imprimen al finalizar una venta en el POS o al cobrar una reparación.
- **Contenido:** Logo del negocio, fecha, productos/servicios, total, método de pago y mensaje de agradecimiento.

### B. Tickets de Orden de Trabajo (Ingreso de Dispositivo)
Al momento de registrar un nuevo dispositivo para reparación, el sistema lanzará automáticamente la impresión de **dos tickets distintos**:

1. **Ticket de Control (Para pegar en el dispositivo):**
   - Tamaño optimizado y compacto.
   - Contiene: Número de Orden, Nombre corto del cliente, Modelo del dispositivo, Fallo principal.
   - *Opcional:* Un código de barras o QR para escanearlo posteriormente en el POS y encontrar la orden rápidamente.

2. **Ticket del Cliente (Comprobante):**
   - Contiene: Datos completos del taller, información del dispositivo ingresado, fallos reportados, fecha estimada y cotización (si aplica).
   - **Código QR de Seguimiento:** Un QR grande que, al ser escaneado por el cliente con su celular, lo lleve al "Portal del Cliente" para ver el estado de su reparación en tiempo real.
   - Términos y condiciones del servicio (Letras pequeñas, ej: "Pasados 30 días no nos hacemos responsables...").

### Cambios Técnicos Necesarios
- **Frontend:**
  - Crear un componente invisible en pantalla pero visible para impresión (ej: `PrintLayout.svelte`).
  - Utilizar estilos CSS rigurosos para impresoras térmicas (ancho fijo en milímetros, fuentes sin serifas, remover márgenes del navegador).
  - Al completar una acción (Nueva Orden o Nueva Venta), llamar a `window.print()` inyectando los datos temporalmente.
- **Generación de QR:** Integrar una librería genérica de JavaScript para generar el QR en el frontend justo antes de imprimir, evitando peticiones pesadas al backend.

---

## 3. Fases de Desarrollo Sugeridas

1. **Fase 1: Preparación del Backend para Ventas:** 
   - Crear tablas `Sale`, `SaleItem`. 
   - Definir endpoints de ventas y enlazar el stock (reducir inventario al vender).
2. **Fase 2: Interfaz POS:** 
   - Reestructurar el carrito de la compra. 
   - Integrar la búsqueda de accesorios y órdenes.
3. **Fase 3: Layouts de Impresión:** 
   - Maquetación HTML/CSS de los 3 formatos (Ticket de Venta, Etiqueta Técnica, Comprobante Cliente).
4. **Fase 4: Integración del Flujo Automático:** 
   - Unir la creación de reparaciones/ventas con el disparador automático de `window.print()`.

---
*Nota: Este documento es un borrador (draft). Puedes solicitarme que comencemos a ejecutar cualquiera de estas fases cuando lo desees.*
