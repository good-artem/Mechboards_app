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
                    <v-icon class="news-icon" size="small">{{ news.icon }}</v-icon>
                    <span class="news-text">{{ news.title }}</span>
                </div>
            </div>
        </div>
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
        }
    }
}
</script>

<style scoped>
.news-carousel-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}
    /* background: var(--tg-theme-bg-color, #ffffff);
    border-bottom: 1px solid #e0e0e0;
} */

.news-carousel {
    height: 150px;
    padding: 16px 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.news-scroll {
    display: flex;
    overflow-x: auto;
    gap: 16px;
    padding: 0 16px;
    height: 100%;
    scrollbar-width: none;
    -ms-overflow-style: none;
}

.news-scroll::-webkit-scrollbar {
    display: none;
}

.news-item {
    flex: 0 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 100px;
    height: 120px;
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
    color: #667eea;
    font-size: 2rem;
    margin-bottom: 8px;
}

.news-text {
    font-size: 0.9rem;
    font-weight: 500;
    text-align: center;
    color: #333;
    line-height: 1.2;
}
</style>