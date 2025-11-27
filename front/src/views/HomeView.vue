<template>
    <v-container class="home-container">
        <!-- Заголовок -->
        <v-row justify="center" class="mb-4">
            <v-col cols="12" class="text-center">
                <v-icon size="56" color="primary" class="mb-2">mdi-keyboard</v-icon>
                <h1 class="text-h5 font-weight-bold">Mechboards Shop</h1>
                <p class="text-body-2 text-medium-emphasis mt-2">
                    Магазин механических клавиатур и аксессуаров
                </p>
            </v-col>
        </v-row>

        <!-- Карточки возможностей -->
        <v-row class="features-grid">
            <v-col cols="6" class="pa-1">
                <v-card class="feature-card" elevation="2" @click="$router.push('/catalog')">
                    <v-card-text class="text-center pa-3">
                        <v-icon size="32" color="primary" class="mb-2">mdi-view-grid</v-icon>
                        <div class="text-caption font-weight-medium">Каталог</div>
                        <div class="text-caption text-medium-emphasis mt-1">
                            Тысячи товаров для энтузиастов
                        </div>
                    </v-card-text>
                </v-card>
            </v-col>

            <v-col cols="6" class="pa-1">
                <v-card class="feature-card" elevation="2" @click="$router.push('/cart')">
                    <v-card-text class="text-center pa-3">
                        <v-icon size="32" color="green" class="mb-2">mdi-cart</v-icon>
                        <div class="text-caption font-weight-medium">Корзина</div>
                        <div class="text-caption text-medium-emphasis mt-1">
                            Быстрое оформление заказа
                        </div>
                    </v-card-text>
                </v-card>
            </v-col>

            <v-col cols="6" class="pa-1">
                <v-card class="feature-card" elevation="2" @click="$router.push('/profile')">
                    <v-card-text class="text-center pa-3">
                        <v-icon size="32" color="orange" class="mb-2">mdi-account</v-icon>
                        <div class="text-caption font-weight-medium">Профиль</div>
                        <div class="text-caption text-medium-emphasis mt-1">
                            История заказов и бонусы
                        </div>
                    </v-card-text>
                </v-card>
            </v-col>

            <v-col cols="6" class="pa-1">
                <v-card class="feature-card" elevation="2" @click="$router.push('/support')">
                    <v-card-text class="text-center pa-3">
                        <v-icon size="32" color="blue" class="mb-2">mdi-tools</v-icon>
                        <div class="text-caption font-weight-medium">Поддержка</div>
                        <div class="text-caption text-medium-emphasis mt-1">
                            Консультации и помощь
                        </div>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>

        <!-- Преимущества -->
        <v-row class="mt-6">
            <v-col cols="12">
                <v-card class="benefits-card" elevation="1">
                    <v-card-text class="pa-3">
                        <div class="text-caption font-weight-bold text-center mb-2">
                            Почему выбирают нас?
                        </div>
                        <v-list density="compact" class="benefits-list">
                            <v-list-item class="benefit-item">
                                <template v-slot:prepend>
                                    <v-icon size="20" color="success">mdi-check-circle</v-icon>
                                </template>
                                <v-list-item-title class="text-caption">
                                    Только оригинальная продукция
                                </v-list-item-title>
                            </v-list-item>
                            <v-list-item class="benefit-item">
                                <template v-slot:prepend>
                                    <v-icon size="20" color="success">mdi-check-circle</v-icon>
                                </template>
                                <v-list-item-title class="text-caption">
                                    Быстрая доставка по РФ
                                </v-list-item-title>
                            </v-list-item>
                            <v-list-item class="benefit-item">
                                <template v-slot:prepend>
                                    <v-icon size="20" color="success">mdi-check-circle</v-icon>
                                </template>
                                <v-list-item-title class="text-caption">
                                    Гарантия на все товары
                                </v-list-item-title>
                            </v-list-item>
                        </v-list>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>

        <!-- Призыв к действию -->
        <v-row class="mt-4">
            <v-col cols="12" class="text-center">
                <v-btn 
                    color="primary" 
                    variant="flat" 
                    size="large"
                    @click="$router.push('/catalog')"
                    class="cta-button"
                    block
                >
                    <v-icon left>mdi-shopping</v-icon>
                    Начать покупки
                </v-btn>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import '@/assets/styles/components/home-view.css'

export default {
    name: 'HomeView'
}
</script>