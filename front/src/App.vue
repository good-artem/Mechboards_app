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
  background: var(--tg-theme-bg-color, #ffffff);
  color: var(--tg-theme-text-color, #000000);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Принудительное применение темы Telegram ко всем элементам */
.v-application {
  background: var(--tg-theme-bg-color, #ffffff) !important;
  color: var(--tg-theme-text-color, #000000) !important;
}

/* Текстовые элементы */
.v-card-title,
.v-card-text,
.v-list-item-title,
.v-list-item-subtitle,
.v-label,
.v-field__input,
.v-select__selection-text {
  color: var(--tg-theme-text-color, #000000) !important;
}

/* Карточки */
.v-card {
  background: var(--tg-theme-bg-color, #ffffff) !important;
  color: var(--tg-theme-text-color, #000000) !important;
  border: 1px solid var(--tg-theme-hint-color, #e0e0e0) !important;
}

/* Списки */
.v-list {
  background: var(--tg-theme-bg-color, #ffffff) !important;
  color: var(--tg-theme-text-color, #000000) !important;
}

.v-list-item {
  color: var(--tg-theme-text-color, #000000) !important;
}

/* Поля ввода */
.v-field {
  background: var(--tg-theme-secondary-bg-color, #f5f5f5) !important;
  color: var(--tg-theme-text-color, #000000) !important;
}

.v-field__input {
  color: var(--tg-theme-text-color, #000000) !important;
}

.v-field__prepend-inner .v-icon {
  color: var(--tg-theme-hint-color, #999999) !important;
}

/* Навбар */
.v-bottom-navigation {
  background: var(--tg-theme-bg-color, #ffffff) !important;
  border-top: 1px solid var(--tg-theme-hint-color, #e0e0e0) !important;
}

.v-btn {
  color: var(--tg-theme-text-color, #000000) !important;
}

.v-btn--active {
  color: var(--tg-theme-button-color, #2481cc) !important;
  background: transparent !important;
}

.v-icon {
  color: inherit !important;
}

/* Диалоги */
.v-dialog .v-card {
  background: var(--tg-theme-bg-color, #ffffff) !important;
  color: var(--tg-theme-text-color, #000000) !important;
}

/* Селекты */
.v-select .v-field {
  background: var(--tg-theme-secondary-bg-color, #f5f5f5) !important;
}

.v-menu .v-overlay__content {
  background: var(--tg-theme-bg-color, #ffffff) !important;
  color: var(--tg-theme-text-color, #000000) !important;
}

.v-list-item--active {
  background: var(--tg-theme-secondary-bg-color, #f5f5f5) !important;
}

.main-content {
  margin-bottom: 120px;
  min-height: calc(100vh - 120px);
  padding: 0 8px;
  background: var(--tg-theme-bg-color, #ffffff);
}

/* Карусель новостей */
.news-carousel-container {
  background: var(--tg-theme-secondary-bg-color, #f8f9fa) !important;
  border-bottom: 1px solid var(--tg-theme-hint-color, #e0e0e0) !important;
}

.carousel-container {
  background: var(--tg-theme-button-color, #2481cc) !important;
}

.news-item {
  background: var(--tg-theme-bg-color, #ffffff) !important;
  color: var(--tg-theme-text-color, #000000) !important;
  border: 1px solid var(--tg-theme-hint-color, #e0e0e0) !important;
}

.news-text {
  color: var(--tg-theme-text-color, #000000) !important;
}

/* Категории */
.category-card {
  background: var(--tg-theme-bg-color, #ffffff) !important;
  color: var(--tg-theme-text-color, #000000) !important;
  border: 1px solid var(--tg-theme-hint-color, #e0e0e0) !important;
}
</style>