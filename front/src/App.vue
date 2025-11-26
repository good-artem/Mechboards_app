<template>
  <v-app>
    <v-main>
      <!-- Новости показываются только на главной и каталоге -->
      <NewsCarousel v-if="$route.name === 'home' || $route.name === 'catalog'" />

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

.main-content {
  margin-top: 150px; /* Высота карусели */
  margin-bottom: 120px;
  min-height: calc(100vh - 270px);
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
  background-color: rgba(var(--v-theme-primary), 0.1) !important;
}
</style>