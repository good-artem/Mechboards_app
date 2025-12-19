<template>
  <v-app class="tg-app">
    <v-main>
      <!-- Состояние загрузки -->
      <div v-if="loading" class="app-loading">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        ></v-progress-circular>
        <div class="loading-text">Загрузка...</div>
      </div>
      <!-- Основной контент -->
      <div v-else class="main-content">
        <router-view />
      </div>
      <!-- Системные уведомления -->
      <v-snackbar
        v-model="showSnackbar"
        :timeout="3000"
        :color="snackbarColor"
        location="bottom"
      >
        {{ snackbarMessage }}
      </v-snackbar>
    </v-main>
    <!-- Навбар - всегда внизу -->
    <NavbarWithSearch/>
  </v-app>
</template>

<script>
import NavbarWithSearch from '@/components/NavbarWithSearch.vue'
// Импортируем глобальные стили
import '@/assets/styles/global.css'
import '@/assets/styles/telegram-theme.css'
import '@/assets/styles/app.css'

export default {
  name: 'App',
  components: {
    NavbarWithSearch
  },
  data() {
    return {
      loading: false,
      showSnackbar: false,
      snackbarMessage: '',
      snackbarColor: 'primary'
    }
  },
  mounted() {
    // Инициализация Telegram Web App
    this.initTelegramApp()
    // Глобальная обработка ошибок
    this.setupErrorHandling()
  },
  methods: {
    initTelegramApp() {
      if (window.Telegram?.WebApp) {
        try {
          window.Telegram.WebApp.ready()
          window.Telegram.WebApp.expand()
          // Устанавливаем тему Telegram
          this.applyTelegramTheme()
        } catch (error) {
          console.error('Ошибка инициализации Telegram Web App:', error)
        }
      }
    },
    applyTelegramTheme() {
      if (window.Telegram?.WebApp) {
        const theme = window.Telegram.WebApp.colorScheme
        document.documentElement.setAttribute('data-theme', theme)
      }
    },
    setupErrorHandling() {
      // Глобальный обработчик ошибок
      window.addEventListener('error', (event) => {
        console.error('Global error:', event.error)
        this.showMessage('Произошла ошибка приложения', 'error')
      })
      // Обработчик обещаний без catch
      window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason)
        this.showMessage('Ошибка загрузки данных', 'error')
      })
    },
    showMessage(message, type = 'info') {
      this.snackbarMessage = message
      this.snackbarColor = type === 'error' ? 'error' : 'primary'
      this.showSnackbar = true
    }
  },
  provide() {
    // Предоставляем глобальные методы дочерним компонентам
    return {
      showAppMessage: this.showMessage,
      setAppLoading: (loading) => { this.loading = loading }
    }
  }
}
</script>

<style scoped>
/* Добавляем отступ для навбара */
.tg-app {
  padding-bottom: 64px; /* Отступ для кнопок навигации (поиск поверх них) */
}

/* Убираем стандартные отступы Vuetify */
.v-main {
  padding-bottom: 0 !important;
}

/* Стили для загрузки */
.app-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}

.loading-text {
  margin-top: 16px;
  font-size: 16px;
  color: var(--tg-theme-text-color, #000);
}

.main-content {
  min-height: calc(100vh - 120px); /* Высота экрана минус высота навбара */
}
</style>