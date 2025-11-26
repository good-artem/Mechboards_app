<template>
  <v-app>
    <v-main>
      <!-- Верхняя часть: Новости и поиск -->
      <div class="top-section">
        <NewsCarousel />
        <SearchBar />
      </div>

      <!-- Основной контент -->
      <div class="main-content">
        <router-view />
      </div>

      <!-- Навбар -->
      <Navbar />
    </v-main>
  </v-app>
</template>

<script>
import Navbar from './components/Navbar.vue'
import SearchBar from './components/SearchBar.vue'
import NewsCarousel from './components/NewsCarousel.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    SearchBar,
    NewsCarousel
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

.top-section {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--tg-theme-bg-color, #ffffff);
  border-bottom: 1px solid #e0e0e0;
}

.main-content {
  margin-top: 160px; /* Высота top-section */
  margin-bottom: 80px; /* Высота навбара */
  padding: 0 8px;
}

/* Стили для Vuetify компонентов */
.v-bottom-navigation {
  position: fixed !important;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.v-btn--active {
  background-color: rgba(var(--v-theme-primary), 0.1) !important;
}
</style>