<template>
    <v-container>
        <v-row>
            <v-col cols="12">
                <v-row class="categories-grid">
                    <v-col 
                        v-for="category in categories" 
                        :key="category.id"
                        cols="4"
                        class="pa-2"
                    >
                        <CategoryCard 
                            :category="category" 
                            @category-selected="onCategorySelected"
                        />
                    </v-col>
                </v-row>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import CategoryCard from '@/components/CategoryCard.vue'

export default {
    name: 'CatalogView',
    components: {
        CategoryCard
    },
    data() {
        return {
            categories: [
                { id: 1, name: 'Весь каталог', icon: 'mdi-view-grid' },
                { id: 2, name: 'Скидки', icon: 'mdi-sale' },
                { id: 3, name: 'Новые клавиатуры', icon: 'mdi-keyboard' },
                { id: 4, name: 'БУ клавиатуры', icon: 'mdi-keyboard-return' },
                { id: 5, name: 'Свитчи', icon: 'mdi-circle-multiple' },
                { id: 6, name: 'Кейкапы', icon: 'mdi-checkbox-multiple-blank' },
                { id: 7, name: 'Стабилизаторы', icon: 'mdi-arrow-split-vertical' },
                { id: 8, name: 'Смазка и моддинг', icon: 'mdi-bottle-tonic' },
                { id: 9, name: 'Аксессуары', icon: 'mdi-cable-data' },
                { id: 10, name: 'Другое', icon: 'mdi-dots-horizontal' }
            ]
        }
    },
    methods: {
        onCategorySelected(category) {
            console.log('Selected category:', category.name)
            // Здесь будет навигация к выбранной категории
        }
    }
}
</script>

<style scoped>
.categories-grid {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}
</style>