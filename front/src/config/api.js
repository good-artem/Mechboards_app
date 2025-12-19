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
      return 'https://verbose-space-orbit-x45v4q7q6wwf6g94-8000.app.github.dev';
    } else if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:8000';
    } else {
      return 'https://verbose-space-orbit-x45v4q7q6wwf6g94-8000.app.github.dev';
    }
  },
  
  // API endpoints
  endpoints: {
    // Пользователи
    users: {
      profile: (userId) => `/api/users/${userId}`,
      create: '/api/users/create',
      stats: (userId) => `/api/users/${userId}/stats`,
      orders: (userId) => `/api/users/${userId}/orders`
    },
    
    categories: {
      list: '/api/categories'
    },
    
    products: {
      list: '/api/products',
      detail: (productId) => `/api/products/${productId}`,
      search: '/api/products/search'
    },
    
    cart: {
      get: (telegramId) => `/api/cart/${telegramId}`,
      add: '/api/cart/add',
      update: '/api/cart/update',
      remove: '/api/cart/remove',
      clear: (telegramId) => `/api/cart/${telegramId}/clear`
    },
    
    orders: {
      create: '/api/orders/create'
    },
    
    news: {
      list: '/api/news'
    },
    
    admin: {
      check: '/api/admin/check'
    },
    
    services: {
      list: '/api/services',
      order: '/api/services/order'
    },
    
    simpleSearch: '/api/simple-search',
    testConnection: '/api/health'
  },
  
  // Полный URL для endpoint
  getUrl(endpointPath) {
    const baseUrl = this.getBaseUrl();
    // Удаляем завершающий слеш у базового URL и начальный слеш у endpointPath
    return `${baseUrl.replace(/\/$/, '')}/${endpointPath.replace(/^\//, '')}`;
  }
}

export default API_CONFIG;