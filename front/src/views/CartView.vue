<template>
    <v-container class="cart-container">
        <v-row>
            <v-col cols="12">
                <v-card class="cart-card pa-3" elevation="2">
                    <v-card-title class="d-flex align-center cart-title pa-3">
                        <v-icon color="primary" class="mr-2">mdi-cart</v-icon>
                        Корзина
                        <v-spacer></v-spacer>
                        <v-chip color="primary" v-if="cartData.items && cartData.items.length > 0">
                            {{ cartData.items.length }} товар(ов)
                        </v-chip>
                    </v-card-title>

                    <!-- Пустая корзина -->
                    <div v-if="!cartData.items || cartData.items.length === 0" class="empty-cart text-center pa-6">
                        <v-icon size="64" color="grey-lighten-1">mdi-cart-outline</v-icon>
                        <div class="text-h6 mt-4">Корзина пуста</div>
                        <div class="text-body-1 mt-2">Добавьте товары из каталога</div>
                        <v-btn 
                            color="primary" 
                            class="mt-4"
                            @click="$router.push('/catalog')"
                        >
                            Перейти в каталог
                        </v-btn>
                    </div>

                    <!-- Список товаров в корзине -->
                    <div v-else>
                        <v-list lines="two" class="cart-list pa-0">
                            <v-list-item
                                v-for="item in cartData.items"
                                :key="item.cart_item_id"
                                class="cart-item pa-3"
                            >
                                <template v-slot:prepend>
                                    <v-avatar rounded="lg" size="50" class="cart-item-image mr-3">
                                        <img 
                                            :src="getProductImage(item.product)" 
                                            :alt="item.product.name"
                                            style="object-fit: cover; width: 100%; height: 100%;"
                                        >
                                    </v-avatar>
                                </template>

                                <div class="cart-item-content">
                                    <div class="cart-item-title font-weight-medium mb-1">
                                        {{ item.product.name }}
                                    </div>
                                    
                                    <div class="cart-item-description text-caption text-grey mb-2 line-clamp-2">
                                        {{ item.product.description || 'Нет описания' }}
                                    </div>
                                    
                                    <div class="cart-item-subtitle text-body-2">
                                        {{ formatPrice(item.product.price) }} × {{ item.quantity }} = 
                                        <span class="font-weight-bold primary--text">{{ formatPrice(item.subtotal) }}</span>
                                    </div>
                                </div>

                                <template v-slot:append>
                                    <div class="d-flex flex-column align-center cart-item-actions">
                                        <!-- Управление количеством -->
                                        <div class="quantity-controls d-flex align-center mb-2">
                                            <v-btn 
                                                icon 
                                                size="x-small"
                                                :disabled="item.quantity <= 1 || updatingItemId === item.cart_item_id"
                                                @click="updateQuantity(item, item.quantity - 1)"
                                                class="quantity-btn"
                                                density="comfortable"
                                            >
                                                <v-icon size="16">mdi-minus</v-icon>
                                            </v-btn>
                                            
                                            <span class="mx-2 quantity-display text-body-2 font-weight-medium">{{ item.quantity }}</span>
                                            
                                            <v-btn 
                                                icon 
                                                size="x-small"
                                                :disabled="item.quantity >= item.product.stock_quantity || updatingItemId === item.cart_item_id"
                                                @click="updateQuantity(item, item.quantity + 1)"
                                                class="quantity-btn"
                                                density="comfortable"
                                            >
                                                <v-icon size="16">mdi-plus</v-icon>
                                            </v-btn>
                                        </div>

                                        <!-- Кнопка удаления -->
                                        <v-btn 
                                            icon 
                                            color="error" 
                                            size="x-small"
                                            @click="removeFromCart(item)"
                                            :loading="removingItemId === item.cart_item_id"
                                            class="remove-btn"
                                            density="comfortable"
                                        >
                                            <v-icon size="18">mdi-delete-outline</v-icon>
                                        </v-btn>
                                    </div>
                                </template>
                            </v-list-item>
                        </v-list>

                        <!-- Итого и кнопка оформления -->
                        <v-card class="mt-3 pa-3 summary-card" elevation="1">
                            <v-row align="center" class="pa-2">
                                <v-col cols="12" sm="6" class="pa-2">
                                    <div class="text-h6 font-weight-medium">Итого:</div>
                                    <div class="text-h4 font-weight-bold primary--text total-price">
                                        {{ formatPrice(cartData.total) }}
                                    </div>
                                </v-col>
                                <v-col cols="12" sm="6" class="pa-2 text-sm-right">
                                    <v-btn 
                                        color="primary" 
                                        size="x-large"
                                        @click="createOrder"
                                        :loading="creatingOrder"
                                        :disabled="cartData.items.length === 0"
                                        class="checkout-btn w-100"
                                        block
                                    >
                                        <span class="checkout-text">Оформить заказ</span>
                                        <v-icon right>mdi-arrow-right</v-icon>
                                    </v-btn>
                                </v-col>
                            </v-row>
                        </v-card>
                    </div>
                </v-card>
            </v-col>
        </v-row>

        <!-- Диалог оформления заказа -->
        <v-dialog v-model="orderDialog" max-width="500" class="order-dialog">
            <v-card>
                <v-card-title class="order-dialog-title pa-4">
                    <v-icon class="mr-2">mdi-checkbox-marked-circle</v-icon>
                    Оформление заказа
                </v-card-title>
                <v-card-text class="order-dialog-content pa-4">
                    <v-text-field
                        v-model="orderData.shipping_address"
                        label="Адрес доставки"
                        placeholder="Введите ваш адрес"
                        variant="outlined"
                        class="mb-3"
                        required
                        density="comfortable"
                    ></v-text-field>
                    
                    <v-select
                        v-model="orderData.shipping_method"
                        :items="shippingMethods"
                        label="Способ доставки"
                        variant="outlined"
                        class="mb-3"
                        required
                        density="comfortable"
                    ></v-select>

                    <v-textarea
                        v-model="orderData.customer_notes"
                        label="Комментарий к заказу"
                        placeholder="Дополнительные пожелания..."
                        variant="outlined"
                        rows="2"
                        class="mb-3"
                        no-resize
                        density="comfortable"
                    ></v-textarea>
                    
                    <div class="order-summary pa-3 mb-3 rounded-lg" style="background-color: #f5f5f5;">
                        <div class="text-subtitle-1 font-weight-bold mb-2">Сумма заказа:</div>
                        <div class="text-h5 font-weight-bold primary--text">
                            {{ formatPrice(cartData.total) }}
                        </div>
                    </div>
                </v-card-text>
                <v-card-actions class="order-dialog-actions pa-4">
                    <v-spacer></v-spacer>
                    <v-btn color="grey" @click="orderDialog = false" variant="text" size="large">Отмена</v-btn>
                    <v-btn 
                        color="primary" 
                        @click="confirmOrder"
                        :loading="creatingOrder"
                        :disabled="!orderData.shipping_address || !orderData.shipping_method"
                        class="confirm-order-btn"
                        size="large"
                    >
                        Подтвердить заказ
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-container>
</template>

<script>
import '@/assets/styles/components/cart-view.css'
import '@/assets/styles/components/product-gallery.css'

export default {
    name: 'CartView',
    data() {
        return {
            cartData: {
                items: [],
                total: 0
            },
            orderDialog: false,
            creatingOrder: false,
            orderData: {
                shipping_method: '',
                shipping_address: '',
                customer_notes: ''
            },
            shippingMethods: [
                'Самовывоз',
                'Яндекс доставка',
                'Белпочта',
                'Европочта',
                'СДЭК'
            ],
            updatingItemId: null,
            removingItemId: null,
            loading: false,
            userProfile: null
        }
    },
    async mounted() {
        await this.fetchCart();
        await this.loadUserProfile();
    },
    methods: {
        formatPrice(price) {
            return new Intl.NumberFormat('ru-BY', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(price) + ' ₽';
        },
        
        getProductImage(product) {
            if (product.images) {
                try {
                    let images = product.images;
                    
                    if (typeof images === 'string') {
                        images = JSON.parse(images);
                    }
                    
                    if (Array.isArray(images) && images.length > 0) {
                        let imagePath = images[0];
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
                    }
                } catch (e) {
                    console.warn('Cannot parse product images:', e);
                }
            }
            return 'https://via.placeholder.com/100x100/667eea/ffffff?text=No+Image';
        },
        
        getApiBaseUrl() {
            if (import.meta.env.VITE_API_BASE_URL) {
                return import.meta.env.VITE_API_BASE_URL;
            }
            
            const hostname = window.location.hostname;
            if (hostname.includes('github.dev')) {
                return 'https://verbose-space-orbit-x45v4q7q6wwf6g94-8000.app.github.dev';
            } else if (hostname === 'localhost' || hostname === '127.0.0.1') {
                return 'http://localhost:8000';
            } else {
                return window.location.origin;
            }
        },
        
        formatPrice(price) {
            return new Intl.NumberFormat('ru-BY', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(price) + ' р.';
        },
        
        getProductImage(product) {
            if (product.images) {
                try {
                    // Если images это строка JSON
                    if (typeof product.images === 'string') {
                        const parsedImages = JSON.parse(product.images);
                        if (Array.isArray(parsedImages) && parsedImages.length > 0) {
                            return parsedImages[0];
                        }
                    }
                    // Если images это массив
                    if (Array.isArray(product.images) && product.images.length > 0) {
                        return product.images[0];
                    }
                } catch (e) {
                    console.warn('Cannot parse product images:', e);
                }
            }
            return 'https://via.placeholder.com/300x400/667eea/ffffff?text=No+Image';
        },
        
        async fetchCart() {
            this.loading = true;
            try {
                const { get, endpoints } = useApi();
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
                
                if (!tg_user) {
                    console.error('❌ Telegram user not found');
                    this.$emit('show-message', 'Ошибка: пользователь не найден');
                    return;
                }

                console.log('🔄 Fetching cart for user:', tg_user.id);
                this.cartData = await get(endpoints.cart.get(tg_user.id));
                console.log('✅ Cart data loaded:', this.cartData);
                
            } catch (error) {
                console.error('❌ Error loading cart:', error);
                this.$emit('show-message', 'Ошибка загрузки корзины');
            }
            this.loading = false;
        },
        
        async updateQuantity(item, newQuantity) {
            if (newQuantity < 1 || newQuantity > item.product.stock_quantity) return;

            this.updatingItemId = item.cart_item_id;
            try {
                const { put, endpoints } = useApi();
                
                await put(endpoints.cart.update, {
                    cart_item_id: item.cart_item_id,
                    quantity: newQuantity
                });
                
                await this.fetchCart(); // Обновляем данные корзины
                this.$emit('cart-updated');
                this.$emit('show-message', 'Количество обновлено');
                
            } catch (error) {
                console.error('❌ Error updating quantity:', error);
                this.$emit('show-message', 'Ошибка обновления количества');
            } finally {
                this.updatingItemId = null;
            }
        },
        
        async removeFromCart(item) {
            this.removingItemId = item.cart_item_id;
            try {
                const { delete: del, endpoints } = useApi();
                
                await del(endpoints.cart.remove, {
                    cart_item_id: item.cart_item_id
                });
                
                await this.fetchCart(); // Обновляем данные корзины
                this.$emit('cart-updated');
                this.$emit('show-message', 'Товар удален из корзины');
                
            } catch (error) {
                console.error('❌ Error removing item:', error);
                this.$emit('show-message', 'Ошибка удаления товара');
            } finally {
                this.removingItemId = null;
            }
        },
        
        createOrder() {
            // Автозаполнение адреса из профиля
            if (this.userProfile && this.userProfile.address) {
                this.orderData.shipping_address = this.userProfile.address;
            }
            this.orderDialog = true;
        },
        
        async confirmOrder() {
            this.creatingOrder = true;
            try {
                const { post, endpoints } = useApi();
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
                
                if (!tg_user) {
                    this.$emit('show-message', 'Ошибка: пользователь не найден');
                    return;
                }

                const orderData = {
                    telegram_id: tg_user.id,
                    ...this.orderData
                };

                console.log('🔄 Creating order:', orderData);
                const result = await post(endpoints.orders.create, orderData);
                console.log('✅ Order created:', result);
                
                this.$emit('show-message', `Заказ №${result.order_number} успешно создан!`);
                this.orderDialog = false;
                await this.fetchCart(); // Обновляем корзину (должна быть пустой)
                this.$emit('cart-updated');
                
                // Можно перенаправить на страницу заказа
                // this.$router.push(`/orders/${result.order_id}`);
                
            } catch (error) {
                console.error('❌ Error creating order:', error);
                this.$emit('show-message', `Ошибка: ${error.message || 'Не удалось создать заказ'}`);
            } finally {
                this.creatingOrder = false;
            }
        },
        async loadUserProfile() {
            try {
                const { get, endpoints } = useApi();
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
                if (tg_user) {
                    this.userProfile = await get(endpoints.users.profile(tg_user.id));
                }
            } catch (error) {
                console.error('Error loading user profile:', error);
            }
        }
    }
}
</script>

<style scoped>

</style>