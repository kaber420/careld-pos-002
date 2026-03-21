<script>
  import { fade, slide } from 'svelte/transition';
  export let items = []; // { to_status: string, description: string, created_at: string }

  const statusIcons = {
    pending: '🕒',
    diagnosing: '🔍',
    waiting_approval: '⚠️',
    in_progress: '🛠️',
    waiting_parts: '📦',
    completed: '✅',
    delivered: '🤝',
    cancelled: '❌'
  };

  const statusColors = {
    pending: 'var(--warning)',
    diagnosing: 'var(--primary)',
    waiting_approval: 'var(--warning)',
    in_progress: 'var(--primary)',
    waiting_parts: 'var(--warning)',
    completed: 'var(--success)',
    delivered: 'var(--success)',
    cancelled: 'var(--danger)'
  };
</script>

<div class="timeline">
  {#each items as item, i (item.id || i)}
    <div class="timeline-item" in:slide={{ delay: i * 50 }}>
      <div class="timeline-marker" style="border-color: {statusColors[item.to_status] || 'var(--border)'}">
        <span class="icon">{statusIcons[item.to_status] || '•'}</span>
      </div>
      <div class="timeline-content glass rounded p-3">
        <div class="flex justify-between items-start mb-1">
          <h3 class="font-semibold text-sm">{item.description}</h3>
          <span class="text-xs text-muted whitespace-nowrap ml-2">
            {new Date(item.created_at).toLocaleDateString()} {new Date(item.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
          </span>
        </div>
      </div>
    </div>
  {/each}
  
  {#if items.length === 0}
    <p class="text-center text-muted text-sm py-4">No hay historial disponible todavía.</p>
  {/if}
</div>

<style>
  .timeline {
    position: relative;
    padding-left: 2rem;
    margin-top: 1rem;
  }
  .timeline::before {
    content: '';
    position: absolute;
    left: 0.75rem;
    top: 0.5rem;
    bottom: 0.5rem;
    width: 2px;
    background: var(--border);
    opacity: 0.5;
  }
  .timeline-item {
    position: relative;
    padding-bottom: 1.5rem;
  }
  .timeline-item:last-child {
    padding-bottom: 0;
  }
  .timeline-marker {
    position: absolute;
    left: -2rem;
    width: 1.5rem;
    height: 1.5rem;
    background: white;
    border: 2px solid var(--border);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  }
  .icon {
    font-size: 0.8rem;
  }
  .timeline-content {
    border-radius: var(--radius);
  }
</style>
