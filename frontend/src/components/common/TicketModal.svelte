<script>
  import { onMount } from 'svelte';
  import QRCode from 'qrcode';
  import { publicSettings } from '../../stores/settings';

  export let show = false;
  export let ticketData = null;
  export let onClose = () => {};
  export let autoPrint = false;

  let printClass = '';
  let qrCodeUrl = '';
  let paperWidth = '80mm'; // Default

  $: if (show && ticketData) {
    if (ticketData.repair && ticketData.repair.portal_token) {
      generateQR();
    } else if (ticketData.qrCode) {
      qrCodeUrl = ticketData.qrCode;
    }
    
    if (autoPrint) {
      setTimeout(() => {
        window.print();
      }, 500);
    }
  }

  async function generateQR() {
    try {
      // Usar variable de entorno o fallback a origin
      const baseUrl = $publicSettings.portal_url || window.location.origin;
      const portalUrl = `${baseUrl}/portal/${ticketData.repair.portal_token}`;
      
      qrCodeUrl = await QRCode.toDataURL(portalUrl, { 
        width: 300,
        margin: 2,
        errorCorrectionLevel: 'M',
        color: {
          dark: '#000000',
          light: '#ffffff'
        }
      });
    } catch (err) {
      console.error('Error generating QR:', err);
    }
  }

  function handlePrint(target) {
    printClass = target;
    setTimeout(() => {
      window.print();
    }, 150);
  }

  if (typeof window !== 'undefined') {
    window.onafterprint = () => { printClass = ''; };
  }
</script>

{#if show && ticketData}
<div class="custom-modal-overlay" on:click|self={onClose}>
  <div class="custom-modal modal-md">
    <div class="custom-modal-header">
      <div>
        <h3 class="custom-modal-title">Impresión de Ticket</h3>
        <div style="display: flex; gap: 1rem; align-items: center; margin-top: 0.25rem;">
           <p class="modal-subtitle" style="margin: 0;">Vista previa</p>
           <select class="select select-sm" bind:value={paperWidth} style="padding: 2px 8px; font-size: 0.75rem;">
             <option value="80mm">Papel 80mm</option>
             <option value="58mm">Papel 58mm</option>
           </select>
        </div>
      </div>
      <button class="custom-modal-close" on:click={onClose}>×</button>
    </div>
    
    <div class="custom-modal-body {printClass} {paperWidth === '58mm' ? 'w-58mm' : 'w-80mm'}" style="background: var(--light); padding: 2rem; max-height: 70vh; overflow-y: auto;">
      <div id="ticket-content" class="ticket">
        {#if ticketData.type === 'recepcion' || ticketData.type === 'etiqueta_full'}
          <!-- TICKET DE RECEPCION -->
          <div class="ticket-page" id="printable-receipt">
            <div class="ticket-header">
              <h2>{$publicSettings.store_name || 'CareldPOS'}</h2>
              <p class="text-sm">Orden de Servicio: {ticketData.repair?.repair_number || 'N/A'}</p>
              <p>Fecha: {new Date(ticketData.date || Date.now()).toLocaleString()}</p>
            </div>

            <div class="ticket-section">
              <p><strong>Cliente:</strong> {ticketData.customer?.name || 'Cliente'}</p>
              <p><strong>Teléfono:</strong> {ticketData.customer?.phone || 'N/A'}</p>
            </div>

            <div class="ticket-section">
              <div class="ticket-title">DATOS DEL EQUIPO</div>
              <p><strong>Equipo:</strong> {ticketData.device?.brand} {ticketData.device?.model}</p>
              <p><strong>Tipo:</strong> {ticketData.device?.device_type || 'Dispositivo'}</p>
              <p><strong>S/N:</strong> {ticketData.device?.serial_number || 'N/A'}</p>
              <p><strong>Color:</strong> {ticketData.device?.color || 'N/A'}</p>
              <p><strong>Contraseña:</strong> {ticketData.device?.password_pattern || 'N/A'}</p>
            </div>

            <div class="ticket-section">
              <div class="ticket-title">TRABAJO A REALIZAR</div>
              <p class="italic">{ticketData.repair?.description || ticketData.device?.description || 'Revisión general'}</p>
            </div>

            {#if qrCodeUrl}
              <div class="ticket-qr">
                <img src={qrCodeUrl} alt="QR de seguimiento" />
                <p class="text-xs mt-2">Escanee para consultar estado</p>
                <p class="text-xs font-bold mt-1">{$publicSettings.portal_url || window.location.host.toUpperCase()}</p>
              </div>
            {/if}

            <div class="ticket-footer">
              <p class="text-xs">{$publicSettings.ticket_footer || 'Conserve este ticket para recoger su equipo.'}</p>
              <p class="text-xs">No nos hacemos responsables por equipos olvidados después de 30 días.</p>
              <p class="mt-2 font-bold">¡Gracias por su preferencia!</p>
            </div>
          </div>

          <!-- ETIQUETA PARA EL DISPOSITIVO -->
          <div class="ticket-page ticket-label" id="printable-label">
            <div class="label-border">
              <div class="label-header">
                <span class="label-id">ID: {ticketData.repair?.repair_number?.split('-').pop() || '000'}</span>
                <span class="label-date">{new Date(ticketData.date || Date.now()).toLocaleDateString()}</span>
              </div>
              <div class="label-body">
                <div class="label-row"><strong>CLTE:</strong> {ticketData.customer?.name?.substring(0, 20) || 'Cliente'}</div>
                <div class="label-row"><strong>EQP:</strong> {ticketData.device?.brand} {ticketData.device?.model}</div>
                <div class="label-row"><strong>FLA:</strong> {(ticketData.repair?.description || ticketData.device?.description)?.substring(0, 40) || 'REVISAR'}</div>
              </div>
            </div>
          </div>
        {/if}

        {#if ticketData.type === 'venta'}
          <div class="ticket-page" id="printable-sale">
            <div class="ticket-header">
              <h2>{$publicSettings.store_name || 'CareldPOS'}</h2>
              <p class="text-sm">Comprobante de Pago</p>
              <p>No. Venta: {ticketData.sale_number || 'TEMP'}</p>
              <p>Fecha: {new Date(ticketData.date || Date.now()).toLocaleString()}</p>
            </div>

            <div class="ticket-section">
              <p><strong>Cliente:</strong> {ticketData.customer?.name || 'Público General'}</p>
            </div>

            <table class="ticket-table">
              <thead>
                <tr>
                  <th class="text-center">Cant</th>
                  <th>Descripción</th>
                  <th class="text-right">Total</th>
                </tr>
              </thead>
              <tbody>
                {#if ticketData.items}
                  {#each ticketData.items as item}
                    <tr>
                      <td class="text-center">{item.quantity}</td>
                      <td>{item.name} <br/> <small>${item.sale_price.toFixed(2)} c/u</small></td>
                      <td class="text-right">${item.subtotal.toFixed(2)}</td>
                    </tr>
                  {/each}
                {/if}
              </tbody>
            </table>

            <div class="ticket-total-section">
              <div class="total-row">
                <span>TOTAL</span>
                <span>${ticketData.total?.toFixed(2) || '0.00'}</span>
              </div>
            </div>

            <div class="ticket-footer mt-4">
              <p class="text-xs">*** Gracias por su compra ***</p>
              <p class="text-xs">Garantía de 30 días en refacciones por defectos de fábrica.</p>
            </div>
          </div>
        {/if}
      </div>
    </div>

    <div class="custom-modal-footer" style="justify-content: space-between;">
      <button class="btn btn-outline" on:click={onClose}>Cerrar</button>
      <div style="display: flex; gap: 0.5rem;">
        {#if ticketData.type === 'recepcion' || ticketData.type === 'etiqueta_full'}
          <button class="btn btn-secondary" on:click={() => handlePrint('print-receipt-only')}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 16px;">
              <path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2M6 14h12v8H6v-8z"/>
            </svg>
            Recibo
          </button>
          <button class="btn btn-secondary" on:click={() => handlePrint('print-label-only')}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 16px;">
              <path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2M6 14h12v8H6v-8z"/>
            </svg>
            Etiqueta
          </button>
        {:else if ticketData.type === 'venta'}
          <button class="btn btn-secondary" on:click={() => handlePrint('print-sale-only')}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 16px;">
              <path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2M6 14h12v8H6v-8z"/>
            </svg>
            Venta
          </button>
        {/if}
        <button class="btn btn-primary" on:click={() => window.print()}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 16px;">
            <path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2M6 14h12v8H6v-8z"/>
          </svg>
          Imprimir Todo
        </button>
      </div>
    </div>
  </div>
</div>
{/if}

<style>
  .ticket {
    font-family: 'Courier New', monospace;
    padding: 0;
    background: white;
    color: #000;
  }

  .ticket-page {
    padding: 1rem;
    background: white;
    width: var(--ticket-width, 80mm);
    margin: 0 auto;
    border: 1px dashed #ccc;
    margin-bottom: 2rem;
  }

  .ticket-label {
    width: var(--ticket-width, 80mm);
    padding: 5mm;
    border: 1px dashed #ccc;
    page-break-before: always;
  }

  .w-58mm { --ticket-width: 58mm; }
  .w-80mm { --ticket-width: 80mm; }

  .label-border {
    border: 2px solid #000;
    padding: 2mm;
    border-radius: 2mm;
  }
  
  .label-header {
    display: flex;
    justify-content: space-between;
    border-bottom: 1px solid #000;
    padding-bottom: 1mm;
    margin-bottom: 1mm;
    font-weight: bold;
    font-size: 1.1rem;
  }

  .label-body {
    font-size: 0.8rem;
    line-height: 1.2;
  }

  .label-row {
    margin-bottom: 1mm;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .ticket-qr {
    text-align: center;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px dashed #000;
  }

  .ticket-qr img {
    max-width: 140px;
    height: auto;
  }

  .ticket-header {
    text-align: center;
    border-bottom: 2px dashed #000;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
  }

  .ticket-header h2 {
    margin: 0;
    font-size: 1.5rem;
  }

  .ticket-title {
    text-align: center;
    background: #000;
    color: #fff;
    padding: 0.25rem;
    margin-bottom: 0.5rem;
    font-size: 0.8rem;
    font-weight: bold;
  }

  .ticket-section {
    margin-bottom: 1rem;
    font-size: 0.85rem;
    line-height: 1.4;
  }

  .ticket-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;
  }

  .ticket-table th {
    border-bottom: 2px solid #000;
    padding: 0.25rem;
  }

  .ticket-table td {
    padding: 0.5rem 0.25rem;
    border-bottom: 1px dashed #666;
    vertical-align: top;
  }

  .ticket-total-section {
    margin-top: 1rem;
    border-top: 2px solid #000;
    padding-top: 0.5rem;
  }

  .total-row {
    display: flex;
    justify-content: space-between;
    font-size: 1.2rem;
    font-weight: bold;
  }

  .ticket-footer {
    text-align: center;
    padding-top: 1rem;
    border-top: 1px dashed #000;
    margin-top: 1rem;
  }

  .mt-2 { margin-top: 0.5rem; }
  .mt-4 { margin-top: 1rem; }
  .text-xs { font-size: 0.7rem; }
  .text-sm { font-size: 0.8rem; }
  .text-right { text-align: right; }
  .text-center { text-align: center; }
  .font-bold { font-weight: bold; }
  .italic { font-style: italic; }

  @media print {
    @page {
      margin: 0;
      size: auto;
    }
    
    /* Aislamiento total del ERP */
    :global(body > *:not(.custom-modal-overlay)) {
      display: none !important;
    }
    
    :global(.custom-modal-overlay) {
      background: white !important;
      position: absolute !important;
      top: 0 !important;
      left: 0 !important;
      width: 100% !important;
      height: auto !important;
      display: block !important;
      padding: 0 !important;
      margin: 0 !important;
    }
    
    :global(.custom-modal-overlay > *:not(.custom-modal)) {
      display: none !important;
    }

    .custom-modal {
      border: none !important;
      box-shadow: none !important;
      width: 100% !important;
      max-width: none !important;
      margin: 0 !important;
      padding: 0 !important;
      background: white !important;
    }
    
    .custom-modal-header, .custom-modal-footer, .custom-modal-close {
      display: none !important;
    }

    #ticket-content {
      display: block !important;
      width: 100% !important;
    }

    .ticket-page, .ticket-label {
      border: none !important;
      margin-bottom: 0 !important;
      width: var(--ticket-width, 80mm) !important;
      padding: 5mm !important;
    }

    /* Reglas de visibilidad específica */
    .print-receipt-only #printable-label { display: none !important; }
    .print-receipt-only #printable-sale { display: none !important; }
    
    .print-label-only #printable-receipt { display: none !important; }
    .print-label-only #printable-sale { display: none !important; }
    
    .print-sale-only #printable-receipt { display: none !important; }
    .print-sale-only #printable-label { display: none !important; }

    /* Forzar visibilidad si el printClass está vacío (Imprimir Todo) */
    .custom-modal-body:not(.print-receipt-only):not(.print-label-only):not(.print-sale-only) .ticket-page {
       display: block !important;
    }
  }

  .modal-subtitle {
    font-size: 0.875rem;
    color: var(--text-light);
    margin-top: 0.25rem;
  }
</style>
