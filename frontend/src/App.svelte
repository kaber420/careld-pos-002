<script>
  import { onMount } from 'svelte';
  import { Router, Route } from 'svelte-routing';
  import { isAuthenticated, user, clearAuth, notify } from './stores/auth';
  import { api } from './stores/api';

  import Login from './views/Login.svelte';
  import Setup from './views/Setup.svelte';
  import Landing from './views/Landing.svelte';
  import Dashboard from './views/Dashboard.svelte';
  import Customers from './views/Customers.svelte';
  import Devices from './views/Devices.svelte';
  import Repairs from './views/Repairs.svelte';
  import Inventory from './views/Inventory.svelte';
  import POS from './views/POS.svelte';
  import NotFound from './views/NotFound.svelte';
  import ClientPortal from './views/ClientPortal.svelte';
  import Settings from './views/Settings.svelte';
  import PartnerDashboard from './views/PartnerDashboard.svelte';
  import PartnerOrders from './views/PartnerOrders.svelte';
  import Users from './views/Users.svelte';
  import { fetchPublicSettings } from './stores/settings';

  let isLoading = true;

  onMount(async () => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      try {
        const userData = await api.getMe();
        user.set(userData);
        isAuthenticated.set(true);
      } catch (error) {
        clearAuth();
      }
    }
    await fetchPublicSettings();
    isLoading = false;
  });

  function handleLogout() {
    clearAuth();
    notify('Sesión cerrada correctamente', 'info');
  }

  // Protección de rutas para socios
  $: if ($isAuthenticated && $user && $user.role === 'partner') {
    const restrictedPaths = ['/dashboard', '/customers', '/devices', '/repairs', '/inventory', '/pos', '/users', '/settings', '/partner-orders'];
    const currentPath = window.location.pathname;
    
    if (restrictedPaths.some(path => currentPath === path || currentPath.startsWith(path + '/'))) {
      notify('Acceso restringido. Redirigiendo a tu panel de socio.', 'warning');
      navigate('/partner-dashboard', { replace: true });
    }
  }
</script>

{#if isLoading}
  <div class="loading-overlay">
    <div class="spinner"></div>
  </div>
{:else}
  <Router>
    <Route path="/" component={Landing} />
    <Route path="/login" component={Login} />
    <Route path="/setup" component={Setup} />
    <Route path="/dashboard" component={Dashboard} />
    <Route path="/customers" component={Customers} />
    <Route path="/devices" component={Devices} />
    <Route path="/repairs" component={Repairs} />
    <Route path="/inventory" component={Inventory} />
    <Route path="/pos" component={POS} />
    <Route path="/portal/:token" component={ClientPortal} />
    <Route path="/settings" component={Settings} />
    <Route path="/users" component={Users} />
    <Route path="/partner-dashboard" component={PartnerDashboard} />
    <Route path="/partner-orders" component={PartnerOrders} />
    <Route path="*" component={NotFound} />
  </Router>
{/if}

<style>
  .loading-overlay {
    position: fixed;
    inset: 0;
    background: var(--light);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 999;
  }
</style>
