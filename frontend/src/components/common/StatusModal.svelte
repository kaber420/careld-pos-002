<script>
  export let show = false;
  export let title = "Cambiar Estado";
  export let currentStatus = "";
  export let options = {}; // { value: label }
  export let onSelect = (status) => {};
  export let onClose = () => {};

  const statusColors = {
    registered: 'border-secondary',
    pending: 'border-warning',
    in_repair: 'border-primary',
    in_progress: 'border-primary',
    diagnosing: 'border-info',
    waiting_parts: 'border-orange',
    waiting_approval: 'border-warning',
    ready: 'border-success',
    completed: 'border-success',
    delivered: 'border-success-dark',
    cancelled: 'border-danger'
  };

  function handleSelect(status) {
    onSelect(status);
    onClose();
  }
</script>

{#if show}
  <div class="custom-modal-overlay" on:click|self={onClose}>
    <div class="custom-modal status-modal">
      <div class="custom-modal-header">
        <h3 class="custom-modal-title">{title}</h3>
        <button class="custom-modal-close" on:click={onClose}>×</button>
      </div>
      <div class="custom-modal-body">
        <div class="status-grid">
          {#each Object.entries(options) as [value, label]}
            <button 
              class="status-btn {statusColors[value] || 'border-secondary'} {currentStatus === value ? 'active' : ''}"
              on:click={() => handleSelect(value)}
            >
              <div class="status-indicator"></div>
              <span class="status-label">{label}</span>
              {#if currentStatus === value}
                <span class="current-badge">Actual</span>
              {/if}
            </button>
          {/each}
        </div>
      </div>
      <div class="custom-modal-footer">
        <button class="btn btn-outline btn-block" on:click={onClose}>Cancelar</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .status-modal {
    max-width: 450px;
    width: 90%;
  }

  .status-grid {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .status-btn {
    display: flex;
    align-items: center;
    padding: 1rem;
    background: white;
    border: 2px solid var(--border-light);
    border-radius: var(--radius);
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
    position: relative;
  }

  .status-btn:hover {
    background: var(--light);
    transform: translateX(4px);
    border-color: var(--primary);
  }

  .status-btn.active {
    background: #f0f7ff;
    border-color: var(--primary);
  }

  .status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 1.25rem;
    flex-shrink: 0;
  }

  /* Colors based on borders */
  .border-primary .status-indicator { background-color: #3b82f6; }
  .border-secondary .status-indicator { background-color: #6b7280; }
  .border-warning .status-indicator { background-color: #f59e0b; }
  .border-success .status-indicator { background-color: #10b981; }
  .border-success-dark .status-indicator { background-color: #065f46; }
  .border-danger .status-indicator { background-color: #ef4444; }
  .border-info .status-indicator { background-color: #06b6d4; }
  .border-orange .status-indicator { background-color: #eb5e28; }

  .status-label {
    font-size: 1rem;
    font-weight: 500;
    color: var(--dark);
    flex: 1;
  }

  .current-badge {
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    background: var(--primary);
    color: white;
    border-radius: 12px;
    font-weight: 600;
  }

  /* Status Colors */
  .border-primary { border-color: #e0f2fe; }
  .border-warning { border-color: #fef3c7; }
  .border-success { border-color: #dcfce7; }
  .border-danger { border-color: #fee2e2; }
  
  .status-btn.active.border-primary { border-color: #3b82f6; }
  .status-btn.active.border-warning { border-color: #f59e0b; }
  .status-btn.active.border-success { border-color: #10b981; }

  .btn-block {
    width: 100%;
  }
</style>
