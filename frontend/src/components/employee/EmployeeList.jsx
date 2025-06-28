// src/components/employee/EmployeeList.jsx
import React from 'react';
import './EmployeeList.css'; 

// Function to format date and time
const formatDateTime = (isoString) => {
  if (!isoString) return 'N/A';
  try {
    const date = new Date(isoString);
    // Customize format as desired, e.g., DD/MM/YYYY HH:MM
    return date.toLocaleString('vi-VN', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      hour12: false // 24-hour format
    });
  } catch (error) {
    console.error("Error formatting date:", isoString, error);
    return 'Invalid Date';
  }
};

// Component to display employee list in a table
const EmployeeList = ({ employees, onOpenActionsModal }) => { 
  return (
    <div className="employee-list-container">
      {/* Employee list title, using utility class for gradient */}
      <h2 className="employee-list-heading text-gradient-light">Employee List</h2>
      {employees.length === 0 ? (
        // Display message if no employees are found
        <p className="no-employees-message">No employees found in the list.</p>
      ) : (
        // Table wrapper for horizontal scrolling on small screens
        <div className="employee-table-wrapper">
          <table className="employee-table">
            {/* Table header */}
            <thead>
              <tr>
                <th>Image</th>
                <th>Employee ID</th>
                <th>Full Name</th>
                <th>Department</th>
                <th>Position</th>
                <th>Email</th>
                <th>Phone Number</th>
                <th>Status</th>
                <th>Start Date</th> 
                <th>Last Update</th> 
                {/* "Actions" column has been REMOVED */}
              </tr>
            </thead>
            {/* Table body */}
            <tbody>
              {employees.map((employee) => (
                // When clicking on a row, call onOpenActionsModal to open the action selection modal
                <tr 
                  key={employee.employee_id} 
                  onClick={() => onOpenActionsModal(employee)} 
                  className="employee-table-row-clickable" 
                >
                  <td>
                    {employee.imageUrl ? ( // Display image if URL exists
                      <img
                        src={employee.imageUrl}
                        alt={employee.full_name}
                        className="employee-table-image"
                        onError={(e) => {
                          e.target.onerror = null; // Prevent error loop
                          e.target.src = 'https://placehold.co/50x50/cccccc/ffffff?text=No+Img'; // Placeholder image if loading fails
                        }}
                      />
                    ) : (
                      // Placeholder icon if no image
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
                    {/* Display status with colored badge */}
                    <span className={`status-indicator ${employee.status ? 'active' : 'inactive'}`}>
                      {employee.status ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>{formatDateTime(employee.created_at)}</td> 
                  <td>{formatDateTime(employee.updated_at)}</td> 
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
