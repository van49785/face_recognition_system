<template>
  <div class="face-capture-overlay">
    <div class="face-capture-container">
      <div class="face-capture-header">
        <h2>🔐 Thu thập dữ liệu khuôn mặt</h2>
        <p>Nhân viên: <strong>{{ userId }}</strong></p>
      </div>

      <div class="face-capture-content">
        <div class="instructions-section">
          <h3>Hướng dẫn thu thập:</h3>
          <ul>
            <li>📸 Hệ thống sẽ thu thập 5 kiểu ảnh khuôn mặt khác nhau</li>
            <li>👀 Vui lòng nhìn theo hướng được yêu cầu</li>
            <li>💡 Đảm bảo ánh sáng đủ và khuôn mặt rõ ràng</li>
            <li>🔄 Hoàn tất sau khi thu thập đủ 5 pose</li>
          </ul>
        </div>

        <div class="video-container">
          <video ref="video" autoplay muted playsinline></video>
          <div class="video-overlay" v-if="!isTraining">
            <div class="overlay-content">
              <v-icon size="64" color="white">mdi-camera</v-icon>
              <p>Nhấn "Bắt đầu" để thu thập dữ liệu khuôn mặt</p>
            </div>
          </div>
          <div class="video-overlay current-pose" v-if="isTraining && currentPose">
            <div class="overlay-content">
              <v-icon size="48" color="white">{{ getPoseIcon(currentPose) }}</v-icon>
              <p>{{ getPoseLabel(currentPose) }}</p>
              <v-progress-circular
                indeterminate
                color="white"
                size="24"
                width="3"
                class="mt-2"
              ></v-progress-circular>
            </div>
          </div>
        </div>

        <div class="progress-section">
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: (samplesCollected / totalSamples * 100) + '%' }"
            ></div>
          </div>
          <p class="progress-text">{{ samplesCollected }}/{{ totalSamples }} mẫu dữ liệu</p>
        </div>

        <div class="poses-grid" v-if="poses.length > 0">
          <div 
            v-for="(pose, index) in poses" 
            :key="pose"
            class="pose-item"
            :class="{
              'completed': index < currentPoseIndex,
              'current': index === currentPoseIndex,
              'pending': index > currentPoseIndex
            }"
          >
            <v-icon size="24" :color="getPoseItemColor(index)">
              {{ getPoseIcon(pose) }}
            </v-icon>
            <span>{{ getPoseLabel(pose) }}</span>
            <v-icon v-if="index < currentPoseIndex" size="16" color="success">
              mdi-check-circle
            </v-icon>
          </div>
        </div>

        <div class="controls">
          <v-btn
            :disabled="isTraining"
            color="primary"
            size="large"
            prepend-icon="mdi-camera"
            @click="startTraining"
            class="control-btn"
          >
            {{ isTraining ? 'Đang thu thập...' : 'Bắt đầu thu thập' }}
          </v-btn>
          <v-btn
            :disabled="!isTraining"
            color="grey-darken-2"
            size="large"
            prepend-icon="mdi-stop"
            @click="stopTraining"
            class="control-btn"
          >
            Dừng
          </v-btn>
          <v-btn
            color="grey-darken-2"
            size="large"
            prepend-icon="mdi-close"
            @click="closeCapture"
            class="control-btn"
          >
            Đóng
          </v-btn>
        </div>

        <div class="status-section" v-if="statusMessage">
          <v-alert
            :type="statusType"
            :text="statusMessage"
            class="status-alert"
          ></v-alert>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { captureFacePose, getRequiredPoses } from '@/services/api.js'
import { defineComponent, ref, onMounted, onUnmounted } from 'vue'

export default defineComponent({
  name: 'FaceCapture',
  props: {
    userId: {
      type: String,
      required: true
    }
  },
  emits: ['completed', 'cancelled'],
  setup(props, { emit }) {
    const video = ref(null)
    const stream = ref(null)
    const isTraining = ref(false)
    const poses = ref(['front', 'left', 'right', 'up', 'down'])
    const currentPoseIndex = ref(0)
    const samplesCollected = ref(0)
    const totalSamples = ref(5)
    const statusMessage = ref('')
    const statusType = ref('info')
    const captureTimeout = ref(null)

    const poseLabels = {
      front: 'Nhìn thẳng vào camera',
      left: 'Quay mặt sang trái',
      right: 'Quay mặt sang phải',
      up: 'Ngước mặt lên',
      down: 'Cúi mặt xuống'
    }

    const poseIcons = {
      front: 'mdi-face-man',
      left: 'mdi-arrow-left',
      right: 'mdi-arrow-right',
      up: 'mdi-arrow-up',
      down: 'mdi-arrow-down'
    }

    const currentPose = ref(null)

    const showStatus = (message, type = 'info') => {
      statusMessage.value = message
      statusType.value = type
      setTimeout(() => {
        statusMessage.value = ''
      }, 5000)
    }

    const getPoseLabel = (pose) => {
      return poseLabels[pose] || pose
    }

    const getPoseIcon = (pose) => {
      return poseIcons[pose] || 'mdi-face-man'
    }

    const getPoseItemColor = (index) => {
      if (index < currentPoseIndex.value) return 'success'
      if (index === currentPoseIndex.value) return 'primary'
      return 'grey'
    }

    const startCamera = async () => {
      try {
        stream.value = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: { ideal: 640 },
            height: { ideal: 480 }
          } 
        })
        video.value.srcObject = stream.value
        await new Promise(resolve => {
          video.value.onloadedmetadata = resolve
        })
        return true
      } catch (error) {
        showStatus('Không thể truy cập camera: ' + error.message, 'error')
        return false
      }
    }

    const stopCamera = () => {
      if (stream.value) {
        stream.value.getTracks().forEach(track => track.stop())
        stream.value = null
      }
    }

    const captureFrame = async () => {
      if (!video.value) return null
      
      const canvas = document.createElement('canvas')
      canvas.width = video.value.videoWidth
      canvas.height = video.value.videoHeight
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video.value, 0, 0)
      
      return new Promise(resolve => {
        canvas.toBlob(resolve, 'image/jpeg', 0.9)
      })
    }

    const sendFaceData = async (pose, imageBlob) => {
        try {
            const formData = new FormData()
            formData.append('image', imageBlob, `${props.userId}_${pose}.jpg`)
            formData.append('employee_id', props.userId)
            formData.append('pose_type', pose)

            const response = await captureFacePose(formData)
            
            // Kiểm tra response structure
            if (!response.data) {
            throw new Error('Invalid response format')
            }

            // Kiểm tra success flag (nếu backend trả về)
            if (response.data.success === false) {
            throw new Error(response.data.error || 'Capture failed')
            }

            return response.data
            
        } catch (error) {
            console.error('Error sending face data:', error)
            
            // Xử lý different error types
            if (error.response?.status === 400) {
            throw new Error(error.response.data.error || 'Invalid request')
            } else if (error.response?.status === 404) {
            throw new Error('Employee not found')
            } else if (error.response?.status === 500) {
            throw new Error('Server error. Please try again later.')
            } else if (error.code === 'ECONNABORTED') {
            throw new Error('Connection timeout. Please try again.')
            } else {
            throw new Error(error.response?.data?.error || 'Network error')
            }
        }
    }

    const captureCurrentPose = async () => {
        if (!isTraining.value || currentPoseIndex.value >= poses.value.length) return

        const pose = poses.value[currentPoseIndex.value]
        currentPose.value = pose
        
        try {
            showStatus(`Đang chuẩn bị chụp ảnh ${getPoseLabel(pose)}...`, 'info')
            
            // Đợi một chút để người dùng chuẩn bị
            await new Promise(resolve => setTimeout(resolve, 2000))
            
            showStatus(`Đang chụp ảnh ${getPoseLabel(pose)}...`, 'info')
            
            const imageBlob = await captureFrame()
            if (!imageBlob) {
            throw new Error('Không thể chụp ảnh')
            }

            const result = await sendFaceData(pose, imageBlob)
            
            // Validate result structure
            if (!result.pose_type || !result.progress) {
            throw new Error('Invalid response data')
            }
            
            samplesCollected.value++
            currentPoseIndex.value++
            
            showStatus(`✅ Đã thu thập ${getPoseLabel(pose)} thành công!`, 'success')
            
            // Log progress for debugging
            console.log('Training progress:', result.progress)
            
            // Nếu chưa hoàn thành, tiếp tục với pose tiếp theo
            if (currentPoseIndex.value < poses.value.length) {
            captureTimeout.value = setTimeout(() => {
                captureCurrentPose()
            }, 2000)
            } else {
            // Hoàn thành tất cả poses
            finishTraining()
            }
            
        } catch (error) {
            console.error('Capture error:', error)
            showStatus(`❌ Lỗi khi thu thập ${getPoseLabel(pose)}: ${error.message}`, 'error')
            
            // Stop training on error
            isTraining.value = false
            currentPose.value = null
            
            // Clear timeout nếu có
            if (captureTimeout.value) {
            clearTimeout(captureTimeout.value)
            captureTimeout.value = null
            }
        }
    }

    const finishTraining = () => {
      isTraining.value = false
      currentPose.value = null
      showStatus('🎉 Hoàn tất thu thập dữ liệu khuôn mặt!', 'success')
      
      setTimeout(() => {
        emit('completed')
      }, 2000)
    }

    const startTraining = async () => {
      if (isTraining.value) return

      const cameraStarted = await startCamera()
      if (!cameraStarted) return

      isTraining.value = true
      currentPoseIndex.value = 0
      samplesCollected.value = 0
      
      showStatus('Bắt đầu thu thập dữ liệu khuôn mặt...', 'info')
      
      // Đợi một chút rồi bắt đầu chụp
      setTimeout(() => {
        captureCurrentPose()
      }, 1000)
    }

    const stopTraining = () => {
      isTraining.value = false
      currentPose.value = null
      if (captureTimeout.value) {
        clearTimeout(captureTimeout.value)
        captureTimeout.value = null
      }
      showStatus('Đã dừng thu thập dữ liệu', 'info')
    }

    const closeCapture = () => {
      stopTraining()
      stopCamera()
      emit('cancelled')
    }

    onMounted(() => {
      startCamera()
    })

    onUnmounted(() => {
      stopCamera()
      if (captureTimeout.value) {
        clearTimeout(captureTimeout.value)
      }
    })

    return {
      video,
      isTraining,
      poses,
      currentPoseIndex,
      samplesCollected,
      totalSamples,
      statusMessage,
      statusType,
      currentPose,
      getPoseLabel,
      getPoseIcon,
      getPoseItemColor,
      startTraining,
      stopTraining,
      closeCapture
    }
  }
})
</script>

<style scoped>
.face-capture-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.face-capture-container {
  background: white;
  border-radius: 20px;
  padding: 30px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.face-capture-header {
  text-align: center;
  margin-bottom: 30px;
}

.face-capture-header h2 {
  color: #333;
  font-size: 2rem;
  margin-bottom: 10px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.instructions-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  border-left: 4px solid #667eea;
}

.instructions-section h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.instructions-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.instructions-section li {
  padding: 8px 0;
  border-bottom: 1px solid #e0e0e0;
  color: #555;
}

.instructions-section li:last-child {
  border-bottom: none;
}

.video-container {
  position: relative;
  width: 100%;
  max-width: 640px;
  margin: 0 auto 20px;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.video-container video {
  width: 100%;
  height: auto;
  display: block;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  font-weight: bold;
  text-align: center;
}

.video-overlay.current-pose {
  background: rgba(102, 126, 234, 0.8);
}

.overlay-content {
  text-align: center;
}

.overlay-content p {
  margin: 10px 0;
  font-size: 1.2rem;
}

.progress-section {
  text-align: center;
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background: #e0e0e0;
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(45deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.progress-text {
  font-weight: bold;
  color: #333;
  font-size: 1.1rem;
}

.poses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.pose-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  border: 2px solid #e0e0e0;
  background: white;
  transition: all 0.3s;
}

.pose-item.completed {
  background: #d4edda;
  border-color: #28a745;
  color: #155724;
}

.pose-item.current {
  background: #e3f2fd;
  border-color: #1976d2;
  color: #0d47a1;
  font-weight: bold;
  animation: pulse 2s infinite;
}

.pose-item.pending {
  background: #f8f9fa;
  border-color: #e0e0e0;
  color: #666;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}

.pose-item span {
  flex: 1;
  margin: 0 10px;
  font-size: 0.9rem;
}

.controls {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.control-btn {
  min-width: 160px;
}

.status-section {
  margin-top: 20px;
}

.status-alert {
  border-radius: 10px;
}

/* Responsive design */
@media (max-width: 768px) {
  .face-capture-container {
    padding: 20px;
    width: 95%;
  }
  
  .face-capture-header h2 {
    font-size: 1.5rem;
  }
  
  .controls {
    flex-direction: column;
    align-items: center;
  }
  
  .control-btn {
    width: 100%;
    max-width: 300px;
  }
  
  .poses-grid {
    grid-template-columns: 1fr;
  }
}
</style>