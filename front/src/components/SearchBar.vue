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
                @keyup.enter="performSearch"
                @click:clear="clearSearch"
            >
            </v-text-field>
        </v-card>
    </div>
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
.search-bar-container {
    position: fixed;
    bottom: 60px; /* Высота навбара */
    left: 0;
    right: 0;
    z-index: 99;
    background: var(--tg-theme-bg-color, #ffffff);
    border-top: 1px solid #e0e0e0;
    border-bottom: 1px solid #e0e0e0;
}

.search-container {
    margin: 0;
    border-radius: 0;
    box-shadow: none !important;
}
</style>