<script>
  import PartnerLayout from '../lib/components/partner/PartnerLayout.svelte';
  import ViewToggle from '../lib/components/ui/partner/ViewToggle.svelte';
  import PartnerSearch from '../lib/components/ui/partner/PartnerSearch.svelte';
  import PartnerRepairCard from '../lib/components/ui/partner/PartnerRepairCard.svelte';
  import PartnerRepairTable from '../lib/components/ui/partner/PartnerRepairTable.svelte';
  import PartnerPartCard from '../lib/components/ui/partner/PartnerPartCard.svelte';
  import PartnerPartTable from '../lib/components/ui/partner/PartnerPartTable.svelte';
  import PhotoCarousel from '../lib/components/ui/partner/PhotoCarousel.svelte';
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import { api } from '../stores/api'; 
  import { cart } from '../stores/cart';
  import { notify } from '../stores/auth';
  import { useLocation } from 'svelte-routing';

  const location = useLocation();

  let repairs = [];
  let products = [];
  let loading = true;
  let error = null;
  let searchTerm = '';
  let activeTab = 'repairs'; 
  let viewType = 'grid'; // 'grid' o 'table'

  let selectedRepair = null;
  let selectedProduct = null;
  let isCarouselOpen = false;

  // Reactividad para detectar cambio de tab en la URL usando el store location
  $: {
    const params = new URLSearchParams($location.search);
    const tab = params.get('tab') || 'repairs';
    if (tab && (tab === 'repairs' || tab === 'parts')) {
      if (activeTab !== tab) {
        activeTab = tab;
        loadData();
      }
    }
  }

  onMount(async () => {
    // Restaurar vista persistida
    const savedView = localStorage.getItem('partner_view_type');
    if (savedView) viewType = savedView;

    await loadData();
  });

  async function loadData() {
    loading = true;
    error = null;
    try {
      if (activeTab === 'repairs') {
        repairs = await api.getPartnerRepairs();
      } else {
        products = await api.getPartnerInventory();
      }
    } catch (err) {
      error = err.message;
      console.error(err);
    } finally {
      loading = false;
    }
  }

  function handleViewChange(e) {
    viewType = e.detail;
    localStorage.setItem('partner_view_type', viewType);
  }

  function handleViewPhotos(e) {
    selectedRepair = e.detail;
    isCarouselOpen = true;
  }

  function handleViewPartPhoto(e) {
    selectedProduct = e.detail;
    // Para simplificar, usamos el mismo carrusel o uno similar
    isCarouselOpen = true;
  }

  function handleAddToCart(e) {
    const product = e.detail;
    cart.addItem(product);
    notify(`Agregado al carrito: ${product.name}`, 'info');
  }

  $: filteredRepairs = repairs.filter(r => 
    r.repair_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (r.device?.brand + ' ' + r.device?.model).toLowerCase().includes(searchTerm.toLowerCase())
  );

  $: filteredProducts = products.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.sku.toLowerCase().includes(searchTerm.toLowerCase())
  );

  function getStatusLabel(status) {
    const labels = {
      'pending': 'Pendiente',
      'diagnosing': 'En Diagnóstico',
      'in_progress': 'En Proceso',
      'completed': 'Listo',
      'delivered': 'Entregado',
      'cancelled': 'Cancelado'
    };
    return labels[status.toLowerCase()] || status;
  }
</script>

<PartnerLayout title={activeTab === 'repairs' ? 'Reparaciones' : 'Catálogo de Refacciones'} {activeTab}>
  <div id="partner-dashboard-root">
    <div class="header-controls">
      <PartnerSearch bind:value={searchTerm} />
      <ViewToggle currentView={viewType} on:change={handleViewChange} />
    </div>

    {#if loading}
      <div class="loading-state" transition:fade>
        <div class="spinner"></div>
        <p>Sincronizando portal...</p>
      </div>
    {:else if error}
      <div class="error-state" transition:fade>
        <h3>Error de Conexión</h3>
        <p>{error}</p>
        <button on:click={() => loadData()}>Reintentar</button>
      </div>
    {:else}
      {#if activeTab === 'repairs'}
        {#if viewType === 'grid'}
          <div class="data-grid">
            {#each filteredRepairs as repair (repair.id)}
              <PartnerRepairCard 
                {repair} 
                on:view-photos={handleViewPhotos}
                on:edit={(e) => console.log('Edit', e.detail)}
                on:status={(e) => console.log('Status', e.detail)}
              />
            {/each}
          </div>
        {:else}
          <PartnerRepairTable 
            repairs={filteredRepairs} 
            on:view-photos={handleViewPhotos}
            on:row-click={(e) => console.log('Row Click', e.detail)}
          />
        {/if}

        {#if filteredRepairs.length === 0}
          <div class="empty-state">
             <p>No se encontraron reparaciones para tu búsqueda.</p>
          </div>
        {/if}
      {:else}
        {#if viewType === 'grid'}
          <div class="data-grid">
            {#each filteredProducts as product (product.id)}
              <PartnerPartCard 
                {product} 
                on:view-photo={handleViewPartPhoto}
                on:add-to-cart={handleAddToCart}
              />
            {/each}
          </div>
        {:else}
          <PartnerPartTable 
            products={filteredProducts} 
            on:view-photo={handleViewPartPhoto}
            on:add-to-cart={handleAddToCart}
          />
        {/if}

        {#if filteredProducts.length === 0}
          <div class="empty-state">
             <p>No se encontraron refacciones para tu búsqueda.</p>
          </div>
        {/if}
      {/if}
    {/if}
  </div>
</PartnerLayout>

<PhotoCarousel 
  isOpen={isCarouselOpen} 
  photos={activeTab === 'repairs' ? (selectedRepair?.photos || []) : (selectedProduct?.photo_url ? [selectedProduct.photo_url] : [])} 
  on:close={() => isCarouselOpen = false} 
/>

<style>
  #partner-dashboard-root {
    --primary: #6366f1;
    --primary-light: #818cf8;
    --secondary: #a855f7;
    --card-bg: rgba(30, 41, 59, 0.5);
    --text-main: #f1f5f9;
    --text-dim: #94a3b8;
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-blur: blur(12px);
  }

  .header-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3.5rem;
    gap: 2rem;
  }

  .data-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
  }

  @media (max-width: 640px) {
    .data-grid { grid-template-columns: 1fr; }
  }

  .loading-state, .error-state, .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5rem;
    background: rgba(30, 41, 59, 0.3);
    border-radius: 2rem;
    border: 1px dashed rgba(255, 255, 255, 0.1);
    text-align: center;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(99, 102, 241, 0.1);
    border-top-color: #6366f1;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error-state h3 { color: #f87171; margin-bottom: 0.5rem; }
  .error-state button {
    margin-top: 1rem;
    padding: 0.5rem 1.5rem;
    background: #6366f1;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
  }
</style>
