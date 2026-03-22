<script>
  import { onMount } from 'svelte';
  import { api } from '../stores/api';
  import { notify } from '../stores/auth';
  import Layout from '../components/Layout.svelte';

  let customers = [];
  let isLoading = true;
  let search = '';
  let showForm = false;
  let editingCustomer = null;

  let formData = {
    name: '',
    email: '',
    phone: '',
    alternate_phone: '',
    address: '',
    notes: ''
  };

  onMount(async () => {
    await loadCustomers();
  });

  async function loadCustomers() {
    isLoading = true;
    try {
      customers = await api.getCustomers({ search });
    } catch (error) {
      notify(error.message, 'danger');
    } finally {
      isLoading = false;
    }
  }

  function handleSearch() {
    loadCustomers();
  }

  function openForm(customer = null) {
    if (customer) {
      editingCustomer = customer;
      formData = {
        name: customer.name || '',
        email: customer.email || '',
        phone: customer.phone || '',
        alternate_phone: customer.alternate_phone || '',
        address: customer.address || '',
        notes: customer.notes || ''
      };
    } else {
      editingCustomer = null;
      formData = {
        name: '',
        email: '',
        phone: '',
        alternate_phone: '',
        address: '',
        notes: ''
      };
    }
    showForm = true;
  }

  function closeForm() {
    showForm = false;
    editingCustomer = null;
  }

  async function handleSubmit() {
    try {
      if (editingCustomer) {
        await api.updateCustomer(editingCustomer.id, formData);
        notify('Cliente actualizado correctamente', 'success');
      } else {
        await api.createCustomer(formData);
        notify('Cliente creado correctamente', 'success');
      }
      closeForm();
      loadCustomers();
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  async function handleDelete(customer) {
    if (!confirm(`¿Estás seguro de eliminar a ${customer.name}?`)) return;

    try {
      await api.deleteCustomer(customer.id);
      notify('Cliente eliminado correctamente', 'success');
      loadCustomers();
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  function formatPhone(phone) {
    if (!phone) return '-';
    return phone;
  }

  function formatEmail(email) {
    if (!email) return '-';
    return email;
  }
</script>

<Layout>
  <div class="customers-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Clientes</h1>
        <p class="page-subtitle">Gestión de clientes del taller</p>
      </div>
    <button class="btn btn-primary" on:click={() => openForm()}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="12" y1="5" x2="12" y2="19"/>
        <line x1="5" y1="12" x2="19" y2="12"/>
      </svg>
      Nuevo Cliente
    </button>
  </div>

  <div class="card">
    <div class="card-body">
      <!-- Search Bar -->
      <div class="actions-bar">
        <input
          type="text"
          class="input search-input"
          placeholder="Buscar por nombre, email o teléfono..."
          bind:value={search}
          on:keyup={(e) => e.key === 'Enter' && handleSearch()}
        />
        <div class="flex gap-2">
          <button class="btn btn-outline" on:click={handleSearch}>
            Buscar
          </button>
          <button class="btn btn-outline" on:click={() => { search = ''; loadCustomers(); }}>
            Limpiar
          </button>
        </div>
      </div>

      <!-- Table -->
      {#if isLoading}
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Cargando clientes...</p>
        </div>
      {:else if customers.length === 0}
        <div class="empty-state">
          <div class="empty-state-icon">👥</div>
          <p class="empty-state-title">No hay clientes registrados</p>
          <p class="empty-state-description">Comienza agregando un nuevo cliente</p>
          <button class="btn btn-primary mt-4" on:click={() => openForm()}>
            Agregar Cliente
          </button>
        </div>
      {:else}
        <div class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Email</th>
                <th>Teléfono</th>
                <th>Teléfono Alt.</th>
                <th>Dirección</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {#each customers as customer}
                <tr>
                  <td class="font-medium">{customer.name}</td>
                  <td>{formatEmail(customer.email)}</td>
                  <td>{formatPhone(customer.phone)}</td>
                  <td>{formatPhone(customer.alternate_phone)}</td>
                  <td>{customer.address || '-'}</td>
                  <td>
                    <div class="flex gap-2">
                      <button
                        class="btn btn-sm btn-outline"
                        on:click={() => openForm(customer)}
                      >
                        Editar
                      </button>
                      <button
                        class="btn btn-sm btn-danger"
                        on:click={() => handleDelete(customer)}
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
      <div class="custom-modal">
        <div class="custom-modal-header">
          <h3 class="custom-modal-title">
            {editingCustomer ? 'Editar Cliente' : 'Nuevo Cliente'}
          </h3>
          <button class="custom-modal-close" on:click={closeForm}>×</button>
        </div>

        <form on:submit|preventDefault={handleSubmit}>
          <div class="custom-modal-body">
            <div class="form-group">
              <label class="label" for="name">Nombre *</label>
              <input
                id="name"
                type="text"
                class="input"
                bind:value={formData.name}
                required
              />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="label" for="email">Email</label>
                <input
                  id="email"
                  type="email"
                  class="input"
                  bind:value={formData.email}
                />
              </div>

              <div class="form-group">
                <label class="label" for="phone">Teléfono *</label>
                <input
                  id="phone"
                  type="tel"
                  class="input"
                  bind:value={formData.phone}
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label class="label" for="alternate_phone">Teléfono Alternativo</label>
              <input
                id="alternate_phone"
                type="tel"
                class="input"
                bind:value={formData.alternate_phone}
              />
            </div>

            <div class="form-group">
              <label class="label" for="address">Dirección</label>
              <textarea
                id="address"
                class="textarea"
                bind:value={formData.address}
                rows="2"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="label" for="notes">Notas</label>
              <textarea
                id="notes"
                class="textarea"
                bind:value={formData.notes}
                rows="3"
              ></textarea>
            </div>
          </div>

          <div class="custom-modal-footer">
            <button type="button" class="btn btn-outline" on:click={closeForm}>
              Cancelar
            </button>
            <button type="submit" class="btn btn-primary">
              {editingCustomer ? 'Actualizar' : 'Crear'} Cliente
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}
  </div>
</Layout>

<style>
  .customers-page {
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

  .empty-state-description {
    color: var(--text-light);
    margin-bottom: 1rem;
  }
</style>
