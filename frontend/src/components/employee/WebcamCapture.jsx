import React, { useRef, useState } from "react";
import Webcam from "react-webcam";

const WebcamCapture = () => {
  const webcamRef = useRef(null);
  const [imageSrc, setImageSrc] = useState(null);
  const [cameraOn, setCameraOn] = useState(true);
  const [isCapturing, setIsCapturing] = useState(false);

  const capture = () => {
    setIsCapturing(true);
    setTimeout(() => {
      const image = webcamRef.current.getScreenshot();
      setImageSrc(image);
      setIsCapturing(false);
    }, 200);
  };

  const toggleCamera = () => {
    setCameraOn(!cameraOn);
    setImageSrc(null);
  };

  const retakePhoto = () => {
    setImageSrc(null);
  };

  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e293b 0%, #7c3aed 50%, #1e293b 100%)',
      padding: '24px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    },
    wrapper: {
      maxWidth: '672px',
      margin: '0 auto'
    },
    header: {
      textAlign: 'center',
      marginBottom: '32px'
    },
    iconWrapper: {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: '64px',
      height: '64px',
      background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
      borderRadius: '50%',
      marginBottom: '16px',
      boxShadow: '0 10px 25px rgba(0,0,0,0.3)'
    },
    userIcon: {
      width: '32px',
      height: '32px',
      fill: 'white'
    },
    title: {
      fontSize: '36px',
      fontWeight: 'bold',
      color: 'white',
      marginBottom: '8px',
      background: 'linear-gradient(135deg, #60a5fa, #a78bfa)',
      backgroundClip: 'text',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent'
    },
    subtitle: {
      color: '#cbd5e1',
      fontSize: '18px'
    },
    mainCard: {
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(20px)',
      borderRadius: '24px',
      padding: '32px',
      boxShadow: '0 25px 50px rgba(0,0,0,0.25)',
      border: '1px solid rgba(255, 255, 255, 0.2)'
    },
    buttonContainer: {
      display: 'flex',
      justifyContent: 'center',
      marginBottom: '24px'
    },
    button: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '12px',
      padding: '12px 24px',
      borderRadius: '16px',
      fontWeight: '600',
      color: 'white',
      border: 'none',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
      fontSize: '16px'
    },
    toggleButton: {
      background: 'linear-gradient(135deg, #ef4444, #ec4899)'
    },
    toggleButtonOn: {
      background: 'linear-gradient(135deg, #10b981, #059669)'
    },
    captureButton: {
      background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
      padding: '16px 32px',
      fontSize: '18px'
    },
    captureButtonDisabled: {
      background: '#6b7280',
      cursor: 'not-allowed'
    },
    retakeButton: {
background: 'linear-gradient(135deg, #f97316, #ef4444)'
    },
    confirmButton: {
      background: 'linear-gradient(135deg, #10b981, #059669)'
    },
    webcamContainer: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '24px'
    },
    webcamWrapper: {
      position: 'relative',
      borderRadius: '24px',
      overflow: 'hidden',
      boxShadow: '0 25px 50px rgba(0,0,0,0.25)',
      border: '4px solid rgba(255, 255, 255, 0.2)'
    },
    webcam: {
      display: 'block'
    },
    overlay: {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      pointerEvents: 'none'
    },
    overlayCorner: {
      position: 'absolute',
      width: '32px',
      height: '32px',
      border: '4px solid #60a5fa'
    },
    overlayCornerTL: {
      top: '16px',
      left: '16px',
      borderRight: 'none',
      borderBottom: 'none',
      borderTopLeftRadius: '8px'
    },
    overlayCornerTR: {
      top: '16px',
      right: '16px',
      borderLeft: 'none',
      borderBottom: 'none',
      borderTopRightRadius: '8px'
    },
    overlayCornerBL: {
      bottom: '16px',
      left: '16px',
      borderRight: 'none',
      borderTop: 'none',
      borderBottomLeftRadius: '8px'
    },
    overlayCornerBR: {
      bottom: '16px',
      right: '16px',
      borderLeft: 'none',
      borderTop: 'none',
      borderBottomRightRadius: '8px'
    },
    photoSection: {
      textAlign: 'center'
    },
    photoTitle: {
      fontSize: '24px',
      fontWeight: 'bold',
      color: 'white',
      marginBottom: '16px'
    },
    photoWrapper: {
      position: 'relative',
      display: 'inline-block',
      borderRadius: '24px',
      overflow: 'hidden',
      boxShadow: '0 25px 50px rgba(0,0,0,0.25)',
      border: '4px solid rgba(34, 197, 94, 0.5)',
      marginBottom: '24px'
    },
    photo: {
      display: 'block'
    },
    successOverlay: {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      // background: 'rgba(34, 197, 94, 0.2)',
      pointerEvents: 'none'
    },
    buttonGroup: {
      display: 'flex',
      gap: '16px',
      justifyContent: 'center'
    },
    cameraOffSection: {
      textAlign: 'center',
      padding: '48px 0'
    },
    cameraOffIcon: {
      width: '96px',
      height: '96px',
      background: 'rgba(71, 85, 105, 0.5)',
      borderRadius: '50%',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      marginBottom: '24px'
    },
    cameraOffTitle: {
      fontSize: '20px',
      fontWeight: '600',
      color: 'white',
      marginBottom: '8px'
    },
    cameraOffText: {
      color: '#94a3b8'
    },
    instructions: {
      marginTop: '32px',
      textAlign: 'center'
    },
    instructionsBadge: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px 16px',
      background: 'rgba(255, 255, 255, 0.1)',
backdropFilter: 'blur(8px)',
      borderRadius: '20px',
      border: '1px solid rgba(255, 255, 255, 0.2)'
    },
    statusDot: {
      width: '8px',
      height: '8px',
      background: '#22c55e',
      borderRadius: '50%',
      animation: 'pulse 2s infinite'
    },
    instructionsText: {
      color: '#cbd5e1',
      fontSize: '14px'
    }
  };

  return (
    <div style={styles.container}>
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        button:hover {
          transform: scale(1.05);
        }
        button:active {
          transform: scale(0.95);
        }
      `}</style>
      
      <div style={styles.wrapper}>
        {/* Header */}
        <div style={styles.header}>
          <div style={styles.iconWrapper}>
            <svg style={styles.userIcon} viewBox="0 0 24 24">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <h1 style={styles.title}>Face Attendance</h1>
          <p style={styles.subtitle}>
            Capture your photo for attendance verification
          </p>
        </div>

        {/* Main Card */}
        <div style={styles.mainCard}>
          {/* Camera Toggle Button */}
          <div style={styles.buttonContainer}>
            <button
              onClick={toggleCamera}
              style={{
                ...styles.button,
                ...(cameraOn ? styles.toggleButton : styles.toggleButtonOn)
              }}
            >
              <span>{cameraOn ? '📷' : '📹'}</span>
              {cameraOn ? 'Turn Off Camera' : 'Turn On Camera'}
            </button>
          </div>

          {/* Camera View */}
          {cameraOn && !imageSrc && (
            <div style={styles.webcamContainer}>
              <div style={styles.webcamWrapper}>
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  width={400}
                  height={300}
                  videoConstraints={{
                    facingMode: "user",
                  }}
                  style={styles.webcam}
                />
                {/* Overlay effect */}
                <div style={styles.overlay}>
                  <div style={{...styles.overlayCorner, ...styles.overlayCornerTL}}></div>
                  <div style={{...styles.overlayCorner, ...styles.overlayCornerTR}}></div>
                  <div style={{...styles.overlayCorner, ...styles.overlayCornerBL}}></div>
                  <div style={{...styles.overlayCorner, ...styles.overlayCornerBR}}></div>
                </div>
              </div>

              {/* Capture Button */}
              <button
                onClick={capture}
                disabled={isCapturing}
                style={{
                  ...styles.button,
                  ...styles.captureButton,
...(isCapturing ? styles.captureButtonDisabled : {})
                }}
              >
                <span>📸</span>
                {isCapturing ? 'Capturing...' : 'Take Photo'}
              </button>
            </div>
          )}

          {/* Photo Preview */}
          {imageSrc && (
            <div style={styles.photoSection}>
              <h3 style={styles.photoTitle}>
                📸 Photo Captured Successfully!
              </h3>
              <div style={styles.photoWrapper}>
                <img 
                  src={imageSrc} 
                  alt="captured" 
                  width={400}
                  style={styles.photo}
                />
                {/* Success overlay */}
                <div style={styles.successOverlay}></div>
              </div>

              {/* Action Buttons */}
              <div style={styles.buttonGroup}>
                <button
                  onClick={retakePhoto}
                  style={{...styles.button, ...styles.retakeButton}}
                >
                  <span>🔄</span>
                  Retake Photo
                </button>
                
                <button
                  style={{...styles.button, ...styles.confirmButton}}
                >
                  <span>✓</span>
                  Confirm Attendance
                </button>
              </div>
            </div>
          )}

          {/* Camera Off State */}
          {!cameraOn && (
            <div style={styles.cameraOffSection}>
              <div style={styles.cameraOffIcon}>
                <svg width="48" height="48" fill="#94a3b8" viewBox="0 0 24 24">
                  <path d="M9.5 6.5v3M15.1 8.4l2.1-2.1M11 1h2v3h-2zM11 20h2v3h-2zM4.2 10.2L1 13l3.2 2.8M20.8 10.2L24 13l-3.2 2.8M6.3 17.7l-2.1 2.1M17.7 6.3l2.1-2.1"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </div>
              <h3 style={styles.cameraOffTitle}>
                Camera is turned off
              </h3>
              <p style={styles.cameraOffText}>
                Click "Turn On Camera" to start capturing photos
              </p>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div style={styles.instructions}>
          <div style={styles.instructionsBadge}>
            <div style={styles.statusDot}></div>
            <span style={styles.instructionsText}>
              Position your face in the frame and click capture
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebcamCapture;