// src/components/common/Message.jsx
import React, { useEffect, useState } from 'react';
import './Message.css'; // Import CSS cho Message component

const GlobalMessage = ({ message, type, onClose }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (message) {
      setIsVisible(true);
      const timer = setTimeout(() => {
        setIsVisible(false);
        // Delay calling onClose until after the fade-out animation
        setTimeout(() => onClose(), 300); // match fade-out duration
      }, 5000); // Message visible for 5 seconds
      return () => clearTimeout(timer);
    } else {
      setIsVisible(false);
    }
  }, [message, onClose]);

  if (!message && !isVisible) return null;

  return (
    <div className={`global-message-container ${type} ${isVisible ? 'show' : 'hide'}`}>
      <p>{message}</p>
      <button onClick={onClose} className="close-message-button">&times;</button>
    </div>
  );
};

export default GlobalMessage;
