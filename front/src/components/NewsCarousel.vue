<template>
    <div class="news-carousel">
        <v-card class="carousel-container" elevation="1" rounded="lg">
            <div class="news-scroll">
                <div 
                    v-for="news in newsItems" 
                    :key="news.id"
                    class="news-item"
                    @click="openNews(news)"
                >
                    <v-icon class="news-icon" size="small">{{ news.icon }}</v-icon>
                    <span class="news-text">{{ news.title }}</span>
                </div>
            </div>
        </v-card>
    </div>
</template>

<script>
export default {
    name: "NewsCarousel",
    data() {
        return {
            newsItems: [
                { id: 1, title: 'Новые клавиатуры', icon: 'mdi-keyboard', url: '#' },
                { id: 2, title: 'Скидки 20%', icon: 'mdi-sale', url: '#' },
                { id: 3, title: 'Доставка за 24ч', icon: 'mdi-truck-fast', url: '#' },
                { id: 4, title: 'Кейкапы', icon: 'mdi-circle-multiple', url: '#' },
                { id: 5, title: 'Аксессуары', icon: 'mdi-cable-data', url: '#' }
            ]
        }
    },
    methods: {
        openNews(news) {
            console.log('Opening news:', news.title)
            // Навигация или открытие модального окна
        }
    }
}
</script>

<style scoped>
.news-carousel {
    margin: 8px 16px;
}

.carousel-container {
    padding: 12px 8px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.news-scroll {
    display: flex;
    overflow-x: auto;
    gap: 16px;
    padding: 4px 0;
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* IE and Edge */
}

.news-scroll::-webkit-scrollbar {
    display: none; /* Chrome, Safari and Opera */
}

.news-item {
    flex: 0 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 80px;
    height: 70px; /* На 10% больше навбара */
    background: rgba(255, 255, 255, 0.9);
    border-radius: 12px;
    padding: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.news-item:hover {
    background: rgba(255, 255, 255, 1);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.news-icon {
    margin-bottom: 4px;
    color: #667eea;
}

.news-text {
    font-size: 0.75rem;
    font-weight: 500;
    text-align: center;
    color: #333;
    line-height: 1.2;
}
</style>