<script>
  import { onMount } from 'svelte';
  import { api } from '../stores/api';
  import PartnerCatalog from '../lib/components/partner/PartnerCatalog.svelte';
  import PartnerCart from '../lib/components/partner/PartnerCart.svelte';
  import PartnerOrderHistory from '../lib/components/partner/PartnerOrderHistory.svelte';
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  let repairs = [];
  let loading = true;
  let error = null;
  let searchTerm = '';
  let activeTab = 'repairs'; 
  let historyComponent;

  onMount(async () => {
    try {
      repairs = await api.getPartnerRepairs();
    } catch (err) {
      error = err.message;
      console.error(err);
    } finally {
      loading = false;
    }
  });

  $: filteredRepairs = repairs.filter(r => 
    r.repair_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (r.device?.brand + ' ' + r.device?.model).toLowerCase().includes(searchTerm.toLowerCase())
  );

  function getStatusClass(status) {
    return status.toLowerCase();
  }

  function handleOrderCreated() {
    if (historyComponent) {
      historyComponent.refreshOrders();
    }
  }
</script>

<div class="partner-dashboard min-h-screen mesh-gradient">
  <div class="max-w-7xl mx-auto p-4 md-p-8">
    <header class="mb-12 relative">
      <div class="absolute -top-10 -left-10 w-40 h-40 bg-indigo-500-10 rounded-full blur-3xl animate-pulse-slow"></div>
      <div class="absolute -top-10 -right-10 w-40 h-40 bg-purple-500-10 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 2s"></div>
      
      <div class="relative flex flex-col md-flex-row md-items-end justify-between gap-8">
        <div in:fly={{ y: -20, duration: 800 }}>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 text-indigo-600 dark-text-indigo-400 text-xs font-black uppercase tracking-widest mb-4">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
            </span>
            Partner Hub
          </div>
          <h1 class="text-4xl md-text-6xl font-black text-gray-900 dark-text-white mb-3 tracking-tight" style="font-family: 'Outfit', sans-serif;">
            Portal de <span class="text-gradient">Socio</span>
          </h1>
          <p class="text-lg text-gray-500 dark-text-gray-400 max-w-xl">
            Gestiona reparaciones en tiempo real y solicita refacciones originales con un clic.
          </p>
        </div>

        <nav class="glass-premium p-1-5 rounded-2xl flex shadow-xl" in:fly={{ x: 20, duration: 800 }}>
          <button 
            class="px-8 py-3 rounded-xl text-sm font-black transition-all duration-300 flex items-center gap-2 {activeTab === 'repairs' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' : 'text-gray-500 hover-text-gray-700 dark-hover-text-gray-200'}"
            on:click={() => activeTab = 'repairs'}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Reparaciones
          </button>
          <button 
            class="px-8 py-3 rounded-xl text-sm font-black transition-all duration-300 flex items-center gap-2 {activeTab === 'parts' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' : 'text-gray-500 hover-text-gray-700 dark-hover-text-gray-200'}"
            on:click={() => activeTab = 'parts'}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            Refacciones
          </button>
        </nav>
      </div>
    </header>

    <main class="relative">
      {#if activeTab === 'repairs'}
        <div class="tab-content" in:fade={{ duration: 400 }}>
          {#if loading}
            <div class="text-center py-40">
              <div class="spinner-premium mx-auto mb-6"></div>
              <p class="text-gray-500 font-bold animate-pulse">Sincronizando tus equipos...</p>
            </div>
          {:else if error}
            <div class="glass-premium p-8 rounded-3xl border-red-100 dark-border-red-900-30 text-red-600 max-w-lg mx-auto text-center" in:scale>
              <div class="text-4xl mb-4">⚠️</div>
              <h2 class="text-xl font-bold mb-2">Error de Sincronización</h2>
              <p class="mb-6 opacity-80">{error}</p>
              <button on:click={() => location.reload()} class="btn-premium">Reintentar</button>
            </div>
          {:else}
            <div class="controls mb-10" in:fly={{ y: 20, duration: 600 }}>
              <div class="relative group max-w-2xl">
                <div class="absolute inset-0 bg-indigo-500-10 rounded-2xl blur-xl group:hover .group-hover-visible transition-all"></div>
                <div class="relative glass-premium flex items-center px-6 py-1-5 rounded-2xl">
                  <span class="text-2xl mr-4 opacity-50">🔍</span>
                  <input 
                    type="text" 
                    bind:value={searchTerm} 
                    placeholder="Buscar por orden o modelo..." 
                    class="w-full bg-transparent py-5 outline-none text-lg font-medium placeholder-gray-400"
                  />
                  <div class="flex items-center gap-2">
                    <span class="text-[10px] px-2 py-1 bg-gray-100 dark-bg-gray-800 rounded-lg text-gray-500 font-black">ESC</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-1 md-grid-cols-2 xl-grid-cols-3 gap-8">
              {#each filteredRepairs as repair, i}
                <div 
                  class="card-premium group" 
                  in:fly={{ y: 30, duration: 600, delay: i * 100, easing: cubicOut }}
                >
                  <div class="p-8">
                    <div class="flex justify-between items-start mb-6">
                      <div class="space-y-1">
                        <span class="text-[10px] font-black text-indigo-500 uppercase tracking-[0.2em]">{repair.repair_number}</span>
                        <h3 class="font-black text-2xl text-gray-900 dark-text-white leading-tight">
                          {repair.device?.brand || ''} <br/>
                          <span class="text-gray-500 dark-text-gray-400 font-bold text-lg">{repair.device?.model || 'Equipo'}</span>
                        </h3>
                      </div>
                      <div class="status-badge {repair.status.toLowerCase()} px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-wider">
                        {repair.status.replace('_', ' ')}
                      </div>
                    </div>
                    
                    <p class="text-gray-500 dark-text-gray-400 mb-8 line-clamp-2 min-h-[3rem] text-sm leading-relaxed">
                      {repair.description}
                    </p>
                    
                    <div class="flex items-center justify-between mb-8 pb-6 border-b border-gray-100 dark-border-gray-800">
                      <div class="flex flex-col">
                        <span class="text-[10px] text-gray-400 uppercase font-black mb-1">Costo Estimado</span>
                        <span class="text-2xl font-black text-gray-900 dark-text-white">
                          ${(repair.final_cost || repair.estimated_cost || 0).toFixed(2)}
                        </span>
                      </div>
                      <div class="text-right">
                        <span class="text-[10px] text-gray-400 uppercase font-black mb-1 block">Ingreso</span>
                        <span class="text-sm font-bold text-gray-600 dark-text-gray-300">
                          {new Date(repair.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>

                    <a href="/portal/{repair.portal_token}" class="btn-premium w-full justify-center group:hover .group-hover-scale hover-move-right transition-transform">
                      Detalles de Reparación
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 transition-transform group:hover .group-hover-move-right" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                      </svg>
                    </a>
                  </div>
                </div>
              {:else}
                <div class="col-span-full glass-premium rounded-3xl p-20 text-center border-dashed border-gray-200 dark-border-gray-700" in:scale>
                  <p class="text-5xl mb-6">🔍</p>
                  <h3 class="text-2xl font-black mb-2 dark-text-white">Sin coincidencias</h3>
                  <p class="text-gray-500">No encontramos reparaciones con "{searchTerm}"</p>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {:else if activeTab === 'parts'}
        <div class="tab-content" in:fly={{ x: 20, duration: 400 }}>
          <div class="grid grid-cols-1 lg-grid-cols-12 gap-10">
            <div class="lg-col-span-8 space-y-12">
              <section in:fly={{ y: 20, duration: 600, delay: 100 }}>
                <header class="mb-8 pl-4 border-l-4 border-purple-500">
                  <h2 class="text-3xl font-black text-gray-900 dark-text-white">Catálogo Premium</h2>
                  <p class="text-gray-500">Selecciona las piezas originales que necesites.</p>
                </header>
                <div class="glass-premium p-6 rounded-[2.5rem] shadow-2xl">
                  <PartnerCatalog />
                </div>
              </section>

              <section in:fly={{ y: 20, duration: 600, delay: 200 }}>
                <header class="mb-8 pl-4 border-l-4 border-indigo-500">
                  <h2 class="text-2xl font-black text-gray-900 dark-text-white">Mis Pedidos Recientes</h2>
                </header>
                <div class="glass-premium p-6 rounded-[2.5rem] shadow-xl">
                  <PartnerOrderHistory bind:this={historyComponent} />
                </div>
              </section>
            </div>

            <aside class="lg-col-span-4 lg-sticky lg-top-8 lg-h-full overflow-visible">
              <div in:fly={{ x: 40, duration: 800, delay: 300 }}>
                <PartnerCart on:orderCreated={handleOrderCreated} />
              </div>
            </aside>
          </div>
        </div>
      {/if}
    </main>
  </div>
</div>

<style>
  .text-gradient {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .status-badge.pending { background: #fef3c7; color: #92400e; }
  .status-badge.diagnosing { background: #dbeafe; color: #1e40af; }
  .status-badge.in_progress { background: #fef9c3; color: #854d0e; }
  .status-badge.completed { background: #dcfce7; color: #166534; }
  .status-badge.cancelled { background: #fee2e2; color: #991b1b; }
</style>
