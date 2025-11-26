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
            @keyup.enter="performSearch"
            @click:clear="clearSearch"
        >
        </v-text-field>
    </v-card>
</template>

<script>
export default {
    name: "SearchBar",
    data() {
        return {
            searchQuery: ''
        }
    },
    methods: {
        performSearch() {
            if (this.searchQuery.trim()) {
                console.log('Searching for:', this.searchQuery)
                // Здесь будет логика поиска
                this.$emit('search', this.searchQuery)
            }
        },
        clearSearch() {
            this.searchQuery = ''
            this.$emit('clear-search')
        }
    }
}
</script>

<style scoped>
.search-container {
    margin: 8px 16px;
    padding: 4px;
}
</style>