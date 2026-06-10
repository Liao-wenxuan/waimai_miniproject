import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('./views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/merchant/:id',
    name: 'Merchant',
    component: () => import('./views/Merchant.vue'),
    meta: { title: '商家详情' }
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('./views/Cart.vue'),
    meta: { title: '购物车' }
  },
  {
    path: '/orders',
    name: 'OrderList',
    component: () => import('./views/OrderList.vue'),
    meta: { title: '订单' }
  },
  {
    path: '/order-detail/:id',
    name: 'OrderDetail',
    component: () => import('./views/OrderDetail.vue'),
    meta: { title: '订单详情' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('./views/Profile.vue'),
    meta: { title: '我的' }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('./views/Favorites.vue'),
    meta: { title: '我的收藏' }
  },
  {
    path: '/help',
    name: 'HelpCenter',
    component: () => import('./views/HelpCenter.vue'),
    meta: { title: '帮助中心' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('./views/Settings.vue'),
    meta: { title: '设置' }
  },
  {
    path: '/merchant-orders',
    name: 'MerchantOrder',
    component: () => import('./views/MerchantOrder.vue'),
    meta: { title: '商家订单' }
  },
  {
    path: '/merchant-profile',
    name: 'MerchantProfile',
    component: () => import('./views/MerchantProfile.vue'),
    meta: { title: '商家中心' }
  },
  {
    path: '/rider-orders',
    name: 'RiderOrder',
    component: () => import('./views/RiderOrder.vue'),
    meta: { title: '骑手订单' }
  },
  {
    path: '/rider-profile',
    name: 'RiderProfile',
    component: () => import('./views/RiderProfile.vue'),
    meta: { title: '骑手中心' }
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('./views/AdminLogin.vue'),
    meta: { title: '管理后台登录' }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('./views/Admin.vue'),
    meta: { title: '管理后台' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  // 公开页面
  const publicPages = ['/login', '/admin/login']
  if (publicPages.includes(to.path)) {
    if (token && to.path === '/login') {
      if (role === 'merchant') return next('/merchant-orders')
      if (role === 'rider') return next('/rider-orders')
      if (role === 'admin') return next('/admin')
      return next('/home')
    }
    if (token && to.path === '/admin/login' && role === 'admin') {
      return next('/admin')
    }
    return next()
  }

  // 需要登录的页面
  if (!token) {
    if (to.path.startsWith('/admin')) {
      return next('/admin/login')
    }
    return next('/login')
  }

  // 角色页面权限
  if (to.path.startsWith('/admin') && role !== 'admin') {
    return next('/login')
  }
  if ((to.path.startsWith('/merchant-orders') || to.path.startsWith('/merchant-profile')) && role !== 'merchant') {
    return next('/login')
  }
  if ((to.path.startsWith('/rider-orders') || to.path.startsWith('/rider-profile')) && role !== 'rider') {
    return next('/login')
  }

  next()
})

export default router
