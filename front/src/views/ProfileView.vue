<template>
    <v-container class="profile-container">
        <v-row justify="center">
            <v-col cols="12" sm="8" md="6">
                <!-- Отладочная информация -->
                <v-alert v-if="debugInfo && debugMode" type="info" class="mb-4">
                    <div><strong>Debug Info:</strong></div>
                    <div>Telegram User: {{ debugInfo.telegramUser ? 'Found' : 'Not found' }}</div>
                    <div>Telegram ID: {{ debugInfo.telegramId }}</div>
                    <div>API Base URL: {{ debugInfo.apiBaseUrl }}</div>
                    <div>Loading: {{ loading }}</div>
                    <div>Error: {{ error }}</div>
                </v-alert>

                <v-card class="profile-card" elevation="2">
                    <v-card-title class="profile-title d-flex align-center">
                        <v-avatar color="primary" size="56" class="profile-avatar mr-4">
                            <v-icon v-if="!user.photo_url" color="white" size="32">mdi-account</v-icon>
                            <img v-else :src="user.photo_url" alt="User Avatar" class="avatar-image">
                        </v-avatar>
                        <div>
                            <div class="text-h5 font-weight-bold">{{ user.name || 'Пользователь' }}</div>
                            <div class="text-body-1 text-grey">{{ user.username || 'Без username' }}</div>
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
                        </v-list>
                    </v-card-text>
                </v-card>
                <v-card v-if="testResult" class="test-result-card mt-4 pa-4">
                    <v-alert :type="testResult.type" :icon="testResult.icon" variant="tonal">
                        {{ testResult.message }}
                    </v-alert>
                </v-card>
            </v-col>
        </v-row>
    </v-container>

    <v-card-actions class="profile-actions pa-4">
        <v-btn 
            v-if="isAdmin" 
            @click="goToAdmin"
            color="secondary" 
            variant="outlined"
            class="admin-btn"
            block
        >
            <v-icon left>mdi-shield-account</v-icon>
            Админ панель
        </v-btn>
        <v-btn @click="testConnection" color="primary" variant="outlined" :loading="testing" block>
            <v-icon left>mdi-connection</v-icon>
            Проверить подключение
        </v-btn>
    </v-card-actions>
  <!-- Добавляем раздел для заказов товаров -->
  <v-card-text v-if="userOrders.length > 0" class="mt-4">
    <v-card-title class="font-weight-bold">Мои заказы товаров</v-card-title>
    <v-list class="mt-2">
      <v-list-item v-for="order in userOrders" :key="order.order_id" class="mb-2">
        <v-list-item-title>Заказ #{{ order.order_number }}</v-list-item-title>
        <v-list-item-subtitle class="text-primary font-weight-bold">
          Сумма: {{ formatPrice(order.total_amount) }}
        </v-list-item-subtitle>
        <v-list-item-subtitle :class="getStatusColor(order.status)">
          Статус: {{ order.status }}
        </v-list-item-subtitle>
        <v-list-item-subtitle>
          Дата: {{ formatDate(order.created_at) }}
        </v-list-item-subtitle>
        <v-expansion-panels>
          <v-expansion-panel>
            <v-expansion-panel-title>Товары в заказе</v-expansion-panel-title>
            <v-expansion-panel-text>
              <v-list dense>
                <v-list-item v-for="(item, index) in order.items" :key="index">
                  <v-list-item-title>{{ item.name }} ({{ item.quantity }} шт.)</v-list-item-title>
                  <v-list-item-subtitle>
                    Цена за шт: {{ formatPrice(item.price) }}. Итого: {{ formatPrice(item.subtotal) }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-list-item>
    </v-list>
  </v-card-text>
  
  <!-- Добавляем раздел для заказанных услуг -->
  <v-card-text v-if="serviceOrders.length > 0" class="mt-4">
    <v-card-title class="font-weight-bold">Мои заказанные услуги</v-card-title>
    <v-list class="mt-2">
      <v-list-item v-for="order in serviceOrders" :key="order.service_order_id" class="mb-2">
        <v-list-item-title>{{ order.service.name }}</v-list-item-title>
        <v-list-item-subtitle>{{ order.service.description }}</v-list-item-subtitle>
        <v-list-item-subtitle class="text-primary font-weight-bold">
          {{ formatPrice(order.price) }}
        </v-list-item-subtitle>
        <v-list-item-subtitle :class="getStatusColor(order.status)">
          Статус: {{ order.status }}
        </v-list-item-subtitle>
        <v-list-item-subtitle v-if="order.notes">
          Комментарий: {{ order.notes }}
        </v-list-item-subtitle>
        <v-list-item-subtitle>
          Заказано: {{ formatDate(order.created_at) }}
        </v-list-item-subtitle>
      </v-list-item>
    </v-list>
  </v-card-text>
 
</template>

<script>
import API_CONFIG from '@/config/api';

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
                is_active: true
            },
            ordersCount: 0,
            completedOrdersCount: 0,
            loading: false,
            testing: false,
            testResult: null,
            debugInfo: null,
            isAdmin: false,
            adminUrl: 'https://verbose-space-orbit-x45v4q7q6wwf6g94-8000.app.github.dev/admin',
            orders: [],
            serviceOrders: [],
            loadingOrders: false,
            loadingServiceOrders: false,
            userOrders: [],
            serviceOrders: []
        }
    },
    async mounted() {
        console.log('🔍 ProfileView mounted');
        await this.initializeProfile();
        await this.checkAdminStatus();
        await this.fetchUserOrders();
        await this.fetchServiceOrders();
    },
    methods: {


        async checkAdminStatus() {
            try {
                const { get } = useApi();
                const result = await get('/api/admin/check');
                this.isAdmin = result.is_admin;
            } catch (error) {
                console.error('❌ Ошибка проверки прав администратора:', error);
                this.isAdmin = false;
            }
        },
        
        goToAdmin() {
            // Открываем админку в новом окне или переходим по роуту
            window.Telegram.WebApp.openLink(this.adminUrl);
        },
        async initializeProfile() {
            console.log('🔍 Initializing profile...');
            
            // Собираем отладочную информацию
            this.debugInfo = {
                telegramUser: window.Telegram?.WebApp?.initDataUnsafe?.user,
                apiBaseUrl: API_CONFIG.getBaseUrl(),
                timestamp: new Date().toISOString()
            };
            
            console.log('🔍 Debug info:', this.debugInfo);
            console.log('🔍 Telegram WebApp available:', !!window.Telegram?.WebApp);
            console.log('🔍 Telegram User data:', window.Telegram?.WebApp?.initDataUnsafe?.user);

            if (!window.Telegram?.WebApp) {
                console.log('❌ Telegram WebApp not available');
                // Для тестирования без Telegram
                this.user = {
                    telegram_id: 391622124,
                    name: 'Test User',
                    username: '@testuser',
                    created_at: new Date().toISOString()
                };
                return;
            }

            await this.fetchUserProfile();
            await this.fetchUserStats();
        },

        async fetchUserProfile() {
            this.loading = true;
            console.log('🔄 Загрузка профиля...');
            
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
                const telegram_id = tg_user?.id || 391622124;
                
                console.log('🔍 Telegram ID:', telegram_id);

                // Используем новый публичный эндпоинт
                const userUrl = `${this.getApiBaseUrl()}/api/user/${telegram_id}`;
                console.log('🔍 API URL:', userUrl);

                const response = await fetch(userUrl);
                console.log('🔍 Статус ответа:', response.status);

                if (response.ok) {
                    const userData = await response.json();
                    console.log('✅ Профиль загружен:', userData);
                    this.user = { ...this.user, ...userData };
                } else {
                    console.error('❌ Ошибка загрузки профиля:', response.status);
                    // Fallback данные
                    this.user = {
                        telegram_id: telegram_id,
                        name: tg_user?.first_name || 'Telegram User',
                        username: tg_user?.username ? `@${tg_user.username}` : null,
                        created_at: new Date().toISOString()
                    };
                }
            } catch (error) {
                console.error('❌ Ошибка сети:', error);
            }
            this.loading = false;
        },
        
        getApiBaseUrl() {
            return window.location.hostname === 'localhost' 
                ? 'http://localhost:8000' 
                : 'https://verbose-space-orbit-x45v4q7q6wwf6g94-8000.app.github.dev';
        },

        async createUser(tgUser) {
            try {
                console.log('🔄 Creating new user for Telegram ID:', tgUser.id);
                
                const createUrl = API_CONFIG.getUrl(API_CONFIG.endpoints.users.create);
                
                const response = await fetch(createUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        telegram_id: tgUser.id,
                        username: tgUser.username ? `@${tgUser.username}` : null,
                        name: tgUser.first_name + (tgUser.last_name ? ` ${tgUser.last_name}` : '')
                    })
                });

                if (response.ok) {
                    const userData = await response.json();
                    console.log('✅ User created successfully:', userData);
                    this.user = { ...this.user, ...userData };
                } else {
                    console.error('❌ Error creating user:', response.status);
                    // Fallback данные
                    this.user = {
                        telegram_id: tgUser.id,
                        name: tgUser.first_name || 'Telegram User',
                        username: tgUser.username ? `@${tgUser.username}` : null,
                        created_at: new Date().toISOString()
                    };
                }
            } catch (error) {
                console.error('❌ Network error creating user:', error);
            }
        },

        async fetchUserStats() {
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
                if (!tg_user) return;

                // ИСПРАВЛЕНО: передаем userId в endpoint stats
                const statsUrl = API_CONFIG.getUrl(API_CONFIG.endpoints.users.stats(tg_user.id));
                console.log('📊 Fetching user stats from:', statsUrl);
                
                const response = await fetch(statsUrl);
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

        async testConnection() {
            this.testing = true;
            this.testResult = null;
            
            try {
                // ИСПРАВЛЕНО: используем API_CONFIG для формирования URL
                const testUrl = API_CONFIG.getUrl(API_CONFIG.endpoints.categories.list);
                
                console.log('🧪 Testing connection to:', testUrl);
                
                const response = await fetch(testUrl);
                
                if (response.ok) {
                    const data = await response.json();
                    this.testResult = {
                        type: 'success',
                        message: `✅ API подключен! Получено категорий: ${data.length}`
                    };
                } else {
                    this.testResult = {
                        type: 'error',
                        message: `❌ Ошибка API: ${response.status} ${response.statusText}`
                    };
                }
            } catch (error) {
                this.testResult = {
                    type: 'error',
                    message: `❌ Ошибка сети: ${error.message}`
                };
            }
            
            this.testing = false;
        },
        getStatusColor(status) {
        const statusColors = {
            'Создан': 'text-grey',
            'Оплачен': 'text-warning',
            'Подтвержден': 'text-info',
            'Отправлен': 'text-success',
            'Доставлен': 'text-primary',
            'Отменен': 'text-error'
        };
        return statusColors[status] || 'text-grey';
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
        async fetchUserOrders() {
            this.loadingOrders = true;
            try {
                const { get } = useApi();
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                const telegramId = tg_user?.id || 391622124;
                
                const orders = await get(`/api/users/${telegramId}/orders`);
                this.orders = orders;
            } catch (error) {
                console.error('❌ Ошибка загрузки заказов:', error);
            } finally {
                this.loadingOrders = false;
            }
        },
        
        async fetchUserServiceOrders() {
            this.loadingServiceOrders = true;
            try {
                const { get } = useApi();
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                const telegramId = tg_user?.id || 391622124;
                
                const serviceOrders = await get(`/api/users/${telegramId}/service_orders`);
                this.serviceOrders = serviceOrders;
            } catch (error) {
                console.error('❌ Ошибка загрузки заказов на услуги:', error);
            } finally {
                this.loadingServiceOrders = false;
            }
        },
        
        getOrderColor(status) {
            const colors = {
                'Создан': 'blue',
                'Оплачен': 'green',
                'Подтвержден': 'orange',
                'Отправлен': 'purple',
                'Доставлен': 'success',
                'Отменен': 'error'
            };
            return colors[status] || 'grey';
        },
        async fetchUserOrders() {
            try {
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                if (!tg_user) return;
                
                const { get, endpoints } = useApi();
                const userId = tg_user.id;
                const orders = await get(endpoints.users.orders(userId));
                this.userOrders = orders || [];
            } catch (error) {
                console.error('❌ Ошибка загрузки заказов:', error);
                this.userOrders = [];
            }
        }, 
        async fetchServiceOrders() {
            try {
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                if (!tg_user) return;
                
                const { get } = useApi();
                const userId = tg_user.id;
                const serviceOrders = await get(`/api/users/${userId}/service_orders`);
                this.serviceOrders = serviceOrders || [];
            } catch (error) {
                console.error('❌ Ошибка загрузки заказанных услуг:', error);
                this.serviceOrders = [];
            }
        },
        formatPrice(number) {
            return new Intl.NumberFormat('ru-BY', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(number).replace('.', ',') + ' p.';
        },
        getOrderIcon(status) {
            const icons = {
                'Создан': 'mdi-clock',
                'Оплачен': 'mdi-credit-card-check',
                'Подтвержден': 'mdi-check-circle',
                'Отправлен': 'mdi-truck',
                'Доставлен': 'mdi-package-variant-check',
                'Отменен': 'mdi-cancel'
            };
            return icons[status] || 'mdi-help-circle';
        }
    }
}
</script>

<style scoped>
.profile-container {
    padding: 16px 8px;
}

.profile-card {
    background: var(--tg-theme-bg-color, #ffffff) !important;
    color: var(--tg-theme-text-color, #000000) !important;
    border-radius: 12px;
}

.profile-title {
    color: var(--tg-theme-text-color, #000000) !important;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 20px 16px 16px !important;
}

.profile-avatar {
    margin-bottom: 8px;
}

.avatar-image {
    object-fit: cover;
    width: 100%;
    height: 100%;
    border-radius: 50%;
}

.profile-content {
    color: var(--tg-theme-text-color, #000000) !important;
    padding: 8px 0 !important;
}

.profile-list {
    background: var(--tg-theme-bg-color, #ffffff) !important;
    color: var(--tg-theme-text-color, #000000) !important;
    padding: 0 !important;
}

.profile-list-item {
    color: var(--tg-theme-text-color, #000000) !important;
    padding: 12px 16px !important;
    min-height: 56px !important;
}

.profile-divider {
    margin: 0 !important;
    border-color: var(--tg-theme-hint-color, #e0e0e0) !important;
}

.test-card {
    background: var(--tg-theme-secondary-bg-color, #f5f5f5) !important;
    border-radius: 12px;
}
.admin-btn {
    margin-bottom: 8px;
}
</style>