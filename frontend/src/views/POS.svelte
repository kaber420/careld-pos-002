<script>
  import { onMount } from 'svelte';
  import { api } from '../stores/api';
  import { notify } from '../stores/auth';
  import { openModal } from '../stores/modals';
  import Layout from '../components/Layout.svelte';

  // POS Components
  import ToggleView from '../components/pos/ToggleView.svelte';
  import DeviceCard from '../components/pos/DeviceCard.svelte';
  import DeviceListItem from '../components/pos/DeviceListItem.svelte';
  import DeviceSearchBar from '../components/pos/DeviceSearchBar.svelte';
  import POSCart from '../components/pos/POSCart.svelte';
  import POSModalHost from '../components/pos/POSModalHost.svelte';

  let viewMode = 'grid';
  let cartItems = [];
  let devices = [];
  let customers = [];
  let deviceSearch = '';
  let deviceFilters = { status: '', device_type: '', brand: '' };
  
  // Minimal local state for host props
  let selectedDeviceRepairs = [];
  let deviceForStatusChange = null;
  let isProcessing = false;

  onMount(async () => {
    try {
      const [c, d] = await Promise.all([
        api.getCustomers({ limit: 100 }),
        api.getDevices()
      ]);
      customers = c || [];
      devices = d || [];
    } catch (e) {
      notify('Error al cargar datos', 'danger');
    }
  });

  async function loadDevices() {
    try {
      devices = await api.getDevices() || [];
    } catch (e) {
      notify('Error al recargar', 'danger');
    }
  }

  $: filteredDevices = (devices || []).filter(d => {
    if (!d) return false;
    const s = (deviceSearch || '').toLowerCase();
    const brand = (d.brand || '').toLowerCase();
    const model = (d.model || '').toLowerCase();
    const customer = (d.customer?.name || '').toLowerCase();
    const serial = (d.serial_number || '').toLowerCase();
    
    const nameMatch = !s || brand.includes(s) || model.includes(s) || customer.includes(s) || serial.includes(s);
    const statusMatch = !deviceFilters.status || d.status === deviceFilters.status;
    const typeMatch = !deviceFilters.device_type || d.device_type === deviceFilters.device_type;
    const brandMatch = !deviceFilters.brand || d.brand === deviceFilters.brand;
    
    return nameMatch && statusMatch && typeMatch && brandMatch;
  });

  function openReceptionModal() { 
    openModal('reception');
  }
  
  async function onViewDevice(device) {
    if (!device) return;
    try { 
      selectedDeviceRepairs = await api.getRepairs({ device_id: device.id }) || []; 
      openModal('detail', { device });
    } catch (e) { 
      notify('Error al cargar detalle', 'danger');
    }
  }

  const deviceStatusLabels = {
    registered: 'Registrado',
    in_repair: 'En Reparación',
    waiting_parts: 'Repuestos',
    ready: 'Listo para Entrega',
    delivered: 'Entregado'
  };

  async function handleCheckout(cartData) {
    try {
      isProcessing = true;
      const itemsForTicket = (cartData.items || []).map(i => ({
        ...i,
        sale_price: i.price || 0,
        subtotal: (i.price || 0) * (i.quantity || 1)
      }));

      for (const item of (cartData.items || [])) {
        if (item.type === 'repair') {
          await api.updateDevice(item.device_id || item.id, { status: 'delivered' });
        }
      }
      
      notify('Cobro realizado', 'success');
      const ticketData = { type: 'venta', items: itemsForTicket, total: cartData.total, date: new Date().toISOString() };
      openModal('ticket', { ticketData });
      
      await loadDevices();
      cartItems = [];
    } catch (e) { notify('Error al procesar cobro', 'danger'); } finally { isProcessing = false; }
  }

  function handleAddToCart(device) {
    if (!device) return;
    api.getRepairs({ device_id: device.id }).then(repairs => {
      const active = (repairs || []).find(r => ['ready', 'completed', 'delivered'].includes(r.status));
      if (active) {
        if (!cartItems.find(i => i.id === active.id)) {
          cartItems = [...cartItems, { 
            id: active.id, 
            device_id: device.id, 
            type: 'repair', 
            name: `Servicio: ${device.brand} ${device.model}`, 
            price: active.final_cost || active.estimated_cost || 0, 
            quantity: 1 
          }];
          notify('Reparación cargada', 'success');
        } else notify('Ya está en el carrito', 'info');
      } else notify('No hay orden lista para entrega', 'warning');
    });
  }

  async function handleStatusSelect(s) {
    if (s && deviceForStatusChange) {
      try { 
        await api.updateDevice(deviceForStatusChange.id, { status: s }); 
        notify('Estado actualizado', 'success'); 
        await loadDevices(); 
      } catch (e) { notify('Error al actualizar estado', 'danger'); }
    }
  }
</script>

<POSModalHost 
  {customers} 
  onSuccessReception={loadDevices} 
  {selectedDeviceRepairs} 
  {deviceStatusLabels} 
  {handleStatusSelect} 
/>

<Layout title="Terminal POS">
  <div class="pos-container bg-slate-50 min-h-screen">
    <div class="max-w-[1920px] mx-auto px-6 py-8">
      
      <!-- Toolbar -->
      <header class="flex flex-col md:flex-row justify-between items-center bg-white p-6 rounded-2xl shadow-sm mb-8 border border-slate-200">
        <h1 class="text-2xl font-bold text-slate-800">Terminal POS</h1>
        <button class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-xl font-bold transition-all shadow-lg shadow-indigo-200 cursor-pointer relative z-10" on:click={openReceptionModal}>
          + REGISTRAR INGRESO
        </button>
      </header>

      <div class="flex flex-col lg:flex-row gap-8 items-start">
        <!-- Main Area -->
        <main class="flex-1 w-full relative z-0">
          <div class="space-y-6">
            <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex flex-wrap items-center gap-4 sticky top-4 z-10">
              <div class="flex-1 min-w-[300px]">
                <DeviceSearchBar bind:value={deviceSearch} bind:filters={deviceFilters} placeholder="Buscar cliente, marca, modelo..." />
              </div>
              <ToggleView bind:viewMode />
            </div>

            {#if filteredDevices.length === 0}
              <div class="bg-white rounded-3xl p-20 text-center border-2 border-dashed border-slate-200">
                <p class="text-slate-400 font-medium">No se encontraron equipos</p>
              </div>
            {:else if viewMode === 'grid'}
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {#each filteredDevices as device (device.id)}
                  <div class="space-y-3">
                    <DeviceCard 
                      {device} 
                      customerName={device.customer?.name || 'Cliente'} 
                      onView={() => onViewDevice(device)} 
                      onEdit={() => notify('Info', 'info')}
                      onStatusChange={() => { deviceForStatusChange = device; openModal('status', {device}); }}
                      onOpenGallery={() => { if(device.photos) { openModal('gallery', { photos: device.photos.split(','), currentIndex: 0 }); } }}
                    />
                    {#if device.status === 'ready'}
                      <button class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl transition-all shadow-md active:scale-95" on:click|stopPropagation={() => handleAddToCart(device)}>
                        CARGAR A CAJA
                      </button>
                    {/if}
                  </div>
                {/each}
              </div>
            {:else}
              <div class="space-y-3">
                {#each filteredDevices as device (device.id)}
                  <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex items-center justify-between gap-4 cursor-pointer relative z-0" on:click={() => onViewDevice(device)} on:keydown={(e) => e.key === 'Enter' && onViewDevice(device)} role="button" tabindex="0">
                    <div class="flex-1">
                      <DeviceListItem {device} customerName={device.customer?.name || 'Cliente'} onView={() => onViewDevice(device)} onStatusChange={() => { deviceForStatusChange = device; openModal('status', {device}); }} />
                    </div>
                    {#if device.status === 'ready'}
                      <button class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-xl font-bold relative z-10" on:click|stopPropagation={() => handleAddToCart(device)}>COBRAR</button>
                    {/if}
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        </main>

        <!-- Sidebar -->
        <aside class="w-full lg:w-[400px] lg:sticky lg:top-8 relative z-0">
          <div class="bg-white rounded-3xl shadow-xl border border-slate-200 overflow-hidden">
            <POSCart bind:cartItems onCheckout={handleCheckout} />
          </div>
        </aside>
      </div>
    </div>
  </div>
</Layout>
