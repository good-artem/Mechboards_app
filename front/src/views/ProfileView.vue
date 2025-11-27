<template>
    <v-container class="profile-container">
        <v-row justify="center">
            <v-col cols="12" sm="8" md="6">
                <!-- Отладочная информация -->
                <v-alert v-if="debugInfo" type="info" class="mb-4">
                    <div><strong>Debug Info:</strong></div>
                    <div>Telegram User: {{ debugInfo.telegramUser ? 'Found' : 'Not found' }}</div>
                    <div>API Base URL: {{ debugInfo.apiBaseUrl }}</div>
                    <div>Loading: {{ loading }}</div>
                    <div>User Data: {{ user }}</div>
                </v-alert>

                <v-card class="profile-card" elevation="2">
                    <v-card-title class="profile-title">
                        <v-avatar color="primary" size="64" class="profile-avatar">
                            <v-icon v-if="!user.photo_url" color="white">mdi-account</v-icon>
                            <img v-else :src="user.photo_url" alt="User Avatar" class="avatar-image">
                        </v-avatar>
                        Профиль
                    </v-card-title>
                    
                    <v-card-text class="profile-content">
                        <div v-if="loading" class="text-center pa-4">
                            <v-progress-circular indeterminate color="primary"></v-progress-circular>
                            <div class="mt-2">Загрузка профиля...</div>
                        </div>
                        
                        <v-list v-else class="profile-list">
                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary">mdi-identifier</v-icon>
                                </template>
                                <v-list-item-title>Telegram ID</v-list-item-title>
                                <v-list-item-subtitle>{{ user.telegram_id || 'Не указан' }}</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="profile-divider"></v-divider>

                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary">mdi-account</v-icon>
                                </template>
                                <v-list-item-title>Имя</v-list-item-title>
                                <v-list-item-subtitle>{{ user.name || 'Не указано' }}</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="profile-divider"></v-divider>

                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary">mdi-account-box</v-icon>
                                </template>
                                <v-list-item-title>Username</v-list-item-title>
                                <v-list-item-subtitle>{{ user.username || 'Не указан' }}</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="profile-divider"></v-divider>

                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary">mdi-calendar</v-icon>
                                </template>
                                <v-list-item-title>Дата регистрации</v-list-item-title>
                                <v-list-item-subtitle>{{ formatDate(user.created_at) }}</v-list-item-subtitle>
                            </v-list-item>
                        </v-list>
                    </v-card-text>
                </v-card>

                <!-- Кнопка для тестирования -->
                <v-card class="test-card mt-4 pa-4 text-center">
                    <v-btn @click="testConnection" color="primary" :loading="testing">
                        Тест подключения к API
                    </v-btn>
                    <div v-if="testResult" class="mt-2">
                        <v-alert :type="testResult.type" dense>
                            {{ testResult.message }}
                        </v-alert>
                    </div>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
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
            debugInfo: null
        }
    },
    async mounted() {
        console.log('🔍 ProfileView mounted');
        await this.initializeProfile();
    },
    methods: {
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
            console.log('🔄 Fetching user profile...');
            
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
                if (!tg_user) {
                    console.error('❌ Telegram user not found');
                    this.loading = false;
                    return;
                }

                console.log('🔍 Telegram user ID:', tg_user.id);

                const userUrl = API_CONFIG.getUrl(API_CONFIG.endpoints.users.profile(tg_user.id));
                console.log('🔍 API URL:', userUrl);

                const response = await fetch(userUrl);
                console.log('🔍 Response status:', response.status);

                if (response.ok) {
                    const userData = await response.json();
                    console.log('✅ User profile loaded:', userData);
                    this.user = { ...this.user, ...userData };
                } else if (response.status === 404) {
                    console.log('👤 User not found, creating new user...');
                    await this.createUser(tg_user);
                } else {
                    console.error('❌ Error loading profile:', response.status);
                    // Fallback данные для тестирования
                    this.user = {
                        telegram_id: tg_user.id,
                        name: tg_user.first_name || 'Telegram User',
                        username: tg_user.username ? `@${tg_user.username}` : null,
                        created_at: new Date().toISOString()
                    };
                }
            } catch (error) {
                console.error('❌ Network error:', error);
                // Fallback данные при ошибке сети
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user;
                if (tg_user) {
                    this.user = {
                        telegram_id: tg_user.id,
                        name: tg_user.first_name || 'Telegram User',
                        username: tg_user.username ? `@${tg_user.username}` : null,
                        created_at: new Date().toISOString()
                    };
                }
            }
            this.loading = false;
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

        formatDate(dateString) {
            if (!dateString) return 'Неизвестно';
            try {
                const date = new Date(dateString);
                return date.toLocaleDateString('ru-RU', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
            } catch (e) {
                return 'Неизвестно';
            }
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
</style>