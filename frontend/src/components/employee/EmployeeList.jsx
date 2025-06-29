// src/components/employee/EmployeeList.jsx
import React from 'react';
import './EmployeeList.css'; 

// Component để hiển thị danh sách nhân viên dưới dạng bảng
const EmployeeList = ({ employees, onOpenActionsModal }) => { 
  return (
    <div className="employee-list-container">
      {/* Tiêu đề danh sách nhân viên */}
      <h2 className="employee-list-heading text-gradient-light">Danh Sách Nhân Viên</h2>
      {employees.length === 0 ? (
        // Hiển thị thông báo nếu không có nhân viên nào
        <p className="no-employees-message">Không tìm thấy nhân viên nào trong danh sách.</p>
      ) : (
        // Wrapper cho bảng để xử lý cuộn ngang trên màn hình nhỏ
        <div className="employee-table-wrapper">
          <table className="employee-table">
            {/* Tiêu đề bảng */}
            <thead>
              <tr>
                <th>Ảnh</th> 
                <th>Mã NV</th>
                <th>Họ Tên</th>
                <th>Phòng Ban</th>
                <th>Chức Vụ</th>
                <th>Email</th> 
                <th>Số ĐT</th> 
                <th>Trạng Thái</th> 
                <th>Ngày Vào Làm</th> 
                <th>Cập Nhật Cuối</th> 
              </tr>
            </thead>
            {/* Thân bảng */}
            <tbody>
              {employees.map((employee) => (
                // Khi nhấp vào một hàng, gọi onOpenActionsModal để mở modal chọn hành động
                <tr 
                  key={employee.employee_id} 
                  onClick={() => onOpenActionsModal(employee)} 
                  className="employee-table-row-clickable" 
                >
                  <td>
                    {/* Hiển thị ảnh nếu có imageUrl, nếu không thì placeholder */}
                    {employee.imageUrl ? (
                      <img
                        src={`http://localhost:5000${employee.imageUrl}`} // <-- Đảm bảo URL đầy đủ
                        alt={employee.full_name}
                        className="employee-table-image"
                        onError={(e) => {
                          e.target.onerror = null; 
                          e.target.src = 'https://placehold.co/50x50/cccccc/ffffff?text=No+Img'; 
                        }}
                      />
                    ) : (
                      // Placeholder icon nếu không có ảnh
                      <div className="employee-table-image-placeholder">
                        <i className="fas fa-user-circle"></i>
                      </div>
                    )}
                  </td>
                  <td>{employee.employee_id}</td>
                  <td>{employee.full_name}</td>
                  <td>{employee.department || 'N/A'}</td> 
                  <td>{employee.position || 'N/A'}</td>
                  <td>{employee.email || 'N/A'}</td> 
                  <td>{employee.phone || 'N/A'}</td> 
                  <td>
                    {/* Hiển thị trạng thái với badge màu sắc */}
                    <span className={`status-indicator ${employee.status ? 'active' : 'inactive'}`}>
                      {employee.status ? 'Đang Làm' : 'Nghỉ Làm'}
                    </span>
                  </td>
                  <td>{employee.created_at || 'N/A'}</td> 
                  <td>{employee.updated_at || 'N/A'}</td> 
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default EmployeeList;
