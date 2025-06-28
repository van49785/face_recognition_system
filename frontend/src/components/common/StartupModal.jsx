// src/components/common/StartupModal.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './StartupModal.css';

const StartupModal = ({ onClose, onAdminSelected }) => { 
  const navigate = useNavigate();

  const handleEmployeeClick = () => {
    navigate('/'); 
    onClose(); 
  };

  const handleAdminClick = () => {
    onAdminSelected(); 
    onClose(); 
  };

  return (
    <div className="startup-modal-overlay">
      <div className="startup-modal-content">
        <h2>Bạn là ai?</h2>
        <p>Vui lòng chọn vai trò của bạn để tiếp tục.</p>
        <div className="startup-modal-actions">
          <button onClick={handleEmployeeClick} className="modal-button employee-button">
            <i className="fas fa-user"></i> Nhân viên
          </button>
          <button onClick={handleAdminClick} className="modal-button admin-button">
            <i className="fas fa-user-shield"></i> Admin
          </button>
        </div>
      </div>
    </div>
  );
};

export default StartupModal;
