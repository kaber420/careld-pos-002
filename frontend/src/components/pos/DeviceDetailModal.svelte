<script>
  export let show = false;
  export let device = null;
  export let customer = null;
  export let repairs = [];
  export let onClose = () => {};
  export let onEdit = () => {};
  export let onStatusChange = () => {};

  const statusLabels = {
    registered: 'Registrado',
    in_repair: 'En Reparación',
    waiting_parts: 'Esperando Repuestos',
    ready: 'Listo para Entrega',
    delivered: 'Entregado'
  };

  const statusColors = {
    registered: 'badge-secondary',
    in_repair: 'badge-primary',
    waiting_parts: 'badge-warning',
    ready: 'badge-success',
    delivered: 'badge-success'
  };

  const deviceIcons = {
    smartphone: '📱',
    tablet: '📟',
    laptop: '💻',
    desktop: '🖥️',
    smartwatch: '⌚',
    console: '🎮',
    other: '📦'
  };

  function getDeviceIcon() {
    return deviceIcons[device?.device_type] || deviceIcons.other;
  }

  function getPhotos() {
    if (!device?.photos) return [];
    return device.photos.split(',').map(p => p.trim()).filter(p => p);
  }

  function formatDate(dateString) {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

{#if show && device}
<div 
  class="custom-modal-overlay" 
  on:click|self={onClose}
  style="position: fixed !important; inset: 0 !important; background: rgba(0,0,0,0.7) !important; z-index: 99999 !important; display: flex !important; align-items: center !important; justify-content: center !important; pointer-events: auto !important;"
>
    <div class="custom-modal modal-xl device-detail-modal">
      <div class="custom-modal-header">
        <div class="header-left">
          <span class="device-icon-large">{getDeviceIcon()}</span>
          <div>
            <h3 class="custom-modal-title">{device.brand} {device.model}</h3>
            <span class="badge {statusColors[device.status]}">
              {statusLabels[device.status]}
            </span>
          </div>
        </div>
        <button class="custom-modal-close" on:click={onClose}>×</button>
      </div>

      <div class="custom-modal-body">
        <div class="detail-grid">
          <!-- Información del cliente -->
          <div class="detail-card">
            <h4 class="detail-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              Cliente
            </h4>
            {#if customer}
              <div class="detail-content">
                <p><strong>Nombre:</strong> {customer.name}</p>
                <p><strong>Teléfono:</strong> {customer.phone}</p>
                {#if customer.email}
                  <p><strong>Email:</strong> {customer.email}</p>
                {/if}
                {#if customer.address}
                  <p><strong>Dirección:</strong> {customer.address}</p>
                {/if}
              </div>
            {:else}
              <p class="text-muted">Cliente no disponible</p>
            {/if}
          </div>

          <!-- Información del dispositivo -->
          <div class="detail-card">
            <h4 class="detail-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="2" width="20" height="8" rx="2" ry="2"/>
                <rect x="2" y="14" width="20" height="8" rx="2" ry="2"/>
                <line x1="6" y1="6" x2="6.01" y2="6"/>
                <line x1="6" y1="18" x2="6.01" y2="18"/>
              </svg>
              Dispositivo
            </h4>
            <div class="detail-content">
              {#if device.device_type}
                <p><strong>Tipo:</strong> {device.device_type}</p>
              {/if}
              {#if device.color}
                <p><strong>Color:</strong> {device.color}</p>
              {/if}
              {#if device.storage}
                <p><strong>Almacenamiento:</strong> {device.storage}</p>
              {/if}
              {#if device.serial_number}
                <p><strong>S/N:</strong> {device.serial_number}</p>
              {/if}
              {#if device.imei}
                <p><strong>IMEI:</strong> {device.imei}</p>
              {/if}
            </div>
          </div>

          <!-- Accesorios y patrón -->
          <div class="detail-card">
            <h4 class="detail-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
              </svg>
              Accesorios y Seguridad
            </h4>
            <div class="detail-content">
              {#if device.accessories}
                <p><strong>Accesorios:</strong> {device.accessories}</p>
              {:else}
                <p class="text-muted">Sin accesorios</p>
              {/if}
              {#if device.password_pattern}
                <p><strong>Patrón:</strong> {device.password_pattern}</p>
              {/if}
            </div>
          </div>

          <!-- Fechas -->
          <div class="detail-card">
            <h4 class="detail-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              Fechas
            </h4>
            <div class="detail-content">
              <p><strong>Creado:</strong> {formatDate(device.created_at)}</p>
              <p><strong>Actualizado:</strong> {formatDate(device.updated_at)}</p>
            </div>
          </div>
        </div>

        <!-- Fotos -->
        {#if getPhotos().length > 0}
          <div class="photos-section">
            <h4 class="section-title">Fotos del dispositivo</h4>
            <div class="photos-grid">
              {#each getPhotos() as photo}
                <div class="photo-item">
                  <img src={photo} alt="Foto del dispositivo" />
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Reparaciones asociadas -->
        {#if repairs && repairs.length > 0}
          <div class="repairs-section">
            <h4 class="section-title">Reparaciones asociadas</h4>
            <div class="repairs-list">
              {#each repairs as repair}
                <div class="repair-item">
                  <div class="repair-header">
                    <span class="repair-number">{repair.repair_number}</span>
                    <span class="badge badge-{
                      repair.status === 'pending' ? 'warning' :
                      repair.status === 'in_progress' ? 'primary' :
                      repair.status === 'completed' || repair.status === 'delivered' ? 'success' :
                      'secondary'
                    }">
                      {repair.status}
                    </span>
                  </div>
                  <p class="repair-description">{repair.description}</p>
                  <div class="repair-meta">
                    <span>Costo: ${repair.estimated_cost || 0}</span>
                    <span>{formatDate(repair.created_at)}</span>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>

      <div class="custom-modal-footer">
        <button type="button" class="btn btn-outline" on:click={onClose}>
          Cerrar
        </button>
        <button type="button" class="btn btn-secondary" on:click={() => onStatusChange(device)}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"/>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
          </svg>
          Cambiar Estado
        </button>
        <button type="button" class="btn btn-primary" on:click={() => onEdit(device)}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          Editar
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .device-detail-modal .custom-modal-body {
    max-height: 65vh;
    overflow-y: auto;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .device-icon-large {
    font-size: 3rem;
  }

  .custom-modal-title {
    margin-bottom: 0.5rem;
  }

  .detail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .detail-card {
    background: var(--light);
    padding: 1rem;
    border-radius: var(--radius);
  }

  .detail-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.75rem;
  }

  .detail-title svg {
    width: 18px;
    height: 18px;
    color: var(--primary);
  }

  .detail-content {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .detail-content p {
    margin: 0;
    font-size: 0.875rem;
    color: var(--text);
  }

  .detail-content strong {
    color: var(--dark);
  }

  .section-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--dark);
    margin-bottom: 1rem;
  }

  .photos-section {
    margin-bottom: 1.5rem;
  }

  .photos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 0.75rem;
  }

  .photo-item {
    aspect-ratio: 1;
    border-radius: var(--radius);
    overflow: hidden;
    background: var(--light);
  }

  .photo-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    cursor: pointer;
    transition: transform 0.2s;
  }

  .photo-item img:hover {
    transform: scale(1.05);
  }

  .repairs-section {
    margin-bottom: 0;
  }

  .repairs-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .repair-item {
    background: var(--light);
    padding: 1rem;
    border-radius: var(--radius);
    border-left: 3px solid var(--primary);
  }

  .repair-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
  }

  .repair-number {
    font-weight: 600;
    color: var(--dark);
  }

  .repair-description {
    font-size: 0.875rem;
    color: var(--text);
    margin-bottom: 0.5rem;
  }

  .repair-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.8125rem;
    color: var(--text-light);
  }

  @media (max-width: 768px) {
    .detail-grid {
      grid-template-columns: 1fr;
    }

    .photos-grid {
      grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    }
  }
</style>
