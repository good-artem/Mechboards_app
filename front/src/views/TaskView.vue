<template>
    <v-container class="fill-height">
        <v-row>
            <v-col cols="12">
                <v-card class="mx-auto" elevation="2">
                    <v-card-title class="d-flex align-center">
                        <v-text-field
                            v-model="newTask"
                            placeholder="Введите задачу..."
                            variant="outlined"
                            density="comfortable"
                            hide-details
                            @keyup.enter="createTask"
                        >
                        </v-text-field>
                        <v-btn 
                            icon 
                            color="primary" 
                            @click="createTask"
                            class="ml-2"
                            :disabled="!newTask"
                        >
                            <v-icon>mdi-plus</v-icon>
                        </v-btn>
                    </v-card-title>

                    <v-list lines="two">
                        <v-list-item
                            v-for="task in tasks"
                            :key="task.id"
                            :title="task.title"
                        >
                            <template v-slot:append>
                                <v-btn
                                    color="success"
                                    variant="tonal"
                                    size="small"
                                    @click="completeTask(task.id)"
                                >
                                    Выполнено
                                </v-btn>
                            </template>
                        </v-list-item>
                    </v-list>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
export default {
    name: 'TasksView',
    data() {
        return {
            tasks: [],
            newTask: ''
        }
    },
    async mounted() {
        await this.fetchTasks()
    },
    methods: {
        async fetchTasks() {
            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user
                const response = await fetch(`https://opulent-train-x45v4q7qgg9c9v57-8000.app.github.dev/api/tasks/${tg_user.id}`)
                const data = await response.json()
                this.tasks = data
            } catch (error) {
                console.log('error', error)
            }
        },
        async createTask() {
            if (!this.newTask) return

            try {
                const tg_user = window.Telegram.WebApp.initDataUnsafe?.user
                const response = await fetch(`https://opulent-train-x45v4q7qgg9c9v57-8000.app.github.dev/api/add`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ tg_id: tg_user.id, title: this.newTask })
                })
                if (response.ok) {
                    this.newTask = ''
                    await this.fetchTasks()
                } else {
                    console.error('Ошибка', response.status)
                }
            } catch (error) {
                console.log('Ошибка', error)
            }
        },
        async completeTask(taskId) {
            try {
                const response = await fetch(`https://opulent-train-x45v4q7qgg9c9v57-8000.app.github.dev/api/completed`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ id: taskId })
                })
                if (response.ok) {
                    await this.fetchTasks()
                } else {
                    console.error('Ошибка', response.status)
                }
            } catch (error) {
                console.log('Ошибка', error)
            }
        }
    }
}
</script>

<style scoped>
/* Дополнительные стили не нужны */
</style>