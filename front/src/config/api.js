// Конфигурация API endpoints
const API_CONFIG = {
  // Базовые URL для разных окружений
  baseUrls: {
    development: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    production: import.meta.env.VITE_API_BASE_URL || 'https://your-production-backend.com'
  },
  
  // Определяем текущее окружение
  getCurrentEnvironment() {
    return import.meta.env.MODE || 'development'
  },
  
  // Получаем базовый URL для текущего окружения
  getBaseUrl() {
    const env = this.getCurrentEnvironment()
    return this.baseUrls[env] || this.baseUrls.development
  },
  
  // API endpoints
  endpoints: {
    // Пользователи
    users: {
      profile: (userId) => `/api/users/${userId}`,
      create: '/api/users/create',
      stats: (userId) => `/api/users/${userId}/stats`
    },
    
    // Категории
    categories: {
      list: '/api/categories'
    },
    
    // Товары
    products: {
      list: '/api/products',
      detail: (productId) => `/api/products/${productId}`,
      search: '/api/products/search'
    },
    
    // Корзина
    cart: {
      get: (telegramId) => `/api/cart/${telegramId}`,
      add: '/api/cart/add',
      update: '/api/cart/update',
      remove: '/api/cart/remove'
    },
    
    // Заказы
    orders: {
      create: '/api/orders/create'
    },
    
    // Новости
    news: {
      list: '/api/news'
    }
  },
  
  // Полный URL для endpoint
  getUrl(endpointPath) {
    const baseUrl = this.getBaseUrl()
    // Убираем дублирующиеся слеши
    return `${baseUrl.replace(/\/$/, '')}/${endpointPath.replace(/^\//, '')}`
  }
}

export default API_CONFIG