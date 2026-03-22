<script>
  export let value = '';
  export let placeholder = 'Buscar por dispositivo, cliente, teléfono...';
  export let filters = {
    status: '',
    device_type: '',
    brand: ''
  };

  export let showFilters = false;

  const statusOptions = [
    { value: '', label: 'Todos los estados' },
    { value: 'registered', label: 'Registrado' },
    { value: 'in_repair', label: 'En Reparación' },
    { value: 'waiting_parts', label: 'Esperando Repuestos' },
    { value: 'ready', label: 'Listo para Entrega' },
    { value: 'delivered', label: 'Entregado' }
  ];

  const deviceTypeOptions = [
    { value: '', label: 'Todos los tipos' },
    { value: 'smartphone', label: '📱 Smartphone' },
    { value: 'tablet', label: '📟 Tablet' },
    { value: 'laptop', label: '💻 Laptop' },
    { value: 'desktop', label: '🖥️ Desktop' },
    { value: 'smartwatch', label: '⌚ Smartwatch' },
    { value: 'console', label: '🎮 Consola' },
    { value: 'other', label: '📦 Otro' }
  ];

  const brandOptions = [
    { value: '', label: 'Todas las marcas' },
    { value: 'Samsung', label: 'Samsung' },
    { value: 'Apple', label: 'Apple' },
    { value: 'Xiaomi', label: 'Xiaomi' },
    { value: 'Huawei', label: 'Huawei' },
    { value: 'HP', label: 'HP' },
    { value: 'Dell', label: 'Dell' },
    { value: 'Lenovo', label: 'Lenovo' },
    { value: 'Asus', label: 'Asus' },
    { value: 'Sony', label: 'Sony' },
    { value: 'LG', label: 'LG' },
    { value: 'Motorola', label: 'Motorola' },
    { value: 'Otro', label: 'Otro' }
  ];

  function clearAll() {
    search = '';
    filters = { status: '', device_type: '', brand: '' };
  }

  function hasActiveFilters() {
    return value || filters.status || filters.device_type || filters.brand;
  }
</script>

<div class="device-search-bar">
  <div class="search-input-wrapper">
    <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="11" cy="11" r="8"/>
      <line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
    <label for="pos-search" class="sr-only">Buscar dispositivos</label>
    <input
      id="pos-search"
      name="search"
      type="text"
      class="search-input"
      {placeholder}
      bind:value
    />
    {#if value}
      <button class="clear-search" on:click={() => { value = ''; }}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    {/if}
  </div>

  <div class="search-actions">
    <button
      class="filter-toggle-btn {showFilters || hasActiveFilters() ? 'active' : ''}"
      on:click={() => showFilters = !showFilters}
      title="Filtros avanzados"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
      </svg>
      <span class="btn-label">Filtros</span>
    </button>
  </div>

  {#if showFilters}
    <div class="filters-panel">
      <div class="filters-grid">
        <div class="filter-group">
          <label for="filter-status" class="filter-label">Estado</label>
          <select id="filter-status" class="filter-select" bind:value={filters.status}>
            {#each statusOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>

        <div class="filter-group">
          <label for="filter-type" class="filter-label">Tipo de dispositivo</label>
          <select id="filter-type" class="filter-select" bind:value={filters.device_type}>
            {#each deviceTypeOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>

        <div class="filter-group">
          <label for="filter-brand" class="filter-label">Marca</label>
          <select id="filter-brand" class="filter-select" bind:value={filters.brand}>
            {#each brandOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>
      </div>

      {#if hasActiveFilters()}
        <div class="filters-footer">
          <button class="clear-all-btn" on:click={clearAll}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            Limpiar filtros
          </button>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .device-search-bar {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .search-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  .search-icon {
    position: absolute;
    left: 1rem;
    width: 20px;
    height: 20px;
    color: var(--text-light);
    pointer-events: none;
  }

  .search-input {
    width: 100%;
    padding: 0.75rem 3rem 0.75rem 3rem;
    font-size: 1rem;
    border: 2px solid var(--border);
    border-radius: var(--radius);
    background: white;
    color: var(--text);
    transition: all 0.2s;
  }

  .search-input:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }

  .search-input::placeholder {
    color: var(--text-light);
  }

  .clear-search {
    position: absolute;
    right: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border: none;
    background: var(--light);
    border-radius: 50%;
    cursor: pointer;
    color: var(--text-light);
    transition: all 0.2s;
  }

  .clear-search:hover {
    background: var(--border);
    color: var(--text);
  }

  .clear-search svg {
    width: 16px;
    height: 16px;
  }

  .search-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 0.75rem;
  }

  .filter-toggle-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.875rem;
    border: 1px solid var(--border);
    background: white;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all 0.2s;
    color: var(--text-light);
    font-size: 0.875rem;
  }

  .filter-toggle-btn svg {
    width: 18px;
    height: 18px;
  }

  .filter-toggle-btn:hover {
    border-color: var(--primary);
    color: var(--primary);
  }

  .filter-toggle-btn.active {
    background: var(--primary);
    border-color: var(--primary);
    color: white;
  }

  .btn-label {
    display: none;
  }

  @media (min-width: 640px) {
    .btn-label {
      display: inline;
    }
  }

  .filters-panel {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
  }

  .filters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
  }

  .filter-label {
    font-size: 0.8125rem;
    font-weight: 500;
    color: var(--text);
  }

  .filter-select {
    padding: 0.625rem 0.875rem;
    font-size: 0.875rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: white;
    color: var(--text);
    cursor: pointer;
    transition: all 0.2s;
  }

  .filter-select:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }

  .filters-footer {
    display: flex;
    justify-content: flex-end;
    margin-top: 1rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--border);
  }

  .clear-all-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.875rem;
    border: 1px solid var(--border);
    background: white;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all 0.2s;
    color: var(--text-light);
    font-size: 0.875rem;
  }

  .clear-all-btn svg {
    width: 16px;
    height: 16px;
  }

  .clear-all-btn:hover {
    border-color: var(--danger);
    color: var(--danger);
  }

  @media (max-width: 640px) {
    .device-search-bar {
      padding: 0.75rem;
    }

    .search-input {
      padding: 0.625rem 2.75rem 0.625rem 2.75rem;
      font-size: 0.9375rem;
    }

    .filters-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
