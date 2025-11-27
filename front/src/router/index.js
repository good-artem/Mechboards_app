import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import '@/assets/styles/main.css'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

// Определяем тему по умолчанию на основе Telegram
const getDefaultTheme = () => {
  if (window.Telegram?.WebApp) {
    return window.Telegram.WebApp.colorScheme === 'dark' ? 'dark' : 'light'
  }
  return 'light'
}

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: getDefaultTheme(),
    themes: {
      light: {
        colors: {
          primary: '#2481cc',
          secondary: '#424242',
          accent: '#82B1FF',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FFC107',
          background: '#ffffff',
          surface: '#ffffff',
        }
      },
      dark: {
        colors: {
          primary: '#2481cc',
          secondary: '#424242',
          accent: '#82B1FF',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FFC107',
          background: '#1e1e1e',
          surface: '#2d2d2d',
        }
      }
    }
  },
  defaults: {
    VBtn: {
      color: 'primary',
      variant: 'flat',
      rounded: 'lg',
    },
    VCard: {
      rounded: 'lg',
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VTextarea: {
      variant: 'outlined',
      density: 'comfortable',
    }
  }
})

const app = createApp(App)

// Инициализация Telegram Web App
if (window.Telegram?.WebApp) {
  window.Telegram.WebApp.ready()
  window.Telegram.WebApp.expand()
  
  // Устанавливаем тему приложения в зависимости от Telegram
  const setAppTheme = () => {
    const theme = window.Telegram.WebApp.colorScheme
    document.documentElement.setAttribute('data-theme', theme)
    
    // Также обновляем тему Vuetify
    vuetify.theme.global.name.value = theme
  }
  
  // Устанавливаем тему при загрузке
  setAppTheme()
  
  // Слушаем изменения темы
  window.Telegram.WebApp.onEvent('themeChanged', setAppTheme)
  
  // Настраиваем основные параметры
  window.Telegram.WebApp.setHeaderColor('#2481cc')
  window.Telegram.WebApp.setBackgroundColor('#f8f9fa')
}

app.use(router)
app.use(vuetify)

app.mount('#app')

// Глобальная обработка ошибок
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue error:', err, 'in', instance, 'at', info)
}

// Глобальные свойства для доступа к Telegram Web App
app.config.globalProperties.$telegram = window.Telegram?.WebApp || null