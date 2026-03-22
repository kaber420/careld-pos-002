<script>
  import { onMount } from 'svelte';
  import { api } from '../stores/api';
  import { notify } from '../stores/auth';
  import Layout from '../components/Layout.svelte';

  let items = [];
  let categories = [];
  let isLoading = true;
  let showForm = false;
  let editingItem = null;

  let showAdjustmentModal = false;
  let adjustingItem = null;
  let adjustmentData = {
    quantity: 0,
    type: 'withdrawal',
    reason: ''
  };

  let filters = {
    category_id: '',
    low_stock: false,
    search: ''
  };

  let formData = {
    name: '',
    sku: '',
    category_id: '',
    description: '',
    unit_price: '',
    cost_price: '',
    stock_quantity: 0,
    min_stock: 5,
    location: '',
    supplier: ''
  };

  onMount(async () => {
    await Promise.all([loadItems(), loadCategories()]);
  });

  async function loadItems() {
    isLoading = true;
    try {
      const params = {};
      if (filters.category_id) params.category_id = filters.category_id;
      if (filters.low_stock) params.low_stock = true;
      if (filters.search) params.search = filters.search;
      items = await api.getInventoryItems(params);
    } catch (error) {
      notify(error.message, 'danger');
    } finally {
      isLoading = false;
    }
  }

  async function loadCategories() {
    try {
      categories = await api.getCategories();
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  }

  function openForm(item = null) {
    if (item) {
      editingItem = item;
      formData = {
        name: item.name || '',
        sku: item.sku || '',
        category_id: item.category_id || '',
        description: item.description || '',
        unit_price: item.unit_price || '',
        cost_price: item.cost_price || '',
        stock_quantity: item.stock_quantity || 0,
        min_stock: item.min_stock || 5,
        location: item.location || '',
        supplier: item.supplier || ''
      };
    } else {
      editingItem = null;
      formData = {
        name: '',
        sku: '',
        category_id: categories[0]?.id || '',
        description: '',
        unit_price: '',
        cost_price: '',
        stock_quantity: 0,
        min_stock: 5,
        location: '',
        supplier: ''
      };
    }
    showForm = true;
  }

  function closeForm() {
    showForm = false;
    editingItem = null;
  }

  async function handleSubmit() {
    try {
      const data = {
        ...formData,
        unit_price: parseFloat(formData.unit_price) || 0,
        cost_price: parseFloat(formData.cost_price) || 0,
        stock_quantity: parseInt(formData.stock_quantity) || 0,
        min_stock: parseInt(formData.min_stock) || 5,
        category_id: formData.category_id || null
      };

      if (editingItem) {
        await api.updateInventoryItem(editingItem.id, data);
        notify('Item actualizado correctamente', 'success');
      } else {
        await api.createInventoryItem(data);
        notify('Item creado correctamente', 'success');
      }
      closeForm();
      loadItems();
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  function openAdjustmentModal(item) {
    adjustingItem = item;
    adjustmentData = {
      quantity: 0,
      type: 'withdrawal',
      reason: ''
    };
    showAdjustmentModal = true;
  }

  function closeAdjustmentModal() {
    showAdjustmentModal = false;
    adjustingItem = null;
  }

  async function submitAdjustment() {
    if (!adjustmentData.quantity || adjustmentData.quantity === 0) {
        notify('Ingresa una cantidad válida', 'warning');
        return;
    }

    try {
      await api.adjustStock(adjustingItem.id, {
        quantity: parseInt(adjustmentData.quantity),
        type: adjustmentData.type,
        reason: adjustmentData.reason
      });
      notify('Stock actualizado correctamente', 'success');
      closeAdjustmentModal();
      loadItems();
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  async function handleDelete(item) {
    if (!confirm(`¿Estás seguro de eliminar "${item.name}"?`)) return;

    try {
      await api.deleteInventoryItem(item.id);
      notify('Item eliminado correctamente', 'success');
      loadItems();
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  function handleFilter() {
    loadItems();
  }

  function getCategoryName(categoryId) {
    if (!categoryId) return 'Sin categoría';
    const category = categories.find(c => c.id === categoryId);
    return category?.name || 'Desconocida';
  }

  function formatCurrency(amount) {
    return `$${(amount || 0).toFixed(2)}`;
  }

  function getStockBadgeClass(item) {
    if (item.stock_quantity === 0) return 'badge-danger';
    if (item.stock_quantity <= item.min_stock) return 'badge-warning';
    return 'badge-success';
  }
</script>

<Layout>
  <div class="inventory-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Inventario</h1>
        <p class="page-subtitle">Gestión de repuestos y productos</p>
      </div>
    <button class="btn btn-primary" on:click={() => openForm()}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="12" y1="5" x2="12" y2="19"/>
        <line x1="5" y1="12" x2="19" y2="12"/>
      </svg>
      Nuevo Item
    </button>
  </div>

  <!-- Stats -->
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-value">{items.length}</div>
      <div class="stat-label">Total Items</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{items.filter(i => i.stock_quantity <= i.min_stock).length}</div>
      <div class="stat-label text-warning">Stock Bajo</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{items.filter(i => i.stock_quantity === 0).length}</div>
      <div class="stat-label text-danger">Sin Stock</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{categories.length}</div>
      <div class="stat-label">Categorías</div>
    </div>
  </div>

  <div class="card mt-6">
    <div class="card-body">
      <!-- Filters -->
      <div class="filters-bar">
        <div class="flex gap-3" style="flex-wrap: wrap;">
          <input
            type="text"
            class="input"
            placeholder="Buscar por nombre o SKU..."
            bind:value={filters.search}
            style="min-width: 200px;"
          />
          <select class="select" bind:value={filters.category_id} style="min-width: 150px;">
            <option value="">Todas las categorías</option>
            {#each categories as category}
              <option value={category.id}>{category.name}</option>
            {/each}
          </select>
          <label class="checkbox-wrapper">
            <input type="checkbox" class="checkbox" bind:checked={filters.low_stock} />
            <span class="text-sm">Solo stock bajo</span>
          </label>
          <button class="btn btn-outline" on:click={handleFilter}>Filtrar</button>
          <button class="btn btn-outline" on:click={() => { filters = { category_id: '', low_stock: false, search: '' }; loadItems(); }}>Limpiar</button>
        </div>
      </div>

      <!-- Table -->
      {#if isLoading}
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Cargando inventario...</p>
        </div>
      {:else if items.length === 0}
        <div class="empty-state">
          <div class="empty-state-icon">📦</div>
          <p class="empty-state-title">No hay items en inventario</p>
          <p class="empty-state-description">Comienza agregando un nuevo item</p>
          <button class="btn btn-primary mt-4" on:click={() => openForm()}>
            Agregar Item
          </button>
        </div>
      {:else}
        <div class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th>SKU</th>
                <th>Nombre</th>
                <th>Categoría</th>
                <th>Stock</th>
                <th>Costo</th>
                <th>Precio</th>
                <th>Ubicación</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {#each items as item}
                <tr class:row-low-stock={item.stock_quantity <= item.min_stock}>
                  <td><code class="text-sm">{item.sku}</code></td>
                  <td class="font-medium">{item.name}</td>
                  <td>{getCategoryName(item.category_id)}</td>
                  <td>
                    <span class="badge {getStockBadgeClass(item)}">
                      {item.stock_quantity} {item.stock_quantity <= item.min_stock ? `(mín: ${item.min_stock})` : ''}
                    </span>
                  </td>
                  <td>{formatCurrency(item.cost_price)}</td>
                  <td>{formatCurrency(item.unit_price)}</td>
                  <td>{item.location || '-'}</td>
                  <td>
                    <div class="flex gap-2">
                      <button
                        class="btn btn-sm btn-outline"
                        on:click={() => openForm(item)}
                      >
                        Editar
                      </button>
                      <button
                        class="btn btn-sm btn-secondary"
                        on:click={() => openAdjustmentModal(item)}
                      >
                        ± Stock
                      </button>
                      <button
                        class="btn btn-sm btn-danger"
                        on:click={() => handleDelete(item)}
                      >
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  </div>

  <!-- Modal Form -->
  {#if showForm}
    <div class="custom-modal-overlay" on:click|self={closeForm}>
      <div class="custom-modal modal-lg">
        <div class="custom-modal-header">
          <h3 class="custom-modal-title">
            {editingItem ? 'Editar Item' : 'Nuevo Item de Inventario'}
          </h3>
          <button class="custom-modal-close" on:click={closeForm}>×</button>
        </div>

        <form on:submit|preventDefault={handleSubmit}>
          <div class="custom-modal-body">
            <div class="form-row">
              <div class="form-group">
                <label class="label" for="name">Nombre *</label>
                <input id="name" type="text" class="input" bind:value={formData.name} required />
              </div>

              <div class="form-group">
                <label class="label" for="sku">SKU *</label>
                <input id="sku" type="text" class="input" bind:value={formData.sku} required />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="label" for="category_id">Categoría</label>
                <select id="category_id" class="select" bind:value={formData.category_id}>
                  <option value="">Sin categoría</option>
                  {#each categories as category}
                    <option value={category.id}>{category.name}</option>
                  {/each}
                </select>
              </div>

              <div class="form-group">
                <label class="label" for="location">Ubicación</label>
                <input id="location" type="text" class="input" bind:value={formData.location} placeholder="ej: Estante A-1" />
              </div>
            </div>

            <div class="form-group">
              <label class="label" for="description">Descripción</label>
              <textarea id="description" class="textarea" bind:value={formData.description} rows="2"></textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="label" for="cost_price">Costo</label>
                <input id="cost_price" type="number" step="0.01" class="input" bind:value={formData.cost_price} />
              </div>

              <div class="form-group">
                <label class="label" for="unit_price">Precio Venta</label>
                <input id="unit_price" type="number" step="0.01" class="input" bind:value={formData.unit_price} />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="label" for="stock_quantity">Stock Actual</label>
                <input id="stock_quantity" type="number" class="input" bind:value={formData.stock_quantity} />
              </div>

              <div class="form-group">
                <label class="label" for="min_stock">Stock Mínimo</label>
                <input id="min_stock" type="number" class="input" bind:value={formData.min_stock} />
              </div>
            </div>

            <div class="form-group">
              <label class="label" for="supplier">Proveedor</label>
              <input id="supplier" type="text" class="input" bind:value={formData.supplier} />
            </div>
          </div>

          <div class="custom-modal-footer">
            <button type="button" class="btn btn-outline" on:click={closeForm}>Cancelar</button>
            <button type="submit" class="btn btn-primary">
              {editingItem ? 'Actualizar' : 'Crear'} Item
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}

  <!-- Adjustment Modal -->
  {#if showAdjustmentModal}
    <div class="custom-modal-overlay" on:click|self={closeAdjustmentModal}>
      <div class="custom-modal">
        <div class="custom-modal-header">
          <h3 class="custom-modal-title">
            Ajustar Stock: {adjustingItem?.name}
          </h3>
          <button class="custom-modal-close" on:click={closeAdjustmentModal}>×</button>
        </div>

        <form on:submit|preventDefault={submitAdjustment}>
          <div class="custom-modal-body">
            <div class="form-group">
              <label class="label" for="adj_quantity">Cantidad (+ para agregar, - para restar) *</label>
              <input id="adj_quantity" type="number" class="input" bind:value={adjustmentData.quantity} required />
              <small class="text-sm text-light mt-1 block">Stock actual: {adjustingItem?.stock_quantity}</small>
            </div>

            <div class="form-group">
              <label class="label" for="adj_type">Motivo del Ajuste *</label>
              <select id="adj_type" class="select" bind:value={adjustmentData.type} required>
                <option value="withdrawal">Salida General (Uso interno)</option>
                <option value="damaged">Producto Dañado/Defectuoso</option>
                <option value="loss">Pérdida o Robo</option>
                <option value="adjustment">Ajuste Manual (Inventario de rutina)</option>
                <option value="purchase">Entrada por Compra</option>
              </select>
            </div>

            <div class="form-group">
              <label class="label" for="adj_reason">Notas adicionales</label>
              <textarea id="adj_reason" class="textarea" bind:value={adjustmentData.reason} rows="3" placeholder="Ej: Se rompió pantalla al instalar, usado en local, etc."></textarea>
            </div>
          </div>

          <div class="custom-modal-footer">
            <button type="button" class="btn btn-outline" on:click={closeAdjustmentModal}>Cancelar</button>
            <button type="submit" class="btn btn-primary">
              Guardar Ajuste
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}
  </div>
</Layout>

<style>
  .inventory-page {
    max-width: 1400px;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .page-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--dark);
    margin-bottom: 0.25rem;
  }

  .page-subtitle {
    color: var(--text-light);
    font-size: 0.875rem;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }

  .stat-card {
    background: white;
    padding: 1.25rem;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    text-align: center;
  }

  .stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--dark);
  }

  .stat-label {
    font-size: 0.875rem;
    color: var(--text-light);
    margin-top: 0.25rem;
  }

  .filters-bar {
    margin-bottom: 1rem;
  }

  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    color: var(--text-light);
  }

  .empty-state {
    text-align: center;
    padding: 3rem 1rem;
  }

  .empty-state-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }

  .row-low-stock {
    background: #fef3c7;
  }

  .text-warning {
    color: var(--warning);
  }

  .text-danger {
    color: var(--danger);
  }

  .modal-lg {
    max-width: 700px;
  }
</style>
