
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
                @click="handleFaceRecognition"
                :disabled="loading"
              >
                <v-icon left class="mr-2">mdi-camera</v-icon>
                Use Facial Recognition
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

</script>

<style scoped>
.login-wrapper {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
  z-index: 1000;
}

.login-container {
  position: absolute !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  width: 90% !important;
  max-width: 480px !important;
  min-width: 380px !important;
  margin: 0 !important;
  padding: 0 !important;
}

.login-card {
  width: 100% !important;
  margin: 0 !important;
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.1) !important;
}

.login-header {
  padding: 40px 40px 20px 40px;
  text-align: center;
  background: linear-gradient(135deg, rgba(25, 118, 210, 0.1), rgba(25, 118, 210, 0.05));
  border-radius: 12px 12px 0 0;
}

.logo-section {
  animation: fadeInUp 0.8s ease-out;
}

.login-form-section {
  padding: 30px 40px !important;
}

.form-group {
  margin-bottom: 8px;
}

.login-btn {
  font-weight: 600 !important;
  text-transform: none !important;
  letter-spacing: 0.5px !important;
  transition: all 0.3s ease !important;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(25, 118, 210, 0.3);
}

.login-options {
  margin-top: 20px;
}

.divider-section {
  display: flex;
  align-items: center;
  margin: 20px 0;
}

.divider {
  flex: 1;
  height: 1px;
  background: #e0e0e0;
  border: none;
}

.divider-text {
  padding: 0 15px;
  color: #9e9e9e;
  font-size: 14px;
}

.facial-recognition-btn {
  font-weight: 500 !important;
  text-transform: none !important;
  transition: all 0.3s ease !important;
}

.facial-recognition-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.login-footer {
  padding: 20px 40px;
  text-align: center;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 0 0 12px 12px;
}


/* Background decorations */
.bg-decoration-1 {
  position: absolute;
  top: -50px;
  right: -50px;
  width: 200px;
  height: 200px;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1), transparent);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.bg-decoration-2 {
  position: absolute;
  bottom: -100px;
  left: -100px;
  width: 300px;
  height: 300px;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.05), transparent);
  border-radius: 50%;
  animation: float 8s ease-in-out infinite reverse;
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

/* Responsive */
@media (max-width: 600px) {
  .login-container {
    width: 95% !important;
    min-width: 300px !important;
  }
  
  .login-header {
    padding: 30px 20px 15px 20px;
  }
  
  .login-form-section {
    padding: 20px 20px !important;
  }
  
  .login-footer {
    padding: 15px 20px;
  }
}

@media (max-width: 400px) {
  .login-container {
    width: 98% !important;
    min-width: 280px !important;
  }
}
</style>

<!-- CSS global để override #app styles cho trang login -->
<style>
.login-page #app {
  max-width: none !important;
  margin: 0 !important;
  padding: 0 !important;
  display: block !important;
  grid-template-columns: none !important;
}

/* Override Vuetify default styles */
.login-page .v-application {
  background: transparent !important;
}
</style>