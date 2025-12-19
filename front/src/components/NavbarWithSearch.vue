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
                
                const { get, endpoints } = useApi();
                const cartData = await get(endpoints.cart.get(telegramId));
                
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
.navbar-with-search {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 1000;
}

/* Поиск - ПОВЕРХ кнопок, но прижат к ним сверху */
.search-container {
    position: absolute;
    bottom: 56px; /* Высота кнопок навигации */
    left: 0;
    right: 0;
    padding: 8px;
    background: var(--tg-theme-bg-color, #ffffff);
    border-bottom: 1px solid var(--tg-theme-divider-color, rgba(0, 0, 0, 0.12));
    z-index: 1001;
}

/* Кнопки навигации СНИЗУ */
.navigation-buttons {
    height: 56px;
    background: var(--tg-theme-bg-color, #ffffff);
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
    position: relative;
    z-index: 1000;
}

.search-field {
    background-color: var(--tg-theme-secondary-bg-color, #f5f5f5);
    border-radius: 12px;
}

/* Адаптивные стили */
@media (max-width: 600px) {
    .search-container {
        padding: 6px;
        bottom: 48px;
    }
    
    .navigation-buttons {
        height: 48px;
    }
}

/* Для iOS Safari */
@supports (-webkit-touch-callout: none) {
    .navbar-with-search {
        padding-bottom: env(safe-area-inset-bottom);
    }
}
</style>