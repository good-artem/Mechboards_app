<template>
    <v-container class="services-container">
        <v-row>
            <v-col cols="12">
                <v-card class="services-header pa-4" elevation="2">
                    <v-card-title class="d-flex align-center">
                        <v-icon size="28" color="primary" class="mr-2">mdi-tools</v-icon>
                        <span class="text-h5 font-weight-bold">Наши услуги</span>
                        <v-spacer></v-spacer>
                        <v-btn 
                            color="primary" 
                            variant="tonal"
                            @click="openSupportChat"
                        >
                            <v-icon left>mdi-message-text</v-icon>
                            Связаться с поддержкой
                        </v-btn>
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
                                    <div class="d-flex">
                                        <div class="service-icon mr-4">
                                            <v-avatar size="50" rounded="lg" color="primary" class="d-flex align-center justify-center">
                                                <v-icon size="24" color="white">mdi-wrench</v-icon>
                                            </v-avatar>
                                        </div>
                                        <div class="service-details flex-grow-1">
                                            <div class="service-name text-h6 font-weight-medium mb-1">
                                                {{ service.name }}
                                            </div>
                                            <div class="service-description text-body-2 text-grey mb-3">
                                                {{ service.description }}
                                            </div>
                                            <div class="d-flex align-center justify-space-between">
                                                <div class="service-price text-h6 font-weight-bold primary--text">
                                                    {{ formatPrice(service.price) }}
                                                </div>
                                                <v-btn 
                                                    color="primary" 
                                                    variant="tonal"
                                                    @click="openAddToCartDialog(service)"
                                                >
                                                    <v-icon left>mdi-cart-plus</v-icon>
                                                    Добавить в корзину
                                                </v-btn>
                                            </div>
                                            <div v-if="service.duration" class="service-duration mt-2 text-caption text-grey">
                                                Примерное время выполнения: {{ service.duration }}
                                            </div>
                                        </div>
                                    </div>
                                </v-card-text>
                            </v-card>
                        </v-list-item>
                    </v-list>
                </div>
                
                <!-- Пустой экран если услуг нет -->
                <div v-else class="empty-services text-center pa-8">
                    <v-icon size="64" color="grey-lighten-1">mdi-wrench</v-icon>
                    <div class="text-h6 mt-4">Услуги не найдены</div>
                    <div class="text-body-1 mt-2">Скоро здесь появятся услуги по обслуживанию клавиатур</div>
                </div>
                
                <!-- Диалог добавления услуги в корзину -->
                <v-dialog v-model="addToCartDialog" max-width="500">
                    <v-card>
                        <v-card-title class="pa-4">
                            <v-icon class="mr-2">mdi-cart-plus</v-icon>
                            Добавить услугу в корзину: {{ selectedService?.name }}
                        </v-card-title>
                        <v-card-text class="pa-4">
                            <div class="service-description mb-4">
                                <span class="font-weight-medium">Описание:</span>
                                {{ selectedService?.description }}
                            </div>
                            
                            <div class="mb-3">
                                <div class="font-weight-medium mb-1">Количество:</div>
                                <v-text-field
                                    v-model.number="serviceQuantity"
                                    type="number"
                                    min="1"
                                    variant="outlined"
                                    density="comfortable"
                                    hide-details
                                ></v-text-field>
                            </div>
                            
                            <v-textarea
                                v-model="serviceNotes"
                                label="Комментарий к услуге"
                                placeholder="Опишите детали. Например: количество свитчей для смазки, особенности проблемы и т.д."
                                rows="3"
                                auto-grow
                                variant="outlined"
                                density="comfortable"
                            ></v-textarea>
                            
                            <div class="text-h6 font-weight-bold primary--text text-right mt-3">
                                Стоимость: {{ formatPrice(selectedService?.price || 0) }}
                            </div>
                        </v-card-text>
                        <v-card-actions class="pa-4">
                            <v-spacer></v-spacer>
                            <v-btn color="grey" variant="text" @click="addToCartDialog = false">Отмена</v-btn>
                            <v-btn 
                                color="primary" 
                                @click="addServiceToCart"
                                :loading="addingToCart"
                            >
                                <v-icon left>mdi-cart-plus</v-icon>
                                Добавить в корзину
                            </v-btn>
                        </v-card-actions>
                    </v-card>
                </v-dialog>
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
            addToCartDialog: false,
            selectedService: null,
            serviceQuantity: 1,
            serviceNotes: '',
            addingToCart: false
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
        
        openAddToCartDialog(service) {
            this.selectedService = service;
            this.serviceQuantity = 1;
            this.serviceNotes = '';
            this.addToCartDialog = true;
        },
        
        async addServiceToCart() {
            this.addingToCart = true;
            try {
                const { post } = useApi();
                const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
                const telegramId = tg_user?.id || 391622124;
                
                const result = await post('/api/cart/add_service', {
                    telegram_id: telegramId,
                    service_id: this.selectedService.service_id,
                    quantity: this.serviceQuantity,
                    notes: this.serviceNotes
                });
                
                this.$root.$emit('show-message', `Услуга "${this.selectedService.name}" добавлена в корзину!`, 'success');
                this.$root.$emit('cart-updated');
                this.addToCartDialog = false;
            } catch (error) {
                console.error('❌ Ошибка добавления услуги в корзину:', error);
                this.$root.$emit('show-message', 'Ошибка добавления услуги в корзину', 'error');
            } finally {
                this.addingToCart = false;
            }
        },
        
        openSupportChat() {
            // Открываем чат с ботом через ссылку
            const botUsername = 'your_bot_username'; // Замените на username вашего бота
            const supportUrl = `https://t.me/${botUsername}`;
            
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.openTelegramLink(supportUrl);
            } else {
                // Для разработки - открываем в новом окне
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
    transition: transform 0.2s ease;
}

.service-card:hover {
    transform: translateY(-2px);
}

.service-icon {
    flex-shrink: 0;
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
</style>