
<template>
  <div class="login-wrapper">
    <div class="login-container">
      <!-- Background decorations -->
      <div class="bg-decoration-1"></div>
      <div class="bg-decoration-2"></div>
      
      <!-- Connection Status -->
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
        <!-- Header Section -->
        <div class="login-header">
          <div class="logo-section">
            <v-icon size="48" color="primary" class="mb-2">mdi-face-recognition</v-icon>
            <h2 class="text-h4 font-weight-bold text-primary mb-1">Admin Portal</h2>
            <p class="text-subtitle-1 text-medium-emphasis">Employee Management System</p>
          </div>
        </div>

        <!-- Login Form -->
        <v-card-text class="login-form-section">
          <v-form ref="loginForm" @submit.prevent="handleLogin" :disabled="loading">
            <div class="form-group">
              <v-text-field
                v-model="form.username"
                label="Username"
                required
                prepend-inner-icon="mdi-account-circle"
                :error-messages="errors.username"
                variant="outlined"
                size="large"
                class="mb-4"
                hide-details="auto"
                :rules="usernameRules"
                autocomplete="username"
                @keyup.enter="handleLogin"
              ></v-text-field>
            </div>

            <div class="form-group">
              <v-text-field
                v-model="form.password"
                label="Password"
                :type="showPassword ? 'text' : 'password'"
                required
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
                :error-messages="errors.password"
                variant="outlined"
                size="large"
                class="mb-6"
                hide-details="auto"
                :rules="passwordRules"
                autocomplete="current-password"
                @keyup.enter="handleLogin"
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
              :disabled="!isFormValid"
            >
              <v-icon left class="mr-2">mdi-login</v-icon>
              {{ loading ? 'Signing In...' : 'Sign In' }}
            </v-btn>

            <!-- Additional Options -->
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
          </v-form>
        </v-card-text>

        <!-- Footer -->
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
import { login, verify, recognizeFace } from '../services/api'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

// Form data
const form = reactive({
  username: '',
  password: '',
})

const errors = reactive({
  username: '',
  password: '',
})

// Loading states
const loading = ref(false)
const connectionError = ref('')

// Form validation
const showPassword = ref(false)
const loginForm = ref(null)

// Validation rules
const usernameRules = [
  v => !!v || 'Username is required',
  v => v.length >= 3 || 'Username must be at least 3 characters',
]

const passwordRules = [
  v => !!v || 'Password is required',
  v => v.length >= 6 || 'Password must be at least 6 characters',
]

// Computed
const isFormValid = computed(() => {
  return form.username.trim().length >= 3 && 
         form.password.trim().length >= 6 &&
         !loading.value
})

// Lifecycle hooks
onMounted(async () => {
  document.body.classList.add('login-page')
  
  // Check if already logged in
  if (authStore.isAuthenticated) {
    try {
      await verify()
      // router.push('/')
    } catch (error) {
      authStore.logout()
    }
  }
})

onUnmounted(() => {
  document.body.classList.remove('login-page')
  stopCamera()
})

// Methods
const handleLogin = async () => {
  if (!isFormValid.value) return
  const { valid } = await loginForm.value.validate()
  if (!valid) return

  loading.value = true
  errors.username = ''
  errors.password = ''

  try {
    console.log('🚀 Starting login process...')
    
    /* ❶ GỌI login API */
    const loginResponse = await login(form.username, form.password)
    console.log('📝 Login response:', loginResponse)
    
    const { token, username, admin_id, employee_id } = loginResponse
    
    /* ❂ LƯU THÔNG TIN ĐẦY ĐỦ NGAY LẦN ĐẦU */
    const userData = {
      username: username || form.username,
      admin_id: admin_id,
      employee_id: employee_id || admin_id
    }
    
    console.log('💾 Saving to store:', { token, userData })
    authStore.login(token, userData)
    
    /* ❸ CHỜ VÀ KIỂM TRA */
    await nextTick()
    
    console.log('🔍 Verifying login state...')
    console.log('  - Store token:', authStore.token)
    console.log('  - Store user:', authStore.user)
    console.log('  - localStorage token:', localStorage.getItem('token'))
    console.log('  - localStorage user:', localStorage.getItem('user'))
    
    /* ❹ VERIFY (optional - để kiểm tra token có hợp lệ không) */
    try {
      await verify()
      console.log('✅ Token verified successfully')
    } catch (verifyError) {
      console.warn('⚠️ Token verification failed:', verifyError.message)
      // Nếu verify fail, vẫn có thể redirect nếu có token
      if (!authStore.token) {
        throw new Error('Login failed - no valid token')
      }
    }
    
    /* ❺ CHUYỂN TRANG */
    router.push('/')
    
  } catch (error) {
    console.error('❌ Login error:', error)
    
    const msg = error.response?.data?.error ?? error.message ?? 'An error occurred during login'
    
    if (msg.includes('locked') || msg.includes('Wrong password')) {
      errors.password = msg
    } else if (msg.includes('Invalid account')) {
      errors.username = msg
    } else {
      errors.username = msg
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