<template>
    <v-bottom-navigation grow color="primary">
        <v-btn value="catalog" to="/catalog">
            <v-icon>mdi-view-grid</v-icon>
        </v-btn>

        <v-btn value="support" to="/support">
            <v-icon>mdi-tools</v-icon>
        </v-btn>

        <v-btn value="cart" to="/cart">
            <v-badge :content="cartItemsCount" color="red" v-if="cartItemsCount > 0">
                <v-icon>mdi-cart</v-icon>
            </v-badge>
            <v-icon v-else>mdi-cart</v-icon>
        </v-btn>

        <v-btn value="profile" to="/profile">
            <v-icon>mdi-account</v-icon>
        </v-btn>
    </v-bottom-navigation>
</template>

<script>

import '@/assets/styles/components/navbar.css'

export default {
    name: "Navbar",
    data() {
        return {
            cartItemsCount: 0
        }
    },
    async mounted() {
        await this.fetchCartCount();
    },
    methods: {
        async fetchCartCount() {
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
                if (tg_user) {
                    const response = await fetch(`/api/cart/${tg_user.id}`);
                    if (response.ok) {
                        const cartData = await response.json();
                        this.cartItemsCount = cartData.items?.length || 0;
                    }
                }
            } catch (error) {
                console.error('Ошибка загрузки корзины:', error);
            }
        }
    }
}
</script>
