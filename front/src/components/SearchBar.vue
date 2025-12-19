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
        
        <!-- Всплывающие результаты поиска -->
        <v-card 
            v-if="showResults && searchResults.length > 0" 
            class="search-results-dropdown" 
            elevation="4"
        >
            <v-list density="compact">
                <v-list-item
                    v-for="result in searchResults"
                    :key="result.product_id"
                    @click="selectProduct(result)"
                    class="search-result-item"
                >
                    <v-list-item-title>{{ result.name }}</v-list-item-title>
                    <v-list-item-subtitle>{{ formatPrice(result.price) }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item 
                    v-if="searchResults.length > 0" 
                    @click="showAllResults"
                    class="search-show-all"
                >
                    <v-list-item-title class="text-center">
                        <v-icon small>mdi-arrow-right</v-icon>
                        Показать все результаты ({{ searchResults.length }})
                    </v-list-item-title>
                </v-list-item>
            </v-list>
        </v-card>
    </div>
</template>

<script>
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
            clearTimeout(this.searchTimeout);
            
            if (this.searchQuery.trim().length > 1) {
                this.searchTimeout = setTimeout(() => {
                    this.performSearch();
                }, 300);
                this.showResults = true;
            } else {
                this.searchResults = [];
                this.showResults = false;
                this.$emit('clear-search');
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
                // Используем эндпоинт поиска
                const baseUrl = this.getApiBaseUrl();
                const apiUrl = `${baseUrl}/api/products/search?q=${encodeURIComponent(this.searchQuery)}&limit=5`;
                
                const response = await fetch(apiUrl);
                
                if (response.ok) {
                    const results = await response.json();
                    this.searchResults = results;
                    this.showResults = true;
                    
                    // Эмитим событие для родительского компонента
                    this.$emit('search', this.searchQuery);
                } else {
                    console.error('Ошибка поиска:', response.status);
                    this.searchResults = [];
                }
            } catch (error) {
                console.error('Ошибка поиска:', error);
                this.searchResults = [];
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
        showAllResults() {
            this.$emit('show-all-results', {
                query: this.searchQuery,
                results: this.searchResults
            });
            this.showResults = false;
        },
        getApiBaseUrl() {
            // Используем URL из переменных окружения или определяем автоматически
            if (import.meta.env.VITE_API_BASE_URL) {
                return import.meta.env.VITE_API_BASE_URL;
            }
            
            // Определяем среду
            const hostname = window.location.hostname;
            if (hostname.includes('github.dev')) {
                return 'https://verbose-space-orbit-x45v4q7q6wwf6g94-8000.app.github.dev';
            } else if (hostname === 'localhost' || hostname === '127.0.0.1') {
                return 'http://localhost:8000';
            } else {
                return window.location.origin;
            }
        }
    },
    mounted() {
        // Закрываем результаты при клике вне компонента
        document.addEventListener('click', (e) => {
            if (!this.$el.contains(e.target)) {
                this.showResults = false;
            }
        });
    }
}
</script>
