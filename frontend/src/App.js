import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';

// Import các component cần thiết
import Layout from './components/Layout/Layout';
import WebcamCapture from './components/employee/WebcamCapture';
import EmployeeManagement from './pages/admin/EmployeeManagement';
import GlobalMessage from './components/common/Message'; 
import StartupModal from './components/common/StartupModal'; 
import LoginModal from './components/common/LoginModal'; 

// import './App.css'; // Comment hoặc xóa dòng này nếu bạn không muốn App.css

function App() {
  // State để quản lý thông báo toàn cục
  const [globalMessage, setGlobalMessageState] = useState(''); 
  const [isError, setIsError] = useState(false); 
  const [showStartupModal, setShowStartupModal] = useState(true); 
  const [showLoginModal, setShowLoginModal] = useState(false); 

  const location = useLocation(); 
  const navigate = useNavigate(); 

  // useEffect để tự động ẩn thông báo sau vài giây
  useEffect(() => {
    let timer;
    if (globalMessage) {
      timer = setTimeout(() => {
        setGlobalMessageState('');
        setIsError(false);
      }, 5000); 
    }
    return () => clearTimeout(timer); 
  }, [globalMessage]);

  // Hàm để đóng thông báo toàn cục
  const handleCloseGlobalMessage = () => { // ĐẢM BẢO HÀM NÀY ĐƯỢC ĐỊNH NGHĨA TRONG COMPONENT
    setGlobalMessageState('');
    setIsError(false);
  };

  // Hàm để đóng modal khởi động
  const handleCloseStartupModal = () => {
    setShowStartupModal(false); 
  };

  // Hàm được gọi khi người dùng chọn "Admin" từ Startup Modal
  const handleAdminSelected = () => {
    setShowStartupModal(false); 
    setShowLoginModal(true);    
  };

  // Hàm xử lý khi đăng nhập thành công
  const handleLoginSuccess = () => {
    setShowLoginModal(false); 
    navigate('/admin/employees'); 
  };

  // Hàm để đóng Login Modal
  const handleCloseLoginModal = () => {
    setShowLoginModal(false);
    navigate('/'); 
  };

  // Hàm này được truyền xuống các component con để chúng có thể gửi thông báo lên App.js.
  const setAppGlobalMessage = (messageText, isErrorMessage = false) => {
    setGlobalMessageState(messageText);
    setIsError(isErrorMessage);
  };

  // Hàm xử lý chụp ảnh từ WebcamCapture và gửi lên server.
  const handleImageCapture = async (imageSrc) => {
    setAppGlobalMessage('', false); 

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
      const response = await fetch('http://localhost:5000/api/recognize', { 
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        setAppGlobalMessage(errorData.error || 'Lỗi không xác định từ máy chủ.', true);
        return;
      }

      const data = await response.json();

      if (data.message) {
        const isErrorResponse = data.message.includes('No face detected') || data.message.includes('No match found') || data.message.includes('Error');
        setAppGlobalMessage(data.message, isErrorResponse);
      } else {
        setAppGlobalMessage('Nhận diện khuôn mặt thành công!', false);
      }

    } catch (error) {
      console.error('Lỗi khi gửi ảnh:', error);
      if (error.response) { 
        setAppGlobalMessage(`Lỗi kết nối: ${error.response.data.error || error.response.statusText}`, true);
      } else if (error.request) { 
        setAppGlobalMessage('Lỗi mạng: Không nhận được phản hồi từ máy chủ. Vui lòng kiểm tra kết nối hoặc địa chỉ máy chủ.', true);
      } else { 
        setAppGlobalMessage('Lỗi không xác định khi gửi ảnh.', true);
      }
    } finally {
      // setIsLoading(false); 
    }
  };

  // Xác định các route không cần Layout (và Sidebar)
  const noLayoutRoutes = ['/']; 
  const currentPathRequiresNoLayout = noLayoutRoutes.includes(location.pathname);


  return (
    <> 
      {globalMessage && (
        <GlobalMessage message={globalMessage} type={isError ? 'error' : 'success'} onClose={handleCloseGlobalMessage}>
          {/* Children prop is not needed if message is passed directly */}
        </GlobalMessage>
      )}

      {showStartupModal ? (
        <StartupModal onClose={handleCloseStartupModal} onAdminSelected={handleAdminSelected} /> 
      ) : showLoginModal ? ( 
        <LoginModal 
          onLoginSuccess={handleLoginSuccess} 
          onClose={handleCloseLoginModal} 
          setAppGlobalMessage={setAppGlobalMessage} 
        />
      ) : (
        currentPathRequiresNoLayout ? (
          <Routes>
            <Route path="/" element={<WebcamCapture onCapture={handleImageCapture} />} />
          </Routes>
        ) : (
          <Layout> 
            <Routes>
              <Route path="/" element={<WebcamCapture onCapture={handleImageCapture} />} /> 
              <Route 
                path="/admin/employees" 
                element={<EmployeeManagement setGlobalMessage={setAppGlobalMessage} />} 
              />
            </Routes>
          </Layout>
        )
      )}
    </>
  );
}

export default App;
