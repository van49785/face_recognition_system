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
    
    console.log("Request interceptor:", {
      url: config.url,
      hasToken: !!token,
      isAuthenticated: authStore.isAuthenticated
    })
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log("Authorization header set")
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log("API Success:", response.config.url, response.status)
    return response
  },
  (error) => {
    const authStore = useAuthStore()
    
    console.log("API Error:", {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data
    })
    
    if (error.response?.status === 401) {
      console.log("401 Unauthorized - Token expired or invalid")
      
      // Chỉ logout nếu không phải request login
      // CẬP NHẬT: Kiểm tra cả admin/login và employee/login
      if (!error.config?.url?.includes('/api/auth/admin/login') && !error.config?.url?.includes('/api/auth/employee/login')) {
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
// CẬP NHẬT: Hàm login cho Admin
export const login = async (username, password) => {
  try {
    console.log('Admin Login request:', { username: username.trim() })
    
    const response = await api.post('/api/auth/admin/login', { // Đổi endpoint
      username: username.trim(), 
      password: password.trim() 
    })
    
    console.log('Admin Login success:', {
      hasToken: !!response.data.token,
      user: response.data.username // Sử dụng username từ response
    })
    
    return response.data
    
  } catch (error) {
    console.error('Admin Login error:', error.response?.data || error.message)
    throw error
  }
}

// THÊM: Hàm login cho Employee
export const loginEmployee = async (username, password) => {
  try {
    console.log('Employee Login request:', { username: username.trim() })
    
    const response = await api.post('/api/auth/employee/login', { // Endpoint mới
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

// CẬP NHẬT: Đổi tên hàm logout thành logoutUser để dùng chung
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
};

// Face recognition API
export const recognizeFace = async (formData) => {
  try {
    console.log('📷 Face recognition request')
    
    const response = await api.post('/api/recognize', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    
    console.log('Face recognition success:', response.data)
    return response.data
    
  } catch (error) {
    console.error('Face recognition error:', error.response?.data || error.message)
    throw error
  }
}

// Attendance API functions
export const getAttendanceHistory = async (employee_id) => {
  try {
    console.log('Get attendance history:', employee_id)
    const response = await api.get(`/api/attendance/${employee_id}`)
    return response.data
  } catch (error) {
    console.error('Get attendance history error:', error.response?.data || error.message)
    throw error
  }
}

// THÊM: Hàm lấy lịch sử chấm công của nhân viên đang đăng nhập
export const getMyAttendanceHistory = async (params = {}) => {
  try {
    console.log('Get my attendance history:', params)
    // Endpoint này không cần employee_id trong URL, nó sẽ lấy từ token
    const response = await api.get('/api/employee/attendance/history', { params })
    return response.data
  } catch (error) {
    console.error('Get my attendance history error:', error.response?.data || error.message)
    throw error
  }
}

export const getTodayAttendance = async (employee_id) => {
  try {
    console.log('Get today attendance:', employee_id)
    const response = await api.get(`/api/attendance/today/${employee_id}`)
    return response.data
  } catch (error) {
    console.error('Get today attendance error:', error.response?.data || error.message)
    throw error
  }
}

// 1. Thêm nhân viên mới (với upload ảnh)
// CẬP NHẬT: Thêm initial_password và username vào formData
export const addEmployee = async (formData) => {
  try {
    console.log('👤 Add employee request')
    
    const response = await api.post('/api/employees', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    
    console.log('Add employee success:', response.data)
    return response.data
    
  } catch (error) {
    console.error('Add employee error:', error.response?.data || error.message)
    throw error
  }
}

// 2. Lấy danh sách nhân viên (đã có - cải thiện)
export const getEmployees = async (params = {}) => {
  try {
    console.log('👥 Get employees:', params)
    
    const response = await api.get('/api/employees', { params })
    
    console.log('Get employees success:', response.data)
    return response.data
    
  } catch (error) {
    console.error('Get employees error:', error.response?.data || error.message)
    throw error
  }
}

// 3. Lấy chi tiết một nhân viên
export const getEmployeeDetail = async (employee_id) => {
  try {
    console.log('Get employee detail:', employee_id)
    
    const response = await api.get(`/api/employees/${employee_id}`)
    
    console.log('Get employee detail success:', response.data)
    return response.data
    
  } catch (error) {
    console.error('Get employee detail error:', error.response?.data || error.message)
    throw error
  }
}

// 4. Cập nhật thông tin nhân viên
export const updateEmployee = async (employee_id, formData) => {
  try {
    console.log('Update employee request:', employee_id)
    
    const response = await api.put(`/api/employees/${employee_id}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    
    console.log('Update employee success:', response.data)
    return response.data
    
  } catch (error) {
    console.error('Update employee error:', error.response?.data || error.message)
    throw error
  }
}

// 5. Xóa mềm nhân viên (đánh dấu inactive)
export const deleteEmployee = async (employee_id) => {
  try {
    console.log('Delete employee request:', employee_id)
    
    const response = await api.delete(`/api/employees/${employee_id}`)
    
    console.log('Delete employee success:', response.data)
    return response.data
    
  } catch (error) {
    console.error('Delete employee error:', error.response?.data || error.message)
    throw error
  }
}

// 6. Khôi phục nhân viên
export const restoreEmployee = async (employee_id) => {
  try {
    console.log('Restore employee request:', employee_id)
    
    const response = await api.put(`/api/employees/${employee_id}/restore`)
    
    console.log('Restore employee success:', response.data)
    return response.data
    
  } catch (error) {
    console.error('Restore employee error:', error.response?.data || error.message)
    throw error
  }
}

// THÊM: Hàm đặt lại mật khẩu cho nhân viên (Admin dùng)
export const setEmployeePassword = async (employee_id, new_password, username = null) => {
  try {
    console.log('Set employee password request:', employee_id)
    const payload = { new_password };
    if (username) {
      payload.username = username;
    }
    const response = await api.post(`/api/employees/${employee_id}/set-password`, payload)
    console.log('Set employee password success:', response.data)
    return response.data
  } catch (error) {
    console.error('Set employee password error:', error.response?.data || error.message)
    throw error
  }
}

export const employeeChangePassword = async (oldPassword, newPassword, confirmNewPassword) => {
  try {
    const response = await api.post('/api/employee/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
      confirm_new_password: confirmNewPassword,
    });
    return response.data;
  } catch (error) {
    console.error('Employee change password error:', error.response?.data || error.message);
    throw error;
  }
};


// Gửi ảnh training (base64 hoặc blob)
export function captureFacePose(data) {
  return api.post('/api/face-training/capture', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
}


// Lấy danh sách pose cần thiết
export function getRequiredPoses() {
  return Promise.resolve(['front', 'left', 'right', 'up', 'down']);
}

// Report API functions
export const getEmployeeReport = async (employee_id, startDate, endDate) => {
  try {
    console.log('Get employee report:', employee_id, startDate, endDate)
    // Corrected: employee_id is a path parameter
    const response = await api.get(`/api/reports/employee/${employee_id}`, {
      params: { start_date: startDate, end_date: endDate }
    })
    return response.data
  } catch (error) {
    console.error('Get employee report error:', error.response?.data || error.message)
    throw error
  }
}

export const getDepartmentReport = async (department, startDate, endDate) => {
  try {
    console.log('Get department report:', department, startDate, endDate)
    // Corrected: department is a path parameter
    const response = await api.get(`/api/reports/department/${department}`, {
      params: { start_date: startDate, end_date: endDate }
    })
    return response.data
  } catch (error) {
    console.error('Get department report error:', error.response?.data || error.message)
    throw error
  }
}

export const exportReport = async (reportType, startDate, endDate) => {
  try {
    console.log('Export report request:', reportType, startDate, endDate)
    const response = await api.get(`/api/reports/export/${reportType}`, {
      params: {
        start_date: startDate,
        end_date: endDate,
        download: true // Request direct file download
      },
      responseType: 'blob' // Important: receive response as a Blob
    })
    return response.data // This will be the Blob
  } catch (error) {
    console.error('Export report error:', error.response?.data || error.message)
    throw error
  }
}

// Utility function to download file from Blob
export const downloadReportFile = (blob, filename) => {
  try {
    console.log('Download report file:', filename)
    
    // Create a temporary URL for the blob
    const url = window.URL.createObjectURL(blob)
    
    // Create an <a> element to trigger download
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    
    // Cleanup
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    console.log('Download file success:', filename)
    return true
    
  } catch (error) {
    console.error('Download file error:', error)
    throw error
  }
}

// Helper function to format report type for export
export const formatReportType = (type, id) => {
  switch (type) {
    case 'employee':
      return `employee/${id}`
    case 'department':
      return `department/${id}`
    default:
      return type
  }
}

// Helper function to parse company config
export const parseCompanyConfig = (config) => {
  const parsed = {}
  
  for (const [key, value] of Object.entries(config)) {
    if (typeof value === 'string' && value.includes(':')) {
      // Parse time strings back to time objects or keep as string
      parsed[key] = value // Keep as string or parse further if needed on frontend
    } else {
      parsed[key] = value
    }
  }
  return parsed
}


// Settings API functions
export const settingsApi = {
  getSettings: async () => {
    try {
      const response = await api.get('/api/settings')
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Get settings error:', error)
      return { success: false, error: error.response?.data?.error || 'Failed to fetch settings' }
    }
  },

  updateSettings: async (data) => {
    try {
      const response = await api.post('/api/settings', data)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Update settings error:', error)
      return { success: false, error: error.response?.data?.error || 'Failed to update settings' }
    }
  },

  createBackup: async () => {
    try {
      const response = await api.post('/api/settings/create-backup')
      return { success: true, message: response.data.message }
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to create backup' }
    }
  },

  resetSystem: async () => {
    try {
      const response = await api.post('/api/settings/reset-system')
      return { success: true, message: response.data.message }
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to reset system' }
    }
  }
}

export const getPendingRecoveryRequests = async () => {
  try {
    console.log('Get pending recovery requests')
    const response = await api.get('/api/admin/attendance/recovery/pending')
    return response.data.pending_requests
  } catch (error) {
    console.error('Get pending recovery requests error:', error.response?.data || error.message)
    throw error
  }
}


export const processRecoveryRequest = async ({ request_id, approved, reason }) => {
  try {

    const requestBody = {
      status: approved ? 'approved' : 'rejected',  
      notes: reason,  
    };
    

    const response = await api.post(`/api/admin/attendance/recovery/process/${request_id}`, requestBody)

    return response.data

  } catch (error) {
    console.error('Process recovery error details:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      url: error.config?.url,
      requestData: error.config?.data
    });
    throw error
  }
}

export const getAllRecoveryRequests = async () => {
  try {
    console.log('Get all recovery requests')
    const response = await api.get('/api/admin/attendance/recovery/all')
    return response.data.requests
  } catch (error) {
    console.error('Get all recovery requests error:', error.response?.data || error.message)
    throw error
  }
}

/**
 * Gửi yêu cầu phục hồi chấm công cho nhân viên.
 * @param {object} data - Dữ liệu yêu cầu phục hồi (request_date, request_type, desired_time, reason).
 * @returns {Promise<object>} Thông báo thành công từ API.
 */
export const submitEmployeeRecoveryRequest = async (data) => {
  try {
    console.log('Submitting employee recovery request:', data);
    // Endpoint: /api/employee/attendance/recovery/submit
    const response = await api.post('/api/employee/attendance/recovery/submit', data); 
    console.log('Employee recovery request submitted successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error submitting employee recovery request:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Lấy danh sách các yêu cầu phục hồi chấm công của nhân viên.
 * @returns {Promise<object>} Danh sách các yêu cầu phục hồi của nhân viên.
 */
export const getEmployeeRecoveryRequests = async () => {
  try {
    console.log('Get employee recovery requests');
    // Endpoint: /api/employee/attendance/recovery/my-requests
    const response = await api.get('/api/employee/attendance/recovery/my-requests'); 
    console.log('Employee recovery requests fetched successfully:', response.data);
    return response.data.requests; // Giả sử response trả về { requests: [...] }
  } catch (error) {
    console.error('Error fetching employee recovery requests:', error.response?.data || error.message);
    throw error;
  }
};
export default api