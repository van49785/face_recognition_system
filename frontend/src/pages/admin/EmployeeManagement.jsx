// src/pages/admin/EmployeeManagement.jsx
import React, { useState, useEffect } from 'react';
import EmployeeList from '../../components/employee/EmployeeList'; 
import EmployeeForm from '../../components/employee/EmployeeForm'; 
import EmployeeActionModal from '../../components/employee/EmployeeActionModal'; 
import './EmployeeManagement.css'; 

const API_BASE_URL = 'http://localhost:5000'; 

const EmployeeManagement = ({ setGlobalMessage }) => {
  const [employees, setEmployees] = useState([]); 
  const [searchTerm, setSearchTerm] = useState(''); 
  const [isFormModalOpen, setIsFormModalOpen] = useState(false); 
  const [currentEmployee, setCurrentEmployee] = useState(null); 

  const [isActionModalOpen, setIsActionModalOpen] = useState(false);
  const [selectedEmployeeForActions, setSelectedEmployeeForActions] = useState(null); 

  // State để quản lý bộ lọc trạng thái (mặc định là 'active')
  const [filterStatus, setFilterStatus] = useState('active'); 

  const fetchEmployees = async () => {
    try {
      // Gọi API với tham số 'status' để backend lọc dữ liệu
      const response = await fetch(`${API_BASE_URL}/api/employees?status=${filterStatus}`);
      if (!response.ok) {
        throw new Error(`Lỗi HTTP! Trạng thái: ${response.status}`);
      }
      const data = await response.json();
      setEmployees(data.employees || []); 
    } catch (error) {
      console.error("Lỗi khi tải danh sách nhân viên:", error);
      setGlobalMessage('Không thể tải danh sách nhân viên. Vui lòng thử lại sau.', true);
    }
  };

  useEffect(() => {
    fetchEmployees(); 
  }, [filterStatus]); // Gọi lại fetchEmployees mỗi khi filterStatus thay đổi

  const filteredEmployees = employees.filter(employee =>
    employee.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    employee.employee_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (employee.email && employee.email.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (employee.phone && employee.phone.includes(searchTerm)) || // Tìm kiếm theo số điện thoại
    (employee.department && employee.department.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleSaveEmployee = async (employeeData, isEditing) => {
    const formData = new FormData(); 
    formData.append('employee_id', employeeData.employee_id.toUpperCase()); 
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
        response = await fetch(`${API_BASE_URL}/api/employees/${employeeData.employee_id.toUpperCase()}`, {
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
        throw new Error(responseData.error || 'Lỗi không xác định từ máy chủ.');
      }

      setGlobalMessage(responseData.message || (isEditing ? 'Đã cập nhật nhân viên thành công!' : 'Đã thêm nhân viên thành công!'), false);
      setIsFormModalOpen(false); 
      setCurrentEmployee(null); 
      fetchEmployees(); 
    } catch (error) {
      console.error("Lỗi khi lưu nhân viên:", error);
      setGlobalMessage(`Lỗi: ${error.message}`, true); 
    }
  };

  const handleDeleteEmployee = async (employeeId) => {
    if (window.confirm('Bạn có chắc chắn muốn ĐẶT TRẠNG THÁI nhân viên này thành "Đã nghỉ việc" không?')) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/employees/${employeeId.toUpperCase()}`, {
          method: 'DELETE', 
        });

        const responseData = await response.json();

        if (!response.ok) {
          throw new Error(responseData.error || 'Lỗi không xác định từ máy chủ.');
        }

        setGlobalMessage(responseData.message || 'Đã đặt trạng thái nhân viên thành công!', false);
        setIsFormModalOpen(false); 
        setIsActionModalOpen(false); 
        setCurrentEmployee(null); 
        setSelectedEmployeeForActions(null); 
        fetchEmployees(); 
      }
      catch (error) {
        console.error("Lỗi khi xóa nhân viên (soft delete):", error);
        setGlobalMessage(`Lỗi: ${error.message}`, true);
      }
    }
  };

  const handleRestoreEmployee = async (employeeId) => { // Thêm hàm restore
    if (window.confirm('Bạn có chắc chắn muốn KHÔI PHỤC trạng thái nhân viên này thành "Đang Hoạt Động" không?')) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/employees/${employeeId.toUpperCase()}/restore`, {
          method: 'PUT',
        });

        const responseData = await response.json();

        if (!response.ok) {
          throw new Error(responseData.error || 'Lỗi không xác định từ máy chủ.');
        }

        setGlobalMessage(responseData.message || 'Đã khôi phục trạng thái nhân viên thành công!', false);
        setIsFormModalOpen(false); 
        setIsActionModalOpen(false); 
        setCurrentEmployee(null); 
        setSelectedEmployeeForActions(null); 
        fetchEmployees(); 
      } catch (error) {
        console.error("Lỗi khi khôi phục nhân viên:", error);
        setGlobalMessage(`Lỗi: ${error.message}`, true);
      }
    }
  };


  const handleEditEmployee = async (employeeFromList) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/employees/${employeeFromList.employee_id.toUpperCase()}`);
      if (!response.ok) {
        throw new Error(`Lỗi HTTP khi tải chi tiết nhân viên! Trạng thái: ${response.status}`);
      }
      const data = await response.json();
      
      // Chuyển đổi định dạng status từ string "active"/"inactive" sang boolean cho form
      data.employee.status = data.employee.status === 'active';

      setCurrentEmployee(data.employee);
      setIsFormModalOpen(true);
    } catch (error) {
      console.error("Lỗi khi tải chi tiết nhân viên để chỉnh sửa:", error);
      setGlobalMessage(`Lỗi: ${error.message}`, true);
    }
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

  return (
    <div className="employee-management-container">
      <h1 className="page-title text-gradient-light">Quản lý Nhân viên</h1>

      <div className="top-action-row">
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
          onRestoreClick={handleRestoreEmployee} 
          onClose={handleCloseActionsModal} 
        />
      )}
    </div>
  );
};

export default EmployeeManagement;
