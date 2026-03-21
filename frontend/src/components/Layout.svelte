<script>
  import { navigate } from 'svelte-routing';
  import { user, clearAuth, notify, notifications, removeNotification } from '../stores/auth';

  let sidebarOpen = true;

  function handleLogout() {
    clearAuth();
    notify('Sesión cerrada correctamente', 'info');
    navigate('/login');
  }

  function toggleSidebar() {
    sidebarOpen = !sidebarOpen;
  }
</script>

<div class="app-layout">
  <!-- Sidebar -->
  <aside class="sidebar" class:collapsed={!sidebarOpen}>
    <div class="sidebar-header">
      <div class="sidebar-logo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
        </svg>
        {#if sidebarOpen}
          <span>CareldPOS</span>
        {/if}
      </div>
    </div>

    <nav class="sidebar-nav">
      {#if $user && $user.role !== 'partner'}
        <a href="/dashboard" class="nav-item" use:activeLink>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/>
          </svg>
          {#if sidebarOpen}<span>Dashboard</span>{/if}
        </a>

        <a href="/pos" class="nav-item" use:activeLink>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="1" y="4" width="22" height="16" rx="2" ry="2"/>
            <line x1="1" y1="10" x2="23" y2="10"/>
          </svg>
          {#if sidebarOpen}<span>POS</span>{/if}
        </a>

        <a href="/customers" class="nav-item" use:activeLink>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          {#if sidebarOpen}<span>Clientes</span>{/if}
        </a>

        <a href="/devices" class="nav-item" use:activeLink>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="5" y="2" width="14" height="20" rx="2"/>
            <line x1="12" y1="18" x2="12.01" y2="18"/>
          </svg>
          {#if sidebarOpen}<span>Dispositivos</span>{/if}
        </a>

        <a href="/repairs" class="nav-item" use:activeLink>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
          </svg>
          {#if sidebarOpen}<span>Reparaciones</span>{/if}
        </a>

        <a href="/inventory" class="nav-item" use:activeLink>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
            <line x1="12" y1="22.08" x2="12" y2="12"/>
          </svg>
          {#if sidebarOpen}<span>Inventario</span>{/if}
        </a>

        <a href="/partner-orders" class="nav-item" use:activeLink>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 12 20 22 4 22 4 12"></polyline>
            <rect x="2" y="7" width="20" height="5"></rect>
            <line x1="12" y1="22" x2="12" y2="7"></line>
            <path d="M12 7L12 3"></path>
          </svg>
          {#if sidebarOpen}<span>Pedidos Socios</span>{/if}
        </a>
      {:else if $user && $user.role === 'partner'}
        <a href="/partner-dashboard" class="nav-item" use:activeLink>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/>
          </svg>
          {#if sidebarOpen}<span>Dashboard Socio</span>{/if}
        </a>
      {/if}

      {#if $user && $user.role === 'admin'}
        <a href="/users" class="nav-item" use:activeLink>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          {#if sidebarOpen}<span>Usuarios</span>{/if}
        </a>

        <a href="/settings" class="nav-item" use:activeLink>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
          {#if sidebarOpen}<span>Configuración</span>{/if}
        </a>
      {/if}
    </nav>

    <div class="sidebar-footer">
      <button class="nav-item logout-btn" on:click={handleLogout}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        {#if sidebarOpen}<span>Cerrar Sesión</span>{/if}
      </button>
    </div>
  </aside>

  <!-- Main Content -->
  <main class="main-content">
    <!-- Header -->
    <header class="top-header">
      <button class="menu-toggle" on:click={toggleSidebar}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="3" y1="12" x2="21" y2="12"/>
          <line x1="3" y1="6" x2="21" y2="6"/>
          <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </button>

      <div class="header-right">
        {#if $user}
          <div class="user-menu">
            <div class="user-avatar">
              {$user.full_name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <div class="user-info">
              <span class="user-name">{$user.full_name}</span>
              <span class="user-role">{$user.role}</span>
            </div>
          </div>
        {/if}
      </div>
    </header>

    <!-- Page Content -->
    <div class="page-content">
      <slot />
    </div>
  </main>

  <!-- Notifications -->
  {#if $notifications.length > 0}
    <div class="notifications-container">
      {#each $notifications as notification (notification.id)}
        <div class="notification notification-{notification.type}">
          {notification.message}
          <button class="notification-close" on:click={() => removeNotification(notification.id)}>×</button>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .app-layout {
    display: flex;
    min-height: 100vh;
  }

  .sidebar {
    width: 260px;
    background: var(--dark);
    color: white;
    display: flex;
    flex-direction: column;
    transition: width 0.3s ease;
    position: fixed;
    height: 100vh;
    z-index: 100;
  }

  .sidebar.collapsed {
    width: 70px;
  }

  .sidebar-header {
    padding: 1.25rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .sidebar-logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.25rem;
    font-weight: 600;
  }

  .sidebar-logo svg {
    width: 32px;
    height: 32px;
    flex-shrink: 0;
  }

  .sidebar-nav {
    flex: 1;
    padding: 1rem 0;
    overflow-y: auto;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1.25rem;
    color: rgba(255, 255, 255, 0.7);
    text-decoration: none;
    transition: all 0.2s;
    cursor: pointer;
    border: none;
    background: none;
    width: 100%;
    text-align: left;
    font-size: 0.875rem;
  }

  .nav-item:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }

  .nav-item.active {
    background: var(--primary);
    color: white;
  }

  .nav-item svg {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
  }

  .sidebar-footer {
    padding: 1rem 0;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .logout-btn {
    color: rgba(255, 255, 255, 0.7);
  }

  .logout-btn:hover {
    color: var(--danger);
  }

  .main-content {
    flex: 1;
    margin-left: 260px;
    transition: margin-left 0.3s ease;
    display: flex;
    flex-direction: column;
  }

  .sidebar.collapsed ~ .main-content {
    margin-left: 70px;
  }

  .top-header {
    background: white;
    border-bottom: 1px solid var(--border);
    padding: 0.75rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 50;
  }

  .menu-toggle {
    background: none;
    border: none;
    padding: 0.5rem;
    cursor: pointer;
    color: var(--text-light);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-sm);
  }

  .menu-toggle:hover {
    background: var(--light);
    color: var(--text);
  }

  .menu-toggle svg {
    width: 24px;
    height: 24px;
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .user-menu {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .user-avatar {
    width: 36px;
    height: 36px;
    background: var(--primary);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.875rem;
  }

  .user-info {
    display: flex;
    flex-direction: column;
  }

  .user-name {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text);
  }

  .user-role {
    font-size: 0.75rem;
    color: var(--text-light);
    text-transform: capitalize;
  }

  .page-content {
    flex: 1;
    padding: 1.5rem;
    background: var(--light);
  }

  .notifications-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .notification {
    padding: 0.875rem 1rem;
    border-radius: var(--radius);
    box-shadow: var(--shadow-md);
    display: flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 300px;
    animation: slideIn 0.3s ease;
  }

  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  .notification-info {
    background: white;
    border-left: 4px solid var(--primary);
  }

  .notification-success {
    background: white;
    border-left: 4px solid var(--success);
  }

  .notification-warning {
    background: white;
    border-left: 4px solid var(--warning);
  }

  .notification-danger {
    background: white;
    border-left: 4px solid var(--danger);
  }

  .notification-close {
    margin-left: auto;
    background: none;
    border: none;
    font-size: 1.25rem;
    color: var(--text-light);
    cursor: pointer;
    padding: 0;
    line-height: 1;
  }

  .notification-close:hover {
    color: var(--text);
  }

  @media (max-width: 768px) {
    .sidebar {
      transform: translateX(-100%);
    }

    .sidebar.open {
      transform: translateX(0);
    }

    .main-content {
      margin-left: 0;
    }
  }
</style>

<script context="module">
  export function activeLink(node, url) {
    const update = () => {
      const currentPath = window.location.pathname;
      if (currentPath === url || (url !== '/' && currentPath.startsWith(url))) {
        node.classList.add('active');
      } else {
        node.classList.remove('active');
      }
    };

    update();

    return {
      update
    };
  }
</script>
