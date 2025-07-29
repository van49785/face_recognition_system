<template>
  <div class="employee-dashboard">
    <!-- Background Elements -->
    <div class="bg-gradient"></div>
    <div class="bg-pattern"></div>
    
    <!-- Header -->
    <header class="employee-header">
      <div class="header-content">
        <div class="brand-section">
          <div class="brand-icon">
            <v-icon size="40" color="white">mdi-account-circle</v-icon>
          </div>
          <div class="brand-text">
            <h1 class="brand-title">Welcome, {{ authStore.fullName || authStore.employeeId }}!</h1>
            <p class="brand-subtitle">Your Employee ID: {{ authStore.employeeId }}</p>
          </div>
        </div>
        
        <div class="header-actions">
          <v-btn
            class="header-btn"
            variant="outlined"
            color="white"
            prepend-icon="mdi-key"
            @click="showChangePasswordDialog = true"
          >
            Change Password
          </v-btn>
          <v-btn
            class="header-btn logout-btn"
            variant="outlined"
            color="white"
            prepend-icon="mdi-logout"
            @click="handleLogout"
          >
            Logout
          </v-btn>
        </div>
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
            <!-- Attendance Summary -->
            <div v-if="currentTab === 'summary'" class="content-panel">
              <div class="panel-content">
                <div v-if="attendanceReport" class="summary-section">
                  <div class="summary-header">
                    <h2 class="section-title">
                      <v-icon>mdi-chart-line</v-icon>
                      Attendance Summary
                    </h2>
                    <v-chip color="blue" variant="outlined" size="small">
                      {{ attendanceReport.period?.start_date }} - {{ attendanceReport.period?.end_date }}
                    </v-chip>
                  </div>

                  <div class="stats-grid">
                    <div class="stat-card normal">
                      <div class="stat-value">{{ attendanceReport.report?.normal_days || 0 }}</div>
                      <div class="stat-label">Normal Days</div>
                    </div>
                    <div class="stat-card late">
                      <div class="stat-value">{{ attendanceReport.report?.late_days || 0 }}</div>
                      <div class="stat-label">Late Days</div>
                    </div>
                    <div class="stat-card half">
                      <div class="stat-value">{{ attendanceReport.report?.half_days || 0 }}</div>
                      <div class="stat-label">Half Days</div>
                    </div>
                    <div class="stat-card recovered">
                      <div class="stat-value">{{ attendanceReport.report?.recovered_days || 0 }}</div>
                      <div class="stat-label">Recovered Days</div>
                    </div>
                    <div class="stat-card absent">
                      <div class="stat-value">{{ attendanceReport.report?.absent_days || 0 }}</div>
                      <div class="stat-label">Absent Days</div>
                    </div>
                  </div>

                  <div class="metrics-grid">
                    <div class="metric-card blue">
                      <div class="metric-content">
                        <div class="metric-info">
                          <div class="metric-value">{{ attendanceReport.report?.attendance_rate }}%</div>
                          <div class="metric-label">Attendance Rate</div>
                        </div>
                        <v-icon size="30" color="white">mdi-calendar-check</v-icon>
                      </div>
                    </div>
                    <div class="metric-card green">
                      <div class="metric-content">
                        <div class="metric-info">
                          <div class="metric-value">{{ attendanceReport.report?.total_work_hours }}h</div>
                          <div class="metric-label">Total Work Hours</div>
                        </div>
                        <v-icon size="30" color="white">mdi-clock</v-icon>
                      </div>
                    </div>
                    <div class="metric-card orange">
                      <div class="metric-content">
                        <div class="metric-info">
                          <div class="metric-value">{{ attendanceReport.report?.total_late_minutes }}min</div>
                          <div class="metric-label">Total Late Minutes</div>
                        </div>
                        <v-icon size="30" color="white">mdi-timer-alert</v-icon>
                      </div>
                    </div>
                  </div>

                  <div class="additional-stats">
                    <div class="stat-item">
                      <div class="stat-value">{{ attendanceReport.report?.avg_checkin_time || 'N/A' }}</div>
                      <div class="stat-label">Avg Check-in</div>
                    </div>
                    <div class="stat-item">
                      <div class="stat-value">{{ attendanceReport.report?.avg_checkout_time || 'N/A' }}</div>
                      <div class="stat-label">Avg Check-out</div>
                    </div>
                    <div class="stat-item">
                      <div class="stat-value">{{ attendanceReport.report?.total_overtime_hours }}h</div>
                      <div class="stat-label">Overtime Hours</div>
                    </div>
                    <div class="stat-item">
                      <div class="stat-value">{{ attendanceReport.report?.forgot_checkout_days }}</div>
                      <div class="stat-label">Forgot Checkout</div>
                    </div>
                  </div>
                </div>
                <div v-else class="loading-section">
                  <v-progress-circular indeterminate color="primary" size="50"></v-progress-circular>
                  <p class="loading-text">Loading attendance summary...</p>
                </div>
              </div>
            </div>

            <!-- Daily Attendance -->
            <div v-else-if="currentTab === 'daily'" class="content-panel">
              <div class="panel-content">
                <div class="section-header">
                  <h2 class="section-title">
                    <v-icon>mdi-calendar-clock</v-icon>
                    Daily Attendance Details
                  </h2>
                </div>

                <div class="filter-section">
                  <div class="filter-row">
                    <v-text-field
                      v-model="historyFilters.startDate"
                      label="Start Date"
                      type="date"
                      variant="outlined"
                      density="comfortable"
                      hide-details
                      class="filter-field"
                    ></v-text-field>
                    <v-text-field
                      v-model="historyFilters.endDate"
                      label="End Date"
                      type="date"
                      variant="outlined"
                      density="comfortable"
                      hide-details
                      class="filter-field"
                    ></v-text-field>
                    <v-btn
                      color="primary"
                      size="large"
                      @click="fetchAttendanceHistory"
                      :loading="historyLoading"
                      class="filter-btn"
                    >
                      <v-icon left>mdi-filter</v-icon> Filter
                    </v-btn>
                  </div>
                </div>

                <div class="table-container">
                  <v-data-table
                    :headers="dailyAttendanceHeaders"
                    :items="dailyAttendanceRecords"
                    :loading="historyLoading"
                    class="attendance-table"
                    :items-per-page="15"
                    item-value="date"
                  >
                    <template v-slot:no-data>
                      <div class="no-data">
                        <v-icon size="50" color="grey">mdi-calendar-remove</v-icon>
                        <p>No attendance records found for the selected period.</p>
                      </div>
                    </template>
                    
                    <template v-slot:item.date="{ item }">
                      <div class="date-cell">{{ formatDisplayDate(item.date) }}</div>
                    </template>
                    
                    <template v-slot:item.status="{ item }">
                      <v-chip :color="getStatusColor(item.status)" label small>
                        {{ item.status }}
                      </v-chip>
                    </template>
                    
                    <template v-slot:item.attendance_type="{ item }">
                      <v-chip 
                        v-if="item.attendance_type !== 'absent'" 
                        :color="getAttendanceTypeColor(item.attendance_type)" 
                        label 
                        small
                      >
                        {{ item.attendance_type }}
                      </v-chip>
                      <span v-else class="text-disabled">-</span>
                    </template>
                    
                    <template v-slot:item.checkin_time="{ item }">
                      <span v-if="item.checkin_time" class="time-cell">{{ item.checkin_time }}</span>
                      <span v-else class="text-disabled">-</span>
                    </template>
                    
                    <template v-slot:item.checkout_time="{ item }">
                      <span v-if="item.checkout_time" class="time-cell">{{ item.checkout_time }}</span>
                      <span v-else class="text-disabled">-</span>
                    </template>
                    
                    <template v-slot:item.work_hours="{ item }">
                      <span v-if="item.work_hours > 0" class="hours-cell">{{ item.work_hours }}h</span>
                      <span v-else class="text-disabled">-</span>
                    </template>
                    
                    <template v-slot:item.late_minutes="{ item }">
                      <v-chip 
                        v-if="item.late_minutes > 0" 
                        color="orange" 
                        size="x-small"
                        variant="text"
                      >
                        +{{ item.late_minutes }}min
                      </v-chip>
                      <span v-else class="text-disabled">-</span>
                    </template>
                    
                    <template v-slot:item.early_minutes="{ item }">
                      <v-chip 
                        v-if="item.early_minutes > 0" 
                        color="red" 
                        size="x-small"
                        variant="text"
                      >
                        -{{ item.early_minutes }}min
                      </v-chip>
                      <span v-else class="text-disabled">-</span>
                    </template>
                    
                    <template v-slot:item.overtime_hours="{ item }">
                      <v-chip 
                        v-if="item.overtime_hours > 0" 
                        color="green" 
                        size="x-small"
                        variant="text"
                      >
                        +{{ item.overtime_hours }}h
                      </v-chip>
                      <span v-else class="text-disabled">-</span>
                    </template>
                  </v-data-table>
                </div>
              </div>
            </div>

            <!-- Recovery Request -->
            <div v-else-if="currentTab === 'recovery'" class="content-panel">
              <div class="panel-content">
                <div class="section-header">
                  <h2 class="section-title">
                    <v-icon>mdi-restore</v-icon>
                    Request Attendance Recovery
                  </h2>
                </div>

                <div class="form-container">
                  <v-form @submit.prevent="submitRecoveryRequest" ref="recoveryFormRef" class="recovery-form">
                    <v-text-field
                      v-model="recoveryForm.request_date"
                      label="Date of Missed Attendance"
                      type="date"
                      variant="outlined"
                      density="comfortable"
                      class="form-field"
                      :rules="[rules.required]"
                    ></v-text-field>

                    <v-textarea
                      v-model="recoveryForm.reason"
                      label="Reason (e.g., Forgot to check-in, System error, etc.)"
                      variant="outlined"
                      density="comfortable"
                      rows="4"
                      class="form-field"
                      :rules="[rules.required, rules.minLength(10)]"
                    ></v-textarea>

                    <v-alert
                      v-if="recoveryErrorMessage"
                      type="error"
                      closable
                      class="form-alert"
                      variant="tonal"
                      density="compact"
                      @click:close="recoveryErrorMessage = ''"
                    >
                      {{ recoveryErrorMessage }}
                    </v-alert>

                    <v-alert
                      v-if="recoverySuccessMessage"
                      type="success"
                      closable
                      class="form-alert"
                      variant="tonal"
                      density="compact"
                      @click:close="recoverySuccessMessage = ''"
                    >
                      {{ recoverySuccessMessage }}
                    </v-alert>

                    <v-btn
                      type="submit"
                      color="primary"
                      block
                      size="large"
                      :loading="recoveryLoading"
                      class="submit-btn"
                    >
                      <v-icon left>mdi-send</v-icon> Submit Request
                    </v-btn>
                  </v-form>
                </div>
              </div>
            </div>

            <!-- My Requests -->
            <div v-else-if="currentTab === 'requests'" class="content-panel">
              <div class="panel-content">
                <div class="section-header">
                  <h2 class="section-title">
                    <v-icon>mdi-history</v-icon>
                    My Recovery Requests
                  </h2>
                  <v-btn
                    color="primary"
                    variant="text"
                    size="small"
                    @click="fetchMyRecoveryRequests"
                    :loading="myRecoveryRequestsLoading"
                    class="refresh-btn"
                  >
                    <v-icon left>mdi-refresh</v-icon>
                    Refresh
                  </v-btn>
                </div>

                <div class="table-container">
                  <v-data-table
                    :headers="recoveryRequestHeaders"
                    :items="myRecoveryRequests"
                    :loading="myRecoveryRequestsLoading"
                    class="requests-table"
                    :items-per-page="10"
                  >
                    <template v-slot:no-data>
                      <div class="no-data">
                        <v-icon size="50" color="grey">mdi-file-document-outline</v-icon>
                        <p>No recovery requests found.</p>
                      </div>
                    </template>
                    <template v-slot:item.request_date="{ item }">
                      {{ formatDate(item.request_date) }}
                    </template>
                    <template v-slot:item.status="{ item }">
                      <v-chip :color="getRecoveryStatusColor(item.status)" label small>
                        {{ item.status }}
                      </v-chip>
                    </template>
                    <template v-slot:item.created_at="{ item }">
                      {{ formatDateTime(item.created_at) }}
                    </template>
                    <template v-slot:item.notes="{ item }">
                      <span v-if="item.notes" class="notes-cell">{{ item.notes }}</span>
                      <span v-else class="text-disabled">No notes</span>
                    </template>
                  </v-data-table>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </main>

    <!-- Change Password Dialog -->
    <v-dialog v-model="showChangePasswordDialog" max-width="500px" persistent>
      <v-card class="dialog-card">
        <v-card-title class="dialog-header">
          <v-icon left>mdi-key</v-icon>
          Change Password
        </v-card-title>
        <v-card-text class="dialog-content">
          <v-form @submit.prevent="changePassword" ref="passwordFormRef">
            <v-text-field
              v-model="passwordForm.oldPassword"
              label="Current Password"
              type="password"
              variant="outlined"
              density="comfortable"
              class="dialog-field"
              :rules="[rules.required]"
              :error-messages="passwordErrorMessage"
            ></v-text-field>

            <v-text-field
              v-model="passwordForm.newPassword"
              label="New Password"
              type="password"
              variant="outlined"
              density="comfortable"
              class="dialog-field"
              :rules="[rules.required, rules.minLength(6)]"
            ></v-text-field>

            <v-text-field
              v-model="passwordForm.confirmNewPassword"
              label="Confirm New Password"
              type="password"
              variant="outlined"
              density="comfortable"
              class="dialog-field"
              :rules="[rules.required, rules.passwordMatch]"
            ></v-text-field>

            <v-alert
              v-if="passwordSuccessMessage"
              type="success"
              class="dialog-alert"
              variant="tonal"
              density="compact"
            >
              {{ passwordSuccessMessage }}
            </v-alert>
          </v-form>
        </v-card-text>
        <v-card-actions class="dialog-actions">
          <v-spacer></v-spacer>
          <v-btn
            color="grey"
            variant="text"
            @click="closePasswordDialog"
            :disabled="passwordLoading"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            @click="changePassword"
            :loading="passwordLoading"
          >
            Change Password
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Global Snackbar for notifications -->
    <v-snackbar
      v-model="showSnackbar"
      :color="snackbarColor"
      :timeout="3000"
      location="top"
    >
      {{ snackbarMessage }}
      <template v-slot:actions>
        <v-btn
          color="white"
          variant="text"
          @click="showSnackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import { useAuthStore } from '../stores/auth';
import * as api from '@/services/api'; 
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

// Current tab state
const currentTab = ref('summary');

// Tab definitions
const tabs = [
  {
    value: 'summary',
    label: 'Attendance Summary',
    icon: 'mdi-chart-line'
  },
  {
    value: 'daily',
    label: 'Daily Details',
    icon: 'mdi-calendar-clock'
  },
  {
    value: 'recovery',
    label: 'Request Recovery',
    icon: 'mdi-restore'
  },
  {
    value: 'requests',
    label: 'My Requests',
    icon: 'mdi-history'
  }
];

// --- Enhanced Attendance History State ---
const attendanceReport = ref(null);
const dailyAttendanceRecords = ref([]);
const historyLoading = ref(false);
const historyFilters = reactive({
  startDate: '',
  endDate: '',
});

// Updated headers for daily attendance details
const dailyAttendanceHeaders = [
  { title: 'Date', key: 'date', sortable: true, width: '120px' },
  { title: 'Status', key: 'status', sortable: true, width: '100px' },
  { title: 'Type', key: 'attendance_type', sortable: true, width: '100px' },
  { title: 'Check-in', key: 'checkin_time', sortable: false, width: '100px' },
  { title: 'Check-out', key: 'checkout_time', sortable: false, width: '100px' },
  { title: 'Work Hours', key: 'work_hours', sortable: true, width: '100px' },
  { title: 'Late', key: 'late_minutes', sortable: true, width: '80px' },
  { title: 'Early', key: 'early_minutes', sortable: true, width: '80px' },
  { title: 'Overtime', key: 'overtime_hours', sortable: true, width: '100px' },
];

// --- Attendance Recovery Request State ---
const recoveryForm = reactive({
  request_date: '',
  reason: '',
});
const recoveryLoading = ref(false);
const recoveryErrorMessage = ref('');
const recoverySuccessMessage = ref('');
const recoveryFormRef = ref(null);

// --- My Recovery Requests State ---
const myRecoveryRequests = ref([]);
const myRecoveryRequestsLoading = ref(false);

const recoveryRequestHeaders = [
  { title: 'Request ID', key: 'request_id', sortable: false },
  { title: 'Date', key: 'request_date', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Submitted', key: 'created_at', sortable: true },
  { title: 'Admin Notes', key: 'notes', sortable: false },
];

// --- Change Password State ---
const showChangePasswordDialog = ref(false);
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmNewPassword: '',
});
const passwordLoading = ref(false);
const passwordErrorMessage = ref('');
const passwordSuccessMessage = ref('');
const passwordFormRef = ref(null);

// --- Global Snackbar State ---
const showSnackbar = ref(false);
const snackbarMessage = ref('');
const snackbarColor = ref('success');

// --- Validation Rules ---
const rules = {
  required: value => !!value || 'This field is required.',
  minLength: (length) => value => (value && value.length >= length) || `Must be at least ${length} characters.`,
  passwordMatch: value => value === passwordForm.newPassword || 'Passwords do not match.',
};

// --- Computed Properties ---
const getAttendanceTypeColor = (type) => {
  switch (type) {
    case 'normal': return 'blue';
    case 'late': return 'orange';
    case 'half_day': return 'purple';
    case 'recovered': return 'teal';
    default: return 'grey';
  }
};

const getStatusColor = (status) => {
  switch (status) {
    case 'present': return 'green';
    case 'absent': return 'red';
    default: return 'grey';
  }
};

const getRecoveryStatusColor = (status) => {
  switch (status) {
    case 'pending': return 'orange';
    case 'approved': return 'green';
    case 'rejected': return 'red';
    default: return 'grey';
  }
};

// --- Utility Methods ---
const showNotification = (message, color = 'success') => {
  snackbarMessage.value = message;
  snackbarColor.value = color;
  showSnackbar.value = true;
};

const formatDateTime = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  return date.toLocaleString('en-GB', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  });
};

const formatDate = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  return date.toLocaleDateString('en-GB');
};

const formatDisplayDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-GB', { 
    weekday: 'short',
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit'
  });
};

// --- Main Methods ---
const fetchAttendanceHistory = async () => {
  historyLoading.value = true;
  try {
    const params = {};
    if (historyFilters.startDate) {
      params.start_date = historyFilters.startDate;
    }
    if (historyFilters.endDate) {
      params.end_date = historyFilters.endDate;
    }
    
    const response = await api.getMyAttendanceHistory(params);
    console.log('Attendance response:', response);
    
    // Store the full report
    attendanceReport.value = response;
    
    // Extract daily records for the table
    dailyAttendanceRecords.value = response.report?.daily_records || [];
    
    showNotification(`Loaded attendance report for ${dailyAttendanceRecords.value.length} days`);
  } catch (error) {
    console.error('Error fetching attendance history:', error);
    showNotification('Failed to fetch attendance history', 'error');
    attendanceReport.value = null;
    dailyAttendanceRecords.value = [];
  } finally {
    historyLoading.value = false;
  }
};

const fetchMyRecoveryRequests = async () => {
  myRecoveryRequestsLoading.value = true;
  try {
    const requests = await api.getEmployeeRecoveryRequests();
    myRecoveryRequests.value = requests || [];
  } catch (error) {
    console.error('Error fetching my recovery requests:', error);
    showNotification('Failed to fetch recovery requests', 'error');
  } finally {
    myRecoveryRequestsLoading.value = false;
  }
};

const submitRecoveryRequest = async () => {
  const { valid } = await recoveryFormRef.value.validate();
  if (!valid) return;

  recoveryLoading.value = true;
  recoveryErrorMessage.value = '';
  recoverySuccessMessage.value = '';

  try {
    const payload = {
      request_date: recoveryForm.request_date,
      reason: recoveryForm.reason.trim(),
    };

    const response = await api.submitEmployeeRecoveryRequest(payload);
    
    recoverySuccessMessage.value = response.message || 'Recovery request submitted successfully!';
    
    // Clear form
    recoveryForm.request_date = '';
    recoveryForm.reason = '';
    recoveryFormRef.value.resetValidation();
    
    // Refresh recovery requests list
    fetchMyRecoveryRequests();
    
    showNotification('Recovery request submitted successfully!');

  } catch (error) {
    recoveryErrorMessage.value = error.response?.data?.error || 'Failed to submit request. Please try again.';
    console.error('Error submitting recovery request:', error);
  } finally {
    recoveryLoading.value = false;
  }
};

const changePassword = async () => {
  const { valid } = await passwordFormRef.value.validate();
  if (!valid) return;

  passwordLoading.value = true;
  passwordErrorMessage.value = '';
  passwordSuccessMessage.value = '';

  try {
    const response = await api.employeeChangePassword(
      passwordForm.oldPassword,
      passwordForm.newPassword,
      passwordForm.confirmNewPassword
    );

    passwordSuccessMessage.value = response.message || 'Password changed successfully!';
    
    // Clear form after success
    setTimeout(() => {
      closePasswordDialog();
      showNotification('Password changed successfully!');
    }, 1500);

  } catch (error) {
    passwordErrorMessage.value = error.response?.data?.error || 'Failed to change password. Please check your current password.';
    console.error('Error changing password:', error);
  } finally {
    passwordLoading.value = false;
  }
};

const closePasswordDialog = () => {
  showChangePasswordDialog.value = false;
  passwordForm.oldPassword = '';
  passwordForm.newPassword = '';
  passwordForm.confirmNewPassword = '';
  passwordErrorMessage.value = '';
  passwordSuccessMessage.value = '';
  if (passwordFormRef.value) {
    passwordFormRef.value.resetValidation();
  }
};

const handleLogout = async () => {
  try {
    await authStore.logout();
    router.push('/login');
    showNotification('Logged out successfully');
  } catch (error) {
    console.error('Logout error:', error);
    // Force redirect even if logout API fails
    router.push('/login');
  }
};

// --- Lifecycle Hooks ---
onMounted(() => {
  // Set default date range to current month if not set
  if (!historyFilters.startDate || !historyFilters.endDate) {
    const now = new Date();
    const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
    const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    
    historyFilters.startDate = firstDay.toISOString().split('T')[0];
    historyFilters.endDate = lastDay.toISOString().split('T')[0];
  }
  
  fetchAttendanceHistory();
  fetchMyRecoveryRequests();
});
</script>

<style scoped>
/* Base Layout */
.employee-dashboard {
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
.employee-header {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.header-btn {
  border: 2px solid rgba(255,255,255,0.3) !important;
  color: white !important;
  backdrop-filter: blur(10px);
  background: rgba(255,255,255,0.1) !important;
  transition: all 0.3s ease;
}

.header-btn:hover {
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
  justify-content: center;
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
  min-width: 160px;
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

.panel-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}

/* Section Headers */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.refresh-btn {
  border-radius: 8px !important;
}

/* Summary Section */
.summary-section {
  width: 100%;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.stat-card.normal {
  border-color: #22c55e;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
}

.stat-card.late {
  border-color: #f97316;
  background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
}

.stat-card.half {
  border-color: #a855f7;
  background: linear-gradient(135deg, #faf5ff 0%, #e9d5ff 100%);
}

.stat-card.recovered {
  border-color: #06b6d4;
  background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%);
}

.stat-card.absent {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: #1e293b;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  border-radius: 16px;
  padding: 24px;
  color: white;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.metric-card.blue {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

.metric-card.green {
  background: linear-gradient(135deg, #10b981 0%, #047857 100%);
}

.metric-card.orange {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.metric-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-value {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 14px;
  opacity: 0.9;
}

/* Additional Stats */
.additional-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.stat-item {
  text-align: center;
}

.stat-item .stat-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.stat-item .stat-label {
  font-size: 12px;
  color: #64748b;
}

/* Loading Section */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
}

.loading-text {
  margin-top: 20px;
  color: #64748b;
  font-size: 16px;
}

/* Filter Section */
.filter-section {
  margin-bottom: 30px;
}

.filter-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 20px;
  align-items: end;
}

.filter-field {
  margin-bottom: 0 !important;
}

.filter-btn {
  height: 56px;
  border-radius: 8px !important;
  font-weight: 600;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.attendance-table,
.requests-table {
  background: transparent;
}

.attendance-table :deep(.v-data-table__thead),
.requests-table :deep(.v-data-table__thead) {
  background: #f8fafc;
}

.attendance-table :deep(.v-data-table__th),
.requests-table :deep(.v-data-table__th) {
  background: #f8fafc !important;
  font-weight: 600 !important;
  color: #374151 !important;
  border-bottom: 2px solid #e5e7eb !important;
}

.attendance-table :deep(.v-data-table__tr:hover),
.requests-table :deep(.v-data-table__tr:hover) {
  background: #f9fafb !important;
}

/* Table Cell Styling */
.date-cell {
  font-weight: 500;
  color: #374151;
}

.time-cell {
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
  font-size: 0.9em;
  color: #374151;
}

.hours-cell {
  font-weight: 500;
  color: #059669;
}

.notes-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-disabled {
  color: #9ca3af;
}

/* No Data State */
.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  text-align: center;
}

.no-data p {
  margin-top: 16px;
  color: #64748b;
  font-size: 16px;
}

/* Form Container */
.form-container {
  max-width: 600px;
  margin: 0 auto;
}

.recovery-form {
  background: #f8fafc;
  border-radius: 16px;
  padding: 30px;
}

.form-field {
  margin-bottom: 24px !important;
}

.form-alert {
  margin: 20px 0 !important;
}

.submit-btn {
  height: 56px !important;
  border-radius: 12px !important;
  font-weight: 600;
  font-size: 16px;
}

/* Dialog Styling */
.dialog-card {
  border-radius: 16px !important;
  overflow: hidden;
}

.dialog-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
  padding: 24px !important;
}

.dialog-content {
  padding: 30px !important;
}

.dialog-field {
  margin-bottom: 20px !important;
}

.dialog-alert {
  margin: 20px 0 !important;
}

.dialog-actions {
  padding: 20px 30px !important;
  background: #f8fafc;
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
@media (max-width: 1200px) {
  .content-container {
    padding: 0 30px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
  
  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }
}

@media (max-width: 768px) {
  .employee-header {
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
  
  .header-actions {
    flex-direction: column;
    width: 100%;
    gap: 8px;
  }
  
  .header-btn {
    width: 100%;
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
  
  .panel-content {
    padding: 20px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .additional-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  
  .filter-row {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .filter-btn {
    height: 48px;
  }
  
  .form-container {
    max-width: 100%;
  }
  
  .recovery-form {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .employee-header {
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
  
  .panel-content {
    padding: 15px;
  }
  
  .stats-grid {
    gap: 12px;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .stat-value {
    font-size: 2rem;
  }
  
  .metric-card {
    padding: 20px;
  }
  
  .metric-value {
    font-size: 1.5rem;
  }
  
  .additional-stats {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .recovery-form {
    padding: 16px;
  }
  
  .dialog-content {
    padding: 20px !important;
  }
  
  .dialog-actions {
    padding: 16px 20px !important;
  }
}

/* Custom Scrollbar */
.content-area::-webkit-scrollbar {
  width: 8px;
}

.content-area::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.content-area::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.content-area::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Table Scrollbar */
.table-container :deep(.v-table__wrapper)::-webkit-scrollbar {
  height: 8px;
}

.table-container :deep(.v-table__wrapper)::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.table-container :deep(.v-table__wrapper)::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.table-container :deep(.v-table__wrapper)::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Animation for stat cards */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-card {
  animation: slideInUp 0.6s ease-out forwards;
}

.stat-card:nth-child(1) { animation-delay: 0.1s; }
.stat-card:nth-child(2) { animation-delay: 0.2s; }
.stat-card:nth-child(3) { animation-delay: 0.3s; }
.stat-card:nth-child(4) { animation-delay: 0.4s; }
.stat-card:nth-child(5) { animation-delay: 0.5s; }

/* Metric cards animation */
.metric-card {
  animation: slideInUp 0.6s ease-out forwards;
}

.metric-card:nth-child(1) { animation-delay: 0.2s; }
.metric-card:nth-child(2) { animation-delay: 0.3s; }
.metric-card:nth-child(3) { animation-delay: 0.4s; }
</style>