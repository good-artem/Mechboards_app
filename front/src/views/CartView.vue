<template>
    <v-container>
        <v-row>
            <v-col cols="12">
                <v-card class="pa-4" elevation="2">
                    <v-card-title class="d-flex align-center">
                        <v-icon color="primary" class="mr-2">mdi-cart</v-icon>
                        Корзина
                        <v-spacer></v-spacer>
                        <v-chip color="primary" v-if="cartData.items && cartData.items.length > 0">
                            {{ cartData.items.length }} товар(ов)
                        </v-chip>
                    </v-card-title>

                    <!-- Пустая корзина -->
                    <div v-if="!cartData.items || cartData.items.length === 0" class="text-center pa-8">
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
                        <v-list lines="two">
                            <v-list-item
                                v-for="item in cartData.items"
                                :key="item.cart_item_id"
                                class="cart-item"
                            >
                                <template v-slot:prepend>
                                    <v-avatar rounded="lg" size="60">
                                        <img 
                                            :src="getProductImage(item.product)" 
                                            :alt="item.product.name"
                                        >
                                    </v-avatar>
                                </template>

                                <v-list-item-title class="font-weight-medium">
                                    {{ item.product.name }}
                                </v-list-item-title>
                                
                                <v-list-item-subtitle>
                                    {{ formatPrice(item.product.price) }} × {{ item.quantity }} = 
                                    <span class="font-weight-bold">{{ formatPrice(item.subtotal) }}</span>
                                </v-list-item-subtitle>

                                <template v-slot:append>
                                    <div class="d-flex align-center">
                                        <!-- Управление количеством -->
                                        <div class="quantity-controls d-flex align-center mr-4">
                                            <v-btn 
                                                icon 
                                                size="small"
                                                :disabled="item.quantity <= 1"
                                                @click="updateQuantity(item, item.quantity - 1)"
                                            >
                                                <v-icon>mdi-minus</v-icon>
                                            </v-btn>
                                            
                                            <span class="mx-2 quantity-display">{{ item.quantity }}</span>
                                            
                                            <v-btn 
                                                icon 
                                                size="small"
                                                :disabled="item.quantity >= item.product.stock_quantity"
                                                @click="updateQuantity(item, item.quantity + 1)"
                                            >
                                                <v-icon>mdi-plus</v-icon>
                                            </v-btn>
                                        </div>

                                        <!-- Кнопка удаления -->
                                        <v-btn 
                                            icon 
                                            color="error" 
                                            size="small"
                                            @click="removeFromCart(item)"
                                            :loading="item.removing"
                                        >
                                            <v-icon>mdi-delete</v-icon>
                                        </v-btn>
                                    </div>
                                </template>
                            </v-list-item>
                        </v-list>

                        <!-- Итого и кнопка оформления -->
                        <v-card class="mt-4 pa-4" elevation="1">
                            <v-row align="center">
                                <v-col cols="6">
                                    <div class="text-h6">Итого:</div>
                                    <div class="text-h5 font-weight-bold primary--text">
                                        {{ formatPrice(cartData.total) }}
                                    </div>
                                </v-col>
                                <v-col cols="6" class="text-right">
                                    <v-btn 
                                        color="primary" 
                                        size="large"
                                        @click="createOrder"
                                        :loading="creatingOrder"
                                        class="w-100"
                                    >
                                        Оформить заказ
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
        <v-dialog v-model="orderDialog" max-width="500">
            <v-card>
                <v-card-title>Оформление заказа</v-card-title>
                <v-card-text>
                    <v-text-field
                        v-model="orderData.shipping_address"
                        label="Адрес доставки"
                        placeholder="Введите ваш адрес"
                        variant="outlined"
                        class="mb-4"
                        required
                    ></v-text-field>
                    
                    <v-select
                        v-model="orderData.shipping_method"
                        :items="shippingMethods"
                        label="Способ доставки"
                        variant="outlined"
                        class="mb-4"
                        required
                    ></v-select>

                    <v-textarea
                        v-model="orderData.customer_notes"
                        label="Комментарий к заказу"
                        placeholder="Дополнительные пожелания"
                        variant="outlined"
                        rows="2"
                    ></v-textarea>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="grey" @click="orderDialog = false">Отмена</v-btn>
                    <v-btn 
                        color="primary" 
                        @click="confirmOrder"
                        :loading="creatingOrder"
                        :disabled="!orderData.shipping_address || !orderData.shipping_method"
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
                'Курьерская доставка',
                'Самовывоз',
                'Почта России',
                'СДЭК'
            ],
            loading: false
        }
    },
    async mounted() {
        await this.fetchCart();
    },
    methods: {
        formatPrice(price) {
            return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
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
        async fetchCart() {
            this.loading = true;
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
                if (!tg_user) {
                    this.$emit('show-message', 'Ошибка: пользователь не найден');
                    return;
                }

                const response = await fetch(`/api/cart/${tg_user.id}`);
                if (response.ok) {
                    this.cartData = await response.json();
                } else {
                    console.error('Ошибка загрузки корзины');
                    this.$emit('show-message', 'Ошибка загрузки корзины');
                }
            } catch (error) {
                console.error('Ошибка:', error);
                this.$emit('show-message', 'Ошибка соединения');
            }
            this.loading = false;
        },
        async updateQuantity(item, newQuantity) {
            if (newQuantity < 1 || newQuantity > item.product.stock_quantity) return;

            try {
                const response = await fetch('/api/cart/update', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        cart_item_id: item.cart_item_id,
                        quantity: newQuantity
                    })
                });

                if (response.ok) {
                    await this.fetchCart(); // Обновляем данные корзины
                    this.$emit('cart-updated');
                } else {
                    this.$emit('show-message', 'Ошибка обновления количества');
                }
            } catch (error) {
                console.error('Ошибка обновления количества:', error);
                this.$emit('show-message', 'Ошибка соединения');
            }
        },
        async removeFromCart(item) {
            item.removing = true;
            try {
                const response = await fetch('/api/cart/remove', {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        cart_item_id: item.cart_item_id
                    })
                });

                if (response.ok) {
                    await this.fetchCart(); // Обновляем данные корзины
                    this.$emit('cart-updated');
                    this.$emit('show-message', 'Товар удален из корзины');
                } else {
                    this.$emit('show-message', 'Ошибка удаления товара');
                }
            } catch (error) {
                console.error('Ошибка удаления товара:', error);
                this.$emit('show-message', 'Ошибка соединения');
            } finally {
                item.removing = false;
            }
        },
        createOrder() {
            this.orderDialog = true;
        },
        async confirmOrder() {
            this.creatingOrder = true;
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
                if (!tg_user) {
                    this.$emit('show-message', 'Ошибка: пользователь не найден');
                    return;
                }

                const response = await fetch('/api/orders/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        telegram_id: tg_user.id,
                        ...this.orderData
                    })
                });

                if (response.ok) {
                    const result = await response.json();
                    this.$emit('show-message', `Заказ №${result.order_number} успешно создан!`);
                    this.orderDialog = false;
                    await this.fetchCart(); // Обновляем корзину (должна быть пустой)
                    this.$emit('cart-updated');
                    
                    // Можно перенаправить на страницу заказа
                    // this.$router.push(`/orders/${result.order_id}`);
                } else {
                    const error = await response.json();
                    this.$emit('show-message', `Ошибка: ${error.detail || 'Не удалось создать заказ'}`);
                }
            } catch (error) {
                console.error('Ошибка создания заказа:', error);
                this.$emit('show-message', 'Ошибка соединения');
            } finally {
                this.creatingOrder = false;
            }
        }
    }
}
</script>

