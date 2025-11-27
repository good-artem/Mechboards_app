import API_CONFIG from '@/config/api'
import { ref } from 'vue'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  // Базовый метод для выполнения запросов
  const apiRequest = async (endpoint, options = {}) => {
    loading.value = true
    error.value = null

    try {
      const url = API_CONFIG.getUrl(endpoint)
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (err) {
      error.value = err.message
      console.error('API request failed:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Специфичные методы для разных типов запросов
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
    apiRequest,
    get,
    post,
    put,
    delete: del,
    endpoints: API_CONFIG.endpoints,
    getBaseUrl: API_CONFIG.getBaseUrl
  }
}