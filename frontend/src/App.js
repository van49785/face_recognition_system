import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';

// Import các component cần thiết
import Layout from './components/Layout/Layout';
import WebcamCapture from './components/employee/WebcamCapture'; 
import EmployeeManagement from './pages/admin/EmployeeManagement';
import GlobalMessage from './components/common/Message'; 
import LoginModal from './components/admin/LoginModal'; 
import { AuthProvider, useAuth } from './context/AuthContext'; 

// Import CSS toàn cục cho các phần tử như nút admin login
import './AppGlobal.css'; // Sẽ tạo file này

function AppContent() { 
  const [globalMessage, setGlobalMessageState] = useState(''); 
  const [isError, setIsError] = useState(false); 
  const [showLoginModal, setShowLoginModal] = useState(false); // Quản lý LoginModal ở đây

  const location = useLocation(); 
  const navigate = useNavigate(); 
  const { isAdminLoggedIn } = useAuth(); 

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

  const handleCloseGlobalMessage = () => {
    setGlobalMessageState('');
    setIsError(false);
  };

  const setAppGlobalMessage = (message, isErrorMessage = false) => {
    setGlobalMessageState(message);
    setIsError(isErrorMessage);
  };

  // Hàm xử lý khi admin bấm đăng nhập (từ nút toàn cục)
  const handleAdminLoginClick = () => {
    setShowLoginModal(true);
  };

  // Hàm xử lý khi LoginModal đóng lại
  const handleCloseLoginModal = () => {
    setShowLoginModal(false);
    // Nếu LoginModal đóng mà không phải do đăng nhập thành công,
    // thì vẫn giữ người dùng ở trang hiện tại (chấm công nếu họ đang ở đó)
  };

  // Hàm xử lý khi đăng nhập admin thành công từ LoginModal
  const handleLoginSuccess = () => {
    setShowLoginModal(false); // Đóng LoginModal
    navigate('/admin/employees'); // Chuyển hướng đến trang quản lý nhân viên
    setAppGlobalMessage('Đăng nhập thành công!', false);
  };


  // Logic mới: Nếu admin đã đăng nhập và đang ở trang gốc ('/'), tự động chuyển hướng
  useEffect(() => {
    if (isAdminLoggedIn && location.pathname === '/') {
      navigate('/admin/employees');
    }
  }, [isAdminLoggedIn, location.pathname, navigate]);

  // Không render gì khi đang chuyển hướng
  if (isAdminLoggedIn && location.pathname === '/') {
    return null; 
  }

  // Xác định các route không cần Layout (chỉ trang chủ là WebcamCapture)
  const noLayoutRoutes = ['/']; 
  const currentPathRequiresNoLayout = noLayoutRoutes.includes(location.pathname);

  return (
    <> 
      {/* GlobalMessage đã được di chuyển ra ngoài AppContent để hiển thị ổn định */}
      
      {currentPathRequiresNoLayout ? (
        // Trang WebcamCapture (chấm công)
        <>
          <Routes>
            <Route path="/" element={<WebcamCapture setAppGlobalMessage={setAppGlobalMessage} />} /> 
          </Routes>
          {/* Nút Đăng nhập Admin toàn cục - chỉ hiển thị trên trang chấm công và khi chưa đăng nhập */}
          {!isAdminLoggedIn && location.pathname === '/' && (
            <button onClick={handleAdminLoginClick} className="global-admin-login-button">
              <i className="fas fa-user-shield"></i> Đăng nhập Admin
            </button>
          )}
        </>
      ) : (
        // Trang admin (ví dụ: Quản lý nhân viên)
        <Layout setAppGlobalMessage={setAppGlobalMessage} > 
          <Routes>
            <Route path="/" element={<WebcamCapture setAppGlobalMessage={setAppGlobalMessage} />} /> 
            <Route 
              path="/admin/employees" 
              element={<EmployeeManagement setGlobalMessage={setAppGlobalMessage} />} 
            />
          </Routes>
        </Layout>
      )}

      {/* Render LoginModal khi showLoginModal là true */}
      {showLoginModal && (
        <LoginModal 
          onLoginSuccess={handleLoginSuccess} 
          onClose={handleCloseLoginModal} 
          setAppGlobalMessage={setAppGlobalMessage} 
        />
      )}
    </>
  );
}

function App() {
  const [globalMessage, setGlobalMessageState] = useState(''); 
  const [isError, setIsError] = useState(false); 

  const setAppGlobalMessage = (message, isErrorMessage = false) => {
    setGlobalMessageState(message);
    setIsError(isErrorMessage);
  };

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


  return (
    <AuthProvider setAppGlobalMessage={(msg, isErr) => {
      setGlobalMessageState(msg);
      setIsError(isErr);
    }}>
      {globalMessage && ( 
        <GlobalMessage message={globalMessage} type={isError ? 'error' : 'success'} onClose={() => {
          setGlobalMessageState('');
          setIsError(false);
        }} />
      )}
      <AppContent />
    </AuthProvider>
  );
}

export default App;
