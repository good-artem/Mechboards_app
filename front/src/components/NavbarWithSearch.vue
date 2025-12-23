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
.navbar-with-search {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: var(--tg-theme-bg-color, #ffffff);
}

.search-container {
  position: absolute;
  bottom: 56px;
  left: 0;
  right: 0;
  padding: 8px;
  background: var(--tg-theme-bg-color, #ffffff);
  border-bottom: 1px solid var(--tg-theme-hint-color, #e0e0e0);
  z-index: 1001;
}

.navigation-buttons {
  height: 56px;
  background: var(--tg-theme-bg-color, #ffffff);
  border-top: 1px solid var(--tg-theme-hint-color, #e0e0e0);
  position: relative;
  z-index: 1000;
}

.search-field {
  border-radius: 12px;
  overflow: hidden;
}

/* Стили для активной кнопки навигации */
.btn-label {
  font-size: 0.7rem;
  margin-top: 2px;
}

/* Адаптация для мобильных */
@media (max-width: 600px) {
  .search-container {
    padding: 6px;
    bottom: 48px;
  }
  
  .navigation-buttons {
    height: 48px;
  }
  
  .search-field {
    font-size: 14px;
  }
  
  .btn-label {
    font-size: 0.65rem;
  }
}

/* Для iOS Safari */
@supports (-webkit-touch-callout: none) {
  .navbar-with-search {
    padding-bottom: env(safe-area-inset-bottom);
  }
}
</style>

<style>
/* Глубокие селекторы для правильного применения стилей Vuetify */

/* Стили для поля поиска */
.navbar-with-search .search-field .v-field {
  background-color: var(--tg-theme-secondary-bg-color, #f1f1f1) !important;
  color: var(--tg-theme-text-color, #000000) !important;
  border: 1px solid transparent !important;
}

.navbar-with-search .search-field .v-field__input {
  color: var(--tg-theme-text-color, #000000) !important;
}

.navbar-with-search .search-field .v-field__prepend-inner .v-icon {
  color: var(--tg-theme-hint-color, #999999) !important;
}

.navbar-with-search .search-field .v-field__clearable .v-icon {
  color: var(--tg-theme-hint-color, #999999) !important;
}

.navbar-with-search .search-field .v-field__placeholder {
  color: var(--tg-theme-hint-color, #999999) !important;
}

/* Состояния поля */
.navbar-with-search .search-field .v-field--focused {
  background-color: var(--tg-theme-secondary-bg-color, #f1f1f1) !important;
  border-color: var(--tg-theme-button-color, #2481cc) !important;
  box-shadow: 0 0 0 1px var(--tg-theme-button-color, #2481cc) !important;
}

.navbar-with-search .search-field .v-field--focused .v-field__prepend-inner .v-icon {
  color: var(--tg-theme-button-color, #2481cc) !important;
}

/* Стили для кнопок навигации */
.navbar-with-search .navigation-buttons .v-btn {
  color: var(--tg-theme-text-color, #000000) !important;
}

.navbar-with-search .navigation-buttons .v-btn--active {
  color: var(--tg-theme-button-color, #2481cc) !important;
}

.navbar-with-search .navigation-buttons .v-btn--active .v-icon {
  color: var(--tg-theme-button-color, #2481cc) !important;
}

.navbar-with-search .navigation-buttons .v-btn--active .btn-label {
  color: var(--tg-theme-button-color, #2481cc) !important;
}

.navbar-with-search .navigation-buttons .v-btn .v-icon {
  color: var(--tg-theme-text-color, #000000) !important;
}

/* Стили для бейджа в корзине */
.navbar-with-search .v-badge .v-badge__badge {
  background-color: var(--tg-theme-button-color, #2481cc) !important;
  color: var(--tg-theme-button-text-color, #ffffff) !important;
  font-size: 10px;
  min-width: 16px;
  height: 16px;
}

/* Темная тема адаптация */
@media (prefers-color-scheme: dark) {
  .navbar-with-search .search-field .v-field {
    background-color: var(--tg-theme-secondary-bg-color, #1c1c1d) !important;
  }
  
  .navbar-with-search .search-field .v-field__input {
    color: var(--tg-theme-text-color, #ffffff) !important;
  }
  
  .navbar-with-search .search-field .v-field__placeholder {
    color: var(--tg-theme-hint-color, #8e8e93) !important;
  }
  
  .navbar-with-search .navigation-buttons .v-btn {
    color: var(--tg-theme-text-color, #ffffff) !important;
  }
  
  .navbar-with-search .navigation-buttons .v-btn .v-icon {
    color: var(--tg-theme-text-color, #ffffff) !important;
  }
}

/* Анимация при фокусе */
.navbar-with-search .search-field .v-field {
  transition: all 0.2s ease;
}
</style>