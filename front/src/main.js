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

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#2481cc',
          background: '#ffffff',
          surface: '#ffffff',
        }
      },
      dark: {
        colors: {
          primary: '#2481cc',
          background: '#1e1e1e',
          surface: '#2d2d2d',
        }
      }
    }
  }
})

const app = createApp(App)

if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
}

app.use(router)
app.use(vuetify)

app.mount('#app')