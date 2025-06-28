// src/components/employee/EmployeeActionModal.jsx
import React from 'react';
import './EmployeeActionModal.css'; // Import CSS for this modal

const EmployeeActionModal = ({ employee, onEditClick, onDeleteClick, onClose }) => {
  // Do not render if no employee data is provided
  if (!employee) return null; 

  return (
    <div className="action-modal-overlay">
      <div className="action-modal-content">
        {/* Close button for the modal */}
        <button className="modal-close-button" onClick={onClose}>&times;</button>
        {/* Modal title displaying the employee's name */}
        <h2 className="action-modal-title">Select Action for {employee.full_name}</h2>
        {/* Subtitle displaying employee ID */}
        <p className="action-modal-subtitle">Employee ID: {employee.employee_id}</p>
        
        <div className="action-buttons-group">
          {/* Button to edit employee information: closes current modal and calls edit function */}
          <button 
            onClick={() => {
              onClose(); // Close the action selection modal
              onEditClick(employee); // Call the function to open the employee edit form
            }} 
            className="action-option-button primary-button"
          >
            <i className="fas fa-edit"></i> Edit Information
          </button>
          
          {/* Button to delete employee: closes current modal and calls delete function */}
          <button 
            onClick={() => {
              onClose(); // Close the action selection modal
              onDeleteClick(employee.employee_id); // Call the employee delete function
            }} 
            className="action-option-button danger-button"
          >
            <i className="fas fa-trash-alt"></i> Delete Employee
          </button>
        </div>
      </div>
    </div>
  );
};

export default EmployeeActionModal;
