<!-- src/views/HomeView.vue -->
<template>
  <div class="admin-dashboard">
    <!-- Background Elements -->
    <div class="bg-gradient"></div>
    <div class="bg-pattern"></div>
    
    <!-- Header -->
    <header class="admin-header">
      <div class="header-content">
        <div class="brand-section">
          <div class="brand-icon">
            <v-icon size="40" color="white">mdi-cog-outline</v-icon>
          </div>
          <div class="brand-text">
            <h1 class="brand-title">Admin Portal</h1>
            <p class="brand-subtitle">Employee Management & System Overview</p>
          </div>
        </div>
        
        <v-btn
          class="logout-btn"
          variant="outlined"
          color="white"
          prepend-icon="mdi-logout"
          @click="handleLogout"
        >
          Logout
        </v-btn>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <div class="content-container">
        <!-- Navigation Tabs -->
        <div class="nav-tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.value"
            :class="['nav-tab', { active: currentTab === tab.value }]"
            @click="currentTab = tab.value"
          >
            <v-icon :icon="tab.icon" size="20" class="tab-icon"></v-icon>
            <span class="tab-label">{{ tab.label }}</span>
          </button>
        </div>

        <!-- Content Area -->
        <div class="content-area">
          <transition name="fade" mode="out-in">
            <div v-if="currentTab === 'employee-management'" class="content-panel">
              <EmployeeManagementTab />
            </div>

            <div v-else-if="currentTab === 'attendance-history'" class="content-panel">
              <h2 class="panel-title">Attendance History</h2>
              <div class="panel-content">
                <div class="placeholder-content">
                  <v-icon size="64" color="primary" class="placeholder-icon">mdi-calendar-clock</v-icon>
                  <h3>Attendance History</h3>
                  <p>Tính năng lịch sử chấm công và xuất Excel sẽ được triển khai tại đây</p>
                </div>
              </div>
            </div>

            <div v-else-if="currentTab === 'audit-logs'" class="content-panel">
              <h2 class="panel-title">Activity Log</h2>
              <div class="panel-content">
                <div class="placeholder-content">
                  <v-icon size="64" color="primary" class="placeholder-icon">mdi-format-list-bulleted-square</v-icon>
                  <h3>Activity Log</h3>
                  <p>Tính năng nhật ký hoạt động hệ thống sẽ được triển khai tại đây</p>
                </div>
              </div>
            </div>

            <div v-else-if="currentTab === 'settings'" class="content-panel">
              <h2 class="panel-title">Cài đặt</h2>
              <div class="panel-content">
                <div class="placeholder-content">
                  <v-icon size="64" color="primary" class="placeholder-icon">mdi-tools</v-icon>
                  <h3>System Settings</h3>
                  <p>Tính năng cài đặt hệ thống sẽ được triển khai tại đây</p>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import '@/assets/css/Login.css';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import EmployeeManagementTab from '@/components/EmployeeManagementTab.vue';

export default {
  name: 'AdminDashboard',
  components: {
    EmployeeManagementTab
  },
  setup() {
    const currentTab = ref('employee-management');
    const router = useRouter();
    const authStore = useAuthStore();
    

    const tabs = [
      {
        value: 'employee-management',
        label: 'Employee Management',
        icon: 'mdi-account-group'
      },
      {
        value: 'attendance-history',
        label: 'Attendance History',
        icon: 'mdi-calendar-clock'
      },
      {
        value: 'audit-logs',
        label: 'Activity Log',
        icon: 'mdi-format-list-bulleted-square'
      },
      {
        value: 'settings',
        label: 'Settings',
        icon: 'mdi-tools'
      }
    ];

  const handleLogout = async () => {
    try {
      await authStore.logout();
      router.push('/login');
      console.log('Admin logged out successfully.');
    } catch (error) {
      console.error('Logout error:', error);
      // Vẫn redirect về login dù có lỗi
      router.push('/login');
    }
  };

    return {
      currentTab,
      tabs,
      handleLogout,
    };
  },
};
</script>

<style scoped>
/* Base Layout */
.admin-dashboard {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  overflow: hidden;
}

/* Background Elements */
.bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 300px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 1;
}

.bg-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 300px;
  background-image: 
    radial-gradient(circle at 20% 80%, rgba(255,255,255,0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%);
  z-index: 2;
}

/* Header */
.admin-header {
  position: relative;
  z-index: 10;
  padding: 30px 40px;
  background: transparent;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.brand-icon {
  width: 60px;
  height: 60px;
  background: rgba(255,255,255,0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.brand-text {
  color: white;
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  line-height: 1.2;
}

.brand-subtitle {
  font-size: 16px;
  margin: 4px 0 0 0;
  opacity: 0.9;
  font-weight: 400;
}

.logout-btn {
  border: 2px solid rgba(255,255,255,0.3) !important;
  color: white !important;
  backdrop-filter: blur(10px);
  background: rgba(255,255,255,0.1) !important;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(255,255,255,0.2) !important;
  border-color: rgba(255,255,255,0.5) !important;
}

/* Main Content */
.main-content {
  flex: 1;
  position: relative;
  z-index: 10;
  overflow: hidden;
}

.content-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Navigation Tabs */
.nav-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 30px;
  background: white;
  padding: 8px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 24px;
  border: none;
  background: transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  color: #64748b;
  min-width: 180px;
  justify-content: center;
}

.nav-tab:hover {
  background: #f1f5f9;
  color: #334155;
}

.nav-tab.active {
  background: #667eea;
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.tab-icon {
  opacity: 0.8;
}

.tab-label {
  font-size: 14px;
  white-space: nowrap;
}

/* Content Area */
.content-area {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 40px;
}

.content-panel {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-title {
  padding: 30px 30px 0 30px;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
}

.panel-content {
  flex: 1;
  padding: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-content {
  text-align: center;
  max-width: 400px;
}

.placeholder-icon {
  opacity: 0.3;
  margin-bottom: 20px;
}

.placeholder-content h3 {
  font-size: 20px;
  font-weight: 600;
  color: #334155;
  margin: 0 0 12px 0;
}

.placeholder-content p {
  color: #64748b;
  margin: 0;
  line-height: 1.6;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .admin-header {
    padding: 20px 20px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .brand-section {
    flex-direction: column;
    gap: 15px;
  }
  
  .brand-title {
    font-size: 24px;
  }
  
  .brand-subtitle {
    font-size: 14px;
  }
  
  .content-container {
    padding: 0 20px;
  }
  
  .nav-tabs {
    flex-direction: column;
    gap: 4px;
  }
  
  .nav-tab {
    min-width: auto;
    width: 100%;
  }
  
  .panel-title {
    padding: 20px 20px 0 20px;
    font-size: 20px;
  }
  
  .panel-content {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .admin-header {
    padding: 15px 15px;
  }
  
  .content-container {
    padding: 0 15px;
  }
  
  .brand-title {
    font-size: 20px;
  }
  
  .brand-subtitle {
    font-size: 13px;
  }
  
  .nav-tab {
    padding: 12px 16px;
  }
  
  .tab-label {
    font-size: 13px;
  }
}

/* Large screens */
@media (min-width: 1400px) {
  .nav-tabs {
    justify-content: center;
  }
  
  .nav-tab {
    min-width: 220px;
  }
}
</style>