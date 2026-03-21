<script>
  import { onMount } from 'svelte';
  import { api } from '../stores/api';
  import { notify } from '../stores/auth';
  import Layout from '../components/Layout.svelte';

  let orders = [];
  let loading = true;

  onMount(loadOrders);

  async function loadOrders() {
    loading = true;
    try {
      orders = await api.getAllPartnerOrders();
    } catch (error) {
      notify('Error al cargar pedidos', 'danger');
    } finally {
      loading = false;
    }
  }

  async function updateStatus(orderId, newStatus) {
    try {
      await api.updatePartnerOrderStatus(orderId, newStatus);
      notify('Estado actualizado', 'success');
      loadOrders();
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  function getStatusLabel(status) {
    const labels = {
      'pending': 'Pendiente',
      'confirmed': 'Confirmado',
      'cancelled': 'Cancelado',
      'completed': 'Completado'
    };
    return labels[status] || status;
  }

  function getStatusClass(status) {
    const classes = {
      'pending': 'badge-warning',
      'confirmed': 'badge-info',
      'cancelled': 'badge-danger',
      'completed': 'badge-success'
    };
    return classes[status] || '';
  }
</script>

<Layout>
  <div class="partner-orders-admin">
    <div class="page-header">
      <div>
        <h1 class="page-title">Pedidos de Socios</h1>
        <p class="page-subtitle">Gestiona las solicitudes de refacciones de los socios comerciales</p>
      </div>
      <button class="btn btn-outline" on:click={loadOrders}>
        Actualizar
      </button>
    </div>

    <div class="card mt-6">
      <div class="card-body">
        {#if loading}
          <div class="text-center py-20">
            <div class="spinner"></div>
            <p>Cargando pedidos...</p>
          </div>
        {:else if orders.length === 0}
          <div class="empty-state">
            <div class="empty-state-icon">📦</div>
            <p class="empty-state-title">No hay pedidos pendientes</p>
          </div>
        {:else}
          <div class="table-container">
            <table class="table">
              <thead>
                <tr>
                  <th>Pedido</th>
                  <th>Socio</th>
                  <th>Fecha</th>
                  <th>Items</th>
                  <th>Total</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {#each orders as order}
                  <tr>
                    <td><code class="text-sm font-bold">{order.order_number}</code></td>
                    <td>
                      <div class="font-medium">{order.partner?.full_name || 'Desconocido'}</div>
                      <div class="text-xs text-light">{order.partner?.username || ''}</div>
                    </td>
                    <td>{new Date(order.created_at).toLocaleDateString()} {new Date(order.created_at).toLocaleTimeString()}</td>
                    <td>
                      <div class="text-xs">
                        {#each order.items as item}
                          <div>{item.quantity}x {item.inventory_item?.name}</div>
                        {/each}
                      </div>
                    </td>
                    <td class="font-bold">${order.total.toFixed(2)}</td>
                    <td>
                      <span class="badge {getStatusClass(order.status)}">
                        {getStatusLabel(order.status)}
                      </span>
                    </td>
                    <td>
                      <div class="flex gap-2">
                        {#if order.status === 'pending'}
                          <button 
                            class="btn btn-sm btn-info"
                            on:click={() => updateStatus(order.id, 'confirmed')}
                          >
                            Confirmar
                          </button>
                        {/if}
                        {#if order.status === 'confirmed'}
                          <button 
                            class="btn btn-sm btn-success"
                            on:click={() => updateStatus(order.id, 'completed')}
                          >
                            Entregado
                          </button>
                        {/if}
                        {#if order.status !== 'completed' && order.status !== 'cancelled'}
                          <button 
                            class="btn btn-sm btn-outline text-danger"
                            on:click={() => updateStatus(order.id, 'cancelled')}
                          >
                            Cancelar
                          </button>
                        {/if}
                      </div>
                    </td>
                  </tr>
                  {#if order.notes}
                    <tr class="notes-row">
                      <td colspan="7" class="text-xs italic bg-light p-2 px-4">
                        <strong>Nota:</strong> {order.notes}
                      </td>
                    </tr>
                  {/if}
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </div>
    </div>
  </div>
</Layout>

<style>
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .page-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--dark);
  }

  .page-subtitle {
    color: var(--text-light);
    font-size: 0.875rem;
  }

  .notes-row td {
    border-top: none;
    padding-top: 0;
  }

  .bg-light {
    background-color: var(--light);
  }
</style>
