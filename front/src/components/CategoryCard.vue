<template>
    <v-card class="category-card" elevation="2" @click="navigateToCategory">
        <v-card-text class="text-center d-flex flex-column justify-center align-center">
            <v-icon size="48" class="mb-3" color="primary">{{ getCategoryIcon(category) }}</v-icon>
            <div class="category-name">{{ category.name }}</div>
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
    width: 100%;
    min-height: 140px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 16px;
    background: var(--tg-theme-bg-color, #ffffff);
    border: 2px solid var(--tg-theme-hint-color, #e0e0e0);
    color: var(--tg-theme-text-color, #000000);
    overflow: hidden;
    margin: 0;
    padding: 0;
}

.category-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.2) !important;
    border-color: var(--tg-theme-button-color, #2481cc);
}

.category-card .v-card-text {
    color: var(--tg-theme-text-color, #000000) !important;
    text-align: center;
    padding: 20px 12px !important;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex-grow: 1;
}

.category-card .v-icon {
    color: var(--tg-theme-button-color, #2481cc) !important;
    margin-bottom: 12px;
    flex-shrink: 0;
}

.category-card .category-name {
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.2;
    color: var(--tg-theme-text-color, #000000);
    width: 100%;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    max-height: 2.4em;
    word-break: break-word;
}

/* Адаптация для маленьких экранов */
@media (max-width: 600px) {
    .category-card {
        min-height: 130px;
        border-radius: 14px;
    }
    
    .category-card .v-card-text {
        padding: 18px 10px !important;
    }
    
    .category-card .v-icon {
        font-size: 42px;
        margin-bottom: 10px;
    }
    
    .category-card .category-name {
        font-size: 0.95rem;
    }
}

@media (max-width: 400px) {
    .category-card {
        min-height: 120px;
        border-radius: 12px;
        border-width: 1px;
    }
    
    .category-card .v-icon {
        font-size: 38px;
        margin-bottom: 8px;
    }
    
    .category-card .category-name {
        font-size: 0.9rem;
    }
}

/* Для очень маленьких экранов */
@media (max-width: 360px) {
    .category-card {
        min-height: 110px;
    }
    
    .category-card .v-icon {
        font-size: 36px;
    }
    
    .category-card .category-name {
        font-size: 0.85rem;
    }
}
</style>