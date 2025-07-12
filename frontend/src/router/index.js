// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import Home from '../views/HomeView.vue';
import Login from '../views/Login.vue';
import Employees from '../views/Employees.vue';
import EmployeeDetail from '../views/EmployeeDetail.vue';
import Attendance from '../views/Attendance.vue';
import Reports from '../views/Reports.vue';
import FaceTraining from '../views/FaceTraining.vue';

const routes = [
  { path: '/', name: 'Home', component: Home, meta: { requiresAuth: true } },
  { path: '/login', name: 'Login', component: Login },
  { path: '/employees', name: 'Employees', component: Employees, meta: { requiresAuth: true } },
  { path: '/employees/:employee_id', name: 'EmployeeDetail', component: EmployeeDetail, meta: { requiresAuth: true } },
  { path: '/attendance', name: 'Attendance', component: Attendance, meta: { requiresAuth: false } },
  { path: '/reports', name: 'Reports', component: Reports, meta: { requiresAuth: true } },
  { path: '/face-training', name: 'FaceTraining', component: FaceTraining, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  // Đảm bảo Pinia đã được khởi tạo
  const authStore = useAuthStore();
  
  // Đợi store khởi tạo xong
  if (!authStore.isInitialized) {
    authStore.initializeFromStorage();
  }
  
  console.log('🔍 Router guard:', {
    to: to.name,
    from: from.name,
    requiresAuth: to.meta.requiresAuth,
    isAuthenticated: authStore.isAuthenticated,
    hasToken: !!authStore.token,
    localStorageToken: !!localStorage.getItem('token')
  });
  
  // Nếu route yêu cầu authentication
  if (to.meta.requiresAuth) {
    if (to.meta.requiresAuth !== true) {
      if (to.name === 'Login' && authStore.isAuthenticated) {
        const redirectPath = to.query.redirect || '/';
        next(redirectPath);
      } else {
        next();
      }
      return; // Quan trọng: return để không chạy code bên dưới
    }
    if (!authStore.isAuthenticated) {
      console.log('🔒 Route requires auth but user not authenticated, redirecting to login');
      // Lưu route đích để redirect sau khi login
      const redirectPath = to.fullPath !== '/login' ? to.fullPath : '/';
      next({ name: 'Login', query: { redirect: redirectPath } });
      return;
    }
    
    // Nếu có token, verify token với server (tùy chọn)
    if (authStore.token) {
      try {
        // Có thể thêm verify token ở đây nếu cần
        console.log('✅ User authenticated, proceeding to route');
        next();
      } catch (error) {
        console.log('❌ Token verification failed, redirecting to login');
        authStore.logout();
        next({ name: 'Login', query: { redirect: to.fullPath } });
      }
    } else {
      console.log('🔒 No token found, redirecting to login');
      next({ name: 'Login', query: { redirect: to.fullPath } });
    }
  } else {
    // Public routes
    if (to.name === 'Login' && authStore.isAuthenticated) {
      console.log('🏠 User already authenticated, checking for redirect');
      // Kiểm tra redirect query param
      const redirectPath = to.query.redirect || '/';
      next(redirectPath);
    } else {
      next();
    }
  }
});

export default router;