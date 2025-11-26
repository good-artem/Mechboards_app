<template>
    <v-container>
        <v-row justify="center">
            <v-col cols="12" md="8">
                <!-- Приветствие -->
                <v-card class="pa-6 mb-4 text-center" elevation="2">
                    <v-icon size="64" color="primary" class="mb-4">mdi-keyboard</v-icon>
                    <v-card-title class="justify-center text-h5">
                        Добро пожаловать в Mechboards!
                    </v-card-title>
                    <v-card-text>
                        Лучшие механические клавиатуры и аксессуары для настоящих ценителей
                    </v-card-text>
                </v-card>

                <!-- Задачи (оставляем посередине) -->
                <TasksComponent />
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import TasksComponent from '@/components/TasksComponent.vue'

export default {
    name: 'HomeView',
    components: {
        TasksComponent
    }
}
</script>