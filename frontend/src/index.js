import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom'; // Import BrowserRouter để bật routing
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { library } from '@fortawesome/fontawesome-svg-core'; // Import library Font Awesome
import { fas } from '@fortawesome/free-solid-svg-icons'; // Import các icon solid của Font Awesome

// Thêm tất cả các icon solid vào thư viện Font Awesome để chúng có thể được sử dụng trong ứng dụng
library.add(fas);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    {/* Bọc component App bằng BrowserRouter để cho phép sử dụng React Router hooks (như useLocation, useNavigate) bên trong App và các component con của nó */}
    <BrowserRouter> 
      <App />
    </BrowserRouter>
  </React.StrictMode>
);

// Nếu bạn muốn bắt đầu đo hiệu suất trong ứng dụng của mình, hãy truyền một hàm
// để ghi lại kết quả (ví dụ: reportWebVitals(console.log))
// hoặc gửi đến một điểm cuối phân tích. Tìm hiểu thêm: https://bit.ly/CRA-vitals
reportWebVitals();
