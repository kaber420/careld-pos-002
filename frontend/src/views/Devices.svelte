<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { api } from '../stores/api';
  import { notify } from '../stores/auth';
  import Layout from '../components/Layout.svelte';
  import DeviceForm from '../components/devices/DeviceForm.svelte';

  let devices = [];
  let customers = [];
  let isLoading = true;
  let showForm = false;
  let editingDevice = null;
  let filters = {
    customer_id: '',
    status: '',
    search: ''
  };
  
  // Para el componente DeviceForm
  let selectedCustomerId = '';
  let photos = [];
  let deviceForm = {
    brand: '',
    model: '',
    serial_number: '',
    imei: '',
    device_type: 'smartphone',
    color: '',
    storage: '',
    password_pattern: '',
    accessories: ''
  };

  const statusLabels = {
    registered: 'Registrado',
    in_repair: 'En Reparación',
    waiting_parts: 'Esperando Repuestos',
    ready: 'Listo',
    delivered: 'Entregado'
  };

  onMount(async () => {
    await loadCustomers();
    await loadDevices();
  });

  async function loadDevices() {
    isLoading = true;
    try {
      const params = {};
      if (filters.customer_id) params.customer_id = filters.customer_id;
      if (filters.status) params.status = filters.status;
      if (filters.search) params.search = filters.search;
      devices = await api.getDevices(params);
    } catch (error) {
      notify(error.message, 'danger');
    } finally {
      isLoading = false;
    }
  }

  async function loadCustomers() {
    try {
      const data = await api.getCustomers({ limit: 1000 });
      customers = data || [];
    } catch (error) {
      console.error('Error loading customers:', error);
      customers = [];
    }
  }

  function openForm(device = null) {
    if (customers.length === 0) {
      notify('Primero debes crear un cliente en la sección de Clientes', 'warning');
      navigate('/customers');
      return;
    }
    if (device) {
      editingDevice = device;
      selectedCustomerId = device.customer_id;
      photos = device.photos ? device.photos.split(',').filter(p => p.trim()) : [];
      deviceForm = {
        brand: device.brand || '',
        model: device.model || '',
        serial_number: device.serial_number || '',
        imei: device.imei || '',
        device_type: device.device_type || 'smartphone',
        color: device.color || '',
        storage: device.storage || '',
        password_pattern: device.password_pattern || '',
        accessories: device.accessories || '',
        description: ''
      };
    } else {
      editingDevice = null;
      selectedCustomerId = customers[0]?.id || '';
      photos = [];
      deviceForm = {
        brand: '',
        model: '',
        serial_number: '',
        imei: '',
        device_type: 'smartphone',
        color: '',
        storage: '',
        password_pattern: '',
        accessories: '',
        description: ''
      };
    }
    showForm = true;
  }

  function closeForm() {
    showForm = false;
    editingDevice = null;
  }

  function handleFormSubmit() {
    closeForm();
    loadDevices();
  }

  async function handleDelete(device) {
    if (!confirm(`¿Estás seguro de eliminar este dispositivo?`)) return;

    try {
      await api.deleteDevice(device.id);
      notify('Dispositivo eliminado correctamente', 'success');
      loadDevices();
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  function handleFilter() {
    loadDevices();
  }

  function getCustomerName(customerId) {
    const customer = customers.find(c => c.id === customerId);
    return customer?.name || 'Desconocido';
  }
</script>

<Layout>
  <div class="devices-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Dispositivos</h1>
        <p class="page-subtitle">Gestión de dispositivos de clientes</p>
      </div>
    <button class="btn btn-primary" on:click={() => openForm()}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="12" y1="5" x2="12" y2="19"/>
        <line x1="5" y1="12" x2="19" y2="12"/>
      </svg>
      Nuevo Dispositivo
    </button>
  </div>

  <div class="card">
    <div class="card-body">
      <!-- Filters -->
      <div class="filters-bar">
        <div class="flex gap-3" style="flex-wrap: wrap;">
          <input
            type="text"
            class="input"
            placeholder="Buscar por marca o modelo..."
            bind:value={filters.search}
            style="min-width: 200px;"
          />
          <select class="select" bind:value={filters.customer_id} style="min-width: 150px;">
            <option value="">Todos los clientes</option>
            {#each customers as customer}
              <option value={customer.id}>{customer.name}</option>
            {/each}
          </select>
          <select class="select" bind:value={filters.status} style="min-width: 150px;">
            <option value="">Todos los estados</option>
            {#each Object.entries(statusLabels) as [value, label]}
              <option value={value}>{label}</option>
            {/each}
          </select>
          <button class="btn btn-outline" on:click={handleFilter}>Filtrar</button>
          <button class="btn btn-outline" on:click={() => { filters = { customer_id: '', status: '', search: '' }; loadDevices(); }}>Limpiar</button>
        </div>
      </div>

      <!-- Table -->
      {#if isLoading}
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Cargando dispositivos...</p>
        </div>
      {:else if devices.length === 0}
        <div class="empty-state">
          <div class="empty-state-icon">📱</div>
          <p class="empty-state-title">No hay dispositivos registrados</p>
          <p class="empty-state-description">
            {#if customers.length === 0}
              Primero crea un cliente para registrar dispositivos
            {:else}
              Comienza agregando un nuevo dispositivo
            {/if}
          </p>
          <button class="btn btn-primary mt-4" on:click={() => customers.length === 0 ? navigate('/customers') : openForm()}>
            {customers.length === 0 ? 'Crear Cliente' : 'Agregar Dispositivo'}
          </button>
        </div>
      {:else}
        <div class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Marca/Modelo</th>
                <th>Tipo</th>
                <th>IMEI/Serial</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {#each devices as device}
                <tr>
                  <td>{getCustomerName(device.customer_id)}</td>
                  <td class="font-medium">{device.brand} {device.model}</td>
                  <td>
                    <span class="badge badge-secondary">{device.device_type}</span>
                  </td>
                  <td>
                    {#if device.imei}
                      <small>IMEI: {device.imei}</small>
                    {:else if device.serial_number}
                      <small>S/N: {device.serial_number}</small>
                    {:else}
                      -
                    {/if}
                  </td>
                  <td>
                    <span class="badge badge-{
                      device.status === 'in_repair' ? 'primary' :
                      device.status === 'ready' ? 'success' :
                      device.status === 'delivered' ? 'success' :
                      'warning'
                    }">
                      {statusLabels[device.status]}
                    </span>
                  </td>
                  <td>
                    <div class="flex gap-2">
                      <button
                        class="btn btn-sm btn-outline"
                        on:click={() => openForm(device)}
                      >
                        Editar
                      </button>
                      <button
                        class="btn btn-sm btn-danger"
                        on:click={() => handleDelete(device)}
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
            {editingDevice ? 'Editar Dispositivo' : 'Nuevo Dispositivo'}
          </h3>
          <button class="custom-modal-close" on:click={closeForm}>×</button>
        </div>

        <DeviceForm
          {customers}
          bind:selectedCustomerId
          bind:deviceForm
          bind:photos
          isEditing={!!editingDevice}
          editingDeviceId={editingDevice?.id}
          submitLabel={editingDevice ? 'Actualizar Dispositivo' : 'Registrar Dispositivo'}
          showDescription={false}
          showPhotos={true}
          onSubmit={handleFormSubmit}
          onClose={closeForm}
        />
      </div>
    </div>
  {/if}
  </div>
</Layout>

<style>
  .devices-page {
    max-width: 1200px;
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

  .empty-state-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--dark);
    margin-bottom: 0.5rem;
  }

  .modal-lg {
    max-width: 700px;
  }
</style>
