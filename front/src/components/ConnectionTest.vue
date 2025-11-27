<template>
  <v-card class="connection-test pa-4 ma-4">
    <v-card-title>Тест соединения с бэкендом</v-card-title>
    <v-card-text>
      <v-btn @click="testConnection" :loading="testing" color="primary">
        Проверить соединение
      </v-btn>
      
      <div v-if="testResult" class="mt-4">
        <v-alert :type="testResult.type" :icon="testResult.icon">
          {{ testResult.message }}
        </v-alert>
        
        <div v-if="testResult.data" class="mt-2">
          <strong>Данные:</strong>
          <pre>{{ JSON.stringify(testResult.data, null, 2) }}</pre>
        </div>
      </div>
      
      <div class="mt-4">
        <strong>Текущий API URL:</strong> {{ currentApiUrl }}
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import { useApi } from '@/composables/useApi'

export default {
  name: 'ConnectionTest',
  data() {
    return {
      testing: false,
      testResult: null,
      currentApiUrl: ''
    }
  },
  methods: {
    async testConnection() {
      const { get, endpoints, getBaseUrl } = useApi()
      
      this.testing = true
      this.testResult = null
      this.currentApiUrl = getBaseUrl()
      
      try {
        // Тестируем endpoint категорий
        const categories = await get(endpoints.categories.list)
        
        this.testResult = {
          type: 'success',
          icon: 'mdi-check',
          message: `✅ Соединение установлено! Получено ${categories.length} категорий`,
          data: categories
        }
      } catch (error) {
        this.testResult = {
          type: 'error',
          icon: 'mdi-alert',
          message: `❌ Ошибка соединения: ${error.message}`,
          data: null
        }
      }
      
      this.testing = false
    }
  }
}
</script>