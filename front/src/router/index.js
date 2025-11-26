import { createRouter, createWebHistory } from 'vue-router'
import TasksView from '../views/TasksView.vue'
import CatalogView from '../views/CatalogView.vue'
import SupportView from '../views/SupportView.vue'
import CartView from '../views/CartView.vue'
import ProfileView from '../views/ProfileView.vue'

const routes = [
  {
    path: '/',
    name: 'tasks',
    component: TasksView
  },
  {
    path: '/catalog',
    name: 'catalog',
    component: CatalogView
  },
  {
    path: '/support',
    name: 'support',
    component: SupportView
  },
  {
    path: '/cart',
    name: 'cart',
    component: CartView
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router