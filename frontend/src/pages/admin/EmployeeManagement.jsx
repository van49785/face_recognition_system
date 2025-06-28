// src/pages/admin/EmployeeManagement.jsx
import React, { useState, useEffect } from 'react';
// import { useNavigate } from 'react-router-dom'; // BỎ IMPORT useNavigate vì không dùng nút Back nữa
import EmployeeList from '../../components/employee/EmployeeList'; 
import EmployeeForm from '../../components/employee/EmployeeForm'; 
import EmployeeActionModal from '../../components/employee/EmployeeActionModal'; 
import './EmployeeManagement.css'; 

// URL cơ sở của API backend (chỉ chứa host và port, không có '/api' ở cuối)
const API_BASE_URL = 'http://localhost:5000'; 

// Component chính cho trang quản lý nhân viên
const EmployeeManagement = ({ setGlobalMessage }) => {
  const [employees, setEmployees] = useState([]); 
  const [searchTerm, setSearchTerm] = useState(''); 
  const [isFormModalOpen, setIsFormModalOpen] = useState(false); 
  const [currentEmployee, setCurrentEmployee] = useState(null); 

  const [isActionModalOpen, setIsActionModalOpen] = useState(false);
  const [selectedEmployeeForActions, setSelectedEmployeeForActions] = useState(null); 

  // State để quản lý bộ lọc trạng thái (mặc định là 'active')
  const [filterStatus, setFilterStatus] = useState('active'); 

  // Hàm tải danh sách nhân viên từ API backend
  const fetchEmployees = async () => {
    try {
      // Điều chỉnh URL để bao gồm tham số filterStatus
      const response = await fetch(`${API_BASE_URL}/api/employees?status=${filterStatus}`);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      setEmployees(data.employees || []); 
    } catch (error) {
      console.error("Error fetching employee list:", error);
      setGlobalMessage('Could not load employee list. Please try again later.', true);
    }
  };

  useEffect(() => {
    fetchEmployees(); 
  }, [filterStatus]); // Gọi lại fetchEmployees mỗi khi filterStatus thay đổi

  const filteredEmployees = employees.filter(employee =>
    employee.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    employee.employee_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (employee.email && employee.email.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleSaveEmployee = async (employeeData, isEditing) => {
    const formData = new FormData(); 
    formData.append('employee_id', employeeData.employee_id.toUpperCase()); // Chuyển sang chữ hoa
    formData.append('full_name', employeeData.full_name);
    formData.append('department', employeeData.department || '');
    formData.append('position', employeeData.position || '');
    formData.append('phone', employeeData.phone || ''); 
    formData.append('email', employeeData.email || ''); 
    formData.append('status', employeeData.status);

    if (employeeData.imageFile) { 
      formData.append('image', employeeData.imageFile);
    } 

    try {
      let response;
      if (isEditing) {
        response = await fetch(`${API_BASE_URL}/api/employees/${employeeData.employee_id.toUpperCase()}`, { // Chuyển sang chữ hoa
          method: 'PUT',
          body: formData, 
        });
      } else {
        response = await fetch(`${API_BASE_URL}/api/employees`, {
          method: 'POST',
          body: formData, 
        });
      }

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(responseData.error || 'Unknown server error.');
      }

      setGlobalMessage(responseData.message || (isEditing ? 'Employee updated successfully!' : 'Employee added successfully!'), false);
      setIsFormModalOpen(false); 
      setCurrentEmployee(null); 
      fetchEmployees(); // Gọi lại để hiển thị danh sách cập nhật (theo filterStatus hiện tại)
    } catch (error) {
      console.error("Error saving employee:", error);
      setGlobalMessage(`Error: ${error.message}`, true); 
    }
  };

  // Hàm xóa MỘT nhân viên (HARD DELETE)
  const handleDeleteEmployee = async (employeeId) => {
    if (window.confirm('Are you sure you want to PERMANENTLY delete this employee and all related data (attendance records, images)? This action cannot be undone.')) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/employees/${employeeId.toUpperCase()}`, { // Chuyển sang chữ hoa
          method: 'DELETE',
        });

        const responseData = await response.json();

        if (!response.ok) {
          throw new Error(responseData.error || 'Unknown server error.');
        }

        setGlobalMessage(responseData.message || 'Employee deleted permanently!', false);
        setIsFormModalOpen(false); 
        setIsActionModalOpen(false); 
        setCurrentEmployee(null); 
        setSelectedEmployeeForActions(null); 
        fetchEmployees(); 
      }
      catch (error) {
        console.error("Error deleting employee:", error);
        setGlobalMessage(`Error: ${error.message}`, true);
      }
    }
  };

  // BỎ HÀM handleDeleteAllEmployees

  const handleEditEmployee = (employee) => {
    setCurrentEmployee(employee);
    setIsFormModalOpen(true);
  };

  const handleOpenForm = () => {
    setCurrentEmployee(null); 
    setIsFormModalOpen(true);
  };

  const handleCloseForm = () => {
    setIsFormModalOpen(false);
    setCurrentEmployee(null); 
  };

  const handleOpenActionsModal = (employee) => {
    setSelectedEmployeeForActions(employee);
    setIsActionModalOpen(true);
  };

  const handleCloseActionsModal = () => {
    setIsActionModalOpen(false);
    setSelectedEmployeeForActions(null);
  };

  // BỎ HÀM handleGoBack()

  return (
    <div className="employee-management-container">
      <h1 className="page-title text-gradient-light">Quản lý Nhân viên</h1>

      <div className="top-action-row"> {/* Dùng class mới cho hàng này */}
        <button onClick={handleOpenForm} className="add-employee-button primary-button">
          <i className="fas fa-user-plus"></i> Thêm Nhân viên
        </button>

        <input
          type="text"
          placeholder="Tìm kiếm nhân viên..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="employee-search-input"
        />
        
        {/* Nhóm nút lọc trạng thái */}
        <div className="filter-buttons-group">
          <button 
            onClick={() => setFilterStatus('active')} 
            className={`filter-button ${filterStatus === 'active' ? 'active-filter' : ''}`}
          >
            <i className="fas fa-user-check"></i> Đang Hoạt Động
          </button>
          <button 
            onClick={() => setFilterStatus('inactive')} 
            className={`filter-button ${filterStatus === 'inactive' ? 'active-filter' : ''}`}
          >
            <i className="fas fa-user-slash"></i> Đã Nghỉ Việc
          </button>
        </div>
      </div>
      
      {/* BỎ NÚT "XÓA TẤT CẢ NHÂN VIÊN VĨNH VIỄN" */}

      <EmployeeList 
        employees={filteredEmployees} 
        onOpenActionsModal={handleOpenActionsModal} 
      />

      {isFormModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button className="modal-close-button" onClick={handleCloseForm}>&times;</button>
            <EmployeeForm 
              onSave={handleSaveEmployee} 
              onCancel={handleCloseForm}
              initialEmployee={currentEmployee} 
            />
          </div>
        </div>
      )}

      {isActionModalOpen && (
        <EmployeeActionModal
          employee={selectedEmployeeForActions} 
          onEditClick={handleEditEmployee} 
          onDeleteClick={handleDeleteEmployee} 
          onClose={handleCloseActionsModal} 
        />
      )}
    </div>
  );
};

export default EmployeeManagement;
