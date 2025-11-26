<template>
    <nav class="navbar">
        <router-link to="/" class="nav-link">Задачи</router-link>
        <router-link to="/profile" class="nav-link">Профиль</router-link>
    </nav>
</template>

<script>
export default {
    name: "Navbar"
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  position: relative;
}

.main-content {
  padding-bottom: 60px; /* Место для навбара */
}

.navbar {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 60px;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-top: 1px solid #ccc;
  
  /* Фиксированное позиционирование */
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.nav-link {
  text-decoration: none;
  color: #333;
  font-size: 16px;
  font-weight: 500;
  padding: 10px 20px;
}

.nav-link.router-link-active {
  color: #007bff; /* Цвет для активной ссылки */
}
</style>