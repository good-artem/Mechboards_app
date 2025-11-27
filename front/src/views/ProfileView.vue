<template>
    <v-container class="profile-container">
        <v-row justify="center">
            <v-col cols="12" sm="8" md="6">
                <v-card class="profile-card" elevation="2">
                    <v-card-title class="profile-title">
                        <v-avatar color="primary" size="64" class="profile-avatar">
                            <v-icon v-if="!user.photo_url" color="white">mdi-account</v-icon>
                            <img v-else :src="user.photo_url" alt="User Avatar" class="avatar-image">
                        </v-avatar>
                        Профиль
                    </v-card-title>
                    
                    <v-card-text class="profile-content">
                        <v-list class="profile-list">
                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary">mdi-identifier</v-icon>
                                </template>
                                <v-list-item-title>Telegram ID</v-list-item-title>
                                <v-list-item-subtitle>{{ user.telegram_id }}</v-list-item-subtitle>
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
                                    <v-icon color="primary">mdi-email</v-icon>
                                </template>
                                <v-list-item-title>Email</v-list-item-title>
                                <v-list-item-subtitle>{{ user.email || 'Не указан' }}</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="profile-divider"></v-divider>

                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary">mdi-phone</v-icon>
                                </template>
                                <v-list-item-title>Телефон</v-list-item-title>
                                <v-list-item-subtitle>{{ user.phone || 'Не указан' }}</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="profile-divider"></v-divider>

                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary">mdi-map-marker</v-icon>
                                </template>
                                <v-list-item-title>Адрес</v-list-item-title>
                                <v-list-item-subtitle>{{ user.address || 'Не указан' }}</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="profile-divider"></v-divider>

                            <v-list-item class="profile-list-item">
                                <template v-slot:prepend>
                                    <v-icon color="success">mdi-calendar</v-icon>
                                </template>
                                <v-list-item-title>Дата регистрации</v-list-item-title>
                                <v-list-item-subtitle>{{ formatDate(user.created_at) }}</v-list-item-subtitle>
                            </v-list-item>
                        </v-list>
                    </v-card-text>
                </v-card>

                <!-- Статистика заказов -->
                <v-card class="stats-card mt-4" elevation="2">
                    <v-card-title class="stats-title">
                        <v-icon color="primary" class="mr-2">mdi-chart-box</v-icon>
                        Статистика
                    </v-card-title>
                    <v-card-text class="stats-content">
                        <v-row class="text-center">
                            <v-col cols="6">
                                <div class="stat-number">{{ ordersCount }}</div>
                                <div class="stat-label">Всего заказов</div>
                            </v-col>
                            <v-col cols="6">
                                <div class="stat-number">{{ completedOrdersCount }}</div>
                                <div class="stat-label">Завершенных</div>
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import '@/assets/styles/components/profile-view.css'

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
            loading: false
        }
    },
    async mounted() {
        await this.fetchUserProfile()
        await this.fetchUserStats()
        
        // Для Telegram user photo
        if (window.Telegram?.WebApp) {
            const tgUser = window.Telegram.WebApp.initDataUnsafe?.user
            if (tgUser?.photo_url) {
                this.user.photo_url = tgUser.photo_url
            }
            // Используем данные из Telegram, если нет в базе
            if (!this.user.name && tgUser?.first_name) {
                this.user.name = tgUser.first_name
                if (tgUser.last_name) {
                    this.user.name += ' ' + tgUser.last_name
                }
            }
            if (!this.user.username && tgUser?.username) {
                this.user.username = '@' + tgUser.username
            }
        }
    },
    methods: {
        async fetchUserProfile() {
            this.loading = true
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user
                if (!tg_user) {
                    console.error('Telegram user not found')
                    return
                }

                // Получаем данные пользователя из бэкенда
                const response = await fetch(`/api/users/${tg_user.id}`)
                if (response.ok) {
                    const userData = await response.json()
                    this.user = { ...this.user, ...userData }
                } else if (response.status === 404) {
                    // Если пользователь не найден, создаем нового
                    await this.createUser(tg_user)
                } else {
                    console.error('Ошибка загрузки профиля')
                }
            } catch (error) {
                console.error('Ошибка:', error)
            }
            this.loading = false
        },

        async createUser(tgUser) {
            try {
                const response = await fetch('/api/users/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        telegram_id: tgUser.id,
                        username: tgUser.username ? `@${tgUser.username}` : null,
                        name: tgUser.first_name + (tgUser.last_name ? ` ${tgUser.last_name}` : '')
                    })
                })

                if (response.ok) {
                    const userData = await response.json()
                    this.user = { ...this.user, ...userData }
                }
            } catch (error) {
                console.error('Ошибка создания пользователя:', error)
            }
        },

        async fetchUserStats() {
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user
                if (!tg_user) return

                // Получаем статистику заказов
                const response = await fetch(`/api/users/${tg_user.id}/stats`)
                if (response.ok) {
                    const stats = await response.json()
                    this.ordersCount = stats.total_orders || 0
                    this.completedOrdersCount = stats.completed_orders || 0
                }
            } catch (error) {
                console.error('Ошибка загрузки статистики:', error)
            }
        },

        formatDate(dateString) {
            if (!dateString) return 'Неизвестно'
            const date = new Date(dateString)
            return date.toLocaleDateString('ru-RU', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            })
        }
    }
}
</script>