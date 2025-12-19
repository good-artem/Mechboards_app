<template>
    <div>
        <!-- Новости показываем только в режиме категорий -->
        <NewsCarousel v-if="!showProducts" />
        
        <v-container :class="{'with-news': !showProducts, 'without-news': showProducts}">
            <!-- SearchBar с обработкой событий -->
            <SearchBar />

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
                        v-if="selectedCategory && selectedCategory.category_id"
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
                    
                    <!-- Галерея изображений -->
                    <div v-if="productImages.length > 0">
                        <v-carousel 
                            v-model="carouselIndex" 
                            height="300" 
                            show-arrows 
                            hide-delimiter-background
                            class="product-gallery"
                        >
                            <v-carousel-item
                                v-for="(image, index) in productImages"
                                :key="index"
                                :src="image"
                                contain
                            >
                            </v-carousel-item>
                        </v-carousel>
                        
                    </div>
                    
                    <div v-else class="text-center pa-4">
                        <v-icon size="100" color="grey-lighten-2">mdi-image-off</v-icon>
                        <div class="text-body-2 mt-2">Нет изображений</div>
                    </div>
                    
                    <v-card-text>
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
                            size="large"
                        >
                            <v-icon left>mdi-cart-plus</v-icon>
                            Добавить в корзину
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
            
            <!-- Тестовая кнопка поиска (временно для отладки) -->
            <v-btn 
                v-if="$route.name === 'catalog' && !showProducts"
                @click="testSearch"
                color="secondary"
                class="ma-2"
                small
            >
                Тест поиска
            </v-btn>
        </v-container>
    </div>
</template>

<script>
import CategoryCard from '@/components/CategoryCard.vue'
import ProductCard from '@/components/ProductCard.vue'
import NewsCarousel from '@/components/NewsCarousel.vue'
import SearchBar from '@/components/SearchBar.vue'

import '@/assets/styles/components/catalog-view.css'
import { useApi } from '@/composables/useApi'

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
            carouselIndex: 0,
            categories: [],
            products: [],
            loading: false,
            allProducts: [],
            snackbar: false,
            snackbarMessage: '',
            snackbarColor: 'success'
        }
    },
    async mounted() {
        await this.fetchCategories();

        if (this.$route.query.search) {
            this.searchQuery = this.$route.query.search;
            await this.fetchProductsForSearch(this.searchQuery);
        }
        
        // Подписываемся на события поиска
        this.$root.$on('search-results', this.handleSearchResults);
        this.$root.$on('clear-search', this.handleClearSearch);
    },
    beforeUnmount() {
        // Отписываемся от событий
        this.$root.$off('search-results', this.handleSearchResults);
        this.$root.$off('clear-search', this.handleClearSearch);
    },
    computed: {
        productImages() {
            if (!this.selectedProduct || !this.selectedProduct.images) {
                return [];
            }
            
            try {
                let images = this.selectedProduct.images;
                
                if (typeof images === 'string') {
                    images = JSON.parse(images);
                }
                
                if (Array.isArray(images)) {
                    return images.map(img => {
                        let imagePath = img;
                        
                        imagePath = imagePath.replace(/\\/g, '/');
                        
                        if (imagePath.startsWith('http')) {
                            return imagePath;
                        }
                        
                        if (imagePath.startsWith('assets/') || imagePath.startsWith('/assets/')) {
                            if (imagePath.startsWith('/')) {
                                imagePath = imagePath.substring(1);
                            }
                            const baseUrl = this.getApiBaseUrl();
                            return `${baseUrl}/${imagePath}`;
                        }
                        
                        return `${this.getApiBaseUrl()}/${imagePath}`;
                    });
                }
            } catch (e) {
                console.warn('Cannot parse product images:', e);
            }
            
            return [];
        },
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
        testSearch() {
            console.log('🧪 Тестирование поиска...');
            this.searchQuery = 'key';
            this.fetchProductsForSearch('key');
        },
        getApiBaseUrl() {
            if (import.meta.env.VITE_API_BASE_URL) {
                return import.meta.env.VITE_API_BASE_URL;
            }
            
            if (import.meta.env.MODE === 'development') {
                return 'http://localhost:8000';
            } else {
                return 'https://verbose-space-orbit-x45v4q7q6wwf6g94-8000.app.github.dev';
            }
        },
        showMessage(message, type = 'success') {
            this.snackbarMessage = message;
            this.snackbarColor = type === 'error' ? 'error' : 'success';
            this.snackbar = true;
            
            setTimeout(() => {
                this.snackbar = false;
            }, 3000);
        },
        formatPrice(price) {
            return new Intl.NumberFormat('ru-BY', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(price) + ' р.';
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
            const { get, endpoints, error } = useApi();
            
            this.loading = true;
            try {
                const categories = await get(endpoints.categories.list);
                this.categories = categories;
                console.log('📦 Загружены категории:', categories);
            } catch (err) {
                console.error('❌ Ошибка загрузки категорий:', error.value);
                this.categories = this.getFallbackCategories();
            }
            this.loading = false;
        },
        async fetchProducts(categoryId = null) {
            const baseUrl = this.getApiBaseUrl();
            let url = `${baseUrl}/api/products`;
            
            if (categoryId) {
                url += `?category_id=${categoryId}`;
            }
            
            this.loading = true;
            try {
                const response = await fetch(url);
                
                if (response.ok) {
                    const products = await response.json();
                    this.products = products;
                    this.allProducts = [...products];
                    console.log('📦 Загружены товары:', products);
                    
                    if (products.length === 0) {
                        this.showMessage('Товаров в этой категории пока нет', 'info');
                    }
                } else {
                    console.error('❌ Ошибка загрузки товаров:', response.status);
                    this.products = this.getFallbackProducts();
                    this.allProducts = [...this.products];
                }
            } catch (error) {
                console.error('❌ Ошибка сети:', error);
                this.products = this.getFallbackProducts();
                this.allProducts = [...this.products];
            }
            this.loading = false;
        },
        getFallbackCategories() {
            return [
                { category_id: 1, name: 'Весь каталог', icon: 'mdi-view-grid' },
                { category_id: 2, name: 'Проблема с загрузкой', icon: 'mdi-sale' },];
        },
        async onCategorySelected(category) {
            console.log('Selected category:', category.name);
            this.selectedCategory = category;
            this.searchQuery = '';
            
            if (category.category_id === 1) {
                await this.fetchProducts();
            } else {
                await this.fetchProducts(category.category_id);
            }
            
            this.showProducts = true;
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
            
            if (this.filters.priceRange) {
                const [min, max] = this.parsePriceRange(this.filters.priceRange);
                filtered = filtered.filter(product => {
                    const price = product.price;
                    return (!min || price >= min) && (!max || price <= max);
                });
            }
            
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
            this.products = this.applyLocalFilters(this.allProducts);
        },
        clearFilters() {
            this.filters = {
                switchType: null,
                caseMaterial: null,
                layout: null,
                priceRange: null
            };
            this.products = [...this.allProducts];
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
                const { post, endpoints } = useApi();
                let telegramId;
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                
                if (tg_user) {
                    telegramId = tg_user.id;
                } else {
                    telegramId = 391622124;
                }

                await post(endpoints.cart.add, {
                    telegram_id: telegramId,
                    product_id: product.product_id,
                    quantity: 1
                });
                
                this.showMessage(`Товар "${product.name}" добавлен в корзину`);
                this.$root.$emit('cart-updated');
                this.productDialog = false;
                
            } catch (error) {
                console.error('Error adding to cart:', error);
                this.showMessage('Ошибка добавления в корзину', 'error');
            }
        },
        handleSearchResults(searchData) {
            console.log('📦 Обработка результатов поиска:', searchData);
            
            if (!searchData || !searchData.results || searchData.results.length === 0) {
                this.products = [];
                this.allProducts = [];
                this.showProducts = true;
                this.selectedCategory = { 
                    name: `Поиск: "${searchData.query}" - ничего не найдено`,
                    category_id: null 
                };
                this.showMessage('Товары не найдены', 'info');
                return;
            }
            
            // Устанавливаем результаты поиска как текущий список товаров
            this.products = searchData.results;
            this.allProducts = [...searchData.results];
            this.searchQuery = searchData.query;
            this.showProducts = true;
            this.selectedCategory = { 
                name: `Результаты поиска: "${searchData.query}"`,
                category_id: null 
            };
            console.log('✅ Товары обновлены для поиска:', this.products.length);
        },
        handleClearSearch() {
            this.searchQuery = '';
            if (this.selectedCategory?.category_id) {
                // Если есть выбранная категория - возвращаемся к ней
                this.fetchProducts(this.selectedCategory.category_id);
            } else {
                // Иначе возвращаемся к списку категорий
                this.backToCategories();
            }
        },
        async fetchProductsForSearch(searchQuery) {
            this.loading = true;
            try {
                // Используйте простой поиск вместо products/search
                const { get } = useApi();
                const products = await get('/api/simple-search', {
                    params: {
                        q: searchQuery,
                        limit: 50
                    }
                });
                
                this.products = products;
                this.allProducts = [...products];
                this.showProducts = true;
                this.searchQuery = searchQuery;
                this.selectedCategory = { 
                    name: `Результаты поиска: "${searchQuery}"`,
                    category_id: null 
                };
            } catch (error) {
                console.error('❌ Ошибка поиска:', error);
                this.showMessage('Ошибка подключения к серверу', 'error');
            } finally {
                this.loading = false;
            }
        },
        handleClearSearch() {
            this.searchQuery = '';
            if (this.showProducts && this.selectedCategory?.category_id) {
                this.fetchProducts(this.selectedCategory.category_id);
            } else {
                this.backToCategories();
            }
        },
        showAllResults(searchData) {
            if (searchData && searchData.results) {
                this.products = searchData.results;
                this.allProducts = [...searchData.results];
                this.searchQuery = searchData.query;
                this.showProducts = true;
                this.selectedCategory = { 
                    name: `Все результаты: "${searchData.query}"`,
                    category_id: null 
                };
            }
        },
        handleCartUpdate() {
            this.$root.$emit('cart-updated');
        }
    }
}
</script>