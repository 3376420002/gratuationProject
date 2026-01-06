import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../layout/index.vue'

const routes = [
  {
    path: '/login',
    component: () => import('../views/login/index.vue')
  },
  {
    path: '/',
    component: Layout,      
    redirect: '/login', 
    children: [
      {
        path: 'dashboard',
        component: () => import('../views/dashboard/index.vue')
      },
      {
        path: 'booking',
        // 预订管理
        component: () => import('../views/booking/index.vue')
      },
      {
        path: 'room-config',
        component: () => import('../views/room-config/index.vue')
      },
      {
        path: 'member',
        component: () => import('../views/member/index.vue')
      },
      {
        path: 'reports',
        component: () => import('../views/reports/index.vue')
      },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router