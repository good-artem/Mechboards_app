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
