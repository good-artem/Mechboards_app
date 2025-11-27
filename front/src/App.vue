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
/* Принудительное применение темы Telegram */
.v-application {
  background: var(--tg-theme-bg-color, #ffffff) !important;
  color: var(--tg-theme-text-color, #000000) !important;
}

/* Навбар */
.v-bottom-navigation {
  background: var(--tg-theme-bg-color, #ffffff) !important;
  border-top: 1px solid var(--tg-theme-secondary-bg-color, #f1f1f1);
}

.v-btn {
  color: var(--tg-theme-text-color, #000000) !important;
}

.v-btn--active {
  color: var(--tg-theme-button-color, #2481cc) !important;
  background: transparent !important;
}

/* Карточки */
.v-card {
  background: var(--tg-theme-bg-color, #ffffff) !important;
  color: var(--tg-theme-text-color, #000000) !important;
  border: 1px solid var(--tg-theme-secondary-bg-color, #f1f1f1);
}

/* Списки */
.v-list {
  background: var(--tg-theme-bg-color, #ffffff) !important;
  color: var(--tg-theme-text-color, #000000) !important;
}

/* Поля ввода */
.v-field {
  background: var(--tg-theme-secondary-bg-color, #f1f1f1) !important;
  color: var(--tg-theme-text-color, #000000) !important;
}

.v-field__input {
  color: var(--tg-theme-text-color, #000000) !important;
}

/* Карусель новостей */
.carousel-container {
  background: var(--tg-theme-button-color, #2481cc) !important;
}

/* Иконки */
.v-icon {
  color: inherit !important;
}

.main-content {
  margin-top: 150px; /* Высота карусели */
  margin-bottom: 120px;
  min-height: calc(100vh - 270px);
  padding: 0 8px;
}
</style>