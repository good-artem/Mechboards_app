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
import { useApi } from '@/composables/useApi'

export default {
    name: "Navbar",
    data() {
        return {
            cartItemsCount: 0,
            unsubscribeEvents: null
        }
    },
    async mounted() {
        await this.fetchCartCount();
        
        // Подписываемся на события обновления корзины
        this.unsubscribeEvents = this.$root.$on('cart-updated', this.fetchCartCount);
    },
    beforeUnmount() {
        // Отписываемся от событий
        if (this.unsubscribeEvents) {
            this.unsubscribeEvents();
        }
    },
    methods: {
        async fetchCartCount() {
            try {
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                
                if (!tg_user) {
                    console.warn('⚠️ Telegram user not found, using default ID for testing');
                    // Для тестирования используем фиктивный ID
                    const testUserId = 391622124;
                    await this.fetchCartForUser(testUserId);
                    return;
                }
                
                await this.fetchCartForUser(tg_user.id);
                
            } catch (error) {
                console.error('❌ Ошибка загрузки корзины для навбара:', error);
                this.cartItemsCount = 0;
            }
        },
        
        async fetchCartForUser(telegramId) {
            try {
                const baseUrl = this.getApiBaseUrl();
                const cartUrl = `${baseUrl}/api/cart/${telegramId}`;
                
                console.log('🔄 Загрузка корзины для навбара:', cartUrl);
                
                const response = await fetch(cartUrl);
                
                if (response.ok) {
                    const cartData = await response.json();
                    this.cartItemsCount = cartData.items?.length || 0;
                    console.log('🛒 Cart count updated:', this.cartItemsCount);
                } else {
                    console.warn('⚠️ Не удалось загрузить корзину, статус:', response.status);
                    this.cartItemsCount = 0;
                }
            } catch (error) {
                console.error('❌ Ошибка загрузки корзины:', error);
                this.cartItemsCount = 0;
            }
        },
        
        getApiBaseUrl() {
            if (import.meta.env.VITE_API_BASE_URL) {
                return import.meta.env.VITE_API_BASE_URL;
            }
            
            const hostname = window.location.hostname;
            if (hostname.includes('github.dev')) {
                return 'https://verbose-space-orbit-x45v4q7q6wwf6g94-8000.app.github.dev';
            } else if (hostname === 'localhost' || hostname === '127.0.0.1') {
                return 'http://localhost:8000';
            } else {
                return window.location.origin;
            }
        }
    }
}
</script>

<style scoped>
@import '@/assets/styles/components/navbar.css';
</style>