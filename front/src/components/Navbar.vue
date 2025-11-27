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

        <v-btn value="profile" to="/profile">
            <v-icon>mdi-account</v-icon>
        </v-btn>
    </v-bottom-navigation>
</template>

<script>
export default {
    name: "Navbar"
}
</script>

<style scoped>
/* Дополнительные стили не нужны, Vuetify все делает */
.navbar {
  padding-bottom: env(safe-area-inset-bottom);
  padding-top: env(safe-area-inset-top);
}
</style>