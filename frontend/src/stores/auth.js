import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref(null)
  const user = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  const isInitialized = ref(false)

  // Getters
  const isAuthenticated = computed(() => {
    return !!token.value && !!user.value
  })
  
  const username = computed(() => user.value?.username || '')
  const adminId = computed(() => user.value?.admin_id || user.value?.employee_id || null)

  // Actions
  const login = (authToken, userData) => {
    console.log('🔑 Login called with:', { token: authToken?.substring(0, 20) + '...', user: userData })
    
    if (!authToken || !userData) {
      console.error('❌ Invalid login data')
      return false
    }
    
    token.value = authToken
    user.value = userData
    
    // Lưu vào localStorage
    try {
      localStorage.setItem('token', authToken)
      localStorage.setItem('user', JSON.stringify(userData))
      
      console.log('✅ Auth data saved to localStorage')
      console.log('✅ isAuthenticated:', isAuthenticated.value)
    } catch (e) {
      console.error('❌ Error saving to localStorage:', e)
    }
    
    error.value = null
    return true
  }

  const logout = () => {
    console.log('🚪 Logout called')
    
    token.value = null
    user.value = null
    
    // Xóa khỏi localStorage
    try {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      console.log('🗑️ localStorage cleared')
    } catch (e) {
      console.error('❌ Error clearing localStorage:', e)
    }
    
    error.value = null
  }

  const setLoading = (loading) => {
    isLoading.value = loading
  }

  const setError = (errorMsg) => {
    error.value = errorMsg
  }

  const clearError = () => {
    error.value = null
  }

  const updateUser = (userData) => {
    console.log('👤 Update user called with:', userData)
    
    if (!userData) return
    
    user.value = { ...user.value, ...userData }
    
    try {
      localStorage.setItem('user', JSON.stringify(user.value))
      console.log('✅ User updated in localStorage')
    } catch (e) {
      console.error('❌ Error updating user in localStorage:', e)
    }
  }

  // Initialize từ localStorage khi store được tạo
  const initializeFromStorage = () => {
    if (isInitialized.value) return
    
    console.log('🔄 Initializing auth store from localStorage...')
    
    try {
      const storedToken = localStorage.getItem('token')
      const storedUser = localStorage.getItem('user')
      
      if (storedToken && storedUser) {
        const parsedUser = JSON.parse(storedUser)
        
        // Validate stored data
        if (parsedUser && parsedUser.username) {
          token.value = storedToken
          user.value = parsedUser
          
          console.log('✅ Auth restored from localStorage:', {
            hasToken: !!token.value,
            username: user.value.username,
            isAuthenticated: isAuthenticated.value
          })
        } else {
          console.log('❌ Invalid user data in localStorage, clearing...')
          localStorage.removeItem('token')
          localStorage.removeItem('user')
        }
      } else {
        console.log('ℹ️ No valid auth data in localStorage')
      }
    } catch (e) {
      console.error('❌ Error initializing from localStorage:', e)
      // Clear corrupted data
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
    
    isInitialized.value = true
  }

  // Validate current session (tùy chọn)
  const validateSession = async () => {
    if (!token.value) return false
    
    try {
      // Gọi API verify token nếu cần
      // const response = await verify()
      // return response.success
      return true
    } catch (error) {
      console.error('❌ Session validation failed:', error)
      logout()
      return false
    }
  }

  // Gọi initialize ngay khi store được tạo
  initializeFromStorage()

  return {
    // State
    token,
    user,
    isLoading,
    error,
    isInitialized,
    
    // Getters
    isAuthenticated,
    username,
    adminId,
    
    // Actions
    login,
    logout,
    setLoading,
    setError,
    clearError,
    updateUser,
    initializeFromStorage,
    validateSession
  }
})