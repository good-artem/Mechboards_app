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
/* Используем CSS-переменные Telegram */
:root {
  --tg-theme-bg-color: #ffffff;
  --tg-theme-text-color: #000000;
  --tg-theme-hint-color: #999999;
  --tg-theme-link-color: #2481cc;
  --tg-theme-button-color: #2481cc;
  --tg-theme-button-text-color: #ffffff;
  --tg-theme-secondary-bg-color: #f1f1f1;
}

/* Применяем тему ко всему приложению */
.v-application {
  background: var(--tg-theme-bg-color) !important;
  color: var(--tg-theme-text-color) !important;
}

/* Навбар */
.v-bottom-navigation {
  background: var(--tg-theme-bg-color) !important;
  border-top: 1px solid var(--tg-theme-secondary-bg-color);
}

.v-btn:not(.v-btn--active) {
  color: var(--tg-theme-text-color) !important;
}

.v-btn--active {
  color: var(--tg-theme-button-color) !important;
}

/* Карточки */
.v-card {
  background: var(--tg-theme-bg-color) !important;
  color: var(--tg-theme-text-color) !important;
}

/* Списки */
.v-list {
  background: var(--tg-theme-bg-color) !important;
  color: var(--tg-theme-text-color) !important;
}

/* Поля ввода */
.v-field {
  background: var(--tg-theme-secondary-bg-color) !important;
  color: var(--tg-theme-text-color) !important;
}

.v-field__input {
  color: var(--tg-theme-text-color) !important;
}

/* Иконки в полях */
.v-field__prepend-inner {
  color: var(--tg-theme-hint-color) !important;
}

/* Карусель новостей */
.carousel-container {
  background: var(--tg-theme-button-color) !important;
}

.news-item {
  background: rgba(255, 255, 255, 0.9) !important;
  color: var(--tg-theme-text-color) !important;
}

.news-icon {
  color: var(--tg-theme-button-color) !important;
}
</style>