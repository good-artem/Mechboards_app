<template>
  <v-app>
    <v-main>
      <!-- Основной контент -->
      <div class="main-content">
        <router-view />
      </div>

      <!-- Поиск всегда над навбаром -->
      <SearchBar />

      <!-- Навбар -->
      <Navbar />
    </v-main>
  </v-app>
</template>

<script>
import Navbar from './components/Navbar.vue'
import SearchBar from './components/SearchBar.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    SearchBar
  }
}
</script>

<style>
/* Глобальные стили для Telegram Mini App */
body {
  margin: 0;
  padding: 0;
  background: var(--tg-theme-bg-color, #f5f5f5);
  color: var(--tg-theme-text-color, #000000);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.main-content {
  margin-bottom: 120px; /* Высота поиска + навбара */
  min-height: calc(100vh - 120px);
  padding: 0 8px;
}

/* Стили для Vuetify компонентов */
.v-bottom-navigation {
  position: fixed !important;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: 60px !important;
}

.v-btn--active {
  color: var(--tg-theme-button-color, #2481cc) !important;
  background: transparent !important;
}
</style>