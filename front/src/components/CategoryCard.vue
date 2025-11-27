<template>
    <v-card class="category-card" elevation="2" @click="navigateToCategory">
        <v-card-text class="text-center pa-4">
            <v-icon size="32" class="mb-2" color="primary">{{ getCategoryIcon(category) }}</v-icon>
            <div class="text-body-2 font-weight-medium">{{ category.name }}</div>
        </v-card-text>
    </v-card>
</template>

<script>

import '@/assets/styles/components/category-card.css'

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
        },
        getCategoryIcon(category) {
            // Если иконка приходит с бэкенда, используем её
            if (category.icon) {
                return category.icon;
            }
            
            // Иначе используем fallback по имени категории
            const iconMap = {
                'Механические клавиатуры': 'mdi-keyboard',
                'Свитчи': 'mdi-circle-multiple',
                'Кейкапы': 'mdi-checkbox-multiple-blank',
                'Стабилизаторы': 'mdi-arrow-split-vertical',
                'Смазка и моддинг': 'mdi-bottle-tonic',
                'Аксессуары': 'mdi-cable-data',
                'Скидки': 'mdi-sale',
                'БУ клавиатуры': 'mdi-keyboard-return',
                'Весь каталог': 'mdi-view-grid',
                'Поддержка': 'mdi-tools'
            };
            
            return iconMap[category.name] || 'mdi-help-circle';
        }
    }
}
</script>

