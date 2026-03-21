import { token, notify, clearAuth } from './auth';

const API_BASE = '/api/v1';

// Función genérica para hacer requests
async function request(endpoint, options = {}) {
  // Obtener token directamente de localStorage para evitar valores stale
  const authToken = localStorage.getItem('token');

  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(authToken && { 'Authorization': `Bearer ${authToken}` }),
      ...options.headers
    }
  };

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, config);

    // Manejar errores de autenticación
    if (response.status === 401) {
      clearAuth(); // Limpia token, user, isAuthenticated y redirige
      throw new Error('Sesión expirada');
    }

    const data = await response.json();

    if (!response.ok) {
      const message = data.detail || data.message || 'Error en la petición';
      throw new Error(message);
    }

    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Métodos HTTP
export const api = {
  // Auth
  async login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const data = await response.json();
      const error = new Error(data.detail || 'Credenciales inválidas');
      error.status = response.status;
      throw error;
    }
    
    return await response.json();
  },

  async setup(userData) {
    return request('/auth/setup', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  },

  async register(userData) {
    return request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  },

  async checkStatus() {
    return request('/auth/status');
  },

  // Usuarios
  async getMe() {
    return request('/users/me');
  },

  async updateMe(userData) {
    return request('/users/me', {
      method: 'PUT',
      body: JSON.stringify(userData)
    });
  },

  async getUsers() {
    return request('/users/');
  },

  async updateUser(id, data) {
    return request(`/users/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  async deleteUser(id) {
    return request(`/users/${id}`, {
      method: 'DELETE'
    });
  },

  // Clientes
  async getCustomers(params = {}) {
    // Solo incluir params que tengan valor
    const validParams = {};
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== '') {
        validParams[key] = value;
      }
    }
    const queryString = new URLSearchParams(validParams).toString();
    return request(`/customers/${queryString ? '?' + queryString : ''}`);
  },

  async getCustomer(id) {
    return request(`/customers/${id}`);
  },

  async createCustomer(data) {
    return request('/customers/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async updateCustomer(id, data) {
    return request(`/customers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  async deleteCustomer(id) {
    return request(`/customers/${id}`, {
      method: 'DELETE'
    });
  },

  // Dispositivos
  async getDevices(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return request(`/devices/${queryString ? '?' + queryString : ''}`);
  },

  async getDevice(id) {
    return request(`/devices/${id}`);
  },

  async createDevice(data) {
    return request('/devices/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async updateDevice(id, data) {
    return request(`/devices/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  async deleteDevice(id) {
    return request(`/devices/${id}`, {
      method: 'DELETE'
    });
  },

  // Reparaciones
  async getRepairs(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return request(`/repairs/${queryString ? '?' + queryString : ''}`);
  },

  async getPartnerRepairs() {
    return request('/repairs/partner/my-devices');
  },

  async getRepair(id) {
    return request(`/repairs/${id}`);
  },

  async createRepair(data) {
    const response = await request('/repairs/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
    return response;
  },

  async updateRepair(id, data) {
    return request(`/repairs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  async deleteRepair(id) {
    return request(`/repairs/${id}`, {
      method: 'DELETE'
    });
  },

  async getRepairItems(repairId) {
    return request(`/repairs/${repairId}/items`);
  },

  async addRepairItem(repairId, data) {
    return request(`/repairs/${repairId}/items`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async removeRepairItem(repairId, itemId) {
    return request(`/repairs/${repairId}/items/${itemId}`, {
      method: 'DELETE'
    });
  },

   async completeRepair(repairId, data) {
     return request(`/repairs/${repairId}/complete`, {
       method: 'POST',
       body: JSON.stringify(data)
     });
   },

   async getRepairByNumber(repairNumber) {
     return request(`/repairs/number/${repairNumber}`);
   },

  // Búsqueda de refacciones para reparaciones
  async searchParts(q = '', limit = 20) {
    const params = new URLSearchParams();
    if (q) params.append('q', q);
    params.append('limit', limit);
    return request(`/inventory/search?${params.toString()}`);
  },

  // Inventario
  async getInventoryItems(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return request(`/inventory/${queryString ? '?' + queryString : ''}`);
  },

  async getInventoryItem(id) {
    return request(`/inventory/${id}`);
  },

  async createInventoryItem(data) {
    return request('/inventory/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async updateInventoryItem(id, data) {
    return request(`/inventory/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  async deleteInventoryItem(id) {
    return request(`/inventory/${id}`, {
      method: 'DELETE'
    });
  },

  async adjustStock(id, data) {
    return request(`/inventory/${id}/stock`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Upload de fotos
  async uploadPhoto(deviceId, file) {
    const authToken = localStorage.getItem('token');

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/uploads/${deviceId}`, {
      method: 'POST',
      headers: {
        ...(authToken && { 'Authorization': `Bearer ${authToken}` })
      },
      body: formData
    });

    if (!response.ok) {
      const text = await response.text();
      try {
        const data = JSON.parse(text);
        throw new Error(data.detail || 'Error al subir foto');
      } catch {
        throw new Error(text || 'Error al subir foto');
      }
    }

    const text = await response.text();
    try {
      return JSON.parse(text);
    } catch {
      // Si no es JSON, devolver objeto con la URL
      return { url: text, filename: file.name };
    }
  },

  // Obtener URL de foto
  getPhotoUrl(filename) {
    return `${API_BASE}/uploads/photo/${filename}`;
  },

  async getCategories() {
    return request('/inventory/categories');
  },

  // Pagos
  async getPayments(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return request(`/payments/${queryString ? '?' + queryString : ''}`);
  },

  async createPayment(data) {
    return request('/payments/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async completePayment(id) {
    return request(`/payments/${id}/complete`, {
      method: 'POST'
    });
  },

  async getPaymentSummary(repairId) {
    return request(`/payments/repair/${repairId}/summary`);
  },

  // Ventas (Sales)
  async getSales(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return request(`/sales/${queryString ? '?' + queryString : ''}`);
  },

  async getSale(id) {
    return request(`/sales/${id}`);
  },

  async createSale(data) {
    return request('/sales/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Socios (Partners)
  async getPartnerInventory() {
    return request('/partners/inventory');
  },

  async createPartnerOrder(orderData) {
    return request('/partners/orders', {
      method: 'POST',
      body: JSON.stringify(orderData)
    });
  },

  async getMyPartnerOrders() {
    return request('/partners/orders');
  },

  // Admin - Pedidos de Socios
  async getAllPartnerOrders() {
    return request('/admin/partners/orders');
  },

  async updatePartnerOrderStatus(orderId, status) {
    return request(`/admin/partners/orders/${orderId}/status?status=${status}`, {
      method: 'PATCH'
    });
  },

  // Generic methods
  async get(endpoint) {
    return request(endpoint);
  },

  async post(endpoint, data) {
    return request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async put(endpoint, data) {
    return request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  async delete(endpoint) {
    return request(endpoint, {
      method: 'DELETE'
    });
  }
};
