<template>
    <div class="navbar-with-search">
        <!-- Поиск ПОВЕРХ кнопок -->
        <div class="search-container">
            <v-text-field
                v-model="searchQuery"
                placeholder="Поиск товаров..."
                variant="solo-filled"
                density="comfortable"
                hide-details
                prepend-inner-icon="mdi-magnify"
                clearable
                @input="handleInput"
                @keyup.enter="performSearch"
                @click:clear="clearSearch"
                :loading="searchLoading"
                class="search-field"
                rounded
                elevation="2"
                :style="{ '--tg-theme-bg-color': '#ffffff', '--tg-theme-text-color': '#000000' }"
            >
            </v-text-field>
        </div>
        
        <!-- Кнопки навигации СНИЗУ -->
        <v-bottom-navigation grow color="primary" class="navigation-buttons">
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
    </div>
</template>

<script>
import { useApi } from '@/composables/useApi'

export default {
    name: "NavbarWithSearch",
    data() {
        return {
            searchQuery: '',
            searchLoading: false,
            searchTimeout: null,
            cartItemsCount: 0
        }
    },
    mounted() {
        this.fetchCartCount();
        this.$root.$on('cart-updated', this.fetchCartCount);
        
        if (this.$route.name === 'catalog' && this.$route.query.q) {
            this.searchQuery = this.$route.query.q;
        }
    },
    beforeUnmount() {
        this.$root.$off('cart-updated', this.fetchCartCount);
    },
    watch: {
        '$route.query.q'(newVal) {
            this.searchQuery = newVal || '';
        }
    },
    methods: {
        handleInput() {
            clearTimeout(this.searchTimeout);
            
            if (this.searchQuery.trim().length >= 1) {
                this.searchTimeout = setTimeout(() => {
                    this.performSearch();
                }, 1000);
            } else {
                if (this.$route.name === 'catalog' && this.$route.query.q) {
                    this.$router.replace({ 
                        path: '/catalog', 
                        query: { ...this.$route.query, q: undefined } 
                    });
                }
            }
        },
        
        async performSearch() {
            if (!this.searchQuery.trim()) return;
            
            this.searchLoading = true;
            
            if (this.$route.name === 'catalog') {
                this.$router.replace({ 
                    path: '/catalog', 
                    query: { q: this.searchQuery.trim() } 
                });
            } else {
                this.$router.push({ 
                    path: '/catalog', 
                    query: { q: this.searchQuery.trim() } 
                });
            }
            
            this.searchLoading = false;
        },
        
        clearSearch() {
            this.searchQuery = '';
            if (this.$route.name === 'catalog' && this.$route.query.q) {
                this.$router.replace({ 
                    path: '/catalog', 
                    query: { ...this.$route.query, q: undefined } 
                });
            }
        },
        
        async fetchCartCount() {
            try {
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                const telegramId = tg_user?.id || 391622124;
                
                const { get } = useApi();
                const cartData = await get(`/api/cart/${telegramId}`);
                
                const itemsCount = cartData.items?.length || 0;
                const serviceItemsCount = cartData.service_items?.length || 0;
                this.cartItemsCount = itemsCount + serviceItemsCount;
            } catch (error) {
                console.error('❌ Ошибка загрузки корзины:', error);
                this.cartItemsCount = 0;
            }
        }
    }
}
</script>

<style scoped>

</style>