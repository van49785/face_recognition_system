// src/services/api/auth.js
import api from './index'

// Admin login
export const login = async (username, password) => {
  try {
    console.log('Admin Login request:', { username: username.trim() })
    
    const response = await api.post('/api/auth/admin/login', {
      username: username.trim(), 
      password: password.trim() 
    })
    
    console.log('Admin Login success:', {
      hasToken: !!response.data.token,
      user: response.data.username
    })
    
    return response.data
    
  } catch (error) {
    console.error('Admin Login error:', error.response?.data || error.message)
    throw error
  }
}

// Employee login
export const loginEmployee = async (username, password) => {
  try {
    console.log('Employee Login request:', { username: username.trim() })
    
    const response = await api.post('/api/auth/employee/login', {
      username: username.trim(), 
      password: password.trim() 
    })
    
    console.log('Employee Login success:', {
      hasToken: !!response.data.token,
      employee_id: response.data.employee_id,
      full_name: response.data.full_name
    })
    
    return response.data
    
  } catch (error) {
    console.error('Employee Login error:', error.response?.data || error.message)
    throw error
  }
}

// Verify token
export const verify = async () => {
  try {
    console.log('Verify request')
    
    const response = await api.get('/api/auth/verify')
    
    console.log('Verify success:', response.data)
    return response.data
    
  } catch (error) {
    console.error('Verify error:', error.response?.data || error.message)
    throw error
  }
}

// Logout
export const logoutAdmin = async () => {
  try {
    console.log('🚪 Logout request')
    
    const response = await api.post('/api/auth/logout')
    
    console.log('Logout success:', response.data)
    return response.data
    
  } catch (error) {
    console.error('Logout error:', error.response?.data || error.message)
    throw error
  }
}