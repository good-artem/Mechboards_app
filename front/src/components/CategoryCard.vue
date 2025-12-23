<template>
    <v-card class="category-card" elevation="2" @click="navigateToCategory">
        <v-card-text class="text-center pa-3">
            <v-icon size="28" class="mb-1" color="primary">{{ getCategoryIcon(category) }}</v-icon>
            <div class="text-caption font-weight-medium text-truncate">{{ category.name }}</div>
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

<style scoped>
.category-card {
    cursor: pointer;
    transition: all 0.3s ease;
    height: 100%;
    min-height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: var(--tg-theme-bg-color, #ffffff);
    border: 1px solid var(--tg-theme-hint-color, #e0e0e0);
    color: var(--tg-theme-text-color, #000000);
    width: 100%;
    overflow: hidden;
}

.category-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

.category-card .v-card-text {
    color: var(--tg-theme-text-color, #000000) !important;
    text-align: center;
    padding: 12px 6px !important;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex-grow: 1;
}

.category-card .v-icon {
    color: var(--tg-theme-button-color, #2481cc) !important;
    margin-bottom: 6px;
    flex-shrink: 0;
}

.category-card .text-caption {
    font-size: 0.75rem;
    font-weight: 500;
    line-height: 1.2;
    color: var(--tg-theme-text-color, #000000);
    width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Адаптация для маленьких экранов */
@media (max-width: 600px) {
    .category-card {
        min-height: 75px;
    }
    
    .category-card .v-card-text {
        padding: 10px 4px !important;
    }
    
    .category-card .v-icon {
        font-size: 24px;
        margin-bottom: 4px;
    }
    
    .category-card .text-caption {
        font-size: 0.7rem;
    }
}

@media (max-width: 400px) {
    .category-card {
        min-height: 70px;
    }
    
    .category-card .v-icon {
        font-size: 22px;
    }
    
    .category-card .text-caption {
        font-size: 0.65rem;
    }
}
</style>