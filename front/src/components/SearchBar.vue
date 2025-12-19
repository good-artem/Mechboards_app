<template>
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
</template>

<script>
import { useApi } from '@/composables/useApi'

export default {
    name: "SearchBar",
    data() {
        return {
            searchQuery: '',
            searchLoading: false,
            searchTimeout: null
        }
    },
    methods: {
        handleInput() {
            clearTimeout(this.searchTimeout);
            
            if (this.searchQuery.trim().length >= 2) {
                // Автоматический поиск через 2 секунды после ввода
                this.searchTimeout = setTimeout(() => {
                    this.performSearch();
                }, 2000);
            } else {
                this.$root.$emit('clear-search');
            }
        },
        async performSearch() {
            if (!this.searchQuery.trim()) return;
            
            this.searchLoading = true;
            try {
                const { get, endpoints } = useApi();
                
                // Используем правильный эндпоинт поиска
                const results = await get(endpoints.products.search, {
                    params: {
                        q: this.searchQuery,
                        limit: 50
                    }
                });
                
                // Отправляем результаты в глобальное событие для обработки в CatalogView
                this.$root.$emit('search-results', {
                    query: this.searchQuery,
                    results: results
                });
            } catch (error) {
                console.error('❌ Ошибка поиска:', error);
                let errorMessage = 'Ошибка поиска товаров';
                
                if (error.response) {
                    // Получаем детали ошибки от сервера
                    const errorData = await error.response.json().catch(() => null);
                    if (errorData && errorData.detail) {
                        errorMessage = `Ошибка поиска: ${errorData.detail}`;
                    }
                }
                
                this.$root.$emit('show-message', errorMessage, 'error');
            } finally {
                this.searchLoading = false;
            }
        },
        clearSearch() {
            this.searchQuery = '';
            this.$root.$emit('clear-search');
        }
    }
}
</script>

<style scoped>
.search-container {
    border-radius: 16px;
    background-color: var(--tg-theme-bg-color, #ffffff);
}
</style>