// src/components/employee/EmployeeForm.jsx
import React, { useState, useEffect } from 'react';
import './EmployeeForm.css';

const EmployeeForm = ({ initialEmployee = null, onSave, onCancel }) => { 
  const [formData, setFormData] = useState({
    employee_id: '',
    full_name: '',
    department: '',
    position: '',
    phone: '', 
    email: '', 
    status: true, 
  });
  const [imageFile, setImageFile] = useState(null); 
  const [imagePreviewUrl, setImagePreviewUrl] = useState(null); 
  const [errors, setErrors] = useState({});
  const isEditing = initialEmployee !== null;

  useEffect(() => {
    if (isEditing && initialEmployee) {
      setFormData({
        employee_id: initialEmployee.employee_id || '',
        full_name: initialEmployee.full_name || '',
        department: initialEmployee.department || '',
        position: initialEmployee.position || '',
        phone: initialEmployee.phone || '', 
        email: initialEmployee.email || '', 
        status: initialEmployee.status, 
      });
      // HIỂN THỊ ẢNH CŨ NẾU CÓ imageUrl TỪ initialEmployee
      setImagePreviewUrl(initialEmployee.imageUrl ? `http://localhost:5000${initialEmployee.imageUrl}` : null); // <-- Đảm bảo URL đầy đủ
      setImageFile(null); 
    } else {
      setFormData({
        employee_id: '',
        full_name: '',
        department: '',
        position: '',
        phone: '',
        email: '',
        status: true,
      });
      setImageFile(null);
      setImagePreviewUrl(null);
    }
    setErrors({}); 
  }, [initialEmployee, isEditing]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setImageFile(file); 
    if (file) {
      setImagePreviewUrl(URL.createObjectURL(file)); 
    } else {
      // Nếu không có file mới, và đang edit nhưng không có ảnh cũ từ initialEmployee, thì không có preview
      setImagePreviewUrl(isEditing && initialEmployee?.imageUrl ? `http://localhost:5000${initialEmployee.imageUrl}` : null); // <-- Đảm bảo URL đầy đủ
    }
    setErrors(prev => ({ ...prev, imageFile: '' })); 
  };

  const validateForm = () => {
    let newErrors = {};
    if (!formData.employee_id) {
      newErrors.employee_id = 'Mã nhân viên là bắt buộc.';
    } else if (formData.employee_id.length !== 8) {
      newErrors.employee_id = 'Mã nhân viên phải gồm 8 ký tự.';
    } else if (!/^[A-Z0-9]{8}$/i.test(formData.employee_id)) {
      newErrors.employee_id = 'Mã nhân viên chỉ có thể chứa chữ cái in hoa (A-Z) và số (0-9).';
    }

    if (!formData.full_name) {
      newErrors.full_name = 'Họ tên là bắt buộc.';
    }

    // Validate email
    if (formData.email && !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(formData.email)) {
      newErrors.email = 'Định dạng email không hợp lệ.';
    }

    // Validate phone number (Vietnam format)
    if (formData.phone && !/^(\+84|0)[0-9]{9,10}$/.test(formData.phone)) {
      newErrors.phone = 'Định dạng số điện thoại không hợp lệ (phải là định dạng Việt Nam).';
    }
    
    // Image validation logic
    if (!isEditing && !imageFile) { 
        newErrors.imageFile = 'Ảnh nhận diện khuôn mặt là bắt buộc.';
    }
    // Khi chỉnh sửa: nếu không có ảnh mới được chọn VÀ không có ảnh cũ tồn tại, thì yêu cầu tải ảnh.
    if (isEditing && !imageFile && !initialEmployee?.imageUrl) {
        newErrors.imageFile = 'Ảnh nhận diện khuôn mặt là bắt buộc khi chỉnh sửa nếu không có ảnh cũ.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSave({ ...formData, imageFile: imageFile }, isEditing); 
    } else {
      console.log("Form có lỗi xác thực.");
    }
  };

  return (
    <div className="employee-form-container">
      <h2 className="employee-form-heading text-gradient-primary">
        {isEditing ? 'Chỉnh Sửa Thông Tin Nhân Viên' : 'Thêm Nhân Viên Mới'}
      </h2>
      <form onSubmit={handleSubmit} className="employee-form">
        <div className="form-layout-two-columns">
          <div className="form-left-column">
            <div className="form-group">
              <label htmlFor="employee_id">Mã Nhân Viên <span className="required">*</span></label>
              <input
                type="text"
                id="employee_id"
                name="employee_id"
                value={formData.employee_id}
                onChange={handleChange}
                readOnly={isEditing} 
                className={isEditing ? 'disabled-input' : ''}
              />
              {errors.employee_id && <p className="error-message">{errors.employee_id}</p>}
            </div>

            <div className="form-group">
              <label htmlFor="full_name">Họ Tên <span className="required">*</span></label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
              />
              {errors.full_name && <p className="error-message">{errors.full_name}</p>}
            </div>

            <div className="form-group">
              <label htmlFor="department">Phòng Ban</label>
              <input
                type="text"
                id="department"
                name="department"
                value={formData.department}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="position">Chức Vụ</label>
              <input
                type="text"
                id="position"
                name="position"
                value={formData.position}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="phone">Số Điện Thoại</label>
              <input
                type="tel" 
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
              />
              {errors.phone && <p className="error-message">{errors.phone}</p>}
            </div>

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email" 
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
              />
              {errors.email && <p className="error-message">{errors.email}</p>}
            </div>

            <div className="form-group checkbox-group">
              <input
                type="checkbox"
                id="status"
                name="status"
                checked={formData.status}
                onChange={handleChange}
              />
              <label htmlFor="status">Đang Hoạt Động</label>
            </div>
          </div> 

          <div className="form-right-column"> 
            <div className="image-upload-section">
              <h3>Ảnh Nhận Diện Khuôn Mặt</h3>
              <div className="image-preview-area-upload">
                {/* Hiển thị ảnh preview mới hoặc ảnh cũ từ initialEmployee */}
                {imagePreviewUrl || initialEmployee?.imageUrl ? (
                  <img
                    src={imagePreviewUrl || `http://localhost:5000${initialEmployee.imageUrl}`} // <-- Đảm bảo URL đầy đủ
                    alt="Ảnh nhân viên"
                    className="employee-photo-preview"
                    onError={(e) => {
                      e.target.onerror = null; 
                      e.target.src = 'https://placehold.co/160x160/cccccc/ffffff?text=No+Img'; 
                    }}
                  />
                ) : (
                  <div className="employee-photo-placeholder">
                    <span>Chưa có ảnh</span>
                    <i className="fas fa-user-circle"></i> 
                  </div>
                )}
              </div>
              <input
                type="file"
                id="imageFile"
                name="imageFile"
                accept="image/*" 
                onChange={handleImageChange}
                className="file-input"
              />
              {errors.imageFile && <p className="error-message">{errors.imageFile}</p>}

              {(imagePreviewUrl || initialEmployee?.imageUrl) && ( 
                <button 
                  type="button" 
                  onClick={() => {
                    setImageFile(null); 
                    setImagePreviewUrl(null); 
                    if (isEditing && initialEmployee) {
                      initialEmployee.imageUrl = null; 
                    }
                  }} 
                  className="clear-image-button danger-button"
                >
                  <i className="fas fa-trash-alt"></i> Xóa ảnh
                </button>
              )}
            </div>
          </div> 
        </div> 

        <div className="form-actions">
          <button type="button" className="cancel-button secondary-button" onClick={onCancel}>
            Hủy Bỏ
          </button>
          <button type="submit" className="save-button primary-button">
            {isEditing ? 'Lưu Thay Đổi' : 'Thêm Nhân Viên'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EmployeeForm;
