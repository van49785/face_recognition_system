import React, { useState } from 'react';
// Đảm bảo đường dẫn này đúng với vị trí file WebcamCapture.js của bạn
// Ví dụ: './components/employee/WebcamCapture' nếu nó nằm trong src/components/employee
import WebcamCapture from './components/employee/WebcamCapture'; 
import axios from 'axios'; // Import axios để gửi HTTP requests

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
    setCapturedImage(imageSrc); // Lưu ảnh đã chụp để hiển thị lại nếu cần
    setServerMessage(''); // Reset thông báo cũ khi bắt đầu một lần gửi mới
    setIsLoading(true); // Bật trạng thái loading

    // --- Bắt đầu chuyển đổi ảnh từ Base64 sang Blob ---
    // `imageSrc` có định dạng "data:image/jpeg;base64,..."
    // Chúng ta cần lấy phần dữ liệu Base64 sau dấu phẩy.
    const base64Data = imageSrc.split(',')[1];
    const byteCharacters = atob(base64Data); // Giải mã chuỗi Base64 thành chuỗi nhị phân
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    // Tạo đối tượng Blob với kiểu MIME là JPEG
    const blob = new Blob([byteArray], { type: 'image/jpeg' }); 
    // --- Kết thúc chuyển đổi ---

    // Tạo FormData để đóng gói file ảnh và gửi lên server
    const formData = new FormData();
    // 'photo' là tên trường (field name) mà backend API của bạn sẽ mong đợi nhận.
    // Đảm bảo tên này khớp với tên mà backend (Thiệp, Vân, Long) đã định nghĩa.
    formData.append('photo', blob, 'webcam_capture.jpg'); 

    try {
      // Gửi yêu cầu POST lên server backend sử dụng axios.
      // !!! CẬP NHẬT URL NÀY CHO KHỚP VỚI ĐỊA CHỈ API CỦA BACKEND CỦA BẠN !!!
      // Ví dụ: 'http://localhost:5000/api/capture'
      const response = await axios.post('http://localhost:5000/api/capture', formData, {
        headers: {
          'Content-Type': 'multipart/form-data' // Rất quan trọng để server hiểu đây là dữ liệu form có chứa file
        }
      });
      // Nếu yêu cầu thành công, cập nhật thông báo với dữ liệu từ server
      setServerMessage(response.data.message || "Ảnh đã được nhận thành công!");
      console.log("Phản hồi từ server:", response.data);
    } catch (error) {
      console.error("Lỗi khi gửi ảnh:", error);
      // Xử lý các loại lỗi khác nhau để hiển thị thông báo phù hợp
      if (error.response) {
        // Lỗi từ phía server (HTTP status code 4xx, 5xx)
        setServerMessage(`Lỗi: ${error.response.data.error || "Không thể kết nối đến server."}`);
      } else if (error.request) {
        // Yêu cầu đã được gửi nhưng không nhận được phản hồi (lỗi mạng, server chưa chạy, CORS)
        setServerMessage("Lỗi mạng: Không nhận được phản hồi từ server. Vui lòng kiểm tra kết nối hoặc địa chỉ server.");
      } else {
        // Lỗi khác xảy ra trong quá trình thiết lập yêu cầu
        setServerMessage("Lỗi không xác định khi gửi ảnh.");
      }
    } finally {
      setIsLoading(false); // Luôn tắt trạng thái loading sau khi yêu cầu hoàn tất (dù thành công hay thất bại)
    }
  };

  return (
    <div className="App">
      {/* Không còn header <h1>Hệ thống chấm công</h1> ở đây nữa vì đã có trong WebcamCapture */}
      {/* Truyền hàm handleImageCapture xuống WebcamCapture qua prop onCapture */}
      <WebcamCapture onCapture={handleImageCapture} />

      {/* Hiển thị trạng thái loading khi ảnh đang được gửi */}
      {isLoading && <p className="loading-message">Đang gửi ảnh...</p>}

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