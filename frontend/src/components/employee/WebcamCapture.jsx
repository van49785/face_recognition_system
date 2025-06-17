import React, { useRef, useState, useCallback } from "react";
import Webcam from "react-webcam";
import './WebcamCapture.css'; // Import the new CSS file

// Receive the 'onCapture' prop from the parent component (App.js)
const WebcamCapture = ({ onCapture }) => { // Add 'onCapture' to props
  const webcamRef = useRef(null);
  const [imageSrc, setImageSrc] = useState(null);
  const [cameraOn, setCameraOn] = useState(true);
  const [isCapturing, setIsCapturing] = useState(false);

  // Use useCallback for performance optimization
  const capture = useCallback(() => {
    setIsCapturing(true);
    // Optional: Small delay to create a capture effect
    setTimeout(() => {
      const image = webcamRef.current.getScreenshot();
      setImageSrc(image);
      setIsCapturing(false);
      // No longer calling onCapture directly here.
      // The image will be sent when the "Confirm Attendance" button is clicked.
    }, 200);
  }, [webcamRef, setImageSrc, setIsCapturing]);

  const toggleCamera = useCallback(() => {
    setCameraOn(prevCameraOn => !prevCameraOn);
    setImageSrc(null); // Clear captured image when toggling camera
  }, []);

  const retakePhoto = useCallback(() => {
    setImageSrc(null); // Clear captured image to allow retaking
  }, []);

  // No more inline styles object here, as styles are now in WebcamCapture.css

  return (
    <div className="webcam-capture-container">
      {/* No need for <style> tag here anymore, as animations are in CSS file */}
      
      <div className="webcam-capture-wrapper">
        {/* Header */}
        <div className="webcam-capture-header">
          <div className="webcam-capture-icon-wrapper">
            <svg className="webcam-capture-user-icon" viewBox="0 0 24 24">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <h1 className="webcam-capture-title">Face Attendance</h1>
          <p className="webcam-capture-subtitle">
            Capture your photo for attendance verification
          </p>
        </div>

        {/* Main Card */}
        <div className="webcam-capture-main-card">
          {/* Camera Toggle Button */}
          <div className="webcam-capture-button-container">
            <button
              onClick={toggleCamera}
              className={`webcam-capture-button ${cameraOn ? 'webcam-capture-toggle-button-off' : 'webcam-capture-toggle-button-on'}`}
            >
              <span>{cameraOn ? '📷' : '📹'}</span>
              {cameraOn ? 'Turn Off Camera' : 'Turn On Camera'}
            </button>
          </div>

          {/* Camera View */}
          {cameraOn && !imageSrc && (
            <div className="webcam-capture-webcam-container">
              <div className="webcam-capture-webcam-wrapper">
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  width={400}
                  height={300}
                  videoConstraints={{
                    facingMode: "user",
                  }}
                  // No inline style, the .webcam-capture-webcam-wrapper video rule handles it
                />
                {/* Overlay effect */}
                <div className="webcam-capture-overlay">
                  <div className="webcam-capture-overlay-corner webcam-capture-overlay-corner-tl"></div>
                  <div className="webcam-capture-overlay-corner webcam-capture-overlay-corner-tr"></div>
                  <div className="webcam-capture-overlay-corner webcam-capture-overlay-corner-bl"></div>
                  <div className="webcam-capture-overlay-corner webcam-capture-overlay-corner-br"></div>
                </div>
              </div>

              {/* Capture Button */}
              <button
                onClick={capture}
                disabled={isCapturing}
                className={`webcam-capture-button webcam-capture-capture-button ${isCapturing ? 'webcam-capture-capture-button-disabled' : ''}`}
              >
                <span>📸</span>
                {isCapturing ? 'Capturing...' : 'Take Photo'}
              </button>
            </div>
          )}

          {/* Photo Preview */}
          {imageSrc && (
            <div className="webcam-capture-photo-section">
              <h3 className="webcam-capture-photo-title">
                📸 Photo Captured Successfully!
              </h3>
              <div className="webcam-capture-photo-wrapper">
                <img 
                  src={imageSrc} 
                  alt="captured" 
                  width={400}
                  // No inline style, .webcam-capture-photo-wrapper img handles it
                />
                {/* Success overlay */}
                <div className="webcam-capture-success-overlay"></div>
              </div>

              {/* Action Buttons */}
              <div className="webcam-capture-button-group">
                <button
                  onClick={retakePhoto}
                  className="webcam-capture-button webcam-capture-retake-button"
                >
                  <span>🔄</span>
                  Retake Photo
                </button>
                
                {/* This button now calls the onCapture prop to send the image to App.js */}
                <button
                  onClick={() => onCapture(imageSrc)} // Call onCapture prop here
                  className="webcam-capture-button webcam-capture-confirm-button"
                >
                  <span>✓</span>
                  Confirm Attendance
                </button>
              </div>
            </div>
          )}

          {/* Camera Off State */}
          {!cameraOn && (
            <div className="webcam-capture-camera-off-section">
              <div className="webcam-capture-camera-off-icon">
                <svg width="48" height="48" fill="#94a3b8" viewBox="0 0 24 24">
                  <path d="M9.5 6.5v3M15.1 8.4l2.1-2.1M11 1h2v3h-2zM11 20h2v3h-2zM4.2 10.2L1 13l3.2 2.8M20.8 10.2L24 13l-3.2 2.8M6.3 17.7l-2.1 2.1M17.7 6.3l2.1-2.1"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </div>
              <h3 className="webcam-capture-camera-off-title">
                Camera is turned off
              </h3>
              <p className="webcam-capture-camera-off-text">
                Click "Turn On Camera" to start capturing photos
              </p>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="webcam-capture-instructions">
          <div className="webcam-capture-instructions-badge">
            <div className="webcam-capture-status-dot"></div>
            <span className="webcam-capture-instructions-text">
              Position your face in the frame and click capture
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebcamCapture;
