<template>
    <v-bottom-navigation grow color="primary">
        <v-btn value="catalog" to="/catalog">
            <v-icon>mdi-view-grid</v-icon>
        </v-btn>

        <v-btn value="services" to="/services">
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
import { useApi } from '@/composables/useApi'

export default {
    name: "Navbar",
    data() {
        return {
            cartItemsCount: 0,
            unsubscribeEvents: null
        }
    },
    mounted() {
        this.fetchCartCount();
        // Подписываемся на события обновления корзины
        this.$root.$on('cart-updated', this.fetchCartCount);
    },
    beforeUnmount() {
        this.$root.$off('cart-updated', this.fetchCartCount);
    },
    methods: {
        async fetchCartCount() {
            try {
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                const telegramId = tg_user?.id || 391622124;
                
                const { get, endpoints } = useApi();
                const cartData = await get(endpoints.cart.get(telegramId));
                
                // Устанавливаем количество товаров из корзины
                this.cartItemsCount = cartData.items?.length || 0;
            } catch (error) {
                console.error('❌ Ошибка загрузки корзины для навбара:', error);
                this.cartItemsCount = 0;
            }
        },
        
        getApiBaseUrl() {
            // ЯВНО указываем URL бэкенда для продакшена
            if (import.meta.env.VITE_API_BASE_URL) {
                return import.meta.env.VITE_API_BASE_URL;
            }
            const hostname = window.location.hostname;
            if (hostname.includes('github.dev')) {
                return 'https://verbose-space-orbit-x45v4q7q6wwf6g94-8000.app.github.dev';
            } else if (hostname === 'localhost' || hostname === '127.0.0.1') {
                return 'http://localhost:8000';
            } else {
                // ЯВНО указываем URL бэкенда для Firebase
                return 'https://verbose-space-orbit-x45v4q7q6wwf6g94-8000.app.github.dev';
            }
        },
        async fetchCartForUser(telegramId) {
            try {
                // Используем useApi для правильной авторизации
                const { get, endpoints } = useApi();
                const cartData = await get(endpoints.cart.get(telegramId));
                this.cartItemsCount = cartData.items?.length || 0;
                console.log('🛒 Cart count updated:', this.cartItemsCount);
            } catch (error) {
                console.error('❌ Ошибка загрузки корзины:', error);
                this.cartItemsCount = 0;
            }
        }
    }
}
</script>

<style scoped>
@import '@/assets/styles/components/navbar.css';
</style>