<template>
    <div class="news-carousel-container">
        <div class="news-carousel">
            <div class="news-scroll">
                <div 
                    v-for="news in newsItems" 
                    :key="news.id"
                    class="news-item"
                    @click="openNews(news)"
                >
                    <div class="news-icon-container">
                        <v-icon class="news-icon">{{ news.icon }}</v-icon>
                    </div>
                    <span class="news-text">{{ news.title }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import '@/assets/styles/components/news-carousel.css'

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
        }
    }
}
</script>
