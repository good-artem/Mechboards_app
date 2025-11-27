<template>
    <div class="product-card" @click="openProduct">
        <img :src="product.image" :alt="product.name" class="product-image">
        
        <!-- Нижняя информационная панель -->
        <div class="product-info">
            <div class="text-content">
                <div class="product-name">{{ product.name }}</div>
                <div class="product-price">{{ formatPrice(product.price) }}</div>
            </div>
            
            <!-- Скидка -->
            <div v-if="product.discount" class="product-discount">
                -{{ product.discount }}%
            </div>
            
            <!-- Кнопка добавления в корзину -->
            <button class="add-to-cart-btn" @click.stop="addToCart">
                <v-icon>mdi-cart-plus</v-icon>
            </button>
        </div>
    </div>
</template>

<script>
export default {
    name: 'ProductCard',
    props: {
        product: {
            type: Object,
            required: true
        }
    },
    methods: {
        formatPrice(price) {
            return new Intl.NumberFormat('ru-RU').format(price) + ' ₽'
        },
        openProduct() {
            this.$emit('product-click', this.product)
        },
        addToCart() {
            this.$emit('add-to-cart', this.product)
        }
    }
}
</script>

<style scoped>
.product-card {
    position: relative;
    width: 100%;
    aspect-ratio: 3/4;
    border-radius: 16px 16px 0 16px;
    overflow: hidden;
    cursor: pointer;
    background: var(--tg-theme-bg-color, #ffffff);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.product-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.product-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.product-info {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 25%;
    background: linear-gradient(
        to top, 
        rgba(0, 0, 0, 0.85) 0%, 
        rgba(0, 0, 0, 0.7) 50%, 
        transparent 100%
    );
    padding: 8px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.text-content {
    flex: 1;
    min-width: 0;
    margin-right: 8px;
}

.product-name {
    color: white;
    font-size: 0.8rem;
    font-weight: 500;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 2px;
}

.product-price {
    color: white;
    font-size: 0.9rem;
    font-weight: 600;
    white-space: nowrap;
}

.product-discount {
    position: absolute;
    top: -35px;
    left: 8px;
    background: #ff4444;
    color: white;
    padding: 4px 8px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
}

.add-to-cart-btn {
    position: absolute;
    bottom: 0;
    right: 0;
    width: 44px;
    height: 44px;
    background: var(--tg-theme-button-color, #2481cc);
    color: white;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    border-radius: 8px 0 0 0;
}

.add-to-cart-btn:hover {
    background: var(--tg-theme-button-color, #1a6fb3);
    transform: scale(1.05);
}

.add-to-cart-btn .v-icon {
    font-size: 20px;
}
</style>