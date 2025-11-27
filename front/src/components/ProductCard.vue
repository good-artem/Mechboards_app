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
import '@/assets/styles/components/product-card.css'

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
