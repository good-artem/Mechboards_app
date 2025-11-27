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
    background: var(--tg-theme-secondary-bg-color, #f8f9fa);
    border-bottom: 1px solid var(--tg-theme-hint-color, #e0e0e0);
}

.news-carousel {
    height: 150px;
    padding: 16px 0;
}

.news-scroll {
    display: flex;
    overflow-x: auto;
    gap: 12px;
    padding: 0 16px;
    height: 100%;
    scrollbar-width: none;
    -ms-overflow-style: none;
    align-items: center;
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
    height: 110px;
    background: var(--tg-theme-bg-color, #ffffff);
    border-radius: 16px;
    padding: 12px 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid var(--tg-theme-hint-color, #f0f0f0);
}

.news-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.news-icon-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    background: var(--tg-theme-button-color, #2481cc);
    border-radius: 12px;
    margin-bottom: 8px;
}

.news-icon {
    color: white !important;
    font-size: 24px;
}

.news-text {
    font-size: 0.8rem;
    font-weight: 500;
    text-align: center;
    color: var(--tg-theme-text-color, #000000);
    line-height: 1.2;
}
</style>