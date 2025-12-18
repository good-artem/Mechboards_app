// Конфигурация API endpoints
const API_CONFIG = {
  // Базовый URL для API
  getBaseUrl() {
    // Используем переменную окружения или прямой URL
    if (import.meta.env.VITE_API_BASE_URL) {
      return import.meta.env.VITE_API_BASE_URL;
    }
    
    // Fallback для разных окружений
    if (import.meta.env.MODE === 'development') {
      return 'https://miniature-goggles-9x7jx4r4rq7295g9-8000.app.github.dev';
    } else {
      return 'https://miniature-goggles-9x7jx4r4rq7295g9-8000.app.github.dev';
    }
  },
  
  // API endpoints
  endpoints: {
    // Пользователи
    users: {
      profile: (userId) => `/api/users/${userId}`,
      create: '/api/users/create',
      stats: (userId) => `/api/users/${userId}/stats`
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
      remove: '/api/cart/remove'
    },
    orders: {
      create: '/api/orders/create'
    },
    news: {
      list: '/api/news'
    }
  },
  
  // Полный URL для endpoint
  getUrl(endpointPath) {
    const baseUrl = this.getBaseUrl();
    return `${baseUrl.replace(/\/$/, '')}/${endpointPath.replace(/^\//, '')}`;
  }
}

export default API_CONFIG;