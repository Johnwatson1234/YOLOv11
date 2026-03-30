import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { title: '系统工作台', icon: 'Monitor' },
    },
    {
      path: '/monitor',
      name: 'Monitor',
      component: () => import('@/views/Monitor.vue'),
      meta: { title: '课堂监测', icon: 'VideoCameraFilled' },
    },
    {
      path: '/attendance',
      name: 'Attendance',
      component: () => import('@/views/Attendance.vue'),
      meta: { title: '智能考勤', icon: 'UserFilled' },
    },
    {
      path: '/report',
      name: 'Report',
      component: () => import('@/views/Report.vue'),
      meta: { title: '课后评估', icon: 'DataAnalysis' },
    },
    {
      path: '/student',
      name: 'StudentProfile',
      component: () => import('@/views/StudentProfile.vue'),
      meta: { title: '学生画像', icon: 'User' },
    },
    {
      path: '/alert',
      name: 'AlertCenter',
      component: () => import('@/views/AlertCenter.vue'),
      meta: { title: '异常预警', icon: 'WarningFilled' },
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('@/views/Settings.vue'),
      meta: { title: '系统设置', icon: 'Setting' },
    },
  ],
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || '慧眼课堂'} — ClassVision`
  next()
})

export default router
