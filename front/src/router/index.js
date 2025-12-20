import { createRouter, createWebHistory } from 'vue-router'
import { checkAdminAccess } from './admin-guard'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/catalog',
    name: 'catalog', 
    component: () => import('@/views/CatalogView.vue'),
    props: (route) => ({
      category: route.query.category,
      filter: route.query.filter,
      search: route.query.search
    })
  },
  {
    path: '/support',
    name: 'support',
    component: () => import('@/views/SupportView.vue')
  },
  {
    path: '/cart',
    name: 'cart',
    component: () => import('@/views/CartView.vue')
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue')
  },
  {
    path: '/services',
    name: 'services',
    component: () => import('@/views/ServicesView.vue')
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/AdminView.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Защита маршрутов для админа
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAdmin) {
    const isAdmin = await checkAdminAccess();
    
    if (isAdmin) {
      next();
    } else {
      alert('Доступ запрещен. Требуются права администратора.');
      next('/profile');
    }
  } else {
    next();
  }
})

export default router