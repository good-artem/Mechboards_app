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

// Создаем кастомные темы для лучшей интеграции с Telegram
const telegramLightTheme = {
  dark: false,
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
    'on-background': '#000000',
    'on-surface': '#000000',
  }
}

const telegramDarkTheme = {
  dark: true,
  colors: {
    primary: '#2481cc',
    secondary: '#BB86FC',
    accent: '#03DAC6',
    error: '#CF6679',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FFC107',
    background: '#121212',
    surface: '#1e1e1e',
    'on-background': '#ffffff',
    'on-surface': '#ffffff',
  }
}

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: getDefaultTheme(),
    themes: {
      light: telegramLightTheme,
      dark: telegramDarkTheme
    },
    variations: {
      colors: ['primary', 'secondary'],
      lighten: 2,
      darken: 2,
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
      variant: 'flat',
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
    },
    VTextarea: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
    },
    VSwitch: {
      color: 'primary',
    },
    VChip: {
      rounded: 'lg',
    }
  }
})

const app = createApp(App)

// Инициализация Telegram Web App с улучшенной обработкой тем
if (window.Telegram?.WebApp) {
  const tg = window.Telegram.WebApp
  
  tg.ready()
  tg.expand()
  
  // Функция для установки темы
  const setAppTheme = () => {
    const theme = tg.colorScheme
    const isDark = theme === 'dark'
    
    // Устанавливаем атрибут data-theme для CSS
    document.documentElement.setAttribute('data-theme', theme)
    
    // Устанавливаем тему Vuetify
    vuetify.theme.global.name.value = theme
    
    // Устанавливаем цвета Telegram
    if (isDark) {
      document.documentElement.style.setProperty('--tg-theme-bg-color', '#121212')
      document.documentElement.style.setProperty('--tg-theme-text-color', '#ffffff')
      document.documentElement.style.setProperty('--tg-theme-hint-color', '#888888')
      document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', '#1e1e1e')
      
      // Настраиваем цвета интерфейса Telegram
      tg.setHeaderColor('#1e1e1e')
      tg.setBackgroundColor('#121212')
    } else {
      document.documentElement.style.setProperty('--tg-theme-bg-color', '#ffffff')
      document.documentElement.style.setProperty('--tg-theme-text-color', '#000000')
      document.documentElement.style.setProperty('--tg-theme-hint-color', '#999999')
      document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', '#f5f5f5')
      
      // Настраиваем цвета интерфейса Telegram
      tg.setHeaderColor('#2481cc')
      tg.setBackgroundColor('#f8f9fa')
    }
    
    // Устанавливаем безопасные зоны для iOS
    const safeArea = tg.safeArea || {}
    document.documentElement.style.setProperty('--tg-safe-area-top', `${safeArea.top || 0}px`)
    document.documentElement.style.setProperty('--tg-safe-area-bottom', `${safeArea.bottom || 0}px`)
    document.documentElement.style.setProperty('--tg-safe-area-left', `${safeArea.left || 0}px`)
    document.documentElement.style.setProperty('--tg-safe-area-right', `${safeArea.right || 0}px`)
    
    // Принудительно обновляем стили
    document.body.style.backgroundColor = getComputedStyle(document.documentElement)
      .getPropertyValue('--tg-theme-bg-color')
    
    console.log(`Telegram theme set to: ${theme}`)
  }
  
  // Устанавливаем тему при загрузке
  setAppTheme()
  
  // Слушаем изменения темы
  tg.onEvent('themeChanged', setAppTheme)
  
  // Настраиваем поведение при закрытии
  tg.onEvent('viewportChanged', (event) => {
    if (event.isStateStable) {
      tg.expand()
    }
  })
  
  // Настраиваем кнопку назад
  tg.BackButton.onClick(() => {
    if (window.history.length > 1) {
      router.back()
    } else {
      tg.close()
    }
  })
  
  // Показываем кнопку назад при необходимости
  const updateBackButton = () => {
    if (window.history.length > 1) {
      tg.BackButton.show()
    } else {
      tg.BackButton.hide()
    }
  }
  
  // Обновляем кнопку назад при изменении маршрута
  router.afterEach(updateBackButton)
  updateBackButton()
  
  // Отключаем контекстное меню для улучшения UX
  document.addEventListener('contextmenu', (e) => {
    if (tg.platform === 'ios' || tg.platform === 'android') {
      e.preventDefault()
    }
  })
}

// Добавляем глобальный миксин для адаптации
app.mixin({
  computed: {
    $isMobile() {
      return window.innerWidth <= 768
    },
    $isTablet() {
      return window.innerWidth > 768 && window.innerWidth <= 1024
    },
    $isDesktop() {
      return window.innerWidth > 1024
    },
    $screenHeight() {
      return window.innerHeight
    },
    $screenWidth() {
      return window.innerWidth
    }
  },
  methods: {
    $formatPrice(price) {
      if (!price && price !== 0) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
      }).format(price)
    },
    $truncateText(text, length = 100) {
      if (!text) return ''
      if (text.length <= length) return text
      return text.substring(0, length) + '...'
    },
    $getStatusColor(status) {
      const statusColors = {
        'Новый': 'warning',
        'В обработке': 'info',
        'Доставлен': 'success',
        'Отменен': 'error',
        'Выполнен': 'success',
        'Закрыт': 'grey',
        'Открыт': 'info',
        'Отвечено': 'success'
      }
      return statusColors[status] || 'primary'
    }
  }
})

app.use(router)
app.use(vuetify)

app.mount('#app')

// Глобальная обработка ошибок
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue error:', err, 'in', instance, 'at', info)
  
  // Можно добавить отправку ошибок на сервер
  if (window.Telegram?.WebApp) {
    try {
      window.Telegram.WebApp.sendData(JSON.stringify({
        type: 'error',
        error: err.message,
        component: instance?.$options.name,
        info: info,
        url: window.location.href,
        userAgent: navigator.userAgent
      }))
    } catch (e) {
      console.error('Failed to send error to Telegram:', e)
    }
  }
}

// Глобальные свойства для доступа к Telegram Web App
app.config.globalProperties.$telegram = window.Telegram?.WebApp || null

// Обработка изменения размера окна для адаптации
let resizeTimeout
window.addEventListener('resize', () => {
  clearTimeout(resizeTimeout)
  resizeTimeout = setTimeout(() => {
    // Обновляем CSS переменные при изменении размера
    if (window.Telegram?.WebApp) {
      const safeArea = window.Telegram.WebApp.safeArea || {}
      document.documentElement.style.setProperty('--tg-safe-area-bottom', `${safeArea.bottom || 0}px`)
    }
    
    // Обновляем высоту окна в CSS переменных
    document.documentElement.style.setProperty('--window-height', `${window.innerHeight}px`)
    document.documentElement.style.setProperty('--window-width', `${window.innerWidth}px`)
  }, 250)
})

// Инициализация CSS переменных при загрузке
document.addEventListener('DOMContentLoaded', () => {
  document.documentElement.style.setProperty('--window-height', `${window.innerHeight}px`)
  document.documentElement.style.setProperty('--window-width', `${window.innerWidth}px`)
})