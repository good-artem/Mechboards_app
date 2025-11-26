<template>
  <v-card class="category-card" elevation="2" @click="navigateToCategory">
    <v-card-text class="text-center">
      <v-icon size="40" class="mb-2">{{ category.icon }}</v-icon>
      <div class="text-body-2">{{ category.name }}</div>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'CategoryCard',
  props: {
    category: {
      type: Object,
      required: true
    }
  },
  methods: {
    navigateToCategory() {
      this.$emit('category-selected', this.category)
    }
  }
}
</script>

<style scoped>
.category-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}
</style>