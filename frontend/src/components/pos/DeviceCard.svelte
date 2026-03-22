<script>
  export let device;
  export let customerName = '';
  export let onView = () => {};
  export let onEdit = () => {};
  export let onStatusChange = () => {};
  export let onOpenGallery = () => {};

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

  function getFirstPhoto() {
    if (device.photos && device.photos.trim()) {
      const photos = device.photos.split(',');
      const firstPhoto = photos[0].trim();
      // Si ya es URL completa, devolverla
      if (firstPhoto.startsWith('http') || firstPhoto.startsWith('/api/')) {
        return firstPhoto;
      }
      // Si es solo nombre de archivo, construir URL
      return `/api/v1/uploads/photo/${firstPhoto}`;
    }
    return null;
  }
</script>

<div class="card-premium group cursor-pointer relative" on:click={() => onView(device)} on:keydown={(e) => e.key === 'Enter' && onView(device)} role="button" tabindex="0">
  <figure class="relative bg-gray-50 dark-bg-gray-900 border-b border-gray-100 dark-border-gray-700 overflow-hidden" style="height: 12rem;">
    {#if getFirstPhoto()}
      <img src={getFirstPhoto()} alt={device.brand} class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
      <div class="absolute top-3 right-3 bg-black/60 backdrop-blur-md text-white text-[10px] font-black px-2 py-1 rounded-lg uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer border border-white/20 hover:bg-black/80" on:click|stopPropagation={() => onOpenGallery(device)} on:keydown={(e) => e.key === 'Enter' && onOpenGallery(device)} role="button" tabindex="0">
        {device.photos.split(',').length} FOTOS
      </div>
    {:else}
      <div class="flex flex-col items-center justify-center w-full h-full opacity-30 group-hover:opacity-60 transition-opacity">
        <span class="text-6xl mb-2">{getDeviceIcon()}</span>
        <span class="text-[10px] font-black uppercase tracking-widest">Sin imagen</span>
      </div>
    {/if}
    
    <div class="absolute top-3 left-3">
      <span class="badge {statusColors[device.status]} border-none font-black text-[10px] px-3 py-2 rounded-lg shadow-sm">
        {statusLabels[device.status]}
      </span>
    </div>
  </figure>

  <div class="card-body p-5 gap-0">
    <div class="flex items-center gap-2 mb-4">
      <div class="w-10 h-10 rounded-xl bg-indigo-50 dark-bg-indigo-900-20 flex items-center justify-center text-xl">
        {getDeviceIcon()}
      </div>
      <div class="flex flex-col">
        <h3 class="card-title text-base font-black text-gray-900 dark-text-white line-clamp-1 leading-tight group-hover:text-indigo-600 transition-colors">
          {device.brand} {device.model}
        </h3>
        <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">#{device.serial_number || 'S/N'}</span>
      </div>
    </div>

    <div class="space-y-2.5 mb-6">
      <div class="flex items-center gap-3 text-sm font-medium text-gray-500 group-hover:text-gray-700 transition-colors">
        <div class="w-5 h-5 flex items-center justify-center opacity-40">👤</div>
        <span class="truncate">{customerName}</span>
      </div>

      {#if device.color || device.storage}
        <div class="flex items-center gap-3 text-[11px] font-bold uppercase tracking-wider text-gray-400">
          <div class="w-5 h-5 flex items-center justify-center opacity-40 italic">ℹ️</div>
          <span class="flex items-center gap-2">
            {#if device.color}{device.color}{/if}
            {#if device.color && device.storage}•{/if}
            {#if device.storage}{device.storage}{/if}
          </span>
        </div>
      {/if}
    </div>

    <div class="card-actions grid grid-cols-3 border-t border-gray-50 dark-border-gray-700 pt-4 -mx-1">
      <button
        class="btn btn-ghost btn-sm flex flex-col h-auto py-2 gap-1 hover:bg-indigo-50 dark:hover-bg-indigo-900-20 text-gray-400 hover:text-indigo-600 transition-all rounded-xl"
        on:click|stopPropagation={() => onView(device)}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-4 h-4">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
        <span class="text-[9px] font-black uppercase">Detalle</span>
      </button>
      
      <button
        class="btn btn-ghost btn-sm flex flex-col h-auto py-2 gap-1 hover:bg-blue-50 dark:hover-bg-blue-900-20 text-gray-400 hover:text-blue-600 transition-all rounded-xl"
        on:click|stopPropagation={() => onEdit(device)}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-4 h-4">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
        <span class="text-[9px] font-black uppercase">Editar</span>
      </button>
      
      <button
        class="btn btn-ghost btn-sm flex flex-col h-auto py-2 gap-1 hover:bg-amber-50 dark:hover-bg-amber-900-20 text-gray-400 hover:text-amber-600 transition-all rounded-xl"
        on:click|stopPropagation={() => onStatusChange(device)}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-4 h-4">
          <polyline points="23 4 23 10 17 10"/>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
        </svg>
        <span class="text-[9px] font-black uppercase">Estado</span>
      </button>
    </div>
  </div>
</div>

<style>
  /* Todos los estilos ahora están en Tailwind v4 o DaisyUI */
  :global(.dark) .dark-bg-indigo-900-20 { background-color: rgba(49, 46, 129, 0.2); }
  :global(.dark) .dark-bg-blue-900-20 { background-color: rgba(30, 58, 138, 0.2); }
  :global(.dark) .dark-bg-amber-900-20 { background-color: rgba(120, 53, 15, 0.2); }
</style>
