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

// Импортируем глобальные стили
import '@/assets/styles/global.css'
import '@/assets/styles/telegram-theme.css'

export default {
  name: 'App',
  components: {
    Navbar,
    SearchBar
  }
}
</script>

