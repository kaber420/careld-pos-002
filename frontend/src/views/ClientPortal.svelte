<script>
  import { onMount } from 'svelte';
  import { notify } from '../stores/auth';
  import { fade } from 'svelte/transition';
  import PremiumCard from '../components/common/PremiumCard.svelte';
  import Timeline from '../components/common/Timeline.svelte';

  export let token = null;
  let repair = null;
  let history = [];
  let loading = true;
  let error = null;
  let approvalStatus = null; // null = pending, true = approved, false = rejected

  // Use token from prop if available, otherwise from URL
  $: effectiveToken = token || window.location.pathname.split('/').pop();

  onMount(async () => {
    if (!effectiveToken) {
      error = 'Enlace de portal inválido';
      loading = false;
      return;
    }

    try {
      const [repairRes, historyRes] = await Promise.all([
        fetch(`/api/v1/repairs/portal/${effectiveToken}`),
        fetch(`/api/v1/repairs/portal/${effectiveToken}/history`)
      ]);

      if (!repairRes.ok) {
        throw new Error(`Error al cargar los detalles de la reparación`);
      }
      
      repair = await repairRes.json();
      
      if (historyRes.ok) {
        history = await historyRes.json();
      }

      // Determine approval status from the repair object
      if (repair.client_approved === true) {
        approvalStatus = true;
      } else if (repair.client_approved === false) {
        approvalStatus = false;
      } else {
        approvalStatus = null; // pending
      }
    } catch (err) {
      error = 'No se pudieron cargar los detalles de la reparación. El enlace puede haber expirado.';
      console.error(err);
    } finally {
      loading = false;
    }
  });

  async function approve() {
    try {
      const response = await fetch(`/api/v1/repairs/portal/${effectiveToken}/approve`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      // Update local state
      repair.client_approved = true;
      approvalStatus = true;
      notify('¡Gracias por aprobar el presupuesto!', 'success');
      
      // Refresh history to show approval
      const historyRes = await fetch(`/api/v1/repairs/portal/${effectiveToken}/history`);
      if (historyRes.ok) history = await historyRes.json();
      
    } catch (err) {
      notify('Error al aprobar el presupuesto. Por favor, inténtalo de nuevo.', 'error');
      console.error(err);
    }
  }

  async function reject() {
    try {
      const response = await fetch(`/api/v1/repairs/portal/${effectiveToken}/reject`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      // Update local state
      repair.client_approved = false;
      approvalStatus = false;
      notify('Hemos registrado tu rechazo. Nos pondremos en contacto contigo.', 'info');
      
      // Refresh history
      const historyRes = await fetch(`/api/v1/repairs/portal/${effectiveToken}/history`);
      if (historyRes.ok) history = await historyRes.json();

    } catch (err) {
      notify('Error al rechazar el presupuesto. Por favor, inténtalo de nuevo.', 'error');
      console.error(err);
    }
  }

  function getStatusLabel(status) {
    const labels = {
      pending: 'Pendiente de revisión',
      diagnosing: 'En diagnóstico',
      waiting_approval: 'Esperando tu aprobación',
      in_progress: 'En reparación',
      waiting_parts: 'Esperando repuestos',
      completed: 'Reparación completada',
      delivered: 'Entregado',
      cancelled: 'Cancelada'
    };
    return labels[status.toLowerCase()] || status;
  }
</script>

<div class="premium-portal-wrapper">
  <div class="background-decor"></div>
  
  <div class="client-portal">
    {#if loading}
      <div class="loading glass rounded-lg">
        <div class="spinner"></div>
        <p>Cargando información de tu reparación...</p>
      </div>
    {:else if error}
      <div class="error glass rounded-lg p-6">
        <h2 class="text-xl font-bold text-danger mb-2">¡Oops!</h2>
        <p class="mb-4">{error}</p>
        <p class="text-sm text-muted">Si crees que esto es un error, por favor contacta al taller directamente.</p>
      </div>
    {:else if repair}
      <header class="mb-8 text-center" in:fade>
        <h1 class="text-3xl font-bold text-gradient mb-2" style="font-family: 'Outfit', sans-serif; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;">Estado de tu Reparación</h1>
        <p class="text-muted">Orden #{repair.repair_number}</p>
      </header>

      <div class="grid-portal">
        <div class="left-col">
          <PremiumCard title="Detalles del Equipo" subtitle="Información registrada en el taller">
            <div class="info-grid">
              <div class="info-item">
                <span class="label">Dispositivo</span>
                <span class="value">{repair.device?.brand || ''} {repair.device?.model || 'Desconocido'}</span>
              </div>
              <div class="info-item">
                <span class="label">Problema</span>
                <span class="value">{repair.description}</span>
              </div>
              <div class="info-item">
                <span class="label">Estado Actual</span>
                <span class="value status-badge {repair.status.toLowerCase()}">
                  {getStatusLabel(repair.status)}
                </span>
              </div>
            </div>
            
            {#if repair.diagnosis}
              <div class="diagnosis-box mt-4 p-3 rounded">
                <span class="label block mb-1">Diagnóstico Técnico</span>
                <p class="text-sm">{repair.diagnosis}</p>
              </div>
            {/if}
          </PremiumCard>

          {#if (repair.estimated_cost !== null || repair.final_cost !== null) && (approvalStatus === null || approvalStatus === true)}
            <PremiumCard title="Presupuesto y Pago" subtitle="Detalle económico de la reparación">
              <div class="cost-summary">
                <div class="flex justify-between items-center mb-4">
                  <span class="text-lg">Total a pagar</span>
                  <span class="text-2xl font-bold text-gradient">
                    ${(repair.final_cost || repair.estimated_cost).toFixed(2)}
                  </span>
                </div>
                
                {#if approvalStatus === null}
                  <p class="text-xs text-muted mb-4">Este costo incluye mano de obra y todos los repuestos necesarios.</p>
                  <div class="flex gap-3">
                    <button on:click={approve} class="btn btn-primary flex-1">Aprobar</button>
                    <button on:click={reject} class="btn btn-outline flex-1">Rechazar</button>
                  </div>
                {:else if approvalStatus === true}
                  <div class="alert alert-success mt-2 mb-0">
                    ✅ Presupuesto aprobado. Estamos trabajando en tu equipo.
                  </div>
                {/if}
              </div>
            </PremiumCard>
          {:else if approvalStatus === false}
            <div class="alert alert-danger glass mb-6">
              ❌ Has rechazado este presupuesto. Nos pondremos en contacto contigo pronto.
            </div>
          {/if}
        </div>

        <div class="right-col">
          <PremiumCard title="Línea de Tiempo" subtitle="Seguimiento paso a paso">
            <Timeline items={history} />
          </PremiumCard>

          {#if repair.delivered_at}
             <div class="glass rounded-lg p-4 text-center">
                <p class="text-sm">Equipo entregado el</p>
                <p class="font-bold">{new Date(repair.delivered_at).toLocaleDateString()}</p>
             </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .premium-portal-wrapper {
    min-height: 100vh;
    padding: 2rem 1rem;
    position: relative;
    overflow: hidden;
    background: #f8fafc;
  }

  .background-decor {
    position: absolute;
    top: -10%;
    right: -10%;
    width: 40%;
    height: 40%;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
    z-index: 0;
  }

  .client-portal {
    max-width: 1000px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
  }

  .grid-portal {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 1.5rem;
  }

  @media (max-width: 768px) {
    .grid-portal {
      grid-template-columns: 1fr;
    }
  }

  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem;
    text-align: center;
  }

  .info-grid {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .info-item .label {
    display: block;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-light);
    margin-bottom: 0.25rem;
  }

  .info-item .value {
    font-weight: 500;
    color: var(--dark);
  }

  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .status-badge.pending { background: #fef3c7; color: #92400e; }
  .status-badge.diagnosing { background: #dbeafe; color: #1e40af; }
  .status-badge.in_progress { background: #dcfce7; color: #166534; }
  .status-badge.completed { background: #dcfce7; color: #166534; border: 1px solid var(--success); }
  
  .diagnosis-box {
    background: rgba(0,0,0,0.03);
    border-left: 3px solid var(--primary);
  }

  .cost-summary {
    padding-top: 0.5rem;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>