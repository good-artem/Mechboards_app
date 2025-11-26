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
            <!-- В будущем замените на: -->
            <!-- <v-avatar size="24" v-if="user.photo_url">
                <img :src="user.photo_url" alt="Profile">
            </v-avatar>
            <v-icon v-else>mdi-account</v-icon> -->
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
        // В будущем для Telegram user photo
        if (window.Telegram?.WebApp) {
            const tgUser = window.Telegram.WebApp.initDataUnsafe?.user
            if (tgUser?.photo_url) {
                this.user.photo_url = tgUser.photo_url
            }
        }
    }
}
</script>

<style scoped>
/* Дополнительные стили не нужны, Vuetify все делает */
</style>