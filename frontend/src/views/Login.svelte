<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { user, isAuthenticated, notify } from '../stores/auth';
  import { api } from '../stores/api';

  let isLoading = true;
  
  let username = '';
  let password = '';
  let error = '';
  let isLoggingIn = false;

  onMount(async () => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      try {
        const userData = await api.getMe();
        user.set(userData);
        isAuthenticated.set(true);
        navigate('/dashboard');
        return;
      } catch {
        localStorage.removeItem('token');
      }
    }

    try {
      const status = await api.checkStatus();
      if (status.needs_setup) {
        navigate('/setup');
        return;
      }
    } catch (err) {
      console.error('Error:', err);
    }
    
    isLoading = false;
  });

  async function handleLogin() {
    if (!username || !password) {
      error = 'Ingresa usuario y contraseña';
      return;
    }

    isLoggingIn = true;
    error = '';
    try {
      const data = await api.login(username, password);
      localStorage.setItem('token', data.access_token);
      const userData = await api.getMe();
      user.set(userData);
      isAuthenticated.set(true);
      notify(`Bienvenido, ${userData.full_name}!`, 'success');
      
      if (userData.role === 'partner') {
        navigate('/partner-dashboard');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      error = err.message;
    } finally {
      isLoggingIn = false;
    }
  }
</script>

<div class="login-container">
  <div class="login-card card">
    {#if isLoading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Cargando...</p>
      </div>
    {:else}
      <div class="login-header">
        <div class="logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
          </svg>
        </div>
        <h1>CareldPOS</h1>
        <p>Sistema de Reparaciones</p>
      </div>

      <form class="login-form" on:submit|preventDefault={handleLogin}>
        {#if error}
          <div class="alert alert-danger">
            {error}
          </div>
        {/if}

        <div class="form-group">
          <label class="label" for="username">Usuario</label>
          <input id="username" type="text" class="input" bind:value={username} placeholder="Ingresa tu usuario" autocomplete="username" />
        </div>

        <div class="form-group">
          <label class="label" for="password">Contraseña</label>
          <input id="password" type="password" class="input" bind:value={password} placeholder="Ingresa tu contraseña" autocomplete="current-password" />
        </div>

        <button type="submit" class="btn btn-primary w-full" disabled={isLoggingIn}>
          {#if isLoggingIn}
            <span class="spinner" style="width: 18px; height: 18px; border-width: 2px;"></span>
            Iniciando sesión...
          {:else}
            Iniciar Sesión
          {/if}
        </button>
      </form>
    {/if}
  </div>
</div>

<style>
  .login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  .login-card {
    width: 100%;
    max-width: 400px;
  }

  .login-header {
    text-align: center;
    padding: 2rem 1.5rem 1.5rem;
  }

  .logo {
    width: 64px;
    height: 64px;
    margin: 0 auto 1rem;
    background: var(--primary);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .logo svg {
    width: 36px;
    height: 36px;
  }

  .login-header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--dark);
    margin-bottom: 0.25rem;
  }

  .login-header p {
    color: var(--text-light);
    font-size: 0.875rem;
  }

  .login-form {
    padding: 0 1.5rem 1.5rem;
  }

  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    color: var(--text-light);
  }
</style>
