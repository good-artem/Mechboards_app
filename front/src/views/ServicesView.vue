<template>
    <v-container class="services-container">
        <v-row>
            <v-col cols="12">
                <v-card class="services-header pa-4" elevation="2">
                    <v-card-title class="d-flex align-center">
                        <v-icon size="28" color="primary" class="mr-2">mdi-tools</v-icon>
                        <span class="text-h5 font-weight-bold">Наши услуги</span>
                    </v-card-title>
                    <v-card-subtitle>
                        Профессиональные услуги по обслуживанию механических клавиатур
                    </v-card-subtitle>
                </v-card>
                
                <!-- Список услуг -->
                <div v-if="services.length > 0" class="services-list mt-4">
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
                
                <!-- Кнопка "Связаться с нами" как отдельная услуга на всю ширину -->
                <v-card class="mt-4 pa-4" elevation="1">
                    <div class="d-flex align-center justify-space-between">
                        <div>
                            <div class="text-h6 font-weight-medium">Нужна помощь?</div>
                            <div class="text-body-2 text-grey">Свяжитесь с нами в Telegram</div>
                        </div>
                        <v-btn 
                            color="primary"
                            @click="openSupportChat"
                            variant="tonal"
                        >
                            <v-icon left>mdi-message-text</v-icon>
                            Написать
                        </v-btn>
                    </div>
                </v-card>
                
                <!-- Пустой экран если услуг нет -->
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import { useApi } from '@/composables/useApi'
import '@/assets/styles/components/services-view.css'

export default {
    name: 'ServicesView',
    data() {
        return {
            services: [],
            loading: false,
            addingServiceId: null
        }
    },
    async mounted() {
        await this.fetchServices();
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
                
                this.$root.$emit('show-message', `Услуга "${service.name}" добавлена в корзину!`, 'success');
                this.$root.$emit('cart-updated');
            } catch (error) {
                console.error('❌ Ошибка добавления услуги в корзину:', error);
                this.$root.$emit('show-message', 'Ошибка добавления услуги в корзину', 'error');
            } finally {
                this.addingServiceId = null;
            }
        },
        
        openSupportChat() {
            // Замените 'your_bot_username' на username вашего бота
            const botUsername = 'MechboardsBot';
            const supportUrl = `https://t.me/${botUsername}`;
            
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.openTelegramLink(supportUrl);
            } else {
                window.open(supportUrl, '_blank');
            }
        }
    }
}
</script>

<style scoped>
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
</style>