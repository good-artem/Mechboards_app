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
            
            <!-- Скидка (если будет в будущем) -->
            <div v-if="product.discount_percent" class="product-discount">
                -{{ product.discount_percent }}%
            </div>
            
            <!-- Кнопка добавления в корзину -->
            <button 
                class="add-to-cart-btn" 
                @click.stop="addToCart"
                :disabled="product.stock_quantity === 0 || addingToCart"
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
            return new Intl.NumberFormat('ru-RU').format(price) + ' ₽'
        },
        getProductImage(product) {
            // Обрабатываем поле images из бэкенда (JSON массив)
            if (product.images && product.images.length > 0) {
                // Если images - это массив URL
                if (Array.isArray(product.images)) {
                    return product.images[0];
                }
                // Если images - это JSON строка, пытаемся распарсить
                try {
                    const parsedImages = JSON.parse(product.images);
                    if (Array.isArray(parsedImages) && parsedImages.length > 0) {
                        return parsedImages[0];
                    }
                } catch (e) {
                    console.warn('Cannot parse product images:', e);
                }
            }
            
            // Fallback изображение
            return 'https://via.placeholder.com/300x400/667eea/ffffff?text=No+Image';
        },
        openProduct() {
            this.$emit('product-click', this.product)
        },
        async addToCart() {
    if (this.product.stock_quantity === 0) return;
    
    this.addingToCart = true;
    
    try {
        const { post, endpoints } = useApi();
        const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
        
        if (!tg_user) {
            this.$emit('show-message', 'Ошибка: пользователь не найден');
            return;
        }

        await post(endpoints.cart.add, {
            telegram_id: tg_user.id,
            product_id: this.product.product_id,
            quantity: 1
        });

        this.$emit('add-to-cart', this.product);
        this.$emit('show-message', `Товар "${this.product.name}" добавлен в корзину`);
        this.$emit('cart-updated');
        
    } catch (error) {
        console.error('Error adding to cart:', error);
        this.$emit('show-message', 'Ошибка: ' + (error.message || 'Не удалось добавить в корзину'));
    } finally {
        this.addingToCart = false;
    }
}
    }
}
</script>