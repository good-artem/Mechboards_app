<template>
  <v-app>
    <v-main>
      <router-view />
      <Navbar />
    </v-main>
  </v-app>
</template>

<script>
import Navbar from './components/Navbar.vue'

export default {
  name: 'App',
  components: {
    Navbar
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
.v-main {
  padding-bottom: 80px !important;
}
</style>
