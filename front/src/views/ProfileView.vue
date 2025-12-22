<template>
    <v-container class="profile-container">
        <v-row justify="center">
            <v-col cols="12" sm="8" md="6">
                <v-card class="profile-card" elevation="2">
                    <v-card-title class="profile-title d-flex align-center">
                        <v-avatar color="primary" size="56" class="profile-avatar mr-4">
                            <v-icon v-if="!user.photo_url" color="white" size="32">mdi-account</v-icon>
                            <img v-else :src="user.photo_url" alt="User Avatar" class="avatar-image">
                        </v-avatar>
                        <div>
                            <div class="text-h5 font-weight-bold">{{ user.name || 'Пользователь' }}</div>
                            <div class="text-body-1 text-grey">{{ user.username || 'Без username' }}</div>
                            <v-chip v-if="user.is_admin" color="primary" size="small" class="mt-1">
                                <v-icon small left>mdi-shield-account</v-icon>
                                Администратор
                            </v-chip>
                        </div>
                    </v-card-title>
                    
                    <v-divider class="my-3"></v-divider>
                    
                    <v-card-text class="profile-content">
                        <div v-if="loading" class="text-center pa-4">
                            <v-progress-circular indeterminate color="primary" size="48"></v-progress-circular>
                            <div class="mt-3 text-body-1">Загрузка профиля...</div>
                        </div>
                        
                        <div v-else-if="error" class="text-center pa-4">
                            <v-icon color="error" size="48" class="mb-3">mdi-alert-circle</v-icon>
                            <div class="text-h6 mb-2">Ошибка загрузки</div>
                            <div class="text-body-1 mb-4">{{ error }}</div>
                            <v-btn @click="initializeProfile" color="primary">Повторить попытку</v-btn>
                        </div>
                        
                        <v-list v-else class="profile-list">
                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary" class="mr-2">mdi-identifier</v-icon>
                                </template>
                                <v-list-item-title class="font-weight-medium">Telegram ID</v-list-item-title>
                                <v-list-item-subtitle class="text-right">{{ user.telegram_id || 'Не указан' }}</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="profile-divider"></v-divider>

                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary" class="mr-2">mdi-account</v-icon>
                                </template>
                                <v-list-item-title class="font-weight-medium">Имя</v-list-item-title>
                                <v-list-item-subtitle class="text-right">{{ user.name || 'Не указано' }}</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="profile-divider"></v-divider>

                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary" class="mr-2">mdi-account-box</v-icon>
                                </template>
                                <v-list-item-title class="font-weight-medium">Username</v-list-item-title>
                                <v-list-item-subtitle class="text-right">{{ user.username || 'Не указан' }}</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="profile-divider"></v-divider>

                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary" class="mr-2">mdi-calendar</v-icon>
                                </template>
                                <v-list-item-title class="font-weight-medium">Дата регистрации</v-list-item-title>
                                <v-list-item-subtitle class="text-right">{{ formatDate(user.created_at) }}</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="profile-divider"></v-divider>

                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary" class="mr-2">mdi-shopping</v-icon>
                                </template>
                                <v-list-item-title class="font-weight-medium">Всего заказов</v-list-item-title>
                                <v-list-item-subtitle class="text-right">{{ ordersCount }}</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="profile-divider"></v-divider>

                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary" class="mr-2">mdi-check-circle</v-icon>
                                </template>
                                <v-list-item-title class="font-weight-medium">Выполненные заказы</v-list-item-title>
                                <v-list-item-subtitle class="text-right">{{ completedOrdersCount }}</v-list-item-subtitle>
                            </v-list-item>

                            <!-- Поле для статуса администратора -->
                            <v-divider class="profile-divider" v-if="user.is_admin"></v-divider>

                            <v-list-item class="profile-list-item" v-if="user.is_admin">
                                <template v-slot:prepend>
                                    <v-icon color="red" class="mr-2">mdi-shield-account</v-icon>
                                </template>
                                <v-list-item-title class="font-weight-medium">Статус</v-list-item-title>
                                <v-list-item-subtitle class="text-right red--text font-weight-bold">Администратор</v-list-item-subtitle>
                            </v-list-item>
                        </v-list>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>

        <v-card class="pa-3 mt-3">
            <v-card-title>Поддержка</v-card-title>
            <v-card-text>
                <p>Есть вопросы или нужна помощь? Напишите нам в Telegram!</p>
                <v-btn 
                    color="primary" 
                    @click="openTelegramSupport"
                    block
                    class="mt-2"
                >
                    <v-icon left>mdi-telegram</v-icon>
                    Написать в поддержку
                </v-btn>
            </v-card-text>
        </v-card>

        <!-- Заказы товаров -->
        <v-card v-if="userOrders.length > 0" class="mt-4" elevation="1">
            <v-card-title class="d-flex align-center">
                <v-icon color="primary" class="mr-2">mdi-package-variant</v-icon>
                Мои заказы товаров
            </v-card-title>
            <v-card-text>
                <v-list>
                    <v-list-item
                        v-for="order in userOrders"
                        :key="order.order_id"
                        class="mb-2"
                    >
                        <template v-slot:prepend>
                            <v-avatar :color="getOrderColor(order.status)" size="40">
                                <v-icon color="white">{{ getOrderIcon(order.status) }}</v-icon>
                            </v-avatar>
                        </template>
                        
                        <v-list-item-title class="font-weight-bold">
                            Заказ #{{ order.order_number }}
                        </v-list-item-title>
                        <v-list-item-subtitle>
                            <div class="d-flex justify-space-between">
                                <span>{{ formatPrice(order.total_amount) }}</span>
                                <span :class="getStatusColor(order.status) + '--text font-weight-bold'">
                                    {{ order.status }}
                                </span>
                            </div>
                            <div class="text-caption text-grey">
                                {{ formatDate(order.created_at) }}
                            </div>
                        </v-list-item-subtitle>
                        
                        <template v-slot:append>
                            <v-btn 
                                icon 
                                @click="viewOrderDetails(order)"
                                size="small"
                                variant="tonal"
                            >
                                <v-icon>mdi-eye</v-icon>
                            </v-btn>
                        </template>
                    </v-list-item>
                </v-list>
            </v-card-text>
        </v-card>

        <!-- Заказы услуг -->
        <v-card v-if="userServiceOrders.length > 0" class="mt-4" elevation="1">
            <v-card-title class="d-flex align-center">
                <v-icon color="primary" class="mr-2">mdi-tools</v-icon>
                Мои заказы услуг
            </v-card-title>
            <v-card-text>
                <v-list>
                    <v-list-item
                        v-for="order in userServiceOrders"
                        :key="order.service_order_id"
                        class="mb-2"
                    >
                        <template v-slot:prepend>
                            <v-avatar :color="getOrderColor(order.status)" size="40">
                                <v-icon color="white">mdi-wrench</v-icon>
                            </v-avatar>
                        </template>
                        
                        <v-list-item-title class="font-weight-bold">
                            {{ order.service?.name || 'Услуга' }}
                        </v-list-item-title>
                        <v-list-item-subtitle>
                            <div class="d-flex justify-space-between">
                                <span>{{ formatPrice(order.price) }}</span>
                                <span :class="getStatusColor(order.status) + '--text font-weight-bold'">
                                    {{ order.status }}
                                </span>
                            </div>
                            <div v-if="order.notes" class="text-caption">
                                <strong>Примечание:</strong> {{ order.notes }}
                            </div>
                            <div class="text-caption text-grey">
                                {{ formatDate(order.created_at) }}
                            </div>
                        </v-list-item-subtitle>
                    </v-list-item>
                </v-list>
            </v-card-text>
        </v-card>

        <!-- Сообщение если нет заказов -->
        <v-card v-if="!loading && userOrders.length === 0 && userServiceOrders.length === 0" class="mt-4" elevation="1">
            <v-card-text class="text-center pa-6">
                <v-icon size="64" color="grey-lighten-1">mdi-package-variant</v-icon>
                <div class="text-h6 mt-4">Заказов пока нет</div>
                <div class="text-body-1 mt-2">Ваши заказы появятся здесь после оформления</div>
                <v-btn 
                    color="primary" 
                    class="mt-4"
                    @click="$router.push('/catalog')"
                >
                    Перейти в каталог
                </v-btn>
            </v-card-text>
        </v-card>

        <!-- Диалог деталей заказа -->
        <v-dialog v-model="orderDetailsDialog" max-width="500">
            <v-card v-if="selectedOrder">
                <v-card-title class="d-flex justify-space-between align-center">
                    <span>Заказ #{{ selectedOrder.order_number }}</span>
                    <v-btn icon @click="orderDetailsDialog = false">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </v-card-title>
                <v-card-text>
                    <div class="mb-3">
                        <div class="text-subtitle-1 font-weight-medium">Статус:</div>
                        <v-chip :color="getOrderColor(selectedOrder.status)" class="mt-1">
                            {{ selectedOrder.status }}
                        </v-chip>
                    </div>
                    
                    <div class="mb-3">
                        <div class="text-subtitle-1 font-weight-medium">Дата создания:</div>
                        <div>{{ formatDate(selectedOrder.created_at) }}</div>
                    </div>
                    
                    <div class="mb-3">
                        <div class="text-subtitle-1 font-weight-medium">Способ доставки:</div>
                        <div>{{ selectedOrder.shipping_method }}</div>
                    </div>
                    
                    <div class="mb-3">
                        <div class="text-subtitle-1 font-weight-medium">Адрес доставки:</div>
                        <div>{{ selectedOrder.shipping_address }}</div>
                    </div>
                    
                    <div v-if="selectedOrder.customer_notes" class="mb-3">
                        <div class="text-subtitle-1 font-weight-medium">Комментарий:</div>
                        <div>{{ selectedOrder.customer_notes }}</div>
                    </div>
                    
                    <div v-if="selectedOrder.items && selectedOrder.items.length > 0" class="mb-3">
                        <div class="text-subtitle-1 font-weight-medium">Товары:</div>
                        <v-list density="compact" class="mt-1">
                            <v-list-item
                                v-for="(item, index) in selectedOrder.items"
                                :key="index"
                                class="px-0"
                            >
                                <v-list-item-title>{{ item.name }} × {{ item.quantity }}</v-list-item-title>
                                <v-list-item-subtitle class="text-right">
                                    {{ formatPrice(item.subtotal) }}
                                </v-list-item-subtitle>
                            </v-list-item>
                        </v-list>
                    </div>
                    
                    <v-divider class="my-3"></v-divider>
                    
                    <div class="text-h6 font-weight-bold primary--text text-right">
                        Итого: {{ formatPrice(selectedOrder.total_amount) }}
                    </div>
                </v-card-text>
            </v-card>
        </v-dialog>

        <v-card v-if="user.is_admin" class="mt-4" elevation="1">
            <v-card-text class="text-center pa-6">
                <v-icon size="48" color="primary" class="mb-3">mdi-shield-account</v-icon>
                <div class="text-h6 font-weight-bold mb-2">Администратор</div>
                <div class="text-body-2 text-grey mb-4">У вас есть доступ к панели администратора</div>
                <v-btn 
                    color="primary"
                    @click="goToAdmin"
                    block
                    size="large"
                    class="admin-button"
                >
                    <v-icon left>mdi-shield-account</v-icon>
                    Перейти в админ панель
                </v-btn>
            </v-card-text>
        </v-card>
    </v-container>
</template>

<script>
import { useApi } from '@/composables/useApi';

export default {
    name: 'ProfileView',
    data() {
        return {
            user: {
                user_id: null,
                telegram_id: null,
                username: '',
                name: '',
                phone: '',
                email: '',
                address: '',
                created_at: null,
                is_active: true,
                is_admin: false  // Исправлено: is_admin вместо isAdmin
            },
            ordersCount: 0,
            completedOrdersCount: 0,
            loading: false,
            error: null,
            userOrders: [],
            userServiceOrders: [],  // Исправлено: переименовано из serviceOrders
            orderDetailsDialog: false,
            selectedOrder: null,
            snackbar: false,
            snackbarMessage: '',
            snackbarColor: 'success'
        }
    },
    computed: {
        isAdmin() {
            return this.user.is_admin === true;
        }
    },
    async mounted() {
        console.log('🔍 ProfileView mounted');
        await this.initializeProfile();
        
        // Загружаем заказы параллельно для скорости
        await Promise.all([
            this.fetchUserOrders(),
            this.fetchServiceOrders()
        ]);
    },
    methods: {
        async initializeProfile() {
            console.log('🔍 Initializing profile...');
            
            this.loading = true;
            
            try {
                // Проверяем доступность Telegram
                if (!window.Telegram?.WebApp) {
                    console.log('❌ Telegram WebApp not available, using test mode');
                    // Для тестирования без Telegram
                    this.user = {
                        telegram_id: 391622124,
                        name: 'Test Administrator',
                        username: '@admin_test',
                        created_at: new Date().toISOString(),
                        is_admin: true  // Для теста делаем админом
                    };
                    this.loading = false;
                    return;
                }

                await this.fetchUserProfile();
                await this.fetchUserStats();
                
            } catch (error) {
                console.error('❌ Ошибка инициализации профиля:', error);
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        },
        
        async fetchUserProfile() {
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
                const telegram_id = tg_user?.id || 391622124;
                
                console.log('🔍 Telegram ID:', telegram_id);

                // Используем прямой fetch для избежания проблем с авторизацией
                const baseUrl = this.getApiBaseUrl();
                const userUrl = `${baseUrl}/api/user/${telegram_id}`;
                console.log('🔍 API URL:', userUrl);

                const headers = {};
                // Добавляем initData если доступен
                if (window.Telegram?.WebApp?.initData) {
                    headers['X-Telegram-Init-Data'] = window.Telegram.WebApp.initData;
                }

                const response = await fetch(userUrl, { headers });
                console.log('🔍 Статус ответа:', response.status);

                if (response.ok) {
                    const userData = await response.json();
                    console.log('✅ Профиль загружен:', userData);
                    this.user = { ...this.user, ...userData };
                    console.log('👑 Статус администратора:', this.user.is_admin);
                } else {
                    console.error('❌ Ошибка загрузки профиля:', response.status);
                    // Fallback данные с пометкой админа для тестового пользователя
                    this.user = {
                        telegram_id: telegram_id,
                        name: tg_user?.first_name || 'Telegram User',
                        username: tg_user?.username ? `@${tg_user.username}` : null,
                        created_at: new Date().toISOString(),
                        is_admin: telegram_id === 391622124  // Для теста делаем админом
                    };
                }
            } catch (error) {
                console.error('❌ Ошибка сети:', error);
            }
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
        
        async fetchUserStats() {
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
                if (!tg_user) return;

                const statsUrl = `${this.getApiBaseUrl()}/api/users/${tg_user.id}/stats`;
                console.log('📊 Fetching user stats from:', statsUrl);
                
                const headers = {};
                if (window.Telegram?.WebApp?.initData) {
                    headers['X-Telegram-Init-Data'] = window.Telegram.WebApp.initData;
                }
                
                const response = await fetch(statsUrl, { headers });
                console.log('📊 Stats response status:', response.status);
                
                if (response.ok) {
                    const stats = await response.json();
                    this.ordersCount = stats.total_orders || 0;
                    this.completedOrdersCount = stats.completed_orders || 0;
                    console.log('📊 User stats loaded:', stats);
                } else {
                    console.warn('⚠️ Could not load user stats:', response.status);
                }
            } catch (error) {
                console.error('❌ Error loading stats:', error);
            }
        },
        
        async fetchUserOrders() {
            try {
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                if (!tg_user) {
                    console.log('Telegram user not found, using test ID');
                    // Для теста загружаем тестовые заказы
                    this.userOrders = this.getMockOrders();
                    return;
                }
                
                const telegramId = tg_user.id;
                console.log('🔄 Загрузка заказов для пользователя:', telegramId);
                
                // Используем прямой fetch
                const baseUrl = this.getApiBaseUrl();
                const url = `${baseUrl}/api/users/${telegramId}/orders`;
                
                const headers = {};
                if (window.Telegram?.WebApp?.initData) {
                    headers['X-Telegram-Init-Data'] = window.Telegram.WebApp.initData;
                }
                
                const response = await fetch(url, { headers });
                
                if (response.ok) {
                    const orders = await response.json();
                    this.userOrders = Array.isArray(orders) ? orders : [];
                    console.log('✅ Заказы загружены:', this.userOrders.length);
                } else {
                    console.error('❌ Ошибка загрузки заказов:', response.status);
                    this.userOrders = [];
                }
            } catch (error) {
                console.error('❌ Ошибка загрузки заказов:', error);
                this.userOrders = [];
            }
        },
        
        async fetchServiceOrders() {
            try {
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                if (!tg_user) {
                    console.log('Telegram user not found');
                    // Для теста загружаем тестовые заказы услуг
                    this.userServiceOrders = this.getMockServiceOrders();
                    return;
                }
                
                const telegramId = tg_user.id;
                console.log('🔄 Загрузка заказов на услуги для пользователя:', telegramId);
                
                // Используем прямой fetch
                const baseUrl = this.getApiBaseUrl();
                const url = `${baseUrl}/api/users/${telegramId}/service_orders`;
                
                const headers = {};
                if (window.Telegram?.WebApp?.initData) {
                    headers['X-Telegram-Init-Data'] = window.Telegram.WebApp.initData;
                }
                
                const response = await fetch(url, { headers });
                
                if (response.ok) {
                    const serviceOrders = await response.json();
                    this.userServiceOrders = Array.isArray(serviceOrders) ? serviceOrders : [];
                    console.log('✅ Заказы на услуги загружены:', this.userServiceOrders.length);
                } else {
                    console.error('❌ Ошибка загрузки заказов на услуги:', response.status);
                    this.userServiceOrders = [];
                }
            } catch (error) {
                console.error('❌ Ошибка загрузки заказов на услуги:', error);
                this.userServiceOrders = [];
            }
        },
        
        getMockOrders() {
            return [
                {
                    order_id: 1,
                    order_number: 'ORDER-123456',
                    total_amount: 4500.00,
                    status: 'Доставлен',
                    shipping_method: 'Самовывоз',
                    shipping_address: 'г. Минск, ул. Примерная, 123',
                    customer_notes: 'Просьба позвонить перед доставкой',
                    created_at: new Date().toISOString(),
                    items: [
                        {
                            name: 'Keychron K2',
                            quantity: 1,
                            subtotal: 4500.00
                        }
                    ]
                }
            ];
        },
        
        getMockServiceOrders() {
            return [
                {
                    service_order_id: 1,
                    service: {
                        name: 'Сборка клавиатуры',
                        description: 'Профессиональная сборка'
                    },
                    price: 1500.00,
                    status: 'В работе',
                    notes: 'Нужно собрать с синими свитчами',
                    created_at: new Date().toISOString()
                }
            ];
        },
        
        goToAdmin() {
            if (this.user.is_admin) {
                this.$router.push('/admin');
            } else {
                this.showMessage('У вас нет прав администратора', 'error');
            }
        },
        
        formatDate(dateString) {
            if (!dateString) return 'Неизвестно';
            const date = new Date(dateString);
            return date.toLocaleDateString('ru-RU', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        formatPrice(price) {
            return new Intl.NumberFormat('ru-BY', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(price) + ' р.';
        },
        
        getOrderColor(status) {
            const colors = {
                'Создан': 'blue',
                'Оплачен': 'green',
                'Подтвержден': 'orange',
                'Отправлен': 'purple',
                'Доставлен': 'success',
                'Отменен': 'error',
                'В работе': 'warning'
            };
            return colors[status] || 'grey';
        },
        
        getStatusColor(status) {
            const colors = {
                'Создан': 'blue',
                'Оплачен': 'green',
                'Подтвержден': 'orange',
                'Отправлен': 'purple',
                'Доставлен': 'success',
                'Отменен': 'error',
                'В работе': 'warning'
            };
            return colors[status] || 'grey';
        },
        
        getOrderIcon(status) {
            const icons = {
                'Создан': 'mdi-clock',
                'Оплачен': 'mdi-credit-card-check',
                'Подтвержден': 'mdi-check-circle',
                'Отправлен': 'mdi-truck',
                'Доставлен': 'mdi-package-variant-check',
                'Отменен': 'mdi-cancel',
                'В работе': 'mdi-progress-wrench'
            };
            return icons[status] || 'mdi-help-circle';
        },
        
        viewOrderDetails(order) {
            this.selectedOrder = order;
            this.orderDetailsDialog = true;
        },
        
        showMessage(message, type = 'success') {
            this.snackbarMessage = message;
            this.snackbarColor = type === 'error' ? 'error' : 'success';
            this.snackbar = true;
            
            setTimeout(() => {
                this.snackbar = false;
            }, 3000);
        },
        async openTelegramSupport() {
            try {
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                const telegramId = tg_user?.id;
                
                if (!telegramId) {
                    alert('Пожалуйста, войдите через Telegram');
                    return;
                }
                
                // Открываем чат с ботом
                const botUsername = "MechboardsBot"; // Замените на username вашего бота
                const url = `https://t.me/${botUsername}?start=support`;
                
                // В Telegram WebApp можно открыть ссылку
                if (window.Telegram?.WebApp?.openLink) {
                    window.Telegram.WebApp.openLink(url);
                } else {
                    window.open(url, '_blank');
                }
                
            } catch (error) {
                console.error('Ошибка открытия поддержки:', error);
                alert('Не удалось открыть чат поддержки');
            }
        }
    }
}
</script>
