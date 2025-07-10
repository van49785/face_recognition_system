<template>
  <div class="container">
    <div class="background-decoration-top"></div>
    <div class="background-decoration-bottom"></div>

    <div class="main-content-wrapper">
      <div class="header">
        <div class="header-icon">
          <User />
        </div>
        <h1 class="header-title">Employee Attendance</h1>
        <p class="header-subtitle">Facial Recognition Check-in System</p>
      </div>

      <div v-if="error" class="error-alert">
        <div class="error-content">
          <AlertCircle />
          <span>Error</span>
        </div>
        <p>{{ error }}</p>
      </div>

      <div class="card">
        <div v-if="currentStep === 'camera'" class="section">
          <div class="camera-section">
            <Camera />
            <h2>Face Recognition</h2>
            <p>{{ statusMessage }}</p> </div>

          <div class="video-container">
            <div class="video-frame">
              <video ref="videoRef" autoplay playsinline muted></video>
              <canvas ref="canvasRef"></canvas>
              
              <div class="face-overlay">
                <div class="top-left"></div>
                <div class="top-right"></div>
                <div class="bottom-left"></div>
                <div class="bottom-right"></div>
              </div>
            </div>
            <div class="action-buttons mt-4">
              <v-btn
                v-if="isCameraActive"
                @click="stopWebcam"
                color="red-darken-2"
                size="large"
                prepend-icon="mdi-webcam-off"
              >
                Turn off Webcam
              </v-btn>
              <v-btn
                v-else
                @click="startCamera"
                color="green-darken-2"
                size="large"
                prepend-icon="mdi-webcam"
              >
                Turn on Webcam
              </v-btn>
            </div>
          </div>
        </div>

        <div v-if="currentStep === 'processing'" class="section processing-section">
          <div>
            <div class="processing-icon">
              <RefreshCw class="animate-spin" />
            </div>
            <h2>Processing...</h2>
            <p>{{ statusMessage }}</p> </div>
          
          <div class="progress-bar">
            <div class="progress-fill"></div>
          </div>
        </div>

        <div v-if="currentStep === 'success' && employee" class="section">
          <div class="success-section">
            <div class="success-icon">
              <CheckCircle />
            </div>
            <h2>Check-{{ employee.status === 'check-in' ? 'in' : 'out' }} Successful!</h2>
            <p>Welcome back to the office</p>
          </div>

          <div class="employee-card">
            <div class="employee-info">
              <div class="employee-avatar">
                {{ employee.full_name.split(' ').map(n => n[0]).join('') }}
              </div>
              <div>
                <h3>{{ employee.full_name }}</h3>
                <p>ID: {{ employee.employee_id }}</p>
                <p>{{ employee.department }}</p>
              </div>
            </div>

            <div class="employee-details">
              <div class="detail-box">
                <Clock />
                <p>Time</p>
                <p>{{ employee.timestamp }}</p>
              </div>
              <div class="detail-box">
                <Calendar />
                <p>Status</p>
                <p>{{ employee.status }}</p>
              </div>
            </div>
          </div>

          <div class="action-buttons">
            <v-btn
              @click="viewHistory"
              color="purple-darken-3"
              size="large"
              prepend-icon="mdi-history"
            >
              View Attendance History
            </v-btn>
            <v-btn
              @click="resetCamera"
              color="blue-grey-darken-1"
              size="large"
              prepend-icon="mdi-refresh"
            >
              New Checkin
            </v-btn>
          </div>
        </div>

        <div v-if="showHistory" class="section">
          <div class="history-header">
            <h2>Attendance History</h2>
            <button @click="showHistory = false" class="refresh-button">
              <RefreshCw />
            </button>
          </div>

          <div class="history-list">
            <div
              v-for="(record, index) in attendanceHistory"
              :key="index"
              class="history-item"
            >
              <div class="history-details">
                <div class="history-icon">
                  <Calendar />
                </div>
                <div>
                  <p>{{ record.date }}</p>
                  <p>
                    In: {{ record.check_in }} • Out: {{ record.check_out }}
                  </p>
                </div>
              </div>
              <span :class="getStatusBadge(record.status)">
                {{ record.status }}
              </span>
            </div>
          </div>

          <div class="history-footer">
            <button @click="showHistory = false" class="back-button">
              Back to Check-in
            </button>
          </div>
        </div>
      </div>

      <div class="footer">
        <p>© 2025 Employee Management System. All rights reserved.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { Camera, User, Clock, Calendar, History, CheckCircle, AlertCircle, RefreshCw } from 'lucide-vue-next';
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useAuthStore } from '../stores/auth';
import { recognizeFace, getAttendanceHistory } from '../services/api';
import { v4 as uuidv4 } from 'uuid'; // Import UUID library

export default {
  name: 'AttendanceInterface',
  components: {
    Camera,
    User,
    Clock,
    Calendar,
    History,
    CheckCircle,
    AlertCircle,
    RefreshCw
  },
  data() {
    return {
      currentStep: 'camera', // 'camera', 'processing', 'success', 'history'
      isProcessing: false,
      employee: null,
      attendanceRecord: null,
      attendanceHistory: [],
      error: '',
      showHistory: false,
      stream: null,
      recognitionInterval: null,
      isCameraActive: false,
      sessionId: null, // THÊM sessionId VÀO DATA
      statusMessage: "Scanning for your face, please look directly at the camera.", // THÊM statusMessage
    };
  },
  watch: {
    currentStep(newVal) {
      if (newVal === 'camera') {
        this.startCamera();
      } else {
        // Stop continuous recognition when not in camera step
        this.stopContinuousRecognition();
      }
    }
  },
  mounted() {
    this.startCamera();
  },
  beforeUnmount() {
    this.stopContinuousRecognition(); // Ensure to stop on unmount
  },
  methods: {
    async startCamera() {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user' }
        });
        this.stream = mediaStream;
        if (this.$refs.videoRef) {
          this.$refs.videoRef.srcObject = mediaStream;
        }
        this.isCameraActive = true;
        this.statusMessage = "Scanning for your face, please look directly at the camera."; // Reset message
        this.startContinuousRecognition();
      } catch (err) {
        this.error = 'Cannot access camera. Please check permissions.';
        this.isCameraActive = false;
        this.statusMessage = "Camera access denied or unavailable.";
      }
    },
    startContinuousRecognition() {
      if (this.recognitionInterval) {
        clearInterval(this.recognitionInterval);
      }
      this.sessionId = uuidv4(); // TẠO MỘT session_id MỚI MỖI KHI BẮT ĐẦU NHẬN DIỆN LIÊN TỤC
      if (this.isCameraActive){
        // Gửi khung hình mỗi 1 giây (1000ms) để backend có đủ dữ liệu liveness
        this.recognitionInterval = setInterval(this.sendFrameForRecognition, 3000); 
      }
    },
    stopContinuousRecognition() {
      if (this.recognitionInterval) {
        clearInterval(this.recognitionInterval);
        this.recognitionInterval = null;
      }
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop());
        this.stream = null;
      }
      this.isCameraActive = false;
      if (this.$refs.videoRef){
        this.$refs.videoRef.srcObject = null;
      }
      this.sessionId = null; // Xóa session ID khi dừng
      this.statusMessage = "Webcam turned off. Ready to start new recognition."; // Reset message
    },

    stopWebcam() {
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop());
        this.stream = null;
      }
      if (this.$refs.videoRef) {
        this.$refs.videoRef.srcObject = null;
      }
      this.isCameraActive = false;
      if (this.recognitionInterval) {
        clearInterval(this.recognitionInterval);
        this.recognitionInterval = null;
      }
      this.sessionId = null; // Xóa session ID khi dừng
      console.log('Webcam is already turn off.');
      this.currentStep = 'camera';
      this.isProcessing = false;
      this.error = '';
      this.statusMessage = "Webcam turned off. Ready to start new recognition."; // Reset message
    },

    async sendFrameForRecognition() {
      // Chỉ xử lý nếu không đang xử lý và ở bước camera
      if (this.isProcessing || this.currentStep !== 'camera') {
        return;
      }

      if (!this.$refs.videoRef || !this.$refs.canvasRef) {
        this.error = 'Camera or canvas not ready.';
        return;
      }

      this.isProcessing = true;
      this.error = ''; // Xóa lỗi cũ
      this.statusMessage = "Processing... Recognizing your face, please wait"; // Hiển thị trạng thái processing

      const canvas = this.$refs.canvasRef;
      const video = this.$refs.videoRef;
      const context = canvas.getContext('2d');

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0);

      try {
        const base64Image = canvas.toDataURL('image/jpeg', 0.9).split(',')[1];
        
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) {
          this.error = 'Please log in to continue.';
          this.currentStep = 'camera';
          this.isProcessing = false;
          this.statusMessage = "Please log in to continue.";
          return;
        }

        // GỬI session_id CÙNG VỚI ẢNH
        const response = await recognizeFace({ base64_image: base64Image, session_id: this.sessionId });

        // THÊM LOGGING ĐỂ DEBUG
        console.log('🎯 Full API Response:', response);
        console.log('🎯 Response message:', response.message);
        console.log('🎯 Response employee:', response.employee);

        // Cập nhật trạng thái và thông báo dựa trên phản hồi từ backend
        if (response.message === 'Attendance recorded successfully') {
          console.log('🎯 Processing successful response...');
          
          // Kiểm tra dữ liệu employee
          if (response.employee && response.employee.full_name) {
            this.employee = {
              employee_id: response.employee.employee_id,
              full_name: response.employee.full_name,
              department: response.employee.department,
              timestamp: response.timestamp,
              status: response.status
            };
            
            this.attendanceRecord = {
              status: response.status,
              attendance_type: response.attendance_type,
              timestamp: response.timestamp
            };
            
            console.log('🎯 Employee data set:', this.employee);
            console.log('🎯 Attendance record set:', this.attendanceRecord);
            
            // Dừng continuous recognition trước khi chuyển step
            this.stopContinuousRecognition();
            
            // Chuyển sang success step
            this.currentStep = 'success';
            this.statusMessage = "Check-in Successful!";
            
            console.log('🎯 Current step changed to:', this.currentStep);
            
          } else {
            console.error('❌ No employee data in response:', response);
            this.error = 'Recognition successful but employee data is missing';
            this.statusMessage = 'Recognition successful but employee data is missing';
            this.currentStep = 'camera';
            this.isProcessing = false;
          }
          
        } else if (response.message && response.message.includes("Loading liveness check")) {
          // Nếu backend đang kiểm tra sự sống, cập nhật thông báo và tiếp tục loop
          this.statusMessage = response.message;
          this.currentStep = 'camera';
          this.isProcessing = false;
          
        } else if (response.message && response.message.includes("Liveness checking successfully")) {
          // Nếu liveness đã thành công nhưng chưa nhận diện được người
          this.statusMessage = response.message + " Detecting face...";
          this.currentStep = 'camera';
          this.isProcessing = false;
          
        } else {
          // Trường hợp lỗi khác
          console.log('🎯 Other response:', response.message);
          this.error = response.message || 'Face recognition failed. Please try again.';
          this.statusMessage = response.message || 'Face recognition failed. Please try again.';
          this.currentStep = 'camera';
          this.isProcessing = false;
        }
        
      } catch (err) {
        console.error('❌ Recognition error:', err);
        this.error = err.response?.data?.error || 'An unexpected error occurred during recognition. Please try again.';
        this.statusMessage = this.error;
        this.currentStep = 'camera';
        this.isProcessing = false;
      }
    },
    async viewHistory() {
      try {
        if (!this.employee || !this.employee.employee_id) {
          this.error = 'Không thể xem lịch sử: Không có thông tin nhân viên được nhận diện.';
          return;
        }

        this.stopWebcam(); // Dừng webcam khi chuyển sang xem lịch sử

        const employeeIdToFetch = this.employee.employee_id;

        const response = await getAttendanceHistory(employeeIdToFetch);
        
        const historyMap = {};
        response.records.forEach(record => {
          const date = new Date(record.timestamp).toLocaleDateString('en-CA'); // YYYY-MM-DD
          if (!historyMap[date]) {
            historyMap[date] = { date, check_in: null, check_out: null, status: 'Absent' };
          }
          if (record.status === 'check-in') {
            historyMap[date].check_in = new Date(record.timestamp).toLocaleTimeString('en-US', { hour12: false });
            historyMap[date].status = record.attendance_type === 'late' ? 'Late' : 'Present';
          } else if (record.status === 'check-out') {
            historyMap[date].check_out = new Date(record.timestamp).toLocaleTimeString('en-US', { hour12: false });
          }
        });

        this.attendanceHistory = Object.values(historyMap).sort((a,b) => new Date(b.date) - new Date(a.date)).slice(0, 50); // Sắp xếp theo ngày giảm dần
        this.showHistory = true;
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load attendance history.';
      }
    },
    resetCamera() {
      this.currentStep = 'camera';
      this.employee = null;
      this.attendanceRecord = null;
      this.error = '';
      this.showHistory = false;
      this.statusMessage = "Scanning for your face, please look directly at the camera."; // Reset message
      // startCamera will be called by the watch:currentStep, which will restart the continuous recognition
    },
    getStatusBadge(status) {
      switch (status) {
        case 'Present': return 'badge badge-present';
        case 'Late': return 'badge badge-late';
        case 'Absent': return 'badge badge-absent';
        default: return 'badge badge-default';
      }
    }
  }
};
</script>

<style scoped>
/* (Giữ nguyên phần CSS đã có) */
.container {
  min-height: 100%;
  overflow: hidden;
  background: linear-gradient(to bottom right, #3b82f6, #9333ea, #6b21a8);
  padding: 16px;
  color: var(--vt-c-text-light-1);
  width: 100vw;
  box-sizing: border-box;
}

.background-decoration-top {
  position: fixed;
  top: 0;
  right: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  transform: translateY(-128px) translateX(128px);
  animation: pulse 3s infinite;
}

.background-decoration-bottom {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
  transform: translateY(192px) translateX(-192px);
  animation: pulse 3s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 0.3; }
  100% { opacity: 0.6; }
}

.main-content-wrapper {
  width: 100%;
  margin: 0;
  padding: 0 16px;
  box-sizing: border-box;
}

.header {
  text-align: center;
  margin-bottom: 32px;
}

.header-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  margin-bottom: 16px;
}

.header-icon svg {
  width: 32px;
  height: 32px;
  color: var(--vt-c-white);
}

.header-title {
  font-size: 30px;
  font-weight: bold;
  color: var(--vt-c-white);
  margin-bottom: 8px;
}

.header-subtitle {
  color: rgba(147, 197, 255, 0.8);
  font-size: 16px;
}

.error-alert {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
  text-align: center;
}

.error-content {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.error-content svg {
  width: 20px;
  height: 20px;
  color: rgba(254, 226, 226, 0.8);
  margin-right: 8px;
}

.error-content span {
  color: rgba(254, 226, 226, 0.8);
  font-weight: 500;
}

.error-alert p {
  color: rgba(254, 226, 226, 0.8);
  font-size: 14px;
}

.card {
  width: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
  overflow-x: hidden;
  max-height: calc(100vh - 260px);
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.section {
  padding: 24px 0;
}

.camera-section {
  text-align: center;
  margin-bottom: 24px;
}

.camera-section svg {
  width: 48px;
  height: 48px;
  color: #2563eb;
  margin: 0 auto 12px;
}

.camera-section h2 {
  font-size: 24px;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 8px;
}

.camera-section p {
  color: #4b5563;
  font-size: 16px;
}

.video-container {
  position: relative;
  max-width: 448px;
  margin: 0 auto;
}

.video-frame {
  aspect-ratio: 1/1;
  background: #f3f4f6;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
}

.video-frame video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-frame canvas {
  display: none;
  width: 100%;
  height: 100%;
}

.face-overlay {
  position: absolute;
  top: 16px;
  right: 16px;
  bottom: 16px;
  left: 16px;
  border: 2px solid #3b82f6;
  border-radius: 12px;
  opacity: 0.6;
}

.face-overlay div {
  position: absolute;
  width: 16px;
  height: 16px;
}

.top-left {
  top: 0;
  left: 0;
  border-top: 4px solid #3b82f6;
  border-left: 4px solid #3b82f6;
  border-top-left-radius: 8px;
}

.top-right {
  top: 0;
  right: 0;
  border-top: 4px solid #3b82f6;
  border-right: 4px solid #3b82f6;
  border-top-right-radius: 8px;
}

.bottom-left {
  bottom: 0;
  left: 0;
  border-bottom: 4px solid #3b82f6;
  border-left: 4px solid #3b82f6;
  border-bottom-left-radius: 8px;
}

.bottom-right {
  bottom: 0;
  right: 0;
  border-bottom: 4px solid #3b82f6;
  border-right: 4px solid #3b82f6;
  border-bottom-right-radius: 8px;
}

/* Removed capture-button styles as the button is removed */

.processing-section {
  text-align: center;
}

.processing-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  background: #dbeafe;
  border-radius: 50%;
  margin-bottom: 16px;
}

.processing-icon svg {
  width: 48px;
  height: 48px;
  color: #2563eb;
}

.processing-section h2 {
  font-size: 24px;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 8px;
}

.processing-section p {
  color: #4b5563;
  font-size: 16px;
}

.progress-bar {
  max-width: 448px;
  margin: 0 auto;
  background: #f3f4f6;
  border-radius: 9999px;
  height: 8px;
  margin-bottom: 16px;
}

.progress-fill {
  width: 70%;
  height: 100%;
  background: #2563eb;
  border-radius: 9999px;
  animation: pulse 2s infinite;
}

.success-section {
  text-align: center;
  margin-bottom: 24px;
}

.success-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: #dcfce7;
  border-radius: 50%;
  margin-bottom: 16px;
}

.success-icon svg {
  width: 48px;
  height: 48px;
  color: #16a34a;
}

.success-section h2 {
  font-size: 24px;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 8px;
}

.success-section p {
  color: #4b5563;
  font-size: 16px;
}

.employee-card {
  background: linear-gradient(to right, #eff6ff, #f3e8ff);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease-in-out;
}

.employee-card:hover {
  transform: translateY(-5px); /* Hiệu ứng nhấc lên khi hover */
}

.employee-info {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.employee-avatar {
  width: 72px;
  height: 64px;
  background: linear-gradient(45deg, #3b82f6, #9333ea);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 24px;
  font-weight: bold;
  margin-right: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.employee-info h3 {
  font-size: 22px;
  font-weight: bold;
  color: #1f2937;
}

.employee-info p {
  color: #6b7280;
  font-size: 14px;
  margin-top: 4px;
}

.employee-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.detail-box {
  background: #ffffff;
  border-radius: 10px;
  padding: 18px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.detail-box svg {
  width: 24px;
  height: 24px;
  color: #2563eb;
  margin: 0 auto 8px;
}

.detail-box p:first-of-type {
  color: #4b5563;
  font-size: 12px;
}

.detail-box p:last-of-type {
  color: #1f2937;
  font-size: 14px;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.history-button,
.reset-button {
  flex: 1;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-button {
  background: #7e22ce;
  color: #ffffff;
}

.history-button:hover {
  background: #6b21a8;
  transform: scale(1.05);
}

.reset-button {
  background: #4b5563;
  color: #ffffff;
}

.reset-button:hover {
  background: #374151;
  transform: scale(1.05);
}

.action-buttons svg {
  width: 20px;
  height: 20px;
  margin-right: 8px;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.history-header h2 {
  font-size: 24px;
  font-weight: bold;
  color: #1f2937;
}

.refresh-button {
  color: #4b5563;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.refresh-button:hover {
  color: #1f2937;
  background: #f3f4f6;
}

.refresh-button svg {
  width: 20px;
  height: 20px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  background: #f9fafb;
  border-radius: 12px;
  padding: 18px;
  transition: all 0.2s ease-in-out;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #e5e7eb;
}

.history-item:hover {
  background: #f3f4f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.history-details {
  display: flex;
  align-items: center;
  flex-grow: 1;
}

.history-icon {
  width: 40px;
  height: 40px;
  background: #dbeafe;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.history-icon svg {
  width: 20px;
  height: 20px;
  color: #2563eb;
}

.history-details p:first-child {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.history-details p:last-child {
  font-size: 13px;
  color: #6b7280;
}

.badge {
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
}

.badge-present {
  background: #dcfce7;
  color: #16a34a;
}

.badge-late {
  background: #fef3c7;
  color: #d97706;
}

.badge-absent {
  background: #fee2e2;
  color: #dc2626;
}

.badge-default {
  background: #f3f4f6;
  color: #4b5563;
}

.history-footer {
  margin-top: 24px;
  text-align: center;
}

.back-button {
  background: #2563eb;
  color: #ffffff;
  padding: 12px 32px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}

.back-button:hover {
  background: #1d4ed8;
  transform: scale(1.05);
}

.footer {
  text-align: center;
  margin-top: 32px;
}

.footer p {
  color: rgba(147, 197, 255, 0.8);
  font-size: 12px;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@media (max-width: 768px) {
  .section {
    padding: 16px 8px;
  }
}
</style>