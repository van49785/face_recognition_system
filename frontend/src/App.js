import React, { useState } from 'react';
import WebcamCapture from './components/employee/WebcamCapture'; 
import axios from 'axios'; 

function App() {
  // State để lưu ảnh đã chụp dưới dạng chuỗi Base64
  const [capturedImage, setCapturedImage] = useState(null);
  // State để lưu thông báo nhận được từ server (thành công hoặc lỗi)
  const [serverMessage, setServerMessage] = useState(''); 
  // State để theo dõi trạng thái gửi ảnh (đang gửi, đã xong)
  const [isLoading, setIsLoading] = useState(false); 

  /**
   * Hàm này được truyền xuống WebcamCapture component qua prop 'onCapture'.
   * Nó sẽ được gọi khi người dùng xác nhận gửi ảnh.
   * Chịu trách nhiệm chuyển đổi ảnh Base64 và gửi lên server.
   * @param {string} imageSrc Chuỗi Base64 của ảnh đã chụp từ WebcamCapture.
   */
  const handleImageCapture = async (imageSrc) => {
  setCapturedImage(imageSrc);
  setServerMessage('');
  setIsLoading(true);

  const base64Data = imageSrc.split(',')[1];
  const byteCharacters = atob(base64Data);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], { type: 'image/jpeg' });

  const formData = new FormData();
  formData.append('image', blob, 'webcam_capture.jpg');

  try {
    const response = await axios.post('http://localhost:5000/api/recognize', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    if (response.data.image) {
      // Nếu nhận được ảnh đã xử lý từ server, hiển thị ảnh
      const processedImage = `data:image/jpeg;base64,${response.data.image}`;
      setCapturedImage(processedImage);
    }

    setServerMessage(response.data.message || 'Photo received successfully!');
    console.log('Phản hồi từ server:', response.data);
  } catch (error) {
    console.error('Lỗi khi gửi ảnh:', error);
    if (error.response) {
      setServerMessage(`Lỗi: ${error.response.data.error || 'Unable to connect to server.'}`);
    } else if (error.request) {
      setServerMessage('Network Error: No response received from server. Please check connection or server address.');
    } else {
      setServerMessage('Unknown error while sending photo.');
    }
  } finally {
    setIsLoading(false);
  }
};

  return (
    <div className="App">
      {/* Không còn header <h1>Hệ thống chấm công</h1> ở đây nữa vì đã có trong WebcamCapture */}
      {/* Truyền hàm handleImageCapture xuống WebcamCapture qua prop onCapture */}
      <WebcamCapture onCapture={handleImageCapture} />

      {/* Hiển thị trạng thái loading khi ảnh đang được gửi */}
      {/* {isLoading && <p className="loading-message">Sending</p>} */}

      {/* Hiển thị thông báo từ server (thành công hoặc lỗi) */}
      {serverMessage && (
        <p className={serverMessage.startsWith('Lỗi') ? 'error-message' : 'success-message'}>
          {serverMessage}
        </p>
      )}

      {/* Bạn có thể tùy chọn hiển thị ảnh đã chụp ở đây nếu muốn,
          nhưng WebcamCapture đã có phần preview ảnh riêng.
          Giữ lại phần này nếu muốn có preview ảnh "tổng quan" ở cấp App.js */}
      {capturedImage && !isLoading && !serverMessage.startsWith('Lỗi') && (
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          {/* <h3>Ảnh đã gửi:</h3> */}
          {/* <img src={capturedImage} alt="Ảnh đã chụp" style={{ maxWidth: '400px', height: 'auto', borderRadius: '12px', boxShadow: '0 4px 8px rgba(0,0,0,0.2)' }} /> */}
        </div>
      )}
    </div>
  );
}

export default App;