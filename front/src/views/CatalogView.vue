<template>
    <div>
        <!-- Новости показываем только в режиме категорий -->
        <NewsCarousel v-if="!showProducts" />
        
        <v-container :class="{'with-news': !showProducts, 'without-news': showProducts}">
            <!-- Панель фильтров и сортировки (только при просмотре товаров) -->
            <div v-if="showProducts" class="filters-bar">
                <v-card class="pa-2" elevation="1" style="background: var(--tg-theme-bg-color, #ffffff);">
                    <v-row align="center" no-gutters>
                        <v-col cols="6">
                            <v-select
                                v-model="sortBy"
                                :items="sortOptions"
                                label="Сортировка"
                                density="compact"
                                variant="outlined"
                                hide-details
                                class="telegram-select"
                            ></v-select>
                        </v-col>
                        <v-col cols="6" class="text-right">
                            <v-btn 
                                icon 
                                @click="showFilters = !showFilters"
                                size="small"
                                class="filter-btn"
                            >
                                <v-icon>mdi-filter</v-icon>
                            </v-btn>
                            <v-btn 
                                icon 
                                @click="backToCategories"
                                size="small"
                                class="back-btn"
                            >
                                <v-icon>mdi-arrow-left</v-icon>
                            </v-btn>
                        </v-col>
                    </v-row>
                </v-card>
            </div>

            <!-- Расширяемая панель фильтров -->
            <v-expand-transition>
                <div v-if="showFilters && showProducts" class="filters-panel">
                    <v-card class="pa-3" elevation="1">
                        <v-row>
                            <v-col cols="6">
                                <v-select
                                    v-model="filters.switchType"
                                    :items="switchTypes"
                                    label="Тип переключателя"
                                    density="compact"
                                    variant="outlined"
                                    hide-details
                                ></v-select>
                            </v-col>
                            <v-col cols="6">
                                <v-select
                                    v-model="filters.caseMaterial"
                                    :items="caseMaterials"
                                    label="Материал корпуса"
                                    density="compact"
                                    variant="outlined"
                                    hide-details
                                ></v-select>
                            </v-col>
                            <v-col cols="6">
                                <v-select
                                    v-model="filters.layout"
                                    :items="layouts"
                                    label="Раскладка"
                                    density="compact"
                                    variant="outlined"
                                    hide-details
                                ></v-select>
                            </v-col>
                            <v-col cols="6">
                                <v-select
                                    v-model="filters.priceRange"
                                    :items="priceRanges"
                                    label="Ценовой диапазон"
                                    density="compact"
                                    variant="outlined"
                                    hide-details
                                ></v-select>
                            </v-col>
                        </v-row>
                    </v-card>
                </div>
            </v-expand-transition>

            <!-- Категории (показываются по умолчанию) -->
            <div v-if="!showProducts">
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
            </div>

            <!-- Товары (показываются при выборе категории) -->
            <div v-else>
                <v-row>
                    <v-col 
                        v-for="product in filteredProducts" 
                        :key="product.id"
                        cols="6" 
                        sm="3"
                        class="pa-2"
                    >
                        <ProductCard 
                            :product="product"
                            @product-click="openProductDetail"
                            @add-to-cart="addToCart"
                        />
                    </v-col>
                </v-row>
            </div>
            
            <!-- Детальная информация о товаре -->
            <v-dialog v-model="productDialog" max-width="400">
                <v-card v-if="selectedProduct">
                    <v-card-title>{{ selectedProduct.name }}</v-card-title>
                    <v-card-text>
                        <img :src="selectedProduct.image" :alt="selectedProduct.name" style="width: 100%; border-radius: 8px;">
                        <div class="mt-4">
                            <p>Цена: {{ selectedProduct.price }} ₽</p>
                            <p v-if="selectedProduct.description">{{ selectedProduct.description }}</p>
                        </div>
                    </v-card-text>
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn color="primary" @click="productDialog = false">Закрыть</v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
        </v-container>
    </div>
</template>

<script>
import CategoryCard from '@/components/CategoryCard.vue'
import ProductCard from '@/components/ProductCard.vue'
import NewsCarousel from '@/components/NewsCarousel.vue'

export default {
    name: 'CatalogView',
    components: {
        CategoryCard,
        ProductCard,
        NewsCarousel
    },
    data() {
        return {
            showProducts: false,
            selectedCategory: null,
            showFilters: false,
            sortBy: 'name',
            sortOptions: [
                { title: 'По названию', value: 'name' },
                { title: 'По цене (возр.)', value: 'price_asc' },
                { title: 'По цене (убыв.)', value: 'price_desc' },
                { title: 'По популярности', value: 'popular' }
            ],
            filters: {
                switchType: null,
                caseMaterial: null,
                layout: null,
                priceRange: null
            },
            switchTypes: ['Механические', 'Мембранные', 'Оптические'],
            caseMaterials: ['Пластик', 'Алюминий', 'Дерево', 'Сталь'],
            layouts: ['60%', '75%', 'TKL', 'Полная'],
            priceRanges: [
                'До 2000 ₽',
                '2000-5000 ₽', 
                '5000-10000 ₽',
                'Выше 10000 ₽'
            ],
            productDialog: false,
            selectedProduct: null,
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
            ],
            products: [
                {
                    id: 1,
                    name: 'Mechanical Keyboard Pro',
                    price: 4500,
                    discount: 15,
                    image: 'https://via.placeholder.com/300x400/667eea/ffffff?text=Keyboard+1',
                    category: 'all'
                },
                {
                    id: 2,
                    name: 'Gaming Keyboard RGB',
                    price: 3200,
                    image: 'https://via.placeholder.com/300x400/764ba2/ffffff?text=Keyboard+2',
                    category: 'all'
                },
                {
                    id: 3,
                    name: 'Compact 60% Keyboard',
                    price: 2800,
                    discount: 10,
                    image: 'https://via.placeholder.com/300x400/f093fb/ffffff?text=Keyboard+3',
                    category: 'all'
                },
                {
                    id: 4,
                    name: 'Wireless Mechanical',
                    price: 5200,
                    image: 'https://via.placeholder.com/300x400/4facfe/ffffff?text=Keyboard+4',
                    category: 'all'
                }
            ]
        }
    },
    computed: {
        filteredProducts() {
            let filtered = [...this.products];
            
            // Сортировка
            switch (this.sortBy) {
                case 'price_asc':
                    filtered.sort((a, b) => a.price - b.price);
                    break;
                case 'price_desc':
                    filtered.sort((a, b) => b.price - a.price);
                    break;
                case 'name':
                    filtered.sort((a, b) => a.name.localeCompare(b.name));
                    break;
                case 'popular':
                    // Здесь можно добавить логику популярности
                    break;
            }
            
            return filtered;
        }
    },
    methods: {
        onCategorySelected(category) {
            if (category.id === 1) { // "Весь каталог"
                this.selectedCategory = category;
                this.showProducts = true;
            } else {
                console.log('Selected category:', category.name);
                // Для других категорий показываем сообщение
                this.$emit('show-message', `Категория "${category.name}" скоро будет доступна`);
            }
        },
        backToCategories() {
            this.showProducts = false;
            this.selectedCategory = null;
            this.showFilters = false;
        },
        openProductDetail(product) {
            this.selectedProduct = product;
            this.productDialog = true;
        },
        addToCart(product) {
            console.log('Adding to cart:', product.name);
            this.$emit('show-message', `Товар "${product.name}" добавлен в корзину`);
        }
    }
}
</script>

<style scoped>
.with-news {
  margin-top: 150px;
}

.without-news {
  margin-top: 0;
}

.filters-bar {
    position: sticky;
    top: 0;
    z-index: 90;
    background: var(--tg-theme-bg-color, #ffffff);
    margin: 0 -16px;
    padding: 0 16px;
    border-bottom: 1px solid var(--tg-theme-hint-color, #e0e0e0);
}

.filters-panel {
    position: sticky;
    top: 60px;
    z-index: 89;
    margin: 0 -16px;
    padding: 0 16px;
    background: var(--tg-theme-bg-color, #ffffff);
}

.categories-grid {
    max-height: calc(100vh - 300px);
    overflow-y: auto;
}

/* Стили для селектов в фильтрах */
:deep(.v-select .v-field) {
  background: var(--tg-theme-secondary-bg-color, #f5f5f5) !important;
  color: var(--tg-theme-text-color, #000000) !important;
}

:deep(.v-select .v-field__input) {
  color: var(--tg-theme-text-color, #000000) !important;
}

:deep(.v-select .v-label) {
  color: var(--tg-theme-text-color, #000000) !important;
}

.filter-btn, .back-btn {
    color: var(--tg-theme-button-color, #2481cc) !important;
}
</style>