<template>
    <v-bottom-navigation grow color="primary">
        <v-btn value="tasks" to="/">
            <v-icon>mdi-format-list-checks</v-icon>
            <span>Задачи</span>
        </v-btn>

        <v-btn value="profile" to="/profile">
            <v-icon>mdi-account</v-icon>
            <span>Профиль</span>
        </v-btn>
    </v-bottom-navigation>
</template>

<script>
export default {
    name: "Navbar"
}
</script>

<style scoped>
/* Дополнительные стили не нужны, Vuetify все делает */
</style>