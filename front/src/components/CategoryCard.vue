<template>
    <v-card class="category-card" elevation="2" @click="navigateToCategory">
        <v-card-text class="text-center pa-4">
            <v-icon size="32" class="mb-2" color="primary">{{ category.icon }}</v-icon>
            <div class="text-body-2 font-weight-medium">{{ category.name }}</div>
        </v-card-text>
    </v-card>
</template>

<script>
export default {
    name: 'CategoryCard',
    props: {
        category: {
            type: Object,
            required: true
        }
    },
    methods: {
        navigateToCategory() {
            this.$emit('category-selected', this.category)
        }
    }
}
</script>

<style scoped>
.category-card {
    cursor: pointer;
    transition: all 0.3s ease;
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: var(--tg-theme-bg-color, #ffffff);
    border: 1px solid var(--tg-theme-hint-color, #e0e0e0);
    color: var(--tg-theme-text-color, #000000);
}

.category-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

:deep(.v-card-text) {
    color: var(--tg-theme-text-color, #000000) !important;
}
</style>