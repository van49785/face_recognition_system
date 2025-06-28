// src/components/employee/EmployeeForm.jsx
import React, { useState, useEffect } from 'react';
import './EmployeeForm.css';

// onDelete is removed from props, as delete functionality is moved to EmployeeActionModal
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
      setImagePreviewUrl(initialEmployee.imageUrl || null); 
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
      setImagePreviewUrl(isEditing && initialEmployee ? initialEmployee.imageUrl : null); 
    }
    setErrors(prev => ({ ...prev, imageFile: '' })); 
  };

  const validateForm = () => {
    let newErrors = {};
    if (!formData.employee_id) {
      newErrors.employee_id = 'Employee ID is required.';
    } else if (formData.employee_id.length !== 8) {
      newErrors.employee_id = 'Employee ID must be 8 characters long.';
    } else if (!/^[A-Z0-9]{8}$/i.test(formData.employee_id)) {
      newErrors.employee_id = 'Employee ID can only contain uppercase letters (A-Z) and numbers (0-9).';
    }

    if (!formData.full_name) {
      newErrors.full_name = 'Full name is required.';
    }

    // Validate email
    if (formData.email && !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(formData.email)) {
      newErrors.email = 'Invalid email format.';
    }

    // Validate phone number (Vietnam format)
    if (formData.phone && !/^(\+84|0)[0-9]{9,10}$/.test(formData.phone)) {
      newErrors.phone = 'Invalid phone number format (must be Vietnam format).';
    }
    
    // Image validation logic
    if (!isEditing && !imageFile) { 
        newErrors.imageFile = 'Face recognition image is required.';
    }
    if (isEditing && !imageFile && !initialEmployee?.imageUrl) {
        newErrors.imageFile = 'Face recognition image is required when editing if no old image exists.';
    }


    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSave({ ...formData, imageFile: imageFile, imageUrl: initialEmployee?.imageUrl || null }, isEditing); 
    } else {
      console.log("Form has validation errors.");
    }
  };

  return (
    <div className="employee-form-container">
      <h2 className="employee-form-heading text-gradient-primary">
        {isEditing ? 'Edit Employee Information' : 'Add New Employee'}
      </h2>
      <form onSubmit={handleSubmit} className="employee-form">
        <div className="form-layout-two-columns">
          <div className="form-left-column">
            <div className="form-group">
              <label htmlFor="employee_id">Employee ID <span className="required">*</span></label>
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
              <label htmlFor="full_name">Full Name <span className="required">*</span></label>
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
              <label htmlFor="department">Department</label>
              <input
                type="text"
                id="department"
                name="department"
                value={formData.department}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="position">Position</label>
              <input
                type="text"
                id="position"
                name="position"
                value={formData.position}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="phone">Phone Number</label>
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
              <label htmlFor="status">Active</label>
            </div>
          </div> 

          <div className="form-right-column"> 
            <div className="image-upload-section">
              <h3>Face Recognition Image</h3>
              <div className="image-preview-area-upload">
                {imagePreviewUrl || (isEditing && initialEmployee?.imageUrl) ? (
                  <img
                    src={imagePreviewUrl || initialEmployee.imageUrl}
                    alt="Employee photo"
                    className="employee-photo-preview"
                  />
                ) : (
                  <div className="employee-photo-placeholder">
                    <span>No image</span>
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

              {(imagePreviewUrl || (isEditing && initialEmployee?.imageUrl)) && (
                <button 
                  type="button" 
                  onClick={() => {
                    setImageFile(null); 
                    setImagePreviewUrl(null); 
                  }} 
                  className="clear-image-button danger-button"
                >
                  <i className="fas fa-trash-alt"></i> Clear Image
                </button>
              )}
            </div>
          </div> 
        </div> 

        <div className="form-actions">
          <button type="button" className="cancel-button secondary-button" onClick={onCancel}>
            Cancel
          </button>
          <button type="submit" className="save-button primary-button">
            {isEditing ? 'Save Changes' : 'Add Employee'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EmployeeForm;
