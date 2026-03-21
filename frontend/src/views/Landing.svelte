<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { api } from '../stores/api';

  let isLoading = true;

  onMount(async () => {
    try {
      const status = await api.checkStatus();
      localStorage.setItem('needs_setup', status.needs_setup);
    } catch (err) {
      console.error('Error:', err);
    }
    isLoading = false;
  });

  function goToApp() {
    const needsSetup = localStorage.getItem('needs_setup') === 'true';
    navigate(needsSetup ? '/setup' : '/login');
  }
</script>

<div class="landing">
  <div class="landing-content">
    <div class="hero">
      <div class="logo-large">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
        </svg>
      </div>
      <h1 class="flex items-center justify-center gap-2">
        CareldPOS
        <div class="badge badge-secondary">v1.0</div>
      </h1>
      <p class="tagline">Sistema de Gestión para Talleres de Reparación</p>
    </div>

    <div class="features">
      <div class="feature">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="5" y="2" width="14" height="20" rx="2" ry="2"/>
          <line x1="12" y1="18" x2="12.01" y2="18"/>
        </svg>
        <h3>Control de Dispositivos</h3>
        <p>Gestiona equipos recibida para reparación</p>
      </div>
      <div class="feature">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
        </svg>
        <h3>Reparaciones</h3>
        <p>Seguimiento completo de reparaciones</p>
      </div>
      <div class="feature">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="1" x2="12" y2="23"/>
          <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
        </svg>
        <h3>Pagos</h3>
        <p>Gestión de pagos y facturación</p>
      </div>
      <div class="feature">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
          <line x1="12" y1="22.08" x2="12" y2="12"/>
        </svg>
        <h3>Inventario</h3>
        <p>Control de refacciones y materiales</p>
      </div>
    </div>

    <button class="btn btn-primary btn-large" on:click={goToApp}>
      Entrar al Sistema
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="5" y1="12" x2="19" y2="12"/>
        <polyline points="12 5 19 12 12 19"/>
      </svg>
    </button>
  </div>
</div>

<style>
  .landing {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }

  .landing-content {
    max-width: 800px;
    text-align: center;
  }

  .hero {
    margin-bottom: 3rem;
  }

  .logo-large {
    width: 120px;
    height: 120px;
    margin: 0 auto 1.5rem;
    background: white;
    border-radius: var(--radius-xl);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--primary);
    box-shadow: 0 20px 40px rgba(0,0,0,0.2);
  }

  .logo-large svg {
    width: 64px;
    height: 64px;
  }

  .hero h1 {
    font-size: 3rem;
    font-weight: 800;
    color: white;
    margin-bottom: 0.5rem;
  }

  .tagline {
    font-size: 1.25rem;
    color: rgba(255,255,255,0.8);
  }

  .features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3rem;
  }

  .feature {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    padding: 1.5rem;
    border-radius: var(--radius-lg);
    color: white;
    text-align: center;
  }

  .feature svg {
    width: 32px;
    height: 32px;
    margin-bottom: 0.75rem;
  }

  .feature h3 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }

  .feature p {
    font-size: 0.875rem;
    color: rgba(255,255,255,0.7);
    margin: 0;
  }

  .btn-large {
    padding: 1rem 2.5rem;
    font-size: 1.125rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
  }

  .btn-large svg {
    width: 20px;
    height: 20px;
  }
</style>
