<template>
    <div class="news-carousel-container">
        <div class="news-carousel">
            <div class="news-scroll">
                <div 
                    v-for="news in newsItems" 
                    :key="news.news_id"
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
            newsItems: [],
            loading: false
        }
    },
    async mounted() {
        await this.fetchNews();
    },
    methods: {
        async fetchNews() {
            this.loading = true;
            try {
                const response = await fetch('/api/news');
                if (response.ok) {
                    const newsData = await response.json();
                    this.newsItems = newsData;
                } else {
                    console.error('Ошибка загрузки новостей');
                    this.newsItems = this.getDefaultNews();
                }
            } catch (error) {
                console.error('Ошибка загрузки новостей:', error);
                this.newsItems = this.getDefaultNews();
            }
            this.loading = false;
        },
        getDefaultNews() {
            // Fallback данные если бэкенд недоступен
            return [
                { news_id: 1, title: 'Новые клавиатуры', icon: 'mdi-keyboard', news_type: 'new_products' },
                { news_id: 2, title: 'Скидки до 20%', icon: 'mdi-sale', news_type: 'discount' },
                { news_id: 3, title: 'Доставка за 24ч', icon: 'mdi-truck-fast', news_type: 'delivery' },
                { news_id: 4, title: 'Кейкапы', icon: 'mdi-circle-multiple', news_type: 'category' },
                { news_id: 5, title: 'Аксессуары', icon: 'mdi-cable-data', news_type: 'category' }
            ];
        },
        openNews(news) {
            console.log('Opening news:', news.title);
            
            // Навигация в зависимости от типа новости
            switch (news.news_type) {
                case 'new_products':
                    this.$router.push('/catalog?filter=new');
                    break;
                case 'discount':
                    this.$router.push('/catalog?filter=discount');
                    break;
                case 'category':
                    // Если есть конкретная категория в action_url
                    if (news.action_url && news.action_url.includes('category=')) {
                        this.$router.push(news.action_url);
                    } else {
                        this.$router.push('/catalog');
                    }
                    break;
                case 'delivery':
                    this.$router.push('/support');
                    break;
                default:
                    // Если есть кастомный URL, используем его
                    if (news.action_url && news.action_url.startsWith('/')) {
                        this.$router.push(news.action_url);
                    } else {
                        console.log('News clicked:', news);
                    }
            }
        }
    }
}
</script>