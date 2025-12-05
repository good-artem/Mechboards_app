import API_CONFIG from '@/config/api'
import { ref } from 'vue'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const apiRequest = async (endpoint, options = {}) => {
    loading.value = true
    error.value = null

    try {
      const url = API_CONFIG.getUrl(endpoint)
      console.log('🔄 API Request to:', url)
      
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })

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