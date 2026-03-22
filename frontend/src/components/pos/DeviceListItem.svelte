<script>
  export let device;
  export let customerName = '';
  export let onView = () => {};
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
    return deviceIcons[device.device_type] || deviceIcons.other;
  }
</script>

<div class="flex items-center justify-between w-full">
  <div class="flex items-center gap-4 flex-1 min-w-0">
    <div class="w-12 h-12 rounded-xl bg-gray-50 dark-bg-gray-900 flex items-center justify-center text-2xl group-hover:bg-indigo-50 dark:group-hover-bg-indigo-900-20 transition-colors">
      {getDeviceIcon()}
    </div>
    
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-3 mb-1">
        <h3 class="text-sm font-black text-gray-900 dark-text-white truncate group-hover:text-indigo-600 transition-colors">
          {device.brand} {device.model}
        </h3>
        <span class="badge {statusColors[device.status]} border-none font-black text-[9px] px-2 py-1 rounded-md">
          {statusLabels[device.status]}
        </span>
      </div>
      
      <div class="flex items-center gap-3 text-[11px] font-medium text-gray-500">
        <span class="flex items-center gap-1 uppercase tracking-wider">
          <span class="opacity-40">👤</span> {customerName}
        </span>
        {#if device.color}<span class="opacity-30">•</span> <span>{device.color}</span>{/if}
        {#if device.storage}<span class="opacity-30">•</span> <span>{device.storage}</span>{/if}
      </div>
    </div>
  </div>

  <div class="flex items-center gap-1 ml-4 border-l border-gray-50 dark-border-gray-700 pl-4 h-10">
    <button
      class="btn btn-ghost btn-xs w-8 h-8 rounded-lg hover:text-indigo-600 transition-colors"
      on:click|stopPropagation={() => onView(device)}
      title="Ver detalles"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-4 h-4">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
        <circle cx="12" cy="12" r="3"/>
      </svg>
    </button>
    
    <button
      class="btn btn-ghost btn-xs w-8 h-8 rounded-lg hover:text-blue-600 transition-colors"
      on:click|stopPropagation={() => onEdit(device)}
      title="Editar"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-4 h-4">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
      </svg>
    </button>
    
    <button
      class="btn btn-ghost btn-xs w-8 h-8 rounded-lg hover:text-amber-600 transition-colors"
      on:click|stopPropagation={() => onStatusChange(device)}
      title="Cambiar estado"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-4 h-4">
        <polyline points="23 4 23 10 17 10"/>
        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
      </svg>
    </button>
  </div>
</div>

<style>
  /* Todos los estilos ahora están en Tailwind v4 o DaisyUI */
  :global(.dark) .dark-group-hover-bg-indigo-900-20:hover { background-color: rgba(49, 46, 129, 0.2); }
</style>
