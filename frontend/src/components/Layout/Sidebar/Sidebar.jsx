// src/components/Layout/Sidebar/Sidebar.jsx
import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <i className="fas fa-fingerprint"></i>
        <span>Hệ Thống Chấm Công</span>
      </div>
      <nav className="sidebar-nav">
        <ul>
          <li>
            <NavLink to="/admin/employees" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <i className="fas fa-users"></i> Quản Lý Nhân Viên
            </NavLink>
          </li>
          {/* Thêm các NavLink khác tại đây nếu có */}
          {/*
          <li>
            <NavLink to="/attendance-logs" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <i className="fas fa-clipboard-list"></i> Lịch Sử Chấm Công
            </NavLink>
          </li>
          <li>
            <NavLink to="/reports" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <i className="fas fa-chart-bar"></i> Báo Cáo
            </NavLink>
          </li>
          */}
        </ul>
      </nav>
      <div className="sidebar-footer">
        <p>&copy; 2025. All Rights Reserved.</p>
      </div>
    </div>
  );
};

export default Sidebar;
