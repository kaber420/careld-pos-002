<script>
  import { onMount } from 'svelte';
  import { api } from '../stores/api';
  import { notify, user as currentUser } from '../stores/auth';
  import Layout from '../components/Layout.svelte';

  let users = [];
  let isLoading = true;
  let showForm = false;
  let editingUser = null;

  let formData = {
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: 'receptionist',
    phone: '',
    is_active: true
  };

  const roles = [
    { id: 'admin', label: 'Administrador' },
    { id: 'technician', label: 'Técnico' },
    { id: 'receptionist', label: 'Recepcionista' },
    { id: 'inventory_manager', label: 'Gestor de Inventario' },
    { id: 'partner', label: 'Socio (Partner)' }
  ];

  onMount(async () => {
    await loadUsers();
  });

  async function loadUsers() {
    isLoading = true;
    try {
      users = await api.getUsers();
    } catch (error) {
      notify(error.message, 'danger');
    } finally {
      isLoading = false;
    }
  }

  function openForm(user = null) {
    if (user) {
      editingUser = user;
      formData = {
        username: user.username,
        email: user.email,
        full_name: user.full_name,
        password: '', // Password stays empty unless changing
        role: user.role,
        phone: user.phone || '',
        is_active: user.is_active
      };
    } else {
      editingUser = null;
      formData = {
        username: '',
        email: '',
        full_name: '',
        password: '',
        role: 'receptionist',
        phone: '',
        is_active: true
      };
    }
    showForm = true;
  }

  function closeForm() {
    showForm = false;
    editingUser = null;
  }

  async function handleSubmit() {
    try {
      if (editingUser) {
        // Enviar solo los campos necesarios para actualizar
        const updateData = { ...formData };
        if (!updateData.password) delete updateData.password;
        delete updateData.username; // Username restricted for update if backend says so

        await api.updateUser(editingUser.id, updateData);
        notify('Usuario actualizado correctamente', 'success');
      } else {
        if (!formData.password) {
          notify('La contraseña es obligatoria para nuevos usuarios', 'warning');
          return;
        }
        await api.register(formData);
        notify('Usuario registrado correctamente', 'success');
      }
      closeForm();
      loadUsers();
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  async function handleDelete(user) {
    if (user.id === $currentUser.id) {
      notify('No puedes eliminarte a ti mismo', 'warning');
      return;
    }
    if (!confirm(`¿Estás seguro de eliminar al usuario ${user.username}?`)) return;

    try {
      await api.deleteUser(user.id);
      notify('Usuario eliminado correctamente', 'success');
      loadUsers();
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  function getRoleLabel(roleId) {
    return roles.find(r => r.id === roleId)?.label || roleId;
  }
</script>

<Layout>
  <div class="users-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Usuarios</h1>
        <p class="page-subtitle">Gestión de accesos y roles del sistema</p>
      </div>
      <button class="btn btn-primary" on:click={() => openForm()}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        Nuevo Usuario
      </button>
    </div>

    <div class="card">
      <div class="card-body">
        {#if isLoading}
          <div class="loading-state">
            <div class="spinner"></div>
            <p>Cargando usuarios...</p>
          </div>
        {:else if users.length === 0}
          <div class="empty-state">
            <div class="empty-state-icon">👤</div>
            <p class="empty-state-title">No hay usuarios registrados</p>
            <p class="empty-state-description">Comienza agregando un nuevo usuario</p>
          </div>
        {:else}
          <div class="table-container">
            <table class="table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Nombre Completo</th>
                  <th>Email</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {#each users as user}
                  <tr>
                    <td class="font-medium">{user.username}</td>
                    <td>{user.full_name}</td>
                    <td>{user.email}</td>
                    <td>
                      <span class="badge badge-outline">{getRoleLabel(user.role)}</span>
                    </td>
                    <td>
                      <span class="badge {user.is_active ? 'badge-success' : 'badge-danger'}">
                        {user.is_active ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td>
                      <div class="flex gap-2">
                        <button class="btn btn-sm btn-outline" on:click={() => openForm(user)}>
                          Editar
                        </button>
                        {#if user.id !== $currentUser.id}
                          <button class="btn btn-sm btn-danger" on:click={() => handleDelete(user)}>
                            Eliminar
                          </button>
                        {/if}
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

    {#if showForm}
      <div 
        class="modal-overlay" 
        on:click|self={closeForm} 
        on:keydown={(e) => e.key === 'Escape' && closeForm()}
        role="button"
        tabindex="0"
        aria-label="Cerrar modal"
      >
        <div class="modal">
          <div class="modal-header">
            <h3 class="modal-title">
              {editingUser ? 'Editar Usuario' : 'Nuevo Usuario'}
            </h3>
            <button class="modal-close" on:click={closeForm}>×</button>
          </div>

          <form on:submit|preventDefault={handleSubmit}>
            <div class="modal-body">
              <div class="form-row">
                <div class="form-group">
                  <label class="label" for="username">Usuario *</label>
                  <input
                    id="username"
                    type="text"
                    class="input"
                    bind:value={formData.username}
                    disabled={editingUser}
                    required
                  />
                </div>
                <div class="form-group">
                  <label class="label" for="role">Rol *</label>
                  <select id="role" class="input" bind:value={formData.role} required>
                    {#each roles as role}
                      <option value={role.id}>{role.label}</option>
                    {/each}
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label class="label" for="full_name">Nombre Completo *</label>
                <input
                  id="full_name"
                  type="text"
                  class="input"
                  bind:value={formData.full_name}
                  required
                />
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label class="label" for="email">Email *</label>
                  <input
                    id="email"
                    type="email"
                    class="input"
                    bind:value={formData.email}
                    required
                  />
                </div>
                <div class="form-group">
                  <label class="label" for="phone">Teléfono</label>
                  <input
                    id="phone"
                    type="tel"
                    class="input"
                    bind:value={formData.phone}
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="label" for="password">
                  Contraseña {editingUser ? '(dejar en blanco para no cambiar)' : '*'}
                </label>
                <input
                  id="password"
                  type="password"
                  class="input"
                  bind:value={formData.password}
                  required={!editingUser}
                  minlength="6"
                />
              </div>

              {#if editingUser}
                <div class="form-group flex items-center gap-2 mt-4">
                  <input
                    id="is_active"
                    type="checkbox"
                    bind:checked={formData.is_active}
                  />
                  <label for="is_active">Usuario Activo</label>
                </div>
              {/if}
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-outline" on:click={closeForm}>
                Cancelar
              </button>
              <button type="submit" class="btn btn-primary">
                {editingUser ? 'Actualizar' : 'Registrar'} Usuario
              </button>
            </div>
          </form>
        </div>
      </div>
    {/if}
  </div>
</Layout>

<style>
  .users-page {
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
