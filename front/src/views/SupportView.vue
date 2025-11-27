<template>
    <v-container class="support-container">
        <v-row>
            <v-col cols="12">
                <!-- Заголовок -->
                <v-card class="support-header text-center pa-6 mb-4">
                    <v-icon size="64" color="primary" class="mb-4">mdi-tools</v-icon>
                    <v-card-title class="justify-center support-title">
                        Сервис и поддержка
                    </v-card-title>
                    <v-card-text class="support-subtitle">
                        Профессиональное обслуживание ваших механических клавиатур
                    </v-card-text>
                </v-card>

                <!-- Услуги -->
                <v-card class="services-card pa-4 mb-4">
                    <v-card-title class="services-title">
                        <v-icon color="primary" class="mr-2">mdi-cog</v-icon>
                        Наши услуги
                    </v-card-title>
                    <v-card-text>
                        <v-list class="services-list">
                            <v-list-item class="service-item">
                                <template v-slot:prepend>
                                    <v-icon color="green" class="service-icon">mdi-bottle-tonic</v-icon>
                                </template>
                                <v-list-item-title>Смазка свитчей</v-list-item-title>
                                <v-list-item-subtitle>Профессиональная смазка механических переключателей</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="service-divider"></v-divider>

                            <v-list-item class="service-item">
                                <template v-slot:prepend>
                                    <v-icon color="blue" class="service-icon">mdi-keyboard</v-icon>
                                </template>
                                <v-list-item-title>Замена свитчей</v-list-item-title>
                                <v-list-item-subtitle>Полная замена переключателей на новые</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="service-divider"></v-divider>

                            <v-list-item class="service-item">
                                <template v-slot:prepend>
                                    <v-icon color="orange" class="service-icon">mdi-wrench</v-icon>
                                </template>
                                <v-list-item-title>Ремонт и диагностика</v-list-item-title>
                                <v-list-item-subtitle>Выявление и устранение неисправностей</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="service-divider"></v-divider>

                            <v-list-item class="service-item">
                                <template v-slot:prepend>
                                    <v-icon color="purple" class="service-icon">mdi-palette</v-icon>
                                </template>
                                <v-list-item-title>Моддинг и кастомизация</v-list-item-title>
                                <v-list-item-subtitle>Улучшение и персонализация вашей клавиатуры</v-list-item-subtitle>
                            </v-list-item>
                        </v-list>
                    </v-card-text>
                </v-card>

                <!-- Контактная информация -->
                <v-card class="contact-card pa-4">
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
                                <v-list-item-subtitle>+7 (999) 123-45-67</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="contact-divider"></v-divider>

                            <v-list-item class="contact-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary" class="contact-icon">mdi-email</v-icon>
                                </template>
                                <v-list-item-title>Email</v-list-item-title>
                                <v-list-item-subtitle>support@mechboards.ru</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider class="contact-divider"></v-divider>

                            <v-list-item class="contact-item">
                                <template v-slot:prepend>
                                    <v-icon color="primary" class="contact-icon">mdi-map-marker</v-icon>
                                </template>
                                <v-list-item-title>Адрес сервиса</v-list-item-title>
                                <v-list-item-subtitle>г. Москва, ул. Клавиатурная, д. 123</v-list-item-subtitle>
                            </v-list-item>
                        </v-list>
                    </v-card-text>
                </v-card>

                <!-- Заглушка для будущего функционала -->
                <v-card class="coming-soon-card pa-4 mt-4 text-center">
                    <v-card-text>
                        <v-icon size="48" color="grey" class="mb-2">mdi-hammer-wrench</v-icon>
                        <div class="text-h6 mb-2">Функционал заявок в разработке</div>
                        <div class="text-body-2">
                            Скоро вы сможете создавать заявки на обслуживание прямо здесь
                        </div>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import '@/assets/styles/components/support-view.css'

export default {
    name: 'SupportView',
    data() {
        return {
            // Здесь в будущем будет данные для формы заявки
        }
    }
}
</script>