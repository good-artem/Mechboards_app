<template>
    <v-bottom-navigation grow color="primary">
        <v-btn value="catalog" to="/catalog">
            <v-icon>mdi-view-grid</v-icon>
        </v-btn>

        <v-btn value="support" to="/support">
            <v-icon>mdi-tools</v-icon>
        </v-btn>

        <v-btn value="cart" to="/cart">
            <v-icon>mdi-cart</v-icon>
        </v-btn>

        <v-btn value="profile" to="/profile" class="profile-btn">
            <v-avatar v-if="user.photo_url" size="24">
                <img :src="user.photo_url" alt="Profile">
            </v-avatar>
            <v-icon v-else>mdi-account</v-icon>
        </v-btn>
    </v-bottom-navigation>
</template>

<script>
export default {
    name: "Navbar",
      data() {
      return {
          user: {
              photo_url: null
          }
      }
  },
  async mounted() {
      if (window.Telegram?.WebApp?.initDataUnsafe?.user) {
          this.user.photo_url = window.Telegram.WebApp.initDataUnsafe.user.photo_url
      }
  }
}
</script>

<style scoped>
/* Дополнительные стили не нужны, Vuetify все делает */
.navbar {
  padding-bottom: env(safe-area-inset-bottom);
  padding-top: env(safe-area-inset-top);
}
.profile-btn .v-avatar {
    margin: 0 auto;
}
</style>