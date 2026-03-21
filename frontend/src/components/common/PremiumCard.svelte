<script>
  export let title = '';
  export let subtitle = '';
  export let padding = 'p-6';
</script>

<div class="premium-card card-premium glass-premium {padding} mb-6">
  {#if title || subtitle}
    <div class="card-header-premium mb-6">
      {#if title}
        <h2 class="text-2xl font-black text-gradient mb-1" style="-webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;">{title}</h2>
      {/if}
      {#if subtitle}
        <p class="text-xs text-gray-400 font-black uppercase tracking-widest">{subtitle}</p>
      {/if}
    </div>
  {/if}
  <div class="card-content">
    <slot />
  </div>
</div>

<style>
  .card-header-premium {
    border-bottom: 1px solid var(--border);
    padding-bottom: 1.5rem;
  }
</style>
