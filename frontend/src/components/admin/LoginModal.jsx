// src/components/common/LoginModal.jsx
import React, { useState } from 'react';
import './LoginModal.css'; // You'll need to create this CSS file for styling
import { useAuth } from '../../context/AuthContext'; // Import useAuth hook

const API_BASE_URL = 'http://localhost:5000'; // Define your Flask API base URL

const LoginModal = ({ onLoginSuccess, onClose, setAppGlobalMessage }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth(); // Get the login function from AuthContext

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setAppGlobalMessage(''); // Clear previous messages

    if (!username.trim() || !password.trim()) {
      setAppGlobalMessage('Tên đăng nhập hoặc mật khẩu không được để trống.', true);
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        // Use the login function from AuthContext to store token and admin info
        login(data.token, data.username); 
        setAppGlobalMessage('Đăng nhập thành công!', false);
        onLoginSuccess(); // Notify parent (App.js) of successful login
        onClose(); // Close the modal
      } else {
        setAppGlobalMessage(data.error || 'Đăng nhập thất bại. Vui lòng thử lại.', true);
      }
    } catch (error) {
      console.error('Lỗi khi đăng nhập:', error);
      setAppGlobalMessage('Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối.', true);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-modal-overlay">
      <div className="login-modal">
        <button className="login-modal-close-button" onClick={onClose}>&times;</button>
        <h2 className="login-modal-title">Đăng Nhập Admin</h2>
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Tên đăng nhập:</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="form-input"
              placeholder="Nhập tên đăng nhập"
              disabled={isLoading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Mật khẩu:</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="form-input"
              placeholder="Nhập mật khẩu"
              disabled={isLoading}
            />
          </div>
          <button type="submit" className="login-button" disabled={isLoading}>
            {isLoading ? 'Đang đăng nhập...' : 'Đăng Nhập'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginModal;
