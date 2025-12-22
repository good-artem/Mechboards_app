<template>
    <v-container class="services-container">
        <v-row>
            <v-col cols="12">
                <v-card class="services-header pa-4" elevation="2">
                    <v-card-title class="d-flex align-center">
                        <v-icon size="28" color="primary" class="mr-2">mdi-tools</v-icon>
                        <span class="text-h5 font-weight-bold">Услуги и поддержка</span>
                    </v-card-title>
                    <v-card-subtitle>
                        Профессиональные услуги по обслуживанию механических клавиатур
                    </v-card-subtitle>
                </v-card>
                
                <!-- Вкладки -->
                <v-tabs v-model="activeTab" color="primary" class="mt-4">
                    <v-tab value="services">Услуги</v-tab>
                    <v-tab value="support">Поддержка</v-tab>
                </v-tabs>
                
                <!-- Контент вкладок -->
                <v-window v-model="activeTab" class="mt-4" :touch="false">
                    <!-- Вкладка Услуг -->
                    <v-window-item value="services">
                        <div v-if="services.length > 0" class="services-list">
                            <v-list class="pa-0">
                                <v-list-item
                                    v-for="service in services"
                                    :key="service.service_id"
                                    class="service-item mb-2"
                                >
                                    <v-card class="service-card" elevation="1">
                                        <v-card-text class="pa-4">
                                            <div class="d-flex align-center justify-space-between">
                                                <div class="service-details flex-grow-1">
                                                    <div class="service-name text-h6 font-weight-medium mb-1">
                                                        {{ service.name }}
                                                    </div>
                                                    <div class="service-description text-body-2 text-grey mb-2">
                                                        {{ service.description }}
                                                    </div>
                                                    <div v-if="service.duration" class="service-duration text-caption text-grey">
                                                        Примерное время выполнения: {{ service.duration }}
                                                    </div>
                                                    <div class="service-price text-h6 font-weight-bold primary--text mt-2">
                                                        {{ formatPrice(service.price) }}
                                                    </div>
                                                </div>
                                                <div class="service-actions ml-4">
                                                    <v-btn 
                                                        color="primary" 
                                                        icon
                                                        @click="addServiceToCartDirectly(service)"
                                                        size="small"
                                                        variant="tonal"
                                                        :loading="addingServiceId === service.service_id"
                                                    >
                                                        <v-icon>mdi-cart-plus</v-icon>
                                                    </v-btn>
                                                </div>
                                            </div>
                                        </v-card-text>
                                    </v-card>
                                </v-list-item>
                            </v-list>
                        </div>
                        
                        <!-- Если услуг нет -->
                        <div v-else class="text-center pa-8">
                            <v-icon size="64" color="grey-lighten-1">mdi-tools</v-icon>
                            <div class="text-h6 mt-4">Услуги временно недоступны</div>
                        </div>
                    </v-window-item>
                    
                    <!-- Вкладка Поддержки -->
                    <v-window-item value="support">
                        <!-- Кнопка "Написать в поддержку" -->
                        <v-card class="support-action-card pa-4 mb-4 text-center">
                            <v-card-text>
                                <v-btn 
                                    color="primary" 
                                    size="x-large"
                                    @click="showTicketDialog = true"
                                    class="write-support-btn"
                                    block
                                >
                                    <v-icon left>mdi-message-text</v-icon>
                                    Написать в поддержку
                                </v-btn>
                                <div class="text-body-2 mt-2">
                                    Ответим на все ваши вопросы по товарам, услугам и заказам
                                </div>
                            </v-card-text>
                        </v-card>
                        
                        <!-- Мои обращения -->
                        <v-card v-if="myTickets.length > 0" class="my-tickets-card pa-4 mb-4">
                            <v-card-title class="my-tickets-title">
                                <v-icon color="primary" class="mr-2">mdi-email</v-icon>
                                Мои обращения
                            </v-card-title>
                            <v-card-text>
                                <v-list class="tickets-list">
                                    <v-list-item
                                        v-for="ticket in myTickets"
                                        :key="ticket.ticket_id"
                                        class="ticket-item"
                                        @click="viewTicketMessages(ticket)"
                                        :disabled="loadingMessages"
                                    >
                                        <template v-slot:prepend>
                                            <v-avatar 
                                                :color="getTicketStatusColor(ticket.status)" 
                                                size="40"
                                            >
                                                <v-icon color="white">mdi-help-circle</v-icon>
                                            </v-avatar>
                                        </template>
                                        
                                        <div class="ticket-content">
                                            <div class="ticket-subject font-weight-medium">
                                                {{ ticket.subject }}
                                            </div>
                                            <div class="ticket-info">
                                                <v-chip 
                                                    :color="getTicketStatusColor(ticket.status)" 
                                                    size="small"
                                                    class="mr-2"
                                                >
                                                    {{ getTicketStatusText(ticket.status) }}
                                                </v-chip>
                                                <span class="text-caption text-grey">
                                                    {{ formatDate(ticket.updated_at) }}
                                                </span>
                                            </div>
                                            <div v-if="ticket.last_message" class="ticket-preview text-caption text-grey">
                                                {{ truncateText(ticket.last_message, 60) }}
                                            </div>
                                        </div>
                                        
                                        <template v-slot:append>
                                            <v-icon>mdi-chevron-right</v-icon>
                                        </template>
                                    </v-list-item>
                                </v-list>
                            </v-card-text>
                        </v-card>
                        
                        <!-- Контактная информация -->
                        <v-card class="contact-card pa-4 mb-4">
                            <v-card-title class="contact-title">
                                <v-icon color="primary" class="mr-2">mdi-information</v-icon>
                                Контакты и информация
                            </v-card-title>
                            <v-card-text>
                                <v-list class="contact-list">
                                    <v-list-item class="contact-item">
                                        <template v-slot:prepend>
                                            <v-icon color="primary" class="contact-icon">mdi-clock</v-icon>
                                        </template>
                                        <v-list-item-title>Время работы</v-list-item-title>
                                        <v-list-item-subtitle>Пн-Пт: 10:00-19:00, Сб: 11:00-17:00</v-list-item-subtitle>
                                    </v-list-item>

                                    <v-divider class="contact-divider"></v-divider>

                                    <v-list-item class="contact-item">
                                        <template v-slot:prepend>
                                            <v-icon color="primary" class="contact-icon">mdi-phone</v-icon>
                                        </template>
                                        <v-list-item-title>Телефон</v-list-item-title>
                                        <v-list-item-subtitle>+375 (321) 123-45-67</v-list-item-subtitle>
                                    </v-list-item>

                                    <v-divider class="contact-divider"></v-divider>

                                    <v-list-item class="contact-item">
                                        <template v-slot:prepend>
                                            <v-icon color="primary" class="contact-icon">mdi-email</v-icon>
                                        </template>
                                        <v-list-item-title>Email</v-list-item-title>
                                        <v-list-item-subtitle>supportmechboards@gmail.com</v-list-item-subtitle>
                                    </v-list-item>

                                    <v-divider class="contact-divider"></v-divider>

                                    <v-list-item class="contact-item">
                                        <template v-slot:prepend>
                                            <v-icon color="primary" class="contact-icon">mdi-map-marker</v-icon>
                                        </template>
                                        <v-list-item-title>Адрес сервиса</v-list-item-title>
                                        <v-list-item-subtitle>г. Минск, ул. Клавиатурная, д. 123</v-list-item-subtitle>
                                    </v-list-item>
                                </v-list>
                            </v-card-text>
                        </v-card>
                    </v-window-item>
                </v-window>
            </v-col>
        </v-row>

        <!-- Диалог создания тикета -->
        <v-dialog v-model="showTicketDialog" max-width="500">
            <v-card>
                <v-card-title class="d-flex justify-space-between align-center">
                    <span>Новое обращение в поддержку</span>
                    <v-btn icon @click="showTicketDialog = false">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </v-card-title>
                <v-card-text>
                    <v-select
                        v-model="newTicket.subject"
                        :items="ticketSubjects"
                        label="Тема обращения"
                        variant="outlined"
                        density="comfortable"
                        class="mb-3"
                        :rules="[v => !!v || 'Выберите тему']"
                    ></v-select>
                    
                    <v-textarea
                        v-model="newTicket.message"
                        label="Сообщение"
                        variant="outlined"
                        density="comfortable"
                        rows="4"
                        placeholder="Опишите вашу проблему или вопрос подробно..."
                        :rules="[v => !!v || 'Введите сообщение']"
                        class="mb-3"
                        counter
                        maxlength="1000"
                    ></v-textarea>
                    
                    <div class="text-caption text-grey">
                        Мы ответим вам в течение 24 часов. Ответ придёт через Telegram бота.
                    </div>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn 
                        color="grey" 
                        variant="text" 
                        @click="showTicketDialog = false"
                        :disabled="creatingTicket"
                    >
                        Отмена
                    </v-btn>
                    <v-btn 
                        color="primary" 
                        @click="createTicket"
                        :loading="creatingTicket"
                        :disabled="!newTicket.subject || !newTicket.message"
                    >
                        Отправить
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- Диалог просмотра тикета -->
        <v-dialog v-model="showMessagesDialog" max-width="600" fullscreen>
            <v-card class="ticket-messages-dialog">
                <v-card-title class="d-flex justify-space-between align-center sticky-header">
                    <div>
                        <div class="text-h6">{{ selectedTicket?.subject }}</div>
                        <div class="text-caption text-grey">
                            Статус: {{ getTicketStatusText(selectedTicket?.status) }}
                        </div>
                    </div>
                    <v-btn icon @click="showMessagesDialog = false">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </v-card-title>
                
                <v-card-text class="messages-container">
                    <!-- Сообщения -->
                    <div v-if="ticketMessages.length > 0" class="messages-list">
                        <div 
                            v-for="message in ticketMessages" 
                            :key="message.message_id"
                            class="message-item"
                            :class="{'message-from-admin': message.is_from_admin}"
                        >
                            <div class="message-header">
                                <div class="message-sender">
                                    <v-icon small class="mr-1">
                                        {{ message.is_from_admin ? 'mdi-shield-account' : 'mdi-account' }}
                                    </v-icon>
                                    {{ message.is_from_admin ? 'Поддержка' : 'Вы' }}
                                </div>
                                <div class="message-time">
                                    {{ formatDateTime(message.created_at) }}
                                </div>
                            </div>
                            <div class="message-content">
                                {{ message.message }}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Нет сообщений -->
                    <div v-else class="text-center py-8">
                        <v-icon size="48" color="grey">mdi-message-off</v-icon>
                        <div class="text-h6 mt-4">Нет сообщений</div>
                    </div>
                </v-card-text>
                
                <!-- Форма ответа (только для открытых тикетов) -->
                <v-card-actions v-if="selectedTicket?.status !== 'closed'" class="sticky-footer">
                    <v-textarea
                        v-model="replyMessage"
                        label="Ответить"
                        variant="outlined"
                        density="comfortable"
                        rows="2"
                        placeholder="Напишите ваш ответ..."
                        auto-grow
                        hide-details
                        class="mr-2"
                    ></v-textarea>
                    <v-btn 
                        color="primary" 
                        @click="sendReply"
                        :loading="sendingReply"
                        :disabled="!replyMessage.trim()"
                        icon
                        size="large"
                    >
                        <v-icon>mdi-send</v-icon>
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- Уведомление -->
        <v-snackbar v-model="showSnackbar" :color="snackbarColor" :timeout="3000">
            {{ snackbarMessage }}
        </v-snackbar>
    </v-container>
</template>

<script>
import { useApi } from '@/composables/useApi'

export default {
    name: 'ServicesView',
    data() {
        return {
            // Данные для услуг
            services: [],
            loading: false,
            addingServiceId: null,
            
            // Данные для поддержки
            activeTab: 'services',
            myTickets: [],
            showTicketDialog: false,
            showMessagesDialog: false,
            creatingTicket: false,
            loadingMessages: false,
            sendingReply: false,
            selectedTicket: null,
            ticketMessages: [],
            replyMessage: '',
            newTicket: {
                subject: '',
                message: ''
            },
            ticketSubjects: [
                'Вопрос о товаре',
                'Вопрос об услуге',
                'Проблема с заказом',
                'Техническая проблема',
                'Сотрудничество',
                'Другое'
            ],
            showSnackbar: false,
            snackbarMessage: '',
            snackbarColor: 'success'
        }
    },
    async mounted() {
        await this.fetchServices();
        // Загружаем тикеты, если пользователь уже был на вкладке поддержки
        await this.loadMyTickets();
    },
    methods: {
        formatPrice(price) {
            return new Intl.NumberFormat('ru-BY', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(price) + ' р.';
        },
        
        async fetchServices() {
            this.loading = true;
            try {
                const { get } = useApi();
                const services = await get('/api/services');
                this.services = services;
            } catch (error) {
                console.error('❌ Ошибка загрузки услуг:', error);
                this.services = this.getFallbackServices();
            } finally {
                this.loading = false;
            }
        },
        
        getFallbackServices() {
            return [
                {
                    service_id: 1,
                    name: "Ремонт клавиатуры",
                    description: "Диагностика и ремонт неисправностей механической клавиатуры",
                    price: 1500.00,
                    duration: "1-3 дня"
                },
                {
                    service_id: 2,
                    name: "Чистка клавиатуры",
                    description: "Глубокая очистка от пыли и загрязнений",
                    price: 800.00,
                    duration: "1 день"
                },
                {
                    service_id: 3,
                    name: "Смазка свитчей",
                    description: "Профессиональная смазка механических переключателей",
                    price: 1200.00,
                    duration: "2-4 дня"
                },
                {
                    service_id: 4,
                    name: "Смазка стабилизаторов",
                    description: "Смазка и настройка стабилизаторов для длинных клавиш",
                    price: 600.00,
                    duration: "1 день"
                },
                {
                    service_id: 5,
                    name: "Шумоизоляция/виброизоляция",
                    description: "Установка материалов для снижения шума и вибрации",
                    price: 900.00,
                    duration: "1-2 дня"
                },
                {
                    service_id: 6,
                    name: "Сборка клавиатуры",
                    description: "Полная сборка механической клавиатуры из комплектующих",
                    price: 2000.00,
                    duration: "3-5 дней"
                }
            ];
        },
        
        async addServiceToCartDirectly(service) {
            this.addingServiceId = service.service_id;
            try {
                const { post } = useApi();
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                const telegramId = tg_user?.id || 391622124;
                
                await post('/api/cart/add_service', {
                    telegram_id: telegramId,
                    service_id: service.service_id,
                    quantity: 1,
                    notes: ''
                });
                
                this.showMessage(`Услуга "${service.name}" добавлена в корзину!`, 'success');
                this.$root.$emit('cart-updated');
            } catch (error) {
                console.error('❌ Ошибка добавления услуги в корзину:', error);
                this.showMessage('Ошибка добавления услуги в корзину', 'error');
            } finally {
                this.addingServiceId = null;
            }
        },
        
        // Методы для поддержки
        getTicketStatusColor(status) {
            const colors = {
                'open': 'orange',
                'pending': 'blue',
                'closed': 'green'
            }
            return colors[status] || 'grey'
        },
        
        getTicketStatusText(status) {
            const texts = {
                'open': 'Открыт',
                'pending': 'В обработке',
                'closed': 'Закрыт'
            }
            return texts[status] || status
        },
        
        formatDate(dateString) {
            if (!dateString) return ''
            const date = new Date(dateString)
            return date.toLocaleDateString('ru-RU')
        },
        
        formatDateTime(dateString) {
            if (!dateString) return ''
            const date = new Date(dateString)
            return date.toLocaleString('ru-RU')
        },
        
        truncateText(text, maxLength) {
            if (!text) return ''
            return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
        },
        
        async loadMyTickets() {
            try {
                const { get } = useApi()
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user
                const telegramId = tg_user?.id || 391622124
                
                // Используйте правильный endpoint с query параметром
                this.myTickets = await get(`/api/support/tickets?telegram_id=${telegramId}`)
            } catch (error) {
                console.error('Ошибка загрузки тикетов:', error)
            }
        },
        
        async createTicket() {
            if (!this.newTicket.subject || !this.newTicket.message) {
                this.showMessage('Заполните тему и сообщение', 'error')
                return
            }
            
            this.creatingTicket = true
            try {
                const { post } = useApi()
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user
                const telegramId = tg_user?.id || 391622124
                
                const response = await post('/api/support/tickets', {
                    telegram_id: telegramId,
                    subject: this.newTicket.subject,
                    message: this.newTicket.message
                })
                
                this.showMessage('Обращение создано!', 'success')
                this.showTicketDialog = false
                this.newTicket = { subject: '', message: '' }
                await this.loadMyTickets()
            } catch (error) {
                console.error('❌ Ошибка создания тикета:', error)
                this.showMessage('Ошибка создания обращения', 'error')
            } finally {
                this.creatingTicket = false
            }
        },
        
        async viewTicketMessages(ticket) {
            this.selectedTicket = ticket
            this.loadingMessages = true
            this.ticketMessages = []
            
            try {
                const { get } = useApi()
                this.ticketMessages = await get(`/api/support/tickets/${ticket.ticket_id}/messages`)
                this.showMessagesDialog = true
            } catch (error) {
                console.error('Ошибка загрузки сообщений:', error)
                this.showMessage('Не удалось загрузить сообщения', 'error')
            } finally {
                this.loadingMessages = false
            }
        },
        
        async sendReply() {
            if (!this.replyMessage.trim()) return
            
            this.sendingReply = true
            try {
                // Здесь нужен API для отправки сообщений пользователем
                // Пока просто обновим тикет
                this.showMessage('Сообщение отправлено', 'success')
                this.replyMessage = ''
                // Обновим сообщения
                await this.viewTicketMessages(this.selectedTicket)
            } catch (error) {
                console.error('Ошибка отправки ответа:', error)
                this.showMessage('Не удалось отправить ответ', 'error')
            } finally {
                this.sendingReply = false
            }
        },
        
        showMessage(message, type = 'success') {
            this.snackbarMessage = message
            this.snackbarColor = type === 'error' ? 'error' : type === 'warning' ? 'warning' : 'success'
            this.showSnackbar = true
            
            setTimeout(() => {
                this.showSnackbar = false
            }, 3000)
        }
    }
}
</script>

<style scoped>
.services-container {
    padding-bottom: 100px;
}

.services-header {
    border-radius: 16px;
}

.service-card {
    border-radius: 12px;
}

.service-details {
    min-width: 0;
}

.service-name {
    color: var(--tg-theme-text-color, #212121);
}

.service-description {
    color: var(--tg-theme-text-color, #212121);
    line-height: 1.4;
}

.service-price {
    color: var(--tg-theme-text-color, #212121);
}

.service-duration {
    color: var(--tg-theme-hint-color, #757575);
}

.service-actions {
    flex-shrink: 0;
}

/* Стили для поддержки */
.support-action-card {
    border-radius: 16px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.support-action-card .v-card-text {
    color: white;
}

.write-support-btn {
    height: 56px;
    font-size: 1.1rem;
}

.my-tickets-card {
    border-radius: 16px;
}

.ticket-item {
    border-radius: 12px;
    margin-bottom: 8px;
    transition: all 0.2s;
    cursor: pointer;
}

.ticket-item:hover {
    background-color: rgba(102, 126, 234, 0.05);
    transform: translateY(-2px);
}

.ticket-content {
    flex: 1;
}

.ticket-subject {
    font-size: 1rem;
    margin-bottom: 4px;
}

.ticket-info {
    display: flex;
    align-items: center;
    margin-bottom: 4px;
}

.ticket-preview {
    line-height: 1.4;
}

/* Стили для диалога сообщений */
.ticket-messages-dialog {
    height: 100vh;
    display: flex;
    flex-direction: column;
}

.sticky-header {
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
    border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

.messages-container {
    flex: 1;
    overflow-y: auto;
    padding-bottom: 80px;
}

.messages-list {
    padding: 16px 0;
}

.message-item {
    margin-bottom: 16px;
    padding: 12px 16px;
    border-radius: 12px;
    background-color: #f5f5f5;
    max-width: 80%;
}

.message-from-admin {
    margin-left: auto;
    background-color: #e3f2fd;
}

.message-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    font-size: 0.85rem;
}

.message-sender {
    font-weight: 500;
    display: flex;
    align-items: center;
}

.message-time {
    color: #757575;
    font-size: 0.75rem;
}

.message-content {
    line-height: 1.5;
    white-space: pre-wrap;
}

.sticky-footer {
    position: sticky;
    bottom: 0;
    background: white;
    padding: 12px;
    border-top: 1px solid rgba(0, 0, 0, 0.12);
    z-index: 10;
}

/* Стили для вкладок */
.v-tabs {
    border-radius: 12px;
    overflow: hidden;
}

.v-window {
    min-height: 300px;
}

/* Адаптивность */
@media (max-width: 600px) {
    .services-header {
        padding: 16px !important;
    }
    
    .support-action-card {
        padding: 16px !important;
    }
    
    .write-support-btn {
        height: 48px;
        font-size: 1rem;
    }
    
    .message-item {
        max-width: 90%;
    }
    
    .contact-item {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
}
</style>