<template>
  <div class="login-wrapper">
    <div class="login-container">
      <div class="bg-decoration-1"></div>
      <div class="bg-decoration-2"></div>
      
      <v-alert
        v-if="connectionError"
        type="error" 
        density="compact"
        class="mb-4"
        closable
        @click:close="connectionError = false"
      >
        {{ connectionError }}
      </v-alert>
      
      <v-card 
        elevation="24" 
        class="login-card"
        rounded="xl"
      >
        <div class="login-header">
          <div class="logo-section">
            <v-icon size="48" color="primary" class="mb-2">mdi-face-recognition</v-icon>
            <h2 class="text-h4 font-weight-bold text-primary mb-1">Employee Management System</h2>
            <p class="text-subtitle-1 text-medium-emphasis">AI-Powered Attendance & HR Portal</p>
          </div>
        </div>

        <v-tabs
          v-model="activeTab"
          align-tabs="center"
          color="primary"
          fixed-tabs
          density="comfortable"
        >
          <v-tab value="admin">
            <v-icon start>mdi-security</v-icon> Admin Login
          </v-tab>
          <v-tab value="employee">
            <v-icon start>mdi-account-group</v-icon> Employee Login
          </v-tab>
        </v-tabs>

        <v-card-text class="login-form-section">
          <v-window v-model="activeTab">
            <v-window-item value="admin">
              <v-form ref="adminLoginForm" @submit.prevent="handleLogin('admin')" :disabled="loading">
                <div class="form-group">
                  <v-text-field
                    v-model="form.adminUsername"
                    label="Username"
                    required
                    prepend-inner-icon="mdi-account-circle"
                    :error-messages="errors.adminUsername"
                    variant="outlined"
                    size="large"
                    class="mb-4"
                    hide-details="auto"
                    :rules="usernameRules"
                    autocomplete="username"
                    @keyup.enter="handleLogin('admin')"
                  ></v-text-field>
                </div>

                <div class="form-group">
                  <v-text-field
                    v-model="form.adminPassword"
                    label="Password"
                    :type="showAdminPassword ? 'text' : 'password'"
                    required
                    prepend-inner-icon="mdi-lock"
                    :append-inner-icon="showAdminPassword ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append-inner="showAdminPassword = !showAdminPassword"
                    :error-messages="errors.adminPassword"
                    variant="outlined"
                    size="large"
                    class="mb-6"
                    hide-details="auto"
                    :rules="passwordRules"
                    autocomplete="current-password"
                    @keyup.enter="handleLogin('admin')"
                  ></v-text-field>
                </div>

                <v-btn
                  type="submit"
                  color="primary"
                  block
                  :loading="loading"
                  size="x-large"
                  class="login-btn mb-4"
                  rounded="lg"
                  :disabled="!isFormValid('admin')"
                >
                  <v-icon left class="mr-2">mdi-login</v-icon>
                  {{ loading ? 'Signing In...' : 'Sign In as Admin' }}
                </v-btn>
              </v-form>
            </v-window-item>

            <v-window-item value="employee">
              <v-form ref="employeeLoginForm" @submit.prevent="handleLogin('employee')" :disabled="loading">
                <div class="form-group">
                  <v-text-field
                    v-model="form.employeeUsername"
                    label="Employee ID or Email"
                    required
                    prepend-inner-icon="mdi-badge-account"
                    :error-messages="errors.employeeUsername"
                    variant="outlined"
                    size="large"
                    class="mb-4"
                    hide-details="auto"
                    :rules="usernameRules"
                    autocomplete="username"
                    @keyup.enter="handleLogin('employee')"
                  ></v-text-field>
                </div>

                <div class="form-group">
                  <v-text-field
                    v-model="form.employeePassword"
                    label="Password"
                    :type="showEmployeePassword ? 'text' : 'password'"
                    required
                    prepend-inner-icon="mdi-lock"
                    :append-inner-icon="showEmployeePassword ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append-inner="showEmployeePassword = !showEmployeePassword"
                    :error-messages="errors.employeePassword"
                    variant="outlined"
                    size="large"
                    class="mb-6"
                    hide-details="auto"
                    :rules="passwordRules"
                    autocomplete="current-password"
                    @keyup.enter="handleLogin('employee')"
                  ></v-text-field>
                </div>

                <v-btn
                  type="submit"
                  color="secondary"
                  block
                  :loading="loading"
                  size="x-large"
                  class="login-btn mb-4"
                  rounded="lg"
                  :disabled="!isFormValid('employee')"
                >
                  <v-icon left class="mr-2">mdi-account-arrow-right</v-icon>
                  {{ loading ? 'Signing In...' : 'Sign In as Employee' }}
                </v-btn>
              </v-form>
            </v-window-item>
          </v-window>

          <div class="login-options">
            <div class="divider-section">
              <hr class="divider">
              <span class="divider-text">or</span>
              <hr class="divider">
            </div>
            
            <v-btn
              color="success"
              variant="outlined"
              block
              size="large"
              class="facial-recognition-btn"
              rounded="lg"
              @click="goToAttendancePage"
              :disabled="loading"
            >
              <v-icon left class="mr-2">mdi-camera</v-icon>
              Go to Attendance
            </v-btn>
          </div>
        </v-card-text>

        <div class="login-footer">
          <p class="text-caption text-medium-emphasis">
            © 2025 Employee Management System. All rights reserved.
          </p>
        </div>
      </v-card>
    </div>
  </div>
</template>

<script setup>
import '@/assets/css/Login.css';
import { ref, reactive, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useAuthStore } from '../stores/auth'
import { login, loginEmployee, verify } from '../services/api' 
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

// Tab hiện tại
const activeTab = ref('admin') // Mặc định là Admin Login

// Form data (chia tách cho Admin và Employee)
const form = reactive({
  adminUsername: '',
  adminPassword: '',
  employeeUsername: '',
  employeePassword: '',
})

const errors = reactive({
  adminUsername: '',
  adminPassword: '',
  employeeUsername: '',
  employeePassword: '',
})

// Loading states
const loading = ref(false)
const connectionError = ref('') // Để hiển thị lỗi kết nối chung

// Form validation
const showAdminPassword = ref(false)
const showEmployeePassword = ref(false)
const adminLoginForm = ref(null) // Ref cho form Admin
const employeeLoginForm = ref(null) // Ref cho form Employee

// Validation rules
const usernameRules = [
  v => !!v || 'Username cannot be empty',
  v => v.length >= 3 || 'Username must have at least 3 characters',
]

const passwordRules = [
  v => !!v || 'Password cannot be empty.',
  v => v.length >= 6 || 'Password must have at least 3 characters',
]

// Computed: Kiểm tra tính hợp lệ của form dựa trên tab đang active
const isFormValid = computed(() => (type) => {
  if (type === 'admin') {
    return form.adminUsername.trim().length >= 3 && 
           form.adminPassword.trim().length >= 6 &&
           !loading.value
  } else if (type === 'employee') {
    return form.employeeUsername.trim().length >= 3 && 
           form.employeePassword.trim().length >= 6 &&
           !loading.value
  }
  return false
})

// Lifecycle hooks
onMounted(async () => {
  document.body.classList.add('login-page')
  
  // Kiểm tra nếu đã đăng nhập và chuyển hướng phù hợp
  if (authStore.isAuthenticated) {
    try {
      console.log('User is authenticated. Verifying session...')
      await verify() // Verify current token
      
      // Chuyển hướng dựa trên vai trò đã lưu trong store
      if (authStore.user && authStore.user.role) {
        if (authStore.user.role === 'admin') {
          router.push('/') 
          console.log('Redirecting authenticated Admin to dashboard.')
        } else if (authStore.user.role === 'employee') {
          router.push('/employees') // Chuyển hướng đến trang nhân viên
          console.log('Redirecting authenticated Employee to dashboard.')
        } else {
          router.push('/login') // Mặc định về login nếu vai trò không xác định
          console.log('Redirecting authenticated user with unknown role to default home.')
        }
      } else {
        console.warn('Authenticated user has no role defined. Redirecting to default home.')
        router.push('/')
      }
    } catch (error) {
      console.error('Session verification failed:', error)
      authStore.logout() // Logout nếu token không hợp lệ/hết hạn
      connectionError.value = 'Your session has been expired or invalid. Please login again.'
    }
  }
})

onUnmounted(() => {
  document.body.classList.remove('login-page')
})

// Methods
const handleLogin = async (userType) => {
  // Reset errors
  errors.adminUsername = ''
  errors.adminPassword = ''
  errors.employeeUsername = ''
  errors.employeePassword = ''
  connectionError.value = ''

  let isValid = false
  if (userType === 'admin') {
    // Kiểm tra các quy tắc validation trước khi gọi validate() của form
    if (!isFormValid.value('admin')) {
      console.log('Admin form is not valid based on basic checks.')
      return
    }
    const { valid } = await adminLoginForm.value.validate()
    isValid = valid
  } else if (userType === 'employee') {
    // Kiểm tra các quy tắc validation trước khi gọi validate() của form
    if (!isFormValid.value('employee')) {
      console.log('Employee form is not valid based on basic checks.')
      return
    }
    const { valid } = await employeeLoginForm.value.validate()
    isValid = valid
  }

  if (!isValid) {
    console.log('Form validation failed.')
    return
  }

  loading.value = true

  try {
    console.log(`🚀 Starting ${userType} login process...`)
    
    let loginResponse
    let userData = {}

    if (userType === 'admin') {
      loginResponse = await login(form.adminUsername, form.adminPassword)
      userData = {
        username: loginResponse.username || form.adminUsername,
        admin_id: loginResponse.admin_id,
        role: 'admin', // Thêm role
      }
    } else if (userType === 'employee') {
      loginResponse = await loginEmployee(form.employeeUsername, form.employeePassword)
      userData = {
        employee_id: loginResponse.employee_id,
        full_name: loginResponse.full_name,
        username: loginResponse.employee_id, // hoặc email, tùy thuộc vào cách bạn muốn hiển thị
        role: 'employee', // Thêm role
        must_change_password: loginResponse.must_change_password,
      }
    }
    
    console.log('Login successful. Response:', loginResponse)
    console.log('Saving to store:', { token: loginResponse.token, userData })
    authStore.login(loginResponse.token, userData)
    
    // Chờ Vue cập nhật DOM và Pinia state
    await nextTick()
    
    console.log('Verifying login state after store update...')
    console.log('  - Store token:', authStore.token ? 'Exists' : 'Not exists')
    console.log('  - Store user:', authStore.user)
    console.log('  - localStorage token:', localStorage.getItem('token') ? 'Exists' : 'Not exists')
    console.log('  - localStorage user:', localStorage.getItem('user'))
    
    // Verify (optional - để kiểm tra token có hợp lệ không)
    try {
      const verifyResponse = await verify()
      console.log('Token verified successfully via API:', verifyResponse)
      // Cập nhật lại user data nếu verify trả về thông tin chi tiết hơn
      if (verifyResponse && verifyResponse.valid) {
        authStore.updateUser({ ...authStore.user, ...verifyResponse })
      }
    } catch (verifyError) {
      console.warn('Token verification failed after login (this is often okay if token is new):', verifyError.message)
      // Nếu verify fail, vẫn có thể redirect nếu có token và user data
      if (!authStore.token || !authStore.user) {
        throw new Error('Login failed - no valid token or user data after verification.')
      }
    }
    
    // Chuyển trang dựa trên vai trò
    if (authStore.user && authStore.user.role) {
      if (authStore.user.role === 'admin') {
        router.push('/') 
        console.log('Redirecting to Admin dashboard.')
      } else if (authStore.user.role === 'employee') {
        // Kiểm tra nếu employee cần đổi mật khẩu lần đầu
        if (authStore.user.must_change_password) {
          router.push('/employee/change-password') // Chuyển hướng đến trang đổi mật khẩu
          console.log('Redirecting to employee change password page.')
        } else {
          router.push('/employees') // Trang chủ nhân viên
          console.log('Redirecting to Employee dashboard.')
        }
      } else {
        router.push('/') // Fallback mặc định
        console.log('Redirecting to default home (unknown role).')
      }
    } else {
      console.warn('User role not found after login, redirecting to default home.')
      router.push('/') // Fallback nếu không có vai trò
    }
    
  } catch (error) {
    console.error('Login error:', error)
    
    const msg = error.response?.data?.error ?? error.message ?? 'Đã xảy ra lỗi trong quá trình đăng nhập.'
    connectionError.value = msg // Hiển thị lỗi chung cho người dùng
    
    if (userType === 'admin') {
      if (msg.includes('locked') || msg.includes('Invalid username or password')) {
        errors.adminPassword = msg
      } else {
        errors.adminUsername = msg
      }
    } else if (userType === 'employee') {
      if (msg.includes('locked') || msg.includes('Invalid username or password')) {
        errors.employeePassword = msg
      } else {
        errors.employeeUsername = msg
      }
    }
    
    // Clear any partial login state
    authStore.logout()
    
  } finally {
    loading.value = false
  }
}

const goToAttendancePage = () => {
  router.push('/attendance')
}
</script>