<template>
    <div class="product-card" @click="openProduct">
        <img :src="getProductImage(product)" :alt="product.name" class="product-image">
        
        <!-- Нижняя информационная панель -->
        <div class="product-info">
            <div class="text-content">
                <div class="product-name">{{ product.name }}</div>
                <div class="product-price">{{ formatPrice(product.price) }}</div>
                <div v-if="product.stock_quantity === 0" class="out-of-stock">
                    Нет в наличии
                </div>
            </div>
            
            <!-- Кнопка добавления в корзину -->
            <button 
                class="add-to-cart-btn" 
                @click.stop="addToCart"
                :disabled="product.stock_quantity === 0 || addingToCart"
                :title="product.stock_quantity === 0 ? 'Нет в наличии' : 'Добавить в корзину'"
            >
                <v-icon v-if="!addingToCart">mdi-cart-plus</v-icon>
                <v-progress-circular 
                    v-else 
                    indeterminate 
                    size="20" 
                    width="2"
                    color="white"
                ></v-progress-circular>
            </button>
        </div>
    </div>
</template>

<script>
import '@/assets/styles/components/product-card.css'

export default {
    name: 'ProductCard',
    props: {
        product: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            addingToCart: false
        }
    },
    methods: {
        formatPrice(price) {
            return new Intl.NumberFormat('ru-BY', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(price) + ' р.';
        },
        
        getProductImage(product) {
            console.log('🖼️ Product images data:', product.images);
            
            if (!product.images) {
                return this.getFallbackImage(product.name);
            }
            
            try {
                let images = product.images;
                
                // Если это строка JSON
                if (typeof images === 'string') {
                    try {
                        images = JSON.parse(images);
                    } catch (e) {
                        console.warn('❌ Cannot parse images JSON, using as is:', e);
                        // Попробуем как обычную строку
                        if (images.startsWith('[') && images.endsWith(']')) {
                            images = images.slice(1, -1).split(',').map(img => img.trim().replace(/['"]/g, ''));
                        } else {
                            images = [images];
                        }
                    }
                }
                
                // Если массив и есть элементы
                if (Array.isArray(images) && images.length > 0) {
                    let imagePath = images[0];
                    
                    // Убираем возможные обратные слеши
                    imagePath = imagePath.replace(/\\/g, '/');
                    
                    // Если путь уже полный URL
                    if (imagePath.startsWith('http')) {
                        return imagePath;
                    }
                    
                    // Если путь относительный
                    if (imagePath.startsWith('assets/') || imagePath.startsWith('/assets/')) {
                        // Убираем начальный слеш если есть
                        if (imagePath.startsWith('/')) {
                            imagePath = imagePath.substring(1);
                        }
                        // Базовый URL
                        const baseUrl = this.getApiBaseUrl();
                        return `${baseUrl}/${imagePath}`;
                    }
                    
                    // Любой другой путь
                    return `${this.getApiBaseUrl()}/${imagePath}`;
                }
            } catch (e) {
                console.error('❌ Error processing image:', e);
            }
            
            return this.getFallbackImage(product.name);
        },
        
        getFallbackImage(productName) {
        const encodedName = encodeURIComponent(productName);
        return `https://via.placeholder.com/300x400/667eea/ffffff?text=${encodedName}`;
        },
        openProduct() {
            this.$emit('product-click', this.product)
        },
        
        async addToCart() {
            if (this.product.stock_quantity === 0) {
                console.log('❌ Product out of stock');
                return;
            }
            
            this.addingToCart = true;
            console.log('🔄 Adding to cart:', this.product.product_id);
            
            try {
                // Получаем пользователя Telegram или используем тестовый ID
                let telegramId;
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                
                if (tg_user) {
                    telegramId = tg_user.id;
                } else {
                    // Для тестирования без Telegram
                    console.warn('⚠️ Telegram user not found, using test ID');
                    telegramId = 391622124;
                }

                // Используем прямой fetch для избежания проблем с авторизацией
                const baseUrl = this.getApiBaseUrl();
                const addToCartUrl = `${baseUrl}/api/cart/add`;
                
                console.log('📤 Sending request to:', addToCartUrl);
                console.log('📤 Request body:', {
                    telegram_id: telegramId,
                    product_id: this.product.product_id,
                    quantity: 1
                });

                const response = await fetch(addToCartUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        telegram_id: telegramId,
                        product_id: this.product.product_id,
                        quantity: 1
                    })
                });

                console.log('📥 Response status:', response.status);
                
                if (response.ok) {
                    const result = await response.json();
                    console.log('✅ Added to cart:', result);
                    
                    // Отправляем события
                    this.$emit('add-to-cart', this.product);
                    this.showMessage(`✅ "${this.product.name}" добавлен в корзину`);
                    
                    // Триггерим обновление навбара
                    if (window.updateCartCount) {
                        window.updateCartCount();
                    }
                    this.$root.$emit('cart-updated');
                    
                } else {
                    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
                    console.error('❌ Error response:', error);
                    this.showMessage(`❌ Ошибка: ${error.detail || 'Не удалось добавить в корзину'}`);
                }
            } catch (error) {
                console.error('❌ Network error:', error);
                this.showMessage('❌ Ошибка соединения с сервером');
            } finally {
                this.addingToCart = false;
            }
        },
        
        getApiBaseUrl() {
            // Проверяем переменные окружения
            if (import.meta.env.VITE_API_BASE_URL) {
                return import.meta.env.VITE_API_BASE_URL;
            }
            
            // Определяем среду
            if (import.meta.env.MODE === 'development') {
                return 'http://localhost:8000';
            } else {
                return 'https://verbose-space-orbit-x45v4q7q6wwf6g94-8000.app.github.dev';
            }
        },
        
        showMessage(message) {
            // Используем родительский компонент для показа сообщений
            if (this.$parent && this.$parent.showMessage) {
                this.$parent.showMessage(message);
            } else if (this.$root && this.$root.showMessage) {
                this.$root.showMessage(message);
            } else {
                console.log('Message:', message);
            }
        }
    }
}
</script>