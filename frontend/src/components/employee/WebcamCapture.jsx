// src/components/employee/WebcamCapture.jsx 
import React, { useRef, useState, useCallback, useEffect } from "react";
import Webcam from "react-webcam"; 
import GlobalMessage from "../../components/common/Message"; 
import './WebcamCapture.css'; 

const API_BASE_URL = 'http://localhost:5000';

const WebcamCapture = ({ setAppGlobalMessage }) => { 
  const webcamRef = useRef(null); 
  const [capturedImage, setCapturedImage] = useState(null); // <-- Tên state là capturedImage, setter là setCapturedImage
  const [isProcessing, setIsProcessing] = useState(false); 
  const [cameraOn, setCameraOn] = useState(true); 
  
  const [recognizedEmployeeBasic, setRecognizedEmployeeBasic] = useState(null); 
  const [attendanceStatus, setAttendanceStatus] = useState(''); 
  const [attendanceTimestamp, setAttendanceTimestamp] = useState(''); 
  const [attendanceMainMessage, setAttendanceMainMessage] = useState(''); 
  
  const [messageType, setMessageType] = useState('success'); 
  const [showResultCard, setShowResultCard] = useState(false); 

  useEffect(() => {
    let timer;
    if (showResultCard) {
      timer = setTimeout(() => {
        setShowResultCard(false);
        setCapturedImage(null); 
        setRecognizedEmployeeBasic(null); 
        setAttendanceStatus('');
        setAttendanceTimestamp('');
        setAttendanceMainMessage('');
      }, 7000); 
    }
    return () => clearTimeout(timer);
  }, [showResultCard, setCapturedImage, setRecognizedEmployeeBasic, setAttendanceStatus, setAttendanceTimestamp, setAttendanceMainMessage]); 

  const capture = useCallback(() => {
    if (!cameraOn) {
      setAppGlobalMessage("Vui lòng bật camera trước.", true); 
      return;
    }
    setIsProcessing(true); 
    setTimeout(() => {
      const image = webcamRef.current.getScreenshot();
      setCapturedImage(image); // <-- Đã sửa: dùng setCapturedImage
      setIsProcessing(false); 
      setRecognizedEmployeeBasic(null); 
      setAttendanceStatus('');
      setAttendanceTimestamp('');
      setAttendanceMainMessage('');
      setShowResultCard(false);
    }, 200); 
  }, [webcamRef, cameraOn, setAppGlobalMessage, setCapturedImage, // <-- Đã sửa: đảm bảo setCapturedImage trong dependency
      setRecognizedEmployeeBasic, setAttendanceStatus, setAttendanceTimestamp, 
      setAttendanceMainMessage, setShowResultCard]); 

  const sendForRecognitionAndAttendance = useCallback(async () => {
    if (!capturedImage) { 
      setAppGlobalMessage('Không có ảnh để chấm công.', true); 
      return;
    }

    setIsProcessing(true); 
    setRecognizedEmployeeBasic(null); 
    setAttendanceStatus('');
    setAttendanceTimestamp('');
    setAttendanceMainMessage('');
    setMessageType('success'); 
    setShowResultCard(false); 

    try {
      const base64Image = capturedImage.split(',')[1]; 
      const byteCharacters = atob(base64Image);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'image/jpeg' });
      const imageFile = new File([blob], 'webcam_capture.jpeg', { type: 'image/jpeg' });

      const formData = new FormData();
      formData.append('image', imageFile);

      const response = await fetch(`${API_BASE_URL}/api/recognize`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setRecognizedEmployeeBasic(data.employee); 
        setAttendanceStatus(data.status); 
        setAttendanceTimestamp(data.timestamp); 
        setAttendanceMainMessage(data.message);
        setMessageType('success');
      } else {
        setRecognizedEmployeeBasic(data.employee || null); 
        setAttendanceMainMessage(data.error || data.message || 'Lỗi không xác định khi chấm công.');
        setMessageType('error');

        if (data.checked_in_at && data.minimum_checkout_time) {
          setAttendanceMainMessage(
            `Chưa thể check-out. Bạn đã check-in lúc ${data.checked_in_at}. ` + 
            `Vui lòng đợi đến ${data.minimum_checkout_time}.`
          );
        }
      }
    } catch (error) {
      console.error('Lỗi khi gửi ảnh chấm công:', error);
      setAppGlobalMessage('Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối.', true); 
    } finally {
      setIsProcessing(false); 
      setShowResultCard(true); 
    }
  }, [capturedImage, setAppGlobalMessage, setRecognizedEmployeeBasic, setAttendanceStatus, setAttendanceTimestamp, setAttendanceMainMessage, setMessageType, setShowResultCard]); 

  const retakePhoto = useCallback(() => {
    setCapturedImage(null); // <-- Đã sửa: dùng setCapturedImage
    setRecognizedEmployeeBasic(null); 
    setAttendanceStatus('');
    setAttendanceTimestamp('');
    setAttendanceMainMessage('');
    setShowResultCard(false);
  }, [setCapturedImage, setRecognizedEmployeeBasic, setAttendanceStatus, setAttendanceTimestamp, 
      setAttendanceMainMessage, setShowResultCard]); 

  const toggleCamera = useCallback(() => {
    setCameraOn(prevCameraOn => !prevCameraOn);
    setCapturedImage(null); // <-- Đã sửa: dùng setCapturedImage
    setRecognizedEmployeeBasic(null); 
    setAttendanceStatus('');
    setAttendanceTimestamp('');
    setAttendanceMainMessage('');
    setShowResultCard(false);
  }, [setCameraOn, setCapturedImage, setRecognizedEmployeeBasic, setAttendanceStatus, 
      setAttendanceTimestamp, setAttendanceMainMessage, setShowResultCard]); 

  return (
    <div className="webcam-capture-container"> 
      <div className="webcam-capture-wrapper"> 
        <header className="webcam-capture-header"> 
          <div className="webcam-capture-icon-wrapper"> 
            <i className="fas fa-fingerprint"></i> 
          </div>
          <h1 className="webcam-capture-title">Hệ Thống Chấm Công Khuôn Mặt</h1> 
          <p className="webcam-capture-subtitle">Chụp ảnh để check-in hoặc check-out hàng ngày.</p> 
        </header>

        <div className={`webcam-layout-container ${!capturedImage ? 'centered' : ''}`}>
          <div className="webcam-display-area">
            {cameraOn ? (
              capturedImage ? ( 
                <img src={capturedImage} alt="Captured Preview" className="webcam-feed" /> 
              ) : (
                <Webcam
                  audio={false} 
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  width={720} 
                  height={540} 
                  videoConstraints={{
                    facingMode: "user" 
                  }}
                  className={`webcam-feed ${isProcessing ? 'capturing-effect' : ''}`}
                />
              )
            ) : (
              <div className="camera-off-placeholder">
                <div className="camera-off-icon">
                  <i className="fas fa-video-slash"></i> 
                </div>
                <h3 className="camera-off-title">Camera Đã Tắt</h3> 
                <p className="camera-off-text">Bấm "Bật Camera" để bắt đầu chụp ảnh.</p> 
              </div>
            )}
          </div>

          {capturedImage && showResultCard && (recognizedEmployeeBasic || attendanceMainMessage) && (
            <div className={`recognition-result-card ${messageType}`}>
              {messageType === 'success' ? (
                <h3 className="result-heading success-heading"><i className="fas fa-check-circle"></i> Thành Công!</h3>
              ) : (
                <h3 className="result-heading error-heading"><i className="fas fa-times-circle"></i> Thất Bại!</h3>
              )}
              
              <p className="attendance-info-message">{attendanceMainMessage}</p>

              {recognizedEmployeeBasic && (
                <div className="employee-details-display-simplified"> 
                  <div className="employee-face-recognition-image-placeholder">
                    <i className="fas fa-user-circle"></i> 
                  </div>

                  <div className="employee-text-details">
                    <p><strong>Mã NV:</strong> {recognizedEmployeeBasic.employee_id}</p>
                    <p><strong>Họ Tên:</strong> {recognizedEmployeeBasic.full_name}</p>
                    <p><strong>Phòng Ban:</strong>{recognizedEmployeeBasic.department}</p> 
                   
                    <p>
                      <strong>Giờ Chấm Công:</strong> {attendanceTimestamp}
                    </p>
                    <p>
                      <strong>Trạng Thái:</strong> 
                      <span className={`status-badge ${
                        attendanceStatus === 'check-in' || attendanceStatus === 'checked_in' ? 'active' : 
                        attendanceStatus === 'check-out' || attendanceStatus === 'completed' ? 'inactive' : '' 
                      }`}>
                        {attendanceStatus === 'check-in' ? 'Check In' : 
                         attendanceStatus === 'check-out' ? 'Check Out' : 
                         attendanceStatus === 'completed' ? 'Hoàn Thành' : 'Đang Xử Lý'}
                      </span>
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div> 

        <div className="webcam-controls">
          {!capturedImage && cameraOn && ( 
            <button 
              onClick={capture} 
              className="webcam-capture-button primary-button" 
              disabled={isProcessing || !cameraOn} 
            >
              <i className="fas fa-camera"></i> Chụp Ảnh
            </button>
          )}

          {capturedImage && ( 
            <>
              <button 
                onClick={sendForRecognitionAndAttendance} 
                className="webcam-capture-button primary-button" 
                disabled={isProcessing}
              >
                {isProcessing ? (
                  <>
                    <i className="fas fa-spinner fa-spin"></i> Đang Xử Lý...
                  </>
                ) : (
                  <>
                    <i className="fas fa-check-circle"></i> Chấm Công
                  </>
                )}
              </button>
              <button onClick={retakePhoto} className="webcam-capture-button secondary-button" disabled={isProcessing}> 
                <i className="fas fa-redo-alt"></i> Chụp Lại
              </button>
            </>
          )}

          <button onClick={toggleCamera} className={`webcam-capture-button ${cameraOn ? 'secondary-button' : 'primary-button'}`}> 
            {cameraOn ? (
              <>
                <i className="fas fa-video-slash"></i> Tắt Camera
              </>
            ) : (
              <>
                <i className="fas fa-video"></i> Bật Camera
              </>
            )}
          </button>
        </div>

        {!capturedImage && cameraOn && ( 
          <div className="webcam-capture-instructions"> 
            <div className="webcam-capture-instructions-badge"> 
              <span className="webcam-capture-status-dot"></span> 
              <span className="webcam-capture-instructions-text"> 
                Hãy nhìn thẳng vào camera để có kết quả tốt nhất.
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WebcamCapture;
