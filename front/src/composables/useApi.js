import API_CONFIG from '@/config/api'
import { ref } from 'vue'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const getTelegramInitData = () => {
    // Получаем initData из Telegram WebApp
    if (window.Telegram?.WebApp?.initData) {
      return window.Telegram.WebApp.initData;
    }
    
    // Для разработки можно использовать фиктивные данные
    if (import.meta.env.MODE === 'development') {
      console.warn('⚠️ В режиме разработки: используем фиктивные данные Telegram');
      return 'user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22Test%22%2C%22last_name%22%3A%22User%22%7D&hash=FAKE_HASH_FOR_DEV';
    }
    
    return null;
  }

  const apiRequest = async (endpoint, options = {}) => {
    loading.value = true
    error.value = null

    try {
      const url = API_CONFIG.getUrl(endpoint)
      console.log('🔄 API Request to:', url)
      
      // Получаем Telegram initData
      const initData = getTelegramInitData();
      
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers
      }
      
      // Добавляем Telegram auth в заголовки
      if (initData) {
        headers['X-Telegram-Init-Data'] = initData;
      } else {
        console.warn('⚠️ Telegram initData не найден. Запрос может быть отклонен бэкендом.');
      }

      const response = await fetch(url, {
        headers,
        ...options
      })

      if (response.status === 401) {
        throw new Error('Требуется авторизация Telegram. Обновите страницу.');
      }
      
      if (response.status === 403) {
        throw new Error('Доступ запрещен. Вы не имеете прав на этот ресурс.');
      }

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }

      const data = await response.json()
      console.log('✅ API Response:', data)
      return data
    } catch (err) {
      error.value = err.message
      console.error('❌ API request failed:', err)
      
      // Показываем понятные сообщения об ошибках
      if (err.message.includes('авторизация')) {
        alert('❌ Ошибка авторизации. Пожалуйста, войдите через Telegram.');
      } else if (err.message.includes('запрещен')) {
        alert('❌ Доступ запрещен. У вас нет прав на это действие.');
      }
      
      throw err
    } finally {
      loading.value = false
    }
  }

  const get = (endpoint) => apiRequest(endpoint)
  
  const post = (endpoint, data) => 
    apiRequest(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  
  const put = (endpoint, data) =>
    apiRequest(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  
  const del = (endpoint, data) =>
    apiRequest(endpoint, {
      method: 'DELETE',
      body: data ? JSON.stringify(data) : undefined
    })

  return {
    loading,
    error,
    get,
    post,
    put,
    delete: del,
    endpoints: API_CONFIG.endpoints
  }
}