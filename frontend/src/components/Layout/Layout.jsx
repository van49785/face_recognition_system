// src/components/Layout/Layout.jsx
import React from 'react';
// useNavigate không còn cần thiết ở đây nếu nút đăng nhập admin bị bỏ
// import { useNavigate } from 'react-router-dom'; 
import Sidebar from './Sidebar/Sidebar';
import './Layout.css';

const Layout = ({ children }) => {
  // Hàm handleLoginClick không còn cần thiết nếu nút đăng nhập admin bị bỏ
  // const navigate = useNavigate();
  // const handleLoginClick = () => {
  //   navigate('/admin/employees'); 
  // };

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="main-content-wrapper">
        {/* Nút Đăng nhập đã bị loại bỏ khỏi đây */}
        {/* <button onClick={handleLoginClick} className="global-admin-login-button">
          Đăng nhập (Admin)
        </button> */}
        
        <main className="main-content-area">
          {children} 
        </main>
      </div>
    </div>
  );
};

export default Layout;
