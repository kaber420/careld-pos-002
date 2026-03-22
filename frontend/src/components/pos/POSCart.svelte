<script>
  import { api } from '../../stores/api';
  import { notify } from '../../stores/auth';

  export let cartItems = [];
  export let onCheckout = () => {};

  let searchQuery = '';
  let searchResults = [];
  let isSearching = false;
  let paymentMethod = 'cash';
  let amountPaid = '';

  $: total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  // Auto-fill amount paid if fully empty, otherwise let user adjust
  $: if (!amountPaid && total > 0) amountPaid = total;
  $: change = Math.max(0, (amountPaid || 0) - total);

  let searchTimeout;

  function handleSearch(e) {
    searchQuery = e.target.value;
    clearTimeout(searchTimeout);
    if (searchQuery.length < 2) {
      searchResults = [];
      return;
    }

    isSearching = true;
    searchTimeout = setTimeout(async () => {
      try {
        searchResults = await api.searchParts(searchQuery);
      } catch (error) {
        console.error(error);
      } finally {
        isSearching = false;
      }
    }, 500);
  }

  function addToCart(product) {
    if (product.stock_quantity <= 0) {
      notify('Producto sin stock', 'warning');
      return;
    }
    
    // Check if item already in cart
    const existing = cartItems.find(i => i.id === product.id && i.type === 'product');
    if (existing) {
      if (existing.quantity >= product.stock_quantity) {
        notify('Stock máximo alcanzado', 'warning');
        return;
      }
      existing.quantity += 1;
      cartItems = [...cartItems];
    } else {
      cartItems = [...cartItems, {
        id: product.id,
        type: 'product',
        name: product.name,
        price: product.unit_price,
        quantity: 1,
        max_quantity: product.stock_quantity
      }];
    }
    searchQuery = '';
    searchResults = [];
  }

  function addRepairToCart(repair) {
    const existing = cartItems.find(i => i.id === repair.id && i.type === 'repair');
    if (existing) return;

    cartItems = [...cartItems, {
      id: repair.id,
      type: 'repair',
      name: `Reparación #${repair.repair_number}`,
      price: repair.final_cost || repair.estimated_cost || 0,
      quantity: 1,
      max_quantity: 1
    }];
  }

  function updateQuantity(index, delta) {
    const item = cartItems[index];
    if (item.type === 'repair') return; // Cannot change quantity for repairs
    
    const newQuantity = item.quantity + delta;
    if (newQuantity > 0 && newQuantity <= item.max_quantity) {
      item.quantity = newQuantity;
      cartItems = [...cartItems];
    } else if (newQuantity <= 0) {
      removeItem(index);
    }
  }

  function removeItem(index) {
    cartItems = cartItems.filter((_, i) => i !== index);
  }

  async function handleCheckout() {
    if (cartItems.length === 0) {
      notify('El carrito está vacío', 'warning');
      return;
    }
    if (amountPaid < total) {
      notify('El monto pagado es insuficiente', 'danger');
      return;
    }

    try {
      await onCheckout({
        items: cartItems,
        payment_method: paymentMethod,
        amount_paid: amountPaid,
        total: total,
        change: change
      });
      // Clear cart on success
      cartItems = [];
      amountPaid = '';
    } catch (error) {
      notify('Error al procesar el pago: ' + error.message, 'danger');
    }
  }
</script>

<div class="flex flex-col h-full overflow-hidden">
  <div class="p-8 border-b border-gray-100 dark-border-gray-700 bg-gray-50/50">
    <h3 class="text-2xl font-black text-gray-900 dark-text-white tracking-tight flex items-center gap-3">
      <span class="text-3xl">🛒</span> Carrito
    </h3>
  </div>

  <div class="p-6 border-b border-gray-100 dark-border-gray-700 bg-white/50 relative z-20">
    <div class="relative group">
      <span class="absolute left-4 top-1/2 -translate-y-1/2 opacity-40 group-focus-within:opacity-100 transition-opacity" aria-hidden="true">🔍</span>
      <label for="cart-product-search" class="sr-only">Buscar productos</label>
      <input 
        id="cart-product-search"
        name="cart-product-search"
        type="text" 
        class="input w-full pl-12 h-14 rounded-2xl bg-gray-50 border-transparent focus:border-indigo-500 transition-all shadow-inner" 
        placeholder="Buscar productos..." 
        value={searchQuery}
        on:input={handleSearch}
      />
    </div>

    <!-- Search Results Dropdown -->
    {#if searchResults.length > 0 && searchQuery.length >= 2}
      <div class="absolute top-full left-6 right-6 bg-white dark-bg-gray-800 border border-gray-100 dark-border-gray-700 rounded-3xl shadow-2xl max-h-[400px] overflow-y-auto mt-4 py-3 z-50 animate-in fade-in slide-in-from-top-4 duration-300">
        <div class="px-6 py-2 border-b border-gray-50 dark-border-gray-700">
          <span class="text-[10px] font-black uppercase text-indigo-400 tracking-widest">Resultados ({searchResults.length})</span>
        </div>
        {#each searchResults as product}
          <div 
            class="flex justify-between items-center p-5 hover:bg-indigo-50 dark:hover-bg-indigo-900-30 cursor-pointer transition-colors group" 
            on:click={() => addToCart(product)}
            on:keydown={(e) => e.key === 'Enter' && addToCart(product)}
            role="button"
            tabindex="0"
          >
            <div class="flex flex-col flex-1">
              <span class="font-bold text-gray-900 dark-text-white group-hover:text-indigo-600 transition-colors">{product.name}</span>
              <div class="flex items-center gap-3 mt-1.5">
                <span class="text-[10px] font-black px-2 py-0.5 bg-gray-100 dark-bg-gray-700 rounded-lg text-gray-500">STOCK: {product.stock_quantity}</span>
                <span class="text-xs font-black text-indigo-600">${product.unit_price}</span>
              </div>
            </div>
            <button class="btn btn-primary btn-sm btn-square rounded-xl opacity-0 group-hover:opacity-100 transition-all scale-75 group-hover:scale-100">
              ➕
            </button>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <div class="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50/30">
    {#if cartItems.length === 0}
      <div class="flex flex-col items-center justify-center h-full opacity-10 text-center py-20">
        <svg class="w-24 h-24 mb-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
          <circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
        </svg>
        <p class="text-xl font-black uppercase tracking-tighter">Sin artículos</p>
      </div>
    {:else}
      {#each cartItems as item, idx}
        <div class="bg-white/80 dark-bg-gray-800 p-5 rounded-3xl border border-gray-100 dark-border-gray-700 shadow-sm flex justify-between items-center group hover:border-indigo-400 transition-all scale-in">
          <div class="flex flex-col flex-1">
            <span class="font-bold text-gray-900 dark-text-white line-clamp-1 leading-tight">{item.name}</span>
            <span class="text-sm text-gray-400 font-black mt-1">${item.price.toFixed(2)}</span>
          </div>
          <div class="flex items-center gap-4 ml-4">
            {#if item.type === 'product' || item.type === 'extra'}
              <div class="flex items-center bg-gray-100/50 p-1.5 rounded-2xl">
                <button class="w-8 h-8 flex items-center justify-center hover:bg-white rounded-xl transition-all font-black" on:click={() => updateQuantity(idx, -1)}>-</button>
                <span class="w-10 text-center font-black text-sm">{item.quantity}</span>
                <button class="w-8 h-8 flex items-center justify-center hover:bg-white rounded-xl transition-all font-black" on:click={() => updateQuantity(idx, 1)}>+</button>
              </div>
            {:else}
              <span class="text-[10px] font-black px-3 py-1 bg-indigo-50 text-indigo-600 rounded-full uppercase tracking-widest">Servicio</span>
            {/if}
            <button class="text-gray-300 hover:text-red-500 transition-colors p-2" on:click={() => removeItem(idx)}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" class="w-5 h-5">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
      {/each}
    {/if}
  </div>

  <div class="p-8 bg-white/60 border-t border-gray-100">
    <div class="flex justify-between items-end mb-10">
      <div>
        <p class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-1">Total del Pago</p>
        <p class="text-5xl font-black text-gray-900 tracking-tighter">${total.toFixed(2)}</p>
      </div>
    </div>

    <div class="space-y-6 mb-10">
      <div class="form-control">
        <label for="payment-method" class="label"><span class="label-text font-black text-[10px] text-gray-400 uppercase tracking-widest">Método de Pago</span></label>
        <select id="payment-method" class="select select-bordered w-full rounded-2xl h-14 bg-white border-gray-100 font-bold" bind:value={paymentMethod}>
          <option value="cash">💵 Efectivo</option>
          <option value="credit_card">💳 Tarjeta</option>
          <option value="transfer">🏦 Transferencia</option>
        </select>
      </div>

      {#if paymentMethod === 'cash'}
        <div class="form-control">
          <label for="amount-paid" class="label"><span class="label-text font-black text-[10px] text-gray-400 uppercase tracking-widest">Monto Recibido</span></label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 font-black text-gray-400">$</span>
            <input id="amount-paid" name="amount-paid" type="number" class="input input-bordered w-full pl-8 h-14 rounded-2xl bg-white border-gray-100 font-black text-xl" bind:value={amountPaid} min={total} step="0.01">
          </div>
        </div>
        {#if change > 0}
          <div class="flex justify-between items-center p-5 bg-green-50 rounded-3xl border border-green-100 border-dashed">
            <span class="text-green-700 font-black uppercase text-[10px] tracking-widest">Cambio</span>
            <span class="text-green-700 font-black text-2xl">${change.toFixed(2)}</span>
          </div>
        {/if}
      {/if}
    </div>

    <button 
      class="btn-premium w-full h-18 text-xl" 
      disabled={cartItems.length === 0 || (paymentMethod === 'cash' && amountPaid < total)}
      on:click={handleCheckout}
    >
      FINALIZAR COBRO
    </button>
  </div>
</div>

<style>
  /* Todos los estilos ahora están en Tailwind v4 o clases personalizadas en app.css */
  .scale-in {
    animation: scaleIn 0.3s ease-out;
  }
  @keyframes scaleIn {
    from { transform: scale(0.95); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
  }
</style>
