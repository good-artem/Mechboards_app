<template>
    <div>
        <!-- Новости показываем только в режиме категорий -->
        <NewsCarousel v-if="!showProducts" />
        
        <v-container :class="{'with-news': !showProducts, 'without-news': showProducts}">
            <!-- SearchBar с обработкой событий -->
            <SearchBar 
                @search="handleSearch"
                @clear-search="handleClearSearch"
                @product-selected="handleProductSelected"
            />

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
                                    @update:modelValue="applyFilters"
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
                                    @update:modelValue="applyFilters"
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
                                    @update:modelValue="applyFilters"
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
                                    @update:modelValue="applyFilters"
                                ></v-select>
                            </v-col>
                        </v-row>
                        <v-row v-if="hasActiveFilters" class="mt-2">
                            <v-col cols="12" class="text-center">
                                <v-btn 
                                    color="error" 
                                    variant="text" 
                                    size="small"
                                    @click="clearFilters"
                                >
                                    <v-icon left>mdi-filter-off</v-icon>
                                    Сбросить фильтры
                                </v-btn>
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
                        :key="category.category_id"
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
            <div v-else class="products-container">
                <!-- Информация о выбранной категории и поиске -->
                <div v-if="selectedCategory || searchQuery" class="mb-4">
                    <v-chip 
                        v-if="selectedCategory"
                        color="primary"
                        class="mr-2"
                        closable
                        @click:close="backToCategories"
                    >
                        {{ selectedCategory.name }}
                    </v-chip>
                    <v-chip 
                        v-if="searchQuery"
                        color="secondary"
                        closable
                        @click:close="clearSearch"
                    >
                        Поиск: "{{ searchQuery }}"
                    </v-chip>
                </div>

                <v-row>
                    <v-col 
                        v-for="product in filteredProducts" 
                        :key="product.product_id"
                        cols="6" 
                        sm="3"
                        class="pa-2"
                    >
                        <ProductCard 
                            :product="product"
                            @product-click="openProductDetail"
                            @add-to-cart="addToCart"
                            @show-message="showMessage"
                            @cart-updated="handleCartUpdate"
                        />
                    </v-col>
                </v-row>

                <!-- Сообщение если товаров нет -->
                <div v-if="filteredProducts.length === 0 && !loading" class="text-center pa-8">
                    <v-icon size="64" color="grey-lighten-1">mdi-package-variant</v-icon>
                    <div class="text-h6 mt-4">Товары не найдены</div>
                    <div class="text-body-1 mt-2">Попробуйте изменить параметры поиска или фильтрации</div>
                    <v-btn 
                        color="primary" 
                        class="mt-4"
                        @click="clearSearchAndFilters"
                    >
                        Сбросить фильтры
                    </v-btn>
                </div>

                <!-- Индикатор загрузки -->
                <div v-if="loading" class="text-center pa-8">
                    <v-progress-circular
                        indeterminate
                        color="primary"
                        size="64"
                    ></v-progress-circular>
                    <div class="text-body-1 mt-4">Загрузка товаров...</div>
                </div>
            </div>
            
            <!-- Детальная информация о товаре -->
            <v-dialog v-model="productDialog" max-width="400">
                <v-card v-if="selectedProduct">
                    <v-card-title class="d-flex justify-space-between align-center">
                        <span>{{ selectedProduct.name }}</span>
                        <v-btn icon @click="productDialog = false">
                            <v-icon>mdi-close</v-icon>
                        </v-btn>
                    </v-card-title>
                    <v-card-text>
                        <img 
                            :src="getProductImage(selectedProduct)" 
                            :alt="selectedProduct.name" 
                            style="width: 100%; border-radius: 8px;"
                        >
                        <div class="mt-4">
                            <p><strong>Цена:</strong> {{ formatPrice(selectedProduct.price) }}</p>
                            <p v-if="selectedProduct.description">
                                <strong>Описание:</strong> {{ selectedProduct.description }}
                            </p>
                            <p v-if="selectedProduct.stock_quantity !== undefined">
                                <strong>В наличии:</strong> 
                                <span :class="selectedProduct.stock_quantity > 0 ? 'success--text' : 'error--text'">
                                    {{ selectedProduct.stock_quantity }} шт.
                                </span>
                            </p>
                            <p v-if="selectedProduct.category">
                                <strong>Категория:</strong> {{ selectedProduct.category.name }}
                            </p>
                        </div>
                    </v-card-text>
                    <v-card-actions>
                        <v-btn 
                            color="primary" 
                            @click="addToCart(selectedProduct)"
                            :disabled="selectedProduct.stock_quantity === 0"
                            block
                        >
                            <v-icon left>mdi-cart-plus</v-icon>
                            Добавить в корзину
                        </v-btn>
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
import SearchBar from '@/components/SearchBar.vue'

import '@/assets/styles/components/catalog-view.css'

export default {
    name: 'CatalogView',
    components: {
        CategoryCard,
        ProductCard,
        NewsCarousel,
        SearchBar
    },
    data() {
        return {
            showProducts: false,
            selectedCategory: null,
            showFilters: false,
            sortBy: 'name',
            searchQuery: '',
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
            categories: [],
            products: [],
            loading: false,
            allProducts: [] // Все товары для локальной фильтрации
        }
    },
    async mounted() {
        await this.fetchCategories();
    },
    computed: {
        filteredProducts() {
            let filtered = [...this.products];
            
            // Применяем поиск если есть запрос
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                filtered = filtered.filter(product => 
                    product.name.toLowerCase().includes(query) ||
                    (product.description && product.description.toLowerCase().includes(query))
                );
            }
            
            // Применяем фильтры
            filtered = this.applyLocalFilters(filtered);
            
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
        },
        hasActiveFilters() {
            return Object.values(this.filters).some(filter => filter !== null);
        }
    },
    methods: {
        formatPrice(price) {
            return new Intl.NumberFormat('ru-RU').format(price) + ' ₽'
        },
        getProductImage(product) {
            if (product.images && product.images.length > 0) {
                if (Array.isArray(product.images)) {
                    return product.images[0];
                }
                try {
                    const parsedImages = JSON.parse(product.images);
                    if (Array.isArray(parsedImages) && parsedImages.length > 0) {
                        return parsedImages[0];
                    }
                } catch (e) {
                    console.warn('Cannot parse product images:', e);
                }
            }
            return 'https://via.placeholder.com/300x400/667eea/ffffff?text=No+Image';
        },
        async fetchCategories() {
            this.loading = true;
            try {
                const response = await fetch('/api/categories');
                if (response.ok) {
                    this.categories = await response.json();
                } else {
                    console.error('Ошибка загрузки категорий');
                    this.categories = this.getFallbackCategories();
                }
            } catch (error) {
                console.error('Ошибка:', error);
                this.categories = this.getFallbackCategories();
            }
            this.loading = false;
        },
        getFallbackCategories() {
            return [
                { category_id: 1, name: 'Весь каталог', icon: 'mdi-view-grid' },
                { category_id: 2, name: 'Скидки', icon: 'mdi-sale' },
                { category_id: 3, name: 'Механические клавиатуры', icon: 'mdi-keyboard' },
                { category_id: 4, name: 'БУ клавиатуры', icon: 'mdi-keyboard-return' },
                { category_id: 5, name: 'Свитчи', icon: 'mdi-circle-multiple' },
                { category_id: 6, name: 'Кейкапы', icon: 'mdi-checkbox-multiple-blank' },
                { category_id: 7, name: 'Стабилизаторы', icon: 'mdi-arrow-split-vertical' },
                { category_id: 8, name: 'Смазка и моддинг', icon: 'mdi-bottle-tonic' },
                { category_id: 9, name: 'Аксессуары', icon: 'mdi-cable-data' },
                { category_id: 10, name: 'Другое', icon: 'mdi-dots-horizontal' }
            ];
        },
        async onCategorySelected(category) {
            if (category.category_id === 1) { // "Весь каталог"
                this.selectedCategory = category;
                await this.fetchProducts();
                this.showProducts = true;
            } else {
                console.log('Selected category:', category.name);
                this.showMessage(`Категория "${category.name}" скоро будет доступна`);
            }
        },
        async fetchProducts(categoryId = null) {
            this.loading = true;
            try {
                let url = '/api/products';
                const params = new URLSearchParams();
                
                if (categoryId) {
                    params.append('category_id', categoryId);
                }
                
                if (this.searchQuery) {
                    params.append('q', this.searchQuery);
                }
                
                if (Object.keys(params).length > 0) {
                    url += `?${params.toString()}`;
                }
                
                const response = await fetch(url);
                if (response.ok) {
                    this.products = await response.json();
                    this.allProducts = [...this.products]; // Сохраняем для локальной фильтрации
                } else {
                    console.error('Ошибка загрузки товаров');
                    this.products = this.getFallbackProducts();
                    this.allProducts = [...this.products];
                }
            } catch (error) {
                console.error('Ошибка:', error);
                this.products = this.getFallbackProducts();
                this.allProducts = [...this.products];
            }
            this.loading = false;
        },
        getFallbackProducts() {
            return [
                {
                    product_id: 1,
                    name: 'Keychron K2',
                    price: 4500,
                    stock_quantity: 15,
                    images: ['https://via.placeholder.com/300x400/667eea/ffffff?text=Keychron+K2']
                },
                {
                    product_id: 2,
                    name: 'Gateron Yellow Switches',
                    price: 800,
                    stock_quantity: 50,
                    images: ['https://via.placeholder.com/300x400/764ba2/ffffff?text=Gateron+Yellow']
                },
                {
                    product_id: 3,
                    name: 'PBT Keycaps Set',
                    price: 1200,
                    stock_quantity: 25,
                    images: ['https://via.placeholder.com/300x400/f093fb/ffffff?text=PBT+Keycaps']
                },
                {
                    product_id: 4,
                    name: 'Стабилизаторы Cherry',
                    price: 400,
                    stock_quantity: 30,
                    images: ['https://via.placeholder.com/300x400/4facfe/ffffff?text=Cherry+Stabs']
                }
            ];
        },
        applyLocalFilters(products) {
            let filtered = [...products];
            
            // Фильтрация по ценовому диапазону
            if (this.filters.priceRange) {
                const [min, max] = this.parsePriceRange(this.filters.priceRange);
                filtered = filtered.filter(product => {
                    const price = product.price;
                    return (!min || price >= min) && (!max || price <= max);
                });
            }
            
            // Здесь можно добавить другие фильтры по необходимости
            
            return filtered;
        },
        parsePriceRange(priceRange) {
            switch (priceRange) {
                case 'До 2000 ₽':
                    return [0, 2000];
                case '2000-5000 ₽':
                    return [2000, 5000];
                case '5000-10000 ₽':
                    return [5000, 10000];
                case 'Выше 10000 ₽':
                    return [10000, null];
                default:
                    return [null, null];
            }
        },
        applyFilters() {
            // Применяем фильтры локально к уже загруженным товарам
            this.products = this.applyLocalFilters(this.allProducts);
        },
        clearFilters() {
            this.filters = {
                switchType: null,
                caseMaterial: null,
                layout: null,
                priceRange: null
            };
            this.products = [...this.allProducts]; // Восстанавливаем все товары
        },
        clearSearchAndFilters() {
            this.clearFilters();
            this.searchQuery = '';
            this.fetchProducts(this.selectedCategory?.category_id);
        },
        backToCategories() {
            this.showProducts = false;
            this.selectedCategory = null;
            this.showFilters = false;
            this.searchQuery = '';
            this.clearFilters();
        },
        openProductDetail(product) {
            this.selectedProduct = product;
            this.productDialog = true;
        },
        async addToCart(product) {
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
                if (!tg_user) {
                    this.showMessage('Ошибка: пользователь не найден');
                    return;
                }

                const response = await fetch('/api/cart/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        telegram_id: tg_user.id,
                        product_id: product.product_id,
                        quantity: 1
                    })
                });

                if (response.ok) {
                    this.showMessage(`Товар "${product.name}" добавлен в корзину`);
                    this.handleCartUpdate();
                } else {
                    const error = await response.json();
                    this.showMessage(`Ошибка: ${error.detail || 'Не удалось добавить в корзину'}`);
                }
            } catch (error) {
                console.error('Error adding to cart:', error);
                this.showMessage('Ошибка соединения');
            }
        },
        // Обработчики для SearchBar
        handleSearch(searchQuery) {
            this.searchQuery = searchQuery;
            if (this.showProducts) {
                this.fetchProducts(this.selectedCategory?.category_id);
            }
        },
        handleClearSearch() {
            this.searchQuery = '';
            if (this.showProducts) {
                this.fetchProducts(this.selectedCategory?.category_id);
            }
        },
        handleProductSelected(product) {
            this.openProductDetail(product);
        },
        handleCartUpdate() {
            this.$emit('cart-updated');
        },
        showMessage(message) {
            this.$emit('show-message', message);
        }
    }
}
</script>

