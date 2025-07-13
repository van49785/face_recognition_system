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
        <!-- Camera Section -->
        <div v-if="currentStep === 'camera'" class="section">
          <div class="camera-section">
            <Camera />
            <h2>Face Recognition</h2>
            <p>{{ statusMessage }}</p>
          </div>

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
            
            <div class="camera-controls">
              <v-btn
                v-if="isCameraActive"
                @click="stopWebcam"
                color="red-darken-2"
                size="large"
                prepend-icon="mdi-webcam-off"
                class="control-button"
              >
                Turn off Webcam
              </v-btn>
              <v-btn
                v-else
                @click="startCamera"
                color="green-darken-2"
                size="large"
                prepend-icon="mdi-webcam"
                class="control-button"
              >
                Turn on Webcam
              </v-btn>
            </div>
          </div>
        </div>

        <!-- Processing Section -->
        <div v-if="currentStep === 'processing'" class="section processing-section">
          <div class="processing-content">
            <div class="processing-icon">
              <RefreshCw class="animate-spin" />
            </div>
            <h2>Processing...</h2>
            <p>{{ statusMessage }}</p>
          </div>
          
          <div class="progress-bar">
            <div class="progress-fill"></div>
          </div>
        </div>

        <!-- Success Section -->
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
              <div class="employee-details-text">
                <h3>{{ employee.full_name }}</h3>
                <p>ID: {{ employee.employee_id }}</p>
                <p>{{ employee.department }}</p>
              </div>
            </div>

            <div class="employee-details">
              <div class="detail-box">
                <Clock />
                <p>Time</p>
                <p>{{ formatTimestamp(employee.timestamp) }}</p>
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
              @click="resetCamera"
              color="blue-grey-darken-1"
              size="large"
              prepend-icon="mdi-refresh"
              class="action-button"
            >
              New Check-in
            </v-btn>
            <v-btn
              @click="viewHistory"
              color="purple-darken-3"
              size="large"
              prepend-icon="mdi-history"
              class="action-button"
            >
              View History
            </v-btn>
          </div>

          <!-- History Section - Moved here, below success section -->
          <div v-if="showHistory" class="history-section">
            <div class="history-header">
              <h3>Recent Attendance History</h3>
              <button @click="showHistory = false" class="close-history-button">
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
                  <div class="history-info">
                    <p class="history-date">{{ formatHistoryDate(record.date) }}</p>
                    <p class="history-time">
                      In: {{ record.check_in || 'N/A' }} • Out: {{ record.check_out || 'N/A' }}
                    </p>
                  </div>
                </div>
                <span :class="getStatusBadge(record.status)">
                  {{ record.status }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Standalone History Section (when accessed directly) -->
        <div v-if="showHistory && currentStep !== 'success'" class="section">
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
                <div class="history-info">
                  <p class="history-date">{{ formatHistoryDate(record.date) }}</p>
                  <p class="history-time">
                    In: {{ record.check_in || 'N/A' }} • Out: {{ record.check_out || 'N/A' }}
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
import { recognizeFace, getAttendanceHistory } from '../services/api';
import { v4 as uuidv4 } from 'uuid';

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
      currentStep: 'camera',
      isProcessing: false,
      employee: null,
      attendanceRecord: null,
      attendanceHistory: [],
      error: '',
      showHistory: false,
      stream: null,
      recognitionInterval: null,
      isCameraActive: false,
      sessionId: null,
      statusMessage: "Scanning for your face, please look directly at the camera.",
    };
  },
  watch: {
    currentStep(newVal) {
      if (newVal === 'camera') {
        this.startCamera();
      } else {
        this.stopContinuousRecognition();
      }
    }
  },
  mounted() {
    this.startCamera();
  },
  beforeUnmount() {
    this.stopContinuousRecognition();
  },
  methods: {
    formatTimestamp(timestamp) {
      if (!timestamp) return 'N/A';
      try {
        let date;
        
        // Check if timestamp is already in DD/MM/YYYY HH:mm:ss format
        if (typeof timestamp === 'string' && timestamp.includes('/')) {
          // Parse DD/MM/YYYY HH:mm:ss format
          const parts = timestamp.split(' ');
          if (parts.length === 2) {
            const datePart = parts[0]; // "13/07/2025"
            const timePart = parts[1]; // "23:55:47"
            
            const dateComponents = datePart.split('/');
            if (dateComponents.length === 3) {
              const day = dateComponents[0];
              const month = dateComponents[1];
              const year = dateComponents[2];
              
              // Create date in MM/DD/YYYY format for JavaScript Date constructor
              const jsDateString = `${month}/${day}/${year} ${timePart}`;
              date = new Date(jsDateString);
            }
          }
        } else {
          // Try parsing as ISO string or other formats
          date = new Date(timestamp);
        }
        
        if (!date || isNaN(date.getTime())) {
          console.error('Invalid date:', timestamp);
          return timestamp; // Return original if parsing fails
        }
        
        return date.toLocaleString('en-US', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        });
      } catch (error) {
        console.error('Error formatting timestamp:', error);
        return timestamp; // Return original if error occurs
      }
    },
    
formatHistoryDate(dateString) {
  if (!dateString) return 'N/A';
  try {
    let date;
    
    // Check if dateString is in YYYY-MM-DD format (from our historyMap)
    if (typeof dateString === 'string' && dateString.match(/^\d{4}-\d{2}-\d{2}$/)) {
      date = new Date(dateString + 'T00:00:00'); // Add time to avoid timezone issues
    } 
    // Check if dateString is in DD/MM/YYYY format
    else if (typeof dateString === 'string' && dateString.includes('/')) {
      const parts = dateString.split('/');
      if (parts.length === 3) {
        const day = parts[0];
        const month = parts[1];
        const year = parts[2];
        
        // Create date in MM/DD/YYYY format for JavaScript Date constructor
        const jsDateString = `${month}/${day}/${year}`;
        date = new Date(jsDateString);
      }
    } else {
      date = new Date(dateString);
    }
    
    if (!date || isNaN(date.getTime())) {
      console.error('Invalid date:', dateString);
      return dateString; // Return original if parsing fails
    }
    
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  } catch (error) {
    console.error('Error formatting history date:', error);
    return dateString; // Return original if error occurs
  }
},

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
        this.statusMessage = "Scanning for your face, please look directly at the camera.";
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
      this.sessionId = uuidv4();
      if (this.isCameraActive) {
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
      if (this.$refs.videoRef) {
        this.$refs.videoRef.srcObject = null;
      }
      this.sessionId = null;
      this.statusMessage = "Webcam turned off. Ready to start new recognition.";
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
      this.sessionId = null;
      console.log('Webcam is already turn off.');
      this.currentStep = 'camera';
      this.isProcessing = false;
      this.error = '';
      this.statusMessage = "Webcam turned off. Ready to start new recognition.";
    },

    async sendFrameForRecognition() {
      if (this.isProcessing || this.currentStep !== 'camera') {
        return;
      }

      if (!this.$refs.videoRef || !this.$refs.canvasRef) {
        this.error = 'Camera or canvas not ready.';
        return;
      }

      this.isProcessing = true;
      this.error = '';
      this.statusMessage = "Processing... Recognizing your face, please wait";

      const canvas = this.$refs.canvasRef;
      const video = this.$refs.videoRef;
      const context = canvas.getContext('2d');

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0);

      try {
        const base64Image = canvas.toDataURL('image/jpeg', 0.9).split(',')[1];
        const response = await recognizeFace({ base64_image: base64Image, session_id: this.sessionId });

        console.log('🎯 Full API Response:', response);

        if (response.message === 'Attendance recorded successfully') {
          console.log('🎯 Processing successful response...');
          
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
            
            this.stopContinuousRecognition();
            this.currentStep = 'success';
            this.statusMessage = "Check-in Successful!";
            
          } else {
            console.error('❌ No employee data in response:', response);
            this.error = 'Recognition successful but employee data is missing';
            this.statusMessage = 'Recognition successful but employee data is missing';
            this.currentStep = 'camera';
            this.isProcessing = false;
          }
          
        } else if (response.message && response.message.includes("Loading liveness check")) {
          this.statusMessage = response.message;
          this.currentStep = 'camera';
          this.isProcessing = false;
          
        } else if (response.message && response.message.includes("Liveness checking successfully")) {
          this.statusMessage = response.message + " Detecting face...";
          this.currentStep = 'camera';
          this.isProcessing = false;
          
        } else {
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

        const employeeIdToFetch = this.employee.employee_id;
        const response = await getAttendanceHistory(employeeIdToFetch);
        
        const historyMap = {};
        
        response.records.forEach(record => {
          let date;
          
          // Parse timestamp từ backend (có thể là DD/MM/YYYY HH:mm:ss)
          if (record.timestamp) {
            if (typeof record.timestamp === 'string' && record.timestamp.includes('/')) {
              // Parse DD/MM/YYYY HH:mm:ss format
              const parts = record.timestamp.split(' ');
              if (parts.length >= 1) {
                const datePart = parts[0]; // "13/07/2025"
                const dateComponents = datePart.split('/');
                if (dateComponents.length === 3) {
                  const day = dateComponents[0];
                  const month = dateComponents[1];
                  const year = dateComponents[2];
                  
                  // Create date in MM/DD/YYYY format for JavaScript Date constructor
                  const jsDateString = `${month}/${day}/${year}`;
                  date = new Date(jsDateString);
                }
              }
            } else {
              // Try parsing as ISO string or other formats
              date = new Date(record.timestamp);
            }
          }
          
          // Fallback to current date if parsing fails
          if (!date || isNaN(date.getTime())) {
            console.error('Invalid timestamp in record:', record.timestamp);
            date = new Date(); // Use current date as fallback
          }
          
          // Format date as YYYY-MM-DD for consistency
          const dateKey = date.toLocaleDateString('en-CA'); // This returns YYYY-MM-DD format
          
          if (!historyMap[dateKey]) {
            historyMap[dateKey] = { 
              date: dateKey, 
              check_in: null, 
              check_out: null, 
              status: 'Absent' 
            };
          }
          
          // Format time for display
          const timeString = date.toLocaleTimeString('en-US', { 
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
          });
          
          if (record.status === 'check-in') {
            historyMap[dateKey].check_in = timeString;
            historyMap[dateKey].status = record.attendance_type === 'late' ? 'Late' : 'Present';
          } else if (record.status === 'check-out') {
            historyMap[dateKey].check_out = timeString;
          }
        });

        this.attendanceHistory = Object.values(historyMap)
          .sort((a, b) => new Date(b.date) - new Date(a.date))
          .slice(0, 10);
        
        this.showHistory = true;
        
      } catch (err) {
        console.error('Error loading attendance history:', err);
        this.error = err.response?.data?.error || 'Failed to load attendance history.';
      }
    },

    resetCamera() {
      this.currentStep = 'camera';
      this.employee = null;
      this.attendanceRecord = null;
      this.error = '';
      this.showHistory = false;
      this.statusMessage = "Scanning for your face, please look directly at the camera.";
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
.container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  color: white;
  width: 100vw;
  box-sizing: border-box;
}

.background-decoration-top {
  position: fixed;
  top: -50px;
  right: -50px;
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: pulse 4s infinite;
}

.background-decoration-bottom {
  position: fixed;
  bottom: -50px;
  left: -50px;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
  animation: pulse 3s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 0.3; transform: scale(1.05); }
}

.main-content-wrapper {
  max-width: 500px;
  margin: 0 auto;
  padding: 0 16px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 70px;
  height: 70px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  margin-bottom: 20px;
  backdrop-filter: blur(10px);
}

.header-icon svg {
  width: 35px;
  height: 35px;
  color: white;
}

.header-title {
  font-size: 32px;
  font-weight: 700;
  color: white;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.header-subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  font-weight: 400;
}

.error-alert {
  background: rgba(239, 68, 68, 0.9);
  border: 1px solid rgba(239, 68, 68, 0.5);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  text-align: center;
  backdrop-filter: blur(10px);
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
  margin-right: 8px;
}

.card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.section {
  padding: 30px 24px;
}

.camera-section {
  text-align: center;
  margin-bottom: 30px;
}

.camera-section svg {
  width: 50px;
  height: 50px;
  color: #667eea;
  margin-bottom: 16px;
}

.camera-section h2 {
  font-size: 26px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 10px;
}

.camera-section p {
  color: #4a5568;
  font-size: 16px;
  line-height: 1.5;
}

.video-container {
  max-width: 400px;
  margin: 0 auto;
}

.video-frame {
  aspect-ratio: 1/1;
  background: #f7fafc;
  border-radius: 20px;
  overflow: hidden;
  position: relative;
  margin-bottom: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.video-frame video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-frame canvas {
  display: none;
}

.face-overlay {
  position: absolute;
  top: 20px;
  right: 20px;
  bottom: 20px;
  left: 20px;
  border: 3px solid #667eea;
  border-radius: 16px;
  opacity: 0.8;
}

.face-overlay div {
  position: absolute;
  width: 20px;
  height: 20px;
}

.top-left {
  top: -3px;
  left: -3px;
  border-top: 6px solid #667eea;
  border-left: 6px solid #667eea;
  border-top-left-radius: 12px;
}

.top-right {
  top: -3px;
  right: -3px;
  border-top: 6px solid #667eea;
  border-right: 6px solid #667eea;
  border-top-right-radius: 12px;
}

.bottom-left {
  bottom: -3px;
  left: -3px;
  border-bottom: 6px solid #667eea;
  border-left: 6px solid #667eea;
  border-bottom-left-radius: 12px;
}

.bottom-right {
  bottom: -3px;
  right: -3px;
  border-bottom: 6px solid #667eea;
  border-right: 6px solid #667eea;
  border-bottom-right-radius: 12px;
}

.camera-controls {
  display: flex;
  justify-content: center;
}

.control-button {
  border-radius: 16px !important;
  padding: 12px 24px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.processing-section {
  text-align: center;
}

.processing-content {
  margin-bottom: 30px;
}

.processing-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
  background: #e6f3ff;
  border-radius: 50%;
  margin-bottom: 20px;
}

.processing-icon svg {
  width: 50px;
  height: 50px;
  color: #667eea;
}

.processing-section h2 {
  font-size: 26px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 10px;
}

.processing-section p {
  color: #4a5568;
  font-size: 16px;
}

.progress-bar {
  width: 100%;
  max-width: 300px;
  margin: 0 auto;
  background: #e2e8f0;
  border-radius: 10px;
  height: 10px;
  overflow: hidden;
}

.progress-fill {
  width: 70%;
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 10px;
  animation: progress-pulse 2s infinite;
}

@keyframes progress-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.success-section {
  text-align: center;
  margin-bottom: 30px;
}

.success-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 90px;
  height: 90px;
  background: #f0fff4;
  border-radius: 50%;
  margin-bottom: 20px;
}

.success-icon svg {
  width: 50px;
  height: 50px;
  color: #48bb78;
}

.success-section h2 {
  font-size: 26px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 10px;
}

.success-section p {
  color: #4a5568;
  font-size: 16px;
}

.employee-card {
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border-radius: 20px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.employee-info {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.employee-avatar {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
  font-weight: 700;
  margin-right: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.employee-details-text h3 {
  font-size: 22px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 5px;
}

.employee-details-text p {
  color: #4a5568;
  font-size: 14px;
  margin-bottom: 3px;
}

.employee-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.detail-box {
  background: white;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.detail-box svg {
  width: 28px;
  height: 28px;
  color: #667eea;
  margin-bottom: 10px;
}

.detail-box p:first-of-type {
  color: #4a5568;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 5px;
}

.detail-box p:last-of-type {
  color: #1a202c;
  font-size: 14px;
  font-weight: 700;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 20px;
}

.action-button {
  border-radius: 16px !important;
  padding: 12px 24px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
  flex: 1;
  max-width: 180px;
}

.history-section {
  border-top: 1px solid #e2e8f0;
  padding-top: 30px;
  margin-top: 20px;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 25px;
}

.history-header h3 {
  font-size: 20px;
  font-weight: 700;
  color: #1a202c;
}

.close-history-button {
  background: none;
  border: none;
  color: #4a5568;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.close-history-button:hover {
  background: #f7fafc;
  color: #1a202c;
}

.close-history-button svg {
  width: 16px;
  height: 16px;
}

.refresh-button {
  background: none;
  border: none;
  color: #4a5568;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-button:hover {
  background: #f7fafc;
  color: #1a202c;
}

.refresh-button svg {
  width: 16px;
  height: 16px;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 5px;
}

.history-item {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}

.history-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.history-item:last-child {
  margin-bottom: 0;
}

.history-details {
  display: flex;
  align-items: center;
  flex: 1;
}

.history-icon {
  width: 45px;
  height: 45px;
  background: #e6f3ff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.history-icon svg {
  width: 20px;
  height: 20px;
  color: #667eea;
}

.history-info {
  flex: 1;
}

.history-date {
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 4px;
}

.history-time {
  font-size: 14px;
  color: #4a5568;
  margin: 0;
}

.badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-present {
  background: #f0fff4;
  color: #38a169;
  border: 1px solid #9ae6b4;
}

.badge-late {
  background: #fffbeb;
  color: #d69e2e;
  border: 1px solid #fbd38d;
}

.badge-absent {
  background: #fed7d7;
  color: #e53e3e;
  border: 1px solid #fbb6ce;
}

.badge-default {
  background: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.history-footer {
  margin-top: 30px;
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.back-button {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 16px;
  padding: 12px 30px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.back-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.footer {
  text-align: center;
  margin-top: 30px;
  padding: 20px;
}

.footer p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .container {
    padding: 15px;
  }
  
  .main-content-wrapper {
    padding: 0 12px;
  }
  
  .header-title {
    font-size: 28px;
  }
  
  .header-subtitle {
    font-size: 14px;
  }
  
  .section {
    padding: 25px 20px;
  }
  
  .camera-section h2 {
    font-size: 22px;
  }
  
  .video-frame {
    aspect-ratio: 4/3;
  }
  
  .employee-info {
    flex-direction: column;
    text-align: center;
  }
  
  .employee-avatar {
    margin-right: 0;
    margin-bottom: 15px;
  }
  
  .employee-details {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 12px;
  }
  
  .action-button {
    max-width: none;
  }
  
  .history-item {
    flex-direction: column;
    align-items: flex-start;
    padding: 15px;
  }
  
  .history-details {
    width: 100%;
    margin-bottom: 10px;
  }
  
  .badge {
    align-self: flex-end;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 10px;
  }
  
  .header-icon {
    width: 60px;
    height: 60px;
  }
  
  .header-icon svg {
    width: 30px;
    height: 30px;
  }
  
  .header-title {
    font-size: 24px;
  }
  
  .section {
    padding: 20px 16px;
  }
  
  .camera-section svg {
    width: 40px;
    height: 40px;
  }
  
  .camera-section h2 {
    font-size: 20px;
  }
  
  .employee-avatar {
    width: 70px;
    height: 70px;
    font-size: 24px;
  }
  
  .processing-icon {
    width: 80px;
    height: 80px;
  }
  
  .processing-icon svg {
    width: 40px;
    height: 40px;
  }
  
  .success-icon {
    width: 75px;
    height: 75px;
  }
  
  .success-icon svg {
    width: 40px;
    height: 40px;
  }
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section {
  animation: fadeIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.history-item {
  animation: slideIn 0.3s ease-out;
}

.history-item:nth-child(1) { animation-delay: 0.1s; }
.history-item:nth-child(2) { animation-delay: 0.2s; }
.history-item:nth-child(3) { animation-delay: 0.3s; }
.history-item:nth-child(4) { animation-delay: 0.4s; }
.history-item:nth-child(5) { animation-delay: 0.5s; }

/* Scrollbar Styling */
.history-list::-webkit-scrollbar {
  width: 6px;
}

.history-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.history-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

.history-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Focus States for Accessibility */
.control-button:focus,
.action-button:focus,
.back-button:focus,
.close-history-button:focus,
.refresh-button:focus {
  outline: 2px solid #667eea;
  outline-offset: 2px;
}

/* Loading States */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* High Contrast Mode Support */
@media (prefers-contrast: high) {
  .card {
    background: white;
    border: 2px solid #000;
  }
  
  .employee-card {
    background: #f0f0f0;
    border: 1px solid #333;
  }
  
  .history-item {
    background: white;
    border: 1px solid #333;
  }
}

/* Reduced Motion Support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  
  .animate-spin {
    animation: none;
  }
  
  .background-decoration-top,
  .background-decoration-bottom {
    animation: none;
  }
}
</style>