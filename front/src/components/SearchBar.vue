<template>
    <div class="search-bar-container">
        <v-card class="search-container" elevation="2" rounded="lg">
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
            >
            </v-text-field>
        </v-card>
        
        <!-- Результаты поиска (опционально) -->
        <v-card v-if="showResults && searchResults.length > 0" class="search-results" elevation="4">
            <v-list density="compact">
                <v-list-item
                    v-for="result in searchResults"
                    :key="result.product_id"
                    @click="selectProduct(result)"
                >
                    <v-list-item-title>{{ result.name }}</v-list-item-title>
                    <v-list-item-subtitle>{{ formatPrice(result.price) }}</v-list-item-subtitle>
                </v-list-item>
            </v-list>
        </v-card>
    </div>
</template>

<script>

import '@/assets/styles/components/search-bar.css'
import { useApi } from '@/composables/useApi'

export default {
    name: "SearchBar",
    data() {
        return {
            searchQuery: '',
            searchLoading: false,
            searchResults: [],
            showResults: false,
            searchTimeout: null
        }
    },
    methods: {
        formatPrice(price) {
            return new Intl.NumberFormat('ru-RU').format(price) + ' ₽'
        },
        handleInput() {
            // Дебаунс для избежания частых запросов
            clearTimeout(this.searchTimeout);
            
            if (this.searchQuery.trim().length > 2) {
                this.searchTimeout = setTimeout(() => {
                    this.performSearch();
                }, 500);
                this.showResults = true;
            } else {
                this.searchResults = [];
                this.showResults = false;
            }
        },
        async performSearch() {
            if (!this.searchQuery.trim()) {
                this.searchResults = [];
                this.showResults = false;
                this.$emit('search', '');
                return;
            }

            this.searchLoading = true;
            
            try {
                const { get, endpoints } = useApi();
                
                // Правильный вызов search endpoint
                const results = await get(`${endpoints.products.search}?q=${encodeURIComponent(this.searchQuery)}&limit=10`);
                
                this.searchResults = results;
                this.showResults = true;
                
                // Эмитим событие для родительского компонента CatalogView
                this.$emit('search', this.searchQuery);
            } catch (error) {
                console.error('Ошибка поиска:', error);
                this.searchResults = [];
                // Используем метод showMessage если он доступен
                if (this.$parent && this.$parent.showMessage) {
                    this.$parent.showMessage('Ошибка поиска товаров', 'error');
                }
            } finally {
                this.searchLoading = false;
            }
        },
        clearSearch() {
            this.searchQuery = '';
            this.searchResults = [];
            this.showResults = false;
            this.$emit('clear-search');
        },
        selectProduct(product) {
            this.$emit('product-selected', product);
            this.searchQuery = product.name;
            this.showResults = false;
        },
        hideResults() {
            // Скрываем результаты при клике вне компонента
            setTimeout(() => {
                this.showResults = false;
            }, 200);
        }
    },
    mounted() {
        // Закрываем результаты при клике вне компонента
        document.addEventListener('click', this.hideResults);
    },
    beforeUnmount() {
        document.removeEventListener('click', this.hideResults);
    }
}
</script>

