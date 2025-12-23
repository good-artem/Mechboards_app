// Конфигурация API endpoints
const API_CONFIG = {
  // Базовый URL для API
  getBaseUrl() {
    // Используем переменную окружения или прямой URL
    if (import.meta.env.VITE_API_BASE_URL) {
      return import.meta.env.VITE_API_BASE_URL;
    }
    
    // Fallback для разных окружений
    const hostname = window.location.hostname;
    if (hostname.includes('github.dev')) {
      return 'https://psychic-adventure-wrpj64gv4jx7h5pwp-8000.app.github.dev';
    } else if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'https://psychic-adventure-wrpj64gv4jx7h5pwp-8000.app.github.dev';
    } else {
      return 'https://psychic-adventure-wrpj64gv4jx7h5pwp-8000.app.github.dev';
    }
  },
  
  // API endpoints (соответствуют FastAPI endpoints)
  endpoints: {
    // Пользователи
    users: {
      get: (telegramId) => `/api/users/${telegramId}`,
      create: '/api/users',
      update: (telegramId) => `/api/users/${telegramId}`,
      // stats больше нет отдельного endpoint
    },
    
    // Категории
    categories: {
      list: '/api/categories',
      get: (categoryId) => `/api/categories/${categoryId}`
    },
    
    // Товары
    products: {
      list: '/api/products',
      get: (productId) => `/api/products/${productId}`
      // search теперь интегрирован в list с параметрами
    },
    
    // Услуги
    services: {
      list: '/api/services',
      get: (serviceId) => `/api/services/${serviceId}`
      // service/order теперь через order endpoint
    },
    
    // Новости
    news: {
      list: '/api/news'
    },
    
    // Корзина
    cart: {
      get: (telegramId) => `/api/cart/${telegramId}`,
      addItem: (telegramId) => `/api/cart/${telegramId}/items`,
      addService: (telegramId) => `/api/cart/${telegramId}/service-items`,
      removeItem: (telegramId, itemId) => `/api/cart/${telegramId}/items/${itemId}`,
      removeService: (telegramId, itemId) => `/api/cart/${telegramId}/service-items/${itemId}`
    },
    
    // Заказы
    orders: {
      create: (telegramId) => `/api/orders/${telegramId}`,
      getUserOrders: (telegramId) => `/api/orders/${telegramId}`,
      updateStatus: (orderId) => `/api/admin/orders/${orderId}/status`
    },
    
    // Заказы на услуги (через ServiceOrder)
    serviceOrders: {
      // Заказы на услуги включены в orders endpoint как service_orders
    },
    
    // Поддержка
    support: {
      getTickets: (telegramId) => `/api/support/tickets?telegram_id=${telegramId}`,
      createTicket: (telegramId) => `/api/support/tickets?telegram_id=${telegramId}`,
      getTicket: (ticketId, telegramId) => `/api/support/tickets/${ticketId}?telegram_id=${telegramId}`,
      addMessage: (ticketId, telegramId) => `/api/support/tickets/${ticketId}/messages?telegram_id=${telegramId}`,
      updateStatus: (ticketId, telegramId) => `/api/support/tickets/${ticketId}/status?telegram_id=${telegramId}`
    },
    
    // Админ
    admin: {
      stats: (telegramId) => `/api/admin/stats?telegram_id=${telegramId}`,
      orders: (telegramId) => `/api/admin/orders?telegram_id=${telegramId}`,
      // check больше нет, используем users endpoint с is_admin полем
    },
    
    // Здоровье системы
    health: {
      check: '/'
    }
  },
  
  // Полный URL для endpoint
  getUrl(endpointPath, params = {}) {
    const baseUrl = this.getBaseUrl();
    let url = `${baseUrl.replace(/\/$/, '')}/${endpointPath.replace(/^\//, '')}`;
    
    // Добавляем query параметры если есть
    if (Object.keys(params).length > 0) {
      const queryString = new URLSearchParams(params).toString();
      url += `?${queryString}`;
    }
    
    return url;
  },
  
  // Утилиты для работы с API
  async makeRequest(endpoint, options = {}) {
    const url = typeof endpoint === 'function' ? endpoint() : endpoint;
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      ...options
    };
    
    try {
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw {
          status: response.status,
          message: errorData.detail || `HTTP error ${response.status}`,
          data: errorData
        };
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  },
  
  // Получить пользователя
  async getUser(telegramId) {
    const endpoint = this.endpoints.users.get(telegramId);
    return await this.makeRequest(endpoint);
  },
  
  // Создать пользователя
  async createUser(userData) {
    const endpoint = this.endpoints.users.create;
    return await this.makeRequest(endpoint, {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  },
  
  // Обновить пользователя
  async updateUser(telegramId, userData) {
    const endpoint = this.endpoints.users.update(telegramId);
    return await this.makeRequest(endpoint, {
      method: 'PUT',
      body: JSON.stringify(userData)
    });
  },
  
  // Получить категории
  async getCategories() {
    return await this.makeRequest(this.endpoints.categories.list);
  },
  
  // Получить товары
  async getProducts(categoryId = null, search = null) {
    const params = {};
    if (categoryId) params.category_id = categoryId;
    if (search) params.search = search;
    
    return await this.makeRequest(this.getUrl(this.endpoints.products.list, params));
  },
  
  // Получить конкретный товар
  async getProduct(productId) {
    const endpoint = this.endpoints.products.get(productId);
    return await this.makeRequest(endpoint);
  },
  
  // Получить услуги
  async getServices() {
    return await this.makeRequest(this.endpoints.services.list);
  },
  
  // Получить новости
  async getNews() {
    return await this.makeRequest(this.endpoints.news.list);
  },
  
  // Получить корзину
  async getCart(telegramId) {
    const endpoint = this.endpoints.cart.get(telegramId);
    return await this.makeRequest(endpoint);
  },
  
  // Добавить товар в корзину
  async addToCart(telegramId, productId, quantity = 1) {
    const endpoint = this.endpoints.cart.addItem(telegramId);
    return await this.makeRequest(endpoint, {
      method: 'POST',
      body: JSON.stringify({ product_id: productId, quantity })
    });
  },
  
  // Добавить услугу в корзину
  async addServiceToCart(telegramId, serviceId, quantity = 1, notes = '') {
    const endpoint = this.endpoints.cart.addService(telegramId);
    return await this.makeRequest(endpoint, {
      method: 'POST',
      body: JSON.stringify({ 
        service_id: serviceId, 
        quantity, 
        notes 
      })
    });
  },
  
  // Удалить товар из корзины
  async removeFromCart(telegramId, itemId) {
    const endpoint = this.endpoints.cart.removeItem(telegramId, itemId);
    return await this.makeRequest(endpoint, {
      method: 'DELETE'
    });
  },
  
  // Удалить услугу из корзины
  async removeServiceFromCart(telegramId, itemId) {
    const endpoint = this.endpoints.cart.removeService(telegramId, itemId);
    return await this.makeRequest(endpoint, {
      method: 'DELETE'
    });
  },
  
  // Создать заказ
  async createOrder(telegramId, orderData) {
    const endpoint = this.endpoints.orders.create(telegramId);
    return await this.makeRequest(endpoint, {
      method: 'POST',
      body: JSON.stringify(orderData)
    });
  },
  
  // Получить заказы пользователя
  async getUserOrders(telegramId) {
    const endpoint = this.endpoints.orders.getUserOrders(telegramId);
    return await this.makeRequest(endpoint);
  },
  
  // Получить тикеты поддержки
  async getSupportTickets(telegramId, status = null) {
    const params = { telegram_id: telegramId };
    if (status) params.status = status;
    
    return await this.makeRequest(this.getUrl('/api/support/tickets', params));
  },
  
  // Создать тикет поддержки
  async createSupportTicket(telegramId, subject) {
    const params = { telegram_id: telegramId };
    return await this.makeRequest(this.getUrl('/api/support/tickets', params), {
      method: 'POST',
      body: JSON.stringify({ subject })
    });
  },
  
  // Получить сообщения тикета
  async getTicketMessages(ticketId, telegramId) {
    const endpoint = this.endpoints.support.getTicket(ticketId, telegramId);
    return await this.makeRequest(endpoint);
  },
  
  // Отправить сообщение в тикет
  async sendTicketMessage(ticketId, telegramId, message, isFromAdmin = false) {
    const endpoint = this.endpoints.support.addMessage(ticketId, telegramId);
    return await this.makeRequest(endpoint, {
      method: 'POST',
      body: JSON.stringify({ 
        message, 
        is_from_admin: isFromAdmin 
      })
    });
  },
  
  // Получить статистику (админ)
  async getAdminStats(telegramId) {
    const endpoint = this.endpoints.admin.stats(telegramId);
    return await this.makeRequest(endpoint);
  },
  
  // Получить все заказы (админ)
  async getAllOrders(telegramId, status = null) {
    const params = { telegram_id: telegramId };
    if (status) params.status = status;
    
    return await this.makeRequest(this.getUrl('/api/admin/orders', params));
  },
  
  // Обновить статус заказа (админ)
  async updateOrderStatus(telegramId, orderId, status) {
    const params = { telegram_id: telegramId, status };
    const endpoint = this.endpoints.orders.updateStatus(orderId);
    
    return await this.makeRequest(this.getUrl(endpoint, params), {
      method: 'PUT'
    });
  },
  
  // Проверить соединение
  async checkConnection() {
    try {
      await this.makeRequest(this.endpoints.health.check);
      return true;
    } catch (error) {
      console.error('Connection check failed:', error);
      return false;
    }
  }
};

export default API_CONFIG;