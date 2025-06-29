// src/components/Layout/Layout.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom'; // Đảm bảo đã import useNavigate
import Sidebar from './Sidebar/Sidebar';
import './Layout.css';
import { useAuth } from '../../context/AuthContext'; // Import useAuth hook

const Layout = ({ children, setAppGlobalMessage }) => { // Nhận setAppGlobalMessage prop
  const { isAdminLoggedIn, adminUsername, logout } = useAuth(); // Lấy trạng thái auth và hàm logout
  const navigate = useNavigate(); // Khởi tạo useNavigate

  const handleLogout = () => {
    logout(setAppGlobalMessage); // Gọi hàm logout từ AuthContext, truyền setAppGlobalMessage
    navigate('/'); // <--- THÊM DÒNG NÀY ĐỂ CHUYỂN HƯỚNG VỀ TRANG CHẤM CÔNG (/)
  };

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="main-content-wrapper">
        {/* Header với thông tin người dùng và nút đăng xuất */}
        <header className="main-header">
          {isAdminLoggedIn ? (
            <div className="admin-info-section">
              <span className="admin-username-display">Xin chào, {adminUsername}</span>
              <button onClick={handleLogout} className="logout-button">
                Đăng Xuất <i className="fas fa-sign-out-alt"></i>
              </button>
            </div>
          ) : (
            // Nếu không phải admin, có thể hiển thị gì đó khác hoặc để trống
            <div className="public-header-placeholder"></div>
          )}
        </header>
        
        <main className="main-content-area">
          {children} 
        </main>
      </div>
    </div>
  );
};

export default Layout;
