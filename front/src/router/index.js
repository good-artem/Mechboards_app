import { createRouter, createWebHistory } from 'vue-router'

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
    // Можно добавить props для передачи параметров через URL
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
  // Добавим catch-all route для 404
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
    try {
      const { get } = await import('@/composables/useApi');
      const api = get();
      const result = await api.get('/api/admin/check');
      
      if (result.is_admin) {
        next();
      } else {
        alert('Доступ запрещен. Требуются права администратора.');
        next('/profile');
      }
    } catch (error) {
      console.error('Ошибка проверки прав администратора:', error);
      alert('Ошибка авторизации. Пожалуйста, войдите через Telegram.');
      next('/profile');
    }
  } else {
    next();
  }
})

export default router