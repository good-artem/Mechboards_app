<template>
    <v-container class="cart-container">
        <v-row>
            <v-col cols="12">
                <v-card class="cart-card pa-3" elevation="2">
                    <v-card-title class="d-flex align-center cart-title pa-3">
                        <v-icon color="primary" class="mr-2">mdi-cart</v-icon>
                        Корзина
                        <v-spacer></v-spacer>
                        <v-chip color="primary" v-if="totalItemsCount > 0">
                            {{ totalItemsCount }} позиций
                        </v-chip>
                    </v-card-title>

                    <!-- Пустая корзина -->
                    <div v-if="totalItemsCount === 0" class="empty-cart text-center pa-6">
                        <v-icon size="64" color="grey-lighten-1">mdi-cart-outline</v-icon>
                        <div class="text-h6 mt-4">Корзина пуста</div>
                        <div class="text-body-1 mt-2">Добавьте товары из каталога или услуги</div>
                        <v-btn 
                            color="primary" 
                            class="mt-4"
                            @click="$router.push('/catalog')"
                        >
                            Перейти в каталог
                        </v-btn>
                        <v-btn 
                            color="secondary" 
                            class="mt-2"
                            @click="$router.push('/services')"
                        >
                            Перейти к услугам
                        </v-btn>
                    </div>

                    <!-- Товары в корзине -->
                    <div v-if="cartData.items && cartData.items.length > 0" class="mb-4">
                        <div class="text-h6 mb-2">Товары:</div>
                        <v-list lines="two" class="cart-list pa-0">
                            <v-list-item
                                v-for="item in cartData.items"
                                :key="item.cart_item_id"
                                class="cart-item pa-3"
                            >
                                <!-- ... существующий код для товаров ... -->
                            </v-list-item>
                        </v-list>
                    </div>

                    <!-- Услуги в корзине -->
                    <div v-if="cartData.service_items && cartData.service_items.length > 0">
                        <div class="text-h6 mb-2">Услуги:</div>
                        <v-list lines="two" class="cart-list pa-0">
                            <v-list-item
                                v-for="serviceItem in cartData.service_items"
                                :key="serviceItem.cart_service_item_id"
                                class="cart-service-item pa-3"
                            >
                                <template v-slot:prepend>
                                    <v-avatar rounded="lg" size="50" class="cart-item-image mr-3">
                                        <v-img 
                                            :src="getServiceImage(serviceItem.service)" 
                                            :alt="serviceItem.service.name"
                                            cover
                                        ></v-img>
                                    </v-avatar>
                                </template>

                                <div class="cart-item-content">
                                    <div class="cart-item-title font-weight-medium mb-1">
                                        {{ serviceItem.service.name }}
                                    </div>
                                    
                                    <div class="cart-item-description text-caption text-grey mb-2 line-clamp-2">
                                        {{ serviceItem.service.description || 'Нет описания' }}
                                    </div>
                                    
                                    <div v-if="serviceItem.notes" class="cart-item-notes text-caption text-grey mb-2">
                                        <strong>Примечание:</strong> {{ serviceItem.notes }}
                                    </div>
                                    
                                    <div class="cart-item-subtitle text-body-2">
                                        {{ formatPrice(serviceItem.service.price) }} × {{ serviceItem.quantity }} = 
                                        <span class="font-weight-bold primary--text">
                                            {{ formatPrice(serviceItem.service.price * serviceItem.quantity) }}
                                        </span>
                                    </div>
                                    
                                    <div v-if="serviceItem.service.duration" class="text-caption text-grey">
                                        Время выполнения: {{ serviceItem.service.duration }}
                                    </div>
                                </div>

                                <template v-slot:append>
                                    <div class="d-flex flex-column align-center cart-item-actions">
                                        <!-- Управление количеством услуг -->
                                        <div class="quantity-controls d-flex align-center mb-2">
                                            <v-btn 
                                                icon 
                                                size="x-small"
                                                :disabled="serviceItem.quantity <= 1 || updatingServiceId === serviceItem.cart_service_item_id"
                                                @click="updateServiceQuantity(serviceItem, serviceItem.quantity - 1)"
                                                class="quantity-btn"
                                                density="comfortable"
                                                variant="tonal"
                                                color="grey"
                                            >
                                                <v-icon size="16">mdi-minus</v-icon>
                                            </v-btn>
                                            
                                            <span class="mx-2 quantity-display text-body-2 font-weight-medium">{{ serviceItem.quantity }}</span>
                                            
                                            <v-btn 
                                                icon 
                                                size="x-small"
                                                :disabled="updatingServiceId === serviceItem.cart_service_item_id"
                                                @click="updateServiceQuantity(serviceItem, serviceItem.quantity + 1)"
                                                class="quantity-btn"
                                                density="comfortable"
                                                variant="tonal"
                                                color="grey"
                                            >
                                                <v-icon size="16">mdi-plus</v-icon>
                                            </v-btn>
                                        </div>

                                        <!-- Кнопка удаления услуги -->
                                        <v-btn 
                                            icon 
                                            color="error" 
                                            size="x-small"
                                            @click="removeServiceFromCart(serviceItem)"
                                            :loading="removingServiceId === serviceItem.cart_service_item_id"
                                            class="remove-btn"
                                            density="comfortable"
                                            variant="tonal"
                                        >
                                            <v-icon size="18">mdi-delete-outline</v-icon>
                                        </v-btn>
                                    </div>
                                </template>
                            </v-list-item>
                        </v-list>
                    </div>

                    <!-- Итого и кнопка оформления -->
                    <div v-if="totalItemsCount > 0">
                        <v-card class="mt-3 pa-3 summary-card" elevation="1">
                            <div class="mb-2">
                                <div class="text-body-1">Товары: {{ formatPrice(cartData.products_total || 0) }}</div>
                                <div class="text-body-1">Услуги: {{ formatPrice(cartData.services_total || 0) }}</div>
                                <v-divider class="my-2"></v-divider>
                                <div class="text-h6 font-weight-medium">Итого:</div>
                                <div class="text-h4 font-weight-bold primary--text">
                                    {{ formatPrice(cartData.total) }}
                                </div>
                            </div>
                            
                            <v-btn 
                                color="primary" 
                                size="x-large"
                                @click="createOrder"
                                :loading="creatingOrder"
                                :disabled="totalItemsCount === 0"
                                class="checkout-btn w-100"
                                block
                            >
                                <span class="checkout-text">Оформить заказ</span>
                            </v-btn>
                        </v-card>
                    </div>
                </v-card>
            </v-col>
        </v-row>

        <!-- Диалог оформления заказа -->
        <!-- ... существующий код диалога ... -->
    </v-container>
</template>

<script>
import '@/assets/styles/components/cart-view.css'
import { useApi } from '@/composables/useApi'

export default {
    name: 'CartView',
    data() {
        return {
            cartData: {
                items: [],
                service_items: [],
                total: 0,
                products_total: 0,
                services_total: 0
            },
            orderDialog: false,
            creatingOrder: false,
            orderData: {
                shipping_method: 'Самовывоз',
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
            updatingServiceId: null,
            removingServiceId: null,
            loading: false
        }
    },
    computed: {
        totalItemsCount() {
            return (this.cartData.items?.length || 0) + (this.cartData.service_items?.length || 0);
        }
    },
    async mounted() {
        await this.fetchCart();
    },
    methods: {
        // ... существующие методы для товаров ...
        
        getServiceImage(service) {
            if (!service || !service.image_url) {
                return 'https://via.placeholder.com/100x100/667eea/ffffff?text=Service';
            }
            return service.image_url;
        },
        
        async updateServiceQuantity(serviceItem, newQuantity) {
            if (!serviceItem || !serviceItem.cart_service_item_id) {
                console.error('Invalid service item for update:', serviceItem);
                return;
            }
            
            if (newQuantity < 1) {
                await this.removeServiceFromCart(serviceItem);
                return;
            }
            
            this.updatingServiceId = serviceItem.cart_service_item_id;
            
            try {
                const { put } = useApi();
                await put('/api/cart/update_service', {
                    cart_service_item_id: serviceItem.cart_service_item_id,
                    quantity: newQuantity,
                    notes: serviceItem.notes
                });
                
                await this.fetchCart();
                this.$root.$emit('cart-updated');
                this.showMessage('Количество обновлено');
            } catch (error) {
                console.error('❌ Error updating service quantity:', error);
                this.showMessage(`Ошибка: ${error.message || 'Не удалось обновить количество'}`, 'error');
            } finally {
                this.updatingServiceId = null;
            }
        },
        
        async removeServiceFromCart(serviceItem) {
            if (!serviceItem || !serviceItem.cart_service_item_id) {
                console.error('Invalid service item for removal:', serviceItem);
                return;
            }
            
            this.removingServiceId = serviceItem.cart_service_item_id;
            
            try {
                const { del } = useApi();
                await del('/api/cart/remove_service', {
                    cart_service_item_id: serviceItem.cart_service_item_id
                });
                
                await this.fetchCart();
                this.$root.$emit('cart-updated');
                this.showMessage('Услуга удалена из корзины');
            } catch (error) {
                console.error('❌ Error removing service item:', error);
                this.showMessage(`Ошибка: ${error.message || 'Не удалось удалить услугу'}`, 'error');
            } finally {
                this.removingServiceId = null;
            }
        },
        formatPrice(price) {
            return new Intl.NumberFormat('ru-BY', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(price) + ' р.';
        },
        
        getProductImage(product) {
            if (!product || !product.images || !product.images.length) {
                return 'https://via.placeholder.com/100x100/667eea/ffffff?text=No+Image';
            }
            
            try {
                let imagePath = product.images[0];
                
                // Если путь уже полный URL
                if (imagePath.startsWith('http')) {
                    return imagePath;
                }
                
                // Если путь начинается с assets/
                if (imagePath.startsWith('assets/') || imagePath.startsWith('/assets/')) {
                    if (imagePath.startsWith('/')) {
                        imagePath = imagePath.substring(1);
                    }
                    const baseUrl = this.getApiBaseUrl();
                    return `${baseUrl}/${imagePath}`;
                }
                
                // Если путь относительный
                const baseUrl = this.getApiBaseUrl();
                if (imagePath.startsWith('/')) {
                    return `${baseUrl}${imagePath}`;
                } else {
                    return `${baseUrl}/${imagePath}`;
                }
            } catch (e) {
                console.error('Error processing product image:', e);
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
                return 'https://verbose-space-orbit-x45v4q7q6wwf6g94-8000.app.github.dev';
            }
        },
        
        async fetchCart() {
            this.loading = true;
            try {
                const { get, endpoints } = useApi();
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                const telegramId = tg_user?.id || 391622124;
                
                const cartData = await get(endpoints.cart.get(telegramId));
                this.cartData = cartData || { items: [], total: 0 };
            } catch (error) {
                console.error('❌ Ошибка загрузки корзины:', error);
                this.cartData = { items: [], total: 0 };
                this.showMessage('Ошибка загрузки корзины. Попробуйте обновить страницу.', 'error');
            }
            this.loading = false;
        },
        
        async updateQuantity(item, newQuantity) {
            if (!item || !item.cart_item_id) {
                console.error('Invalid item for update:', item);
                return;
            }
            
            if (newQuantity < 1) {
                await this.removeFromCart(item);
                return;
            }
            
            if (item.product && item.product.stock_quantity && newQuantity > item.product.stock_quantity) {
                this.showMessage(`Нельзя добавить больше ${item.product.stock_quantity} шт. этого товара`, 'warning');
                return;
            }
            
            this.updatingItemId = item.cart_item_id;
            
            try {
                const { put, endpoints } = useApi();
                await put(endpoints.cart.update, {
                    cart_item_id: item.cart_item_id,
                    quantity: newQuantity
                });
                
                await this.fetchCart();
                this.$root.$emit('cart-updated');
                this.showMessage('Количество обновлено');
            } catch (error) {
                console.error('❌ Error updating quantity:', error);
                this.showMessage(`Ошибка: ${error.message || 'Не удалось обновить количество'}`, 'error');
            } finally {
                this.updatingItemId = null;
            }
        },
        
        async removeFromCart(item) {
            if (!item || !item.cart_item_id) {
                console.error('Invalid item for removal:', item);
                return;
            }
            
            this.removingItemId = item.cart_item_id;
            
            try {
                const { del, endpoints } = useApi();
                await del(endpoints.cart.remove, {
                    cart_item_id: item.cart_item_id
                });
                
                await this.fetchCart();
                this.$root.$emit('cart-updated');
                this.showMessage('Товар удален из корзины');
            } catch (error) {
                console.error('❌ Error removing item:', error);
                this.showMessage(`Ошибка: ${error.message || 'Не удалось удалить товар'}`, 'error');
            } finally {
                this.removingItemId = null;
            }
        },
        
        createOrder() {
            this.orderDialog = true;
        },
        
        async confirmOrder() {
            this.creatingOrder = true;
            try {
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                let telegramId;
                
                if (tg_user) {
                    telegramId = tg_user.id;
                } else {
                    // Для тестирования
                    telegramId = 391622124;
                }
                
                // Валидация данных заказа
                if (!this.orderData.shipping_address || !this.orderData.shipping_method) {
                    throw new Error('Заполните адрес доставки и выберите способ доставки');
                }
                
                // Проверяем товары в корзине
                if (!this.cartData.items || this.cartData.items.length === 0) {
                    throw new Error('Корзина пуста');
                }
                
                const { post, endpoints } = useApi();
                
                const orderData = {
                    telegram_id: telegramId,
                    shipping_method: this.orderData.shipping_method,
                    shipping_address: this.orderData.shipping_address,
                    customer_notes: this.orderData.customer_notes
                };
                
                console.log('🔄 Creating order with data:', orderData);
                const result = await post(endpoints.orders.create, orderData);
                
                if (result && result.order_number) {
                    this.showMessage(`Заказ №${result.order_number} успешно создан!`);
                    this.orderDialog = false;
                    
                    // Обновляем корзину
                    await this.fetchCart();
                    this.$root.$emit('cart-updated');
                    
                    // Перенаправляем на страницу профиля
                    this.$router.push({ 
                        path: '/profile', 
                        query: { success: 'order_created', orderNumber: result.order_number } 
                    });
                } else {
                    throw new Error('Не удалось создать заказ. Попробуйте еще раз.');
                }
            } catch (error) {
                console.error('❌ Error creating order:', error);
                this.showMessage(`Ошибка: ${error.message || 'Не удалось создать заказ'}`, 'error');
            } finally {
                this.creatingOrder = false;
            }
        },
        
        showMessage(message, type = 'success') {
            // Показываем через родительский компонент
            if (this.$root && this.$root.$emit) {
                this.$root.$emit('show-message', message, type);
            } else {
                console.log(`[${type.toUpperCase()}] ${message}`);
            }
        }
    }
}
</script>