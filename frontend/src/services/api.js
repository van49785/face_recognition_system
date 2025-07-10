// src/services/api.js
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

// Tạo axios instance
const api = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    
    // Đảm bảo store đã được khởi tạo
    if (!authStore.isInitialized) {
      authStore.initializeFromStorage()
    }
    
    const token = authStore.token
    
    console.log("🔍 Request interceptor:", {
      url: config.url,
      hasToken: !!token,
      isAuthenticated: authStore.isAuthenticated
    })
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log("✅ Authorization header set")
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log("✅ API Success:", response.config.url, response.status)
    return response
  },
  (error) => {
    const authStore = useAuthStore()
    
    console.log("❌ API Error:", {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data
    })
    
    if (error.response?.status === 401) {
      console.log("🚨 401 Unauthorized - Token expired or invalid")
      
      // Chỉ logout nếu không phải request login
      if (!error.config?.url?.includes('/api/auth/login')) {
        authStore.logout()
        
        // Redirect về login với current route
        const currentRoute = router.currentRoute.value
        if (currentRoute.name !== 'Login') {
          router.push({ 
            name: 'Login', 
            query: { redirect: currentRoute.fullPath } 
          })
        }
      }
    }
    
    // Xử lý lỗi network
    if (error.code === 'ECONNABORTED') {
      error.message = 'Connection timeout. Please try again.'
    } else if (error.code === 'ERR_NETWORK') {
      error.message = 'Cannot connect to the server. Please check your network connection.'
    }
    
    return Promise.reject(error)
  }
)

// Auth API functions
export const login = async (username, password) => {
  try {
    console.log('🔐 Login request:', { username: username.trim() })
    
    const response = await api.post('/api/auth/login', { 
      username: username.trim(), 
      password: password.trim() 
    })
    
    console.log('✅ Login success:', {
      hasToken: !!response.data.token,
      user: response.data.user?.username
    })
    
    return response.data
    
  } catch (error) {
    console.error('❌ Login error:', error.response?.data || error.message)
    throw error
  }
}

export const verify = async () => {
  try {
    console.log('🔍 Verify request')
    
    const response = await api.get('/api/auth/verify')
    
    console.log('✅ Verify success:', response.data)
    return response.data
    
  } catch (error) {
    console.error('❌ Verify error:', error.response?.data || error.message)
    throw error
  }
}

export const logout = async () => {
  try {
    console.log('🚪 Logout request')
    
    await api.post('/api/auth/logout')
    
    console.log('✅ Logout success')
    return true
    
  } catch (error) {
    console.error('❌ Logout error:', error.response?.data || error.message)
    // Vẫn logout local ngay cả khi API fail
    return false
  }
}

// Face recognition API
export const recognizeFace = async (formData) => {
  try {
    console.log('📷 Face recognition request')
    
    const response = await api.post('/api/recognize', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    
    console.log('✅ Face recognition success:', response.data)
    return response.data
    
  } catch (error) {
    console.error('❌ Face recognition error:', error.response?.data || error.message)
    throw error
  }
}

// Attendance API functions
export const getAttendanceHistory = async (employee_id) => {
  try {
    console.log('📊 Get attendance history:', employee_id)
    const response = await api.get(`/api/attendance/${employee_id}`)
    return response.data
  } catch (error) {
    console.error('❌ Get attendance history error:', error.response?.data || error.message)
    throw error
  }
}

export const getTodayAttendance = async (employee_id) => {
  try {
    console.log('📅 Get today attendance:', employee_id)
    const response = await api.get(`/api/attendance/today/${employee_id}`)
    return response.data
  } catch (error) {
    console.error('❌ Get today attendance error:', error.response?.data || error.message)
    throw error
  }
}

// Employee API functions
export const getEmployees = async () => {
  try {
    console.log('👥 Get employees')
    const response = await api.get('/api/employees')
    return response.data
  } catch (error) {
    console.error('❌ Get employees error:', error.response?.data || error.message)
    throw error
  }
}

export default api