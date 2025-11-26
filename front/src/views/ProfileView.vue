<template>
    <v-container>
        <v-row justify="center">
            <v-col cols="12" sm="8" md="6">
                <v-card class="pa-4" elevation="2">
                    <v-card-title class="text-h5 text-center">
                        <v-avatar color="primary" size="64" class="mr-2">
                            <v-icon v-if="!user.photo_url" dark>mdi-account</v-icon>
                            <img v-else :src="user.photo_url" alt="Profile">
                        </v-avatar>
                        Профиль
                    </v-card-title>
                    
                    <v-card-text>
                        <v-list>
                            <v-list-item>
                                <template v-slot:prepend>
                                    <v-icon color="primary">mdi-identifier</v-icon>
                                </template>
                                <v-list-item-title>ID</v-list-item-title>
                                <v-list-item-subtitle>{{ user.id }}</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider></v-divider>

                            <v-list-item>
                                <template v-slot:prepend>
                                    <v-icon color="primary">mdi-account</v-icon>
                                </template>
                                <v-list-item-title>Имя</v-list-item-title>
                                <v-list-item-subtitle>{{ user.name }}</v-list-item-subtitle>
                            </v-list-item>

                            <v-divider></v-divider>

                            <v-list-item>
                                <template v-slot:prepend>
                                    <v-icon color="success">mdi-check-all</v-icon>
                                </template>
                                <v-list-item-title>Выполнено задач</v-list-item-title>
                                <v-list-item-subtitle>{{ user.completedTasks }}</v-list-item-subtitle>
                            </v-list-item>
                        </v-list>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
export default {
    name: 'ProfileView',
    data() {
        return {
            user: {
                id: '',
                name: '',
                completedTasks: 0,
                photo_url: null
            }
        }
    },
    async mounted() {
        await this.fetchProfile()
        
        // Для Telegram user photo
        if (window.Telegram?.WebApp) {
            const tgUser = window.Telegram.WebApp.initDataUnsafe?.user
            if (tgUser?.photo_url) {
                this.user.photo_url = tgUser.photo_url
            }
        }
    },
    methods: {
        async fetchProfile() {
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user
                const response = await fetch(`https://opulent-train-x45v4q7qgg9c9v57-8000.app.github.dev/api/main/${tg_user.id}`)
                const data = await response.json()
                this.user.id = tg_user.id
                this.user.name = tg_user.first_name
                this.user.completedTasks = data.completedTasks
            } catch (error) {
                console.log(error)
            }
        }
    }
}
</script>