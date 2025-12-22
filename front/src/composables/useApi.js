import API_CONFIG from '@/config/api'
import { ref } from 'vue'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const getTelegramInitData = () => {
    if (window.Telegram?.WebApp?.initData) {
      return window.Telegram.WebApp.initData;
    }
    
    if (import.meta.env.DEV) {
      const testUserId = 391622124;
      const mockUser = {
        id: testUserId,
        first_name: "Test",
        last_name: "User",
        username: "testuser",
        language_code: "ru"
      };
      const authDate = Math.floor(Date.now() / 1000);
      
      return `user=${JSON.stringify(mockUser)}&auth_date=${authDate}&hash=fake_hash_for_dev`;
    }
    
    console.warn('⚠️ Telegram initData не найден!');
    return null;
  }

  const getAuthHeaders = () => {
    const headers = {};
    const telegramInitData = getTelegramInitData();
    
    if (telegramInitData) {
      headers['X-Telegram-Init-Data'] = telegramInitData;
    }
    
    return headers;
  }

  const buildUrlWithParams = (endpoint, params = {}) => {
    const url = API_CONFIG.getUrl(endpoint);
    if (!params || Object.keys(params).length === 0) {
      return url;
    }
    
    const queryString = new URLSearchParams(params).toString();
    return `${url}${url.includes('?') ? '&' : '?'}${queryString}`;
  }

  const apiRequest = async (endpoint, options = {}) => {
    loading.value = true;
    error.value = null;

    try {
      let url = endpoint;
      
      if (endpoint.startsWith('/') || !endpoint.startsWith('http')) {
        url = buildUrlWithParams(endpoint, options.params);
      }
      
      console.log('🔄 API Request to:', url, 'Method:', options.method || 'GET');
      
      const headers = {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...options.headers
      };

      const fetchOptions = {
        headers,
        method: options.method || 'GET'
      };

      // Добавляем тело запроса для POST/PUT/PATCH/DELETE
      if (options.body && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(fetchOptions.method)) {
        fetchOptions.body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
      }

      const response = await fetch(url, fetchOptions);

      if (response.status === 401) {
        throw new Error('Требуется авторизация Telegram. Обновите страницу.');
      }
      
      if (response.status === 403) {
        throw new Error('Доступ запрещен. Вы не имеете прав на этот ресурс.');
      }

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          errorData = { detail: await response.text() };
        }
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        console.log('✅ API Response:', data);
        return data;
      } else {
        const text = await response.text();
        console.log('✅ API Text Response:', text);
        return text;
      }
    } catch (err) {
      error.value = err.message;
      console.error('❌ API request failed:', err);
      
      if (err.message.includes('авторизация')) {
        alert('❌ Ошибка авторизации. Пожалуйста, войдите через Telegram.');
      } else if (err.message.includes('запрещен')) {
        alert('❌ Доступ запрещен. У вас нет прав на это действие.');
      }
      
      throw err;
    } finally {
      loading.value = false;
    }
  }

  const get = (endpoint, options = {}) => apiRequest(endpoint, { ...options, method: 'GET' });
  
  const post = (endpoint, data, options = {}) => 
    apiRequest(endpoint, { ...options, method: 'POST', body: data });
  
  const put = (endpoint, data, options = {}) =>
    apiRequest(endpoint, { ...options, method: 'PUT', body: data });
  
  const del = (endpoint, data = null, options = {}) => {
    // Для DELETE запросов
    let url = endpoint;
    let fetchOptions = {
        ...options,
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders(),
            ...options.headers
        }
    };

    // Если есть данные, добавляем их в тело запроса
    if (data && Object.keys(data).length > 0) {
        fetchOptions.body = JSON.stringify(data);
    }
    
    return apiRequest(url, fetchOptions);
  };

  const getBaseUrl = () => API_CONFIG.getBaseUrl();

  return {
    loading,
    error,
    get,
    post,
    put,
    delete: del,  // Используем delete как alias для del
    endpoints: API_CONFIG.endpoints,
    getBaseUrl
  }
}