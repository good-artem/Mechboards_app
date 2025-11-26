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
      <SearchBar v-if="$route.name === 'home' || $route.name === 'catalog'" />

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
/* Принудительные стили для консистентности */
body {
  background: var(--tg-theme-bg-color, #ffffff) !important;
  color: var(--tg-theme-text-color, #000000) !important;
}

.v-application {
  background: var(--tg-theme-bg-color, #ffffff) !important;
}

.main-content {
  margin-top: 150px;
  margin-bottom: 120px;
  min-height: calc(100vh - 270px);
  padding: 0 8px;
}
</style>