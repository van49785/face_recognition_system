// src/context/AuthContext.js
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children, setAppGlobalMessage }) => {
  const [authToken, setAuthToken] = useState(localStorage.getItem('jwt_token'));
  const [isAdminLoggedIn, setIsAdminLoggedIn] = useState(!!localStorage.getItem('jwt_token'));
  const [adminUsername, setAdminUsername] = useState(localStorage.getItem('admin_username'));

  const API_BASE_URL = 'http://localhost:5000'; // Đảm bảo URL này đúng

  // Function to save login info
  const login = (token, username) => {
    localStorage.setItem('jwt_token', token);
    localStorage.setItem('admin_username', username);
    setAuthToken(token);
    setIsAdminLoggedIn(true);
    setAdminUsername(username);
  };

  // Function to clear login info (logout)
  const logout = useCallback(async () => {
    const token = localStorage.getItem('jwt_token');
    
    // Luôn xóa thông tin đăng nhập client-side ngay lập tức
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('admin_username');
    setAuthToken(null);
    setIsAdminLoggedIn(false);
    setAdminUsername(null);

    if (token) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          if (setAppGlobalMessage) {
            setAppGlobalMessage('Đăng xuất thành công!', false);
          }
        } else {
          const errorData = await response.json();
          console.error("Logout failed on server:", errorData.message || response.statusText);
          if (setAppGlobalMessage) {
            setAppGlobalMessage(`Đăng xuất có vấn đề: ${errorData.message || 'Lỗi không xác định.'}`, true);
          }
        }
      } catch (error) {
        console.error("Error during logout network request:", error);
        if (setAppGlobalMessage) {
          setAppGlobalMessage('Không thể kết nối đến máy chủ để đăng xuất. Đã đăng xuất khỏi trình duyệt.', true);
        }
      }
    } else {
      if (setAppGlobalMessage) {
        setAppGlobalMessage('Bạn chưa đăng nhập hoặc phiên đã hết hạn.', true);
      }
    }
  }, [setAppGlobalMessage]); // logout dependency includes setAppGlobalMessage

  // Verify token on app load (e.g., if token might be expired)
  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem('jwt_token');
      if (token) {
        try {
          const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          if (!response.ok) {
            console.log("Token invalid or expired, logging out.");
            logout(); // Auto-logout if token is invalid
          } else {
            const data = await response.json();
            setAdminUsername(data.username);
            setIsAdminLoggedIn(true);
          }
        } catch (error) {
          console.error("Error verifying token:", error);
          logout();
        }
      }
    };
    verifyToken();
  }, [logout]); // logout is a dependency for useEffect

  return (
    <AuthContext.Provider value={{ authToken, isAdminLoggedIn, adminUsername, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
