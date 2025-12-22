<template>
  <v-app class="tg-app">
    <v-main>
      <!-- Состояние загрузки - временно показываем только если Telegram не загружен -->
      <div v-if="loading && showLoading" class="app-loading">
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
    <!-- Навбар - всегда внизу, но только на мобильных экранах -->
    <NavbarWithSearch v-if="!isDesktop" />
  </v-app>
</template>

<script>
import NavbarWithSearch from '@/components/NavbarWithSearch.vue'
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
      showLoading: true, // Новая переменная для контроля показа загрузки
      showSnackbar: false,
      snackbarMessage: '',
      snackbarColor: 'primary',
      isDesktop: false
    }
  },
  mounted() {
    this.initApp();
  },
  methods: {
    initApp() {
      // Проверяем, мобильное ли устройство
      this.checkIfDesktop();
      
      // Инициализируем Telegram Web App с таймаутом
      setTimeout(() => {
        this.initTelegramApp();
      }, 100);
      
      // Скрываем загрузку через 2 секунды максимум
      setTimeout(() => {
        this.showLoading = false;
      }, 2000);
      
      // Глобальная обработка ошибок
      this.setupErrorHandling();
    },
    
    checkIfDesktop() {
      // Проверяем размер экрана и user agent для определения десктопа
      const width = window.innerWidth;
      const userAgent = navigator.userAgent.toLowerCase();
      this.isDesktop = width > 768 && !userAgent.includes('mobile');
    },
    
    initTelegramApp() {
      if (window.Telegram?.WebApp) {
        try {
          window.Telegram.WebApp.ready();
          window.Telegram.WebApp.expand();
          // Скрываем загрузку сразу после инициализации Telegram
          this.showLoading = false;
          this.loading = false;
          // Устанавливаем тему Telegram
          this.applyTelegramTheme();
        } catch (error) {
          console.error('Ошибка инициализации Telegram Web App:', error);
          this.showLoading = false;
          this.loading = false;
        }
      } else {
        // Если Telegram не доступен, все равно скрываем загрузку
        console.log('Telegram WebApp не найден, работает в режиме браузера');
        this.showLoading = false;
        this.loading = false;
      }
    },
    
    applyTelegramTheme() {
      if (window.Telegram?.WebApp) {
        const theme = window.Telegram.WebApp.colorScheme;
        document.body.setAttribute('data-theme', theme);
      }
    },
    
    setupErrorHandling() {
      // Глобальная обработка ошибок
      window.addEventListener('error', (event) => {
        console.error('Global error:', event.error);
      });
      
      window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
      });
    }
  }
}
</script>