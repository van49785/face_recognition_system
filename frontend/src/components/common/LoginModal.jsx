// src/components/common/LoginModal.jsx
import React, { useState } from 'react';
import './LoginModal.css'; // Import CSS cho modal đăng nhập

const LoginModal = ({ onLoginSuccess, onClose, setAppGlobalMessage }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  const handleLoginSubmit = (e) => {
    e.preventDefault();
    setLoginError(''); // Xóa lỗi cũ khi thử đăng nhập lại

    // Logic đăng nhập cứng cho mục đích demo
    if (username === 'admin' && password === 'admin123') { 
      setAppGlobalMessage('Đăng nhập Admin thành công!', false); // Thông báo thành công
      onLoginSuccess(); // Gọi hàm callback khi đăng nhập thành công
    } else {
      setLoginError('Tên đăng nhập hoặc mật khẩu không đúng.'); // Đặt thông báo lỗi
      setAppGlobalMessage('Đăng nhập Admin thất bại: Tên đăng nhập hoặc mật khẩu không đúng.', true); // Thông báo lỗi toàn cục
    }
  };

  return (
    <div className="login-modal-overlay">
      <div className="login-modal-content">
        {/* Nút đóng modal */}
        <button className="modal-close-button" onClick={onClose}>&times;</button>
        {/* Tiêu đề modal */}
        <h2 className="text-gradient-light">Đăng nhập Admin</h2>
        <p className="login-modal-description">Vui lòng nhập thông tin đăng nhập.</p>
        
        <form onSubmit={handleLoginSubmit} className="login-form">
          {/* Nhóm trường Tên đăng nhập */}
          <div className="form-group">
            <label htmlFor="username">Tên đăng nhập:</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="login-input"
            />
          </div>
          {/* Nhóm trường Mật khẩu */}
          <div className="form-group">
            <label htmlFor="password">Mật khẩu:</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="login-input"
            />
          </div>
          {/* Hiển thị thông báo lỗi đăng nhập nếu có */}
          {loginError && <p className="login-error-message">{loginError}</p>}
          {/* Nút Đăng nhập */}
          <button type="submit" className="login-submit-button primary-button">
            Đăng nhập
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginModal;
