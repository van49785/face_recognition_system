<template>
  <div class="attendance-history-tab">
    <h2 class="panel-title">Attendance History & Reports</h2>
    <div class="panel-content">
      <v-container fluid>
        <v-row class="align-center">
          <v-col cols="12" md="3" sm="6">
            <v-select
              v-model="reportType"
              :items="reportTypes"
              label="Report Type"
              variant="outlined"
              density="compact"
              hide-details
            ></v-select>
          </v-col>
          <v-col cols="12" md="3" sm="6">
            <v-text-field
              v-if="reportType === 'employee'"
              v-model="employeeId"
              label="Employee ID (e.g., EMP001)"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            ></v-text-field>
            <v-select
              v-else-if="reportType === 'department'"
              v-model="department"
              :items="departments"
              label="Department"
              variant="outlined"
              density="compact"
              hide-details
            ></v-select>
          </v-col>
          <v-col cols="12" md="3" sm="6">
            <v-text-field
              label="Start Date"
              type="date"
              v-model="startDateInput"
              variant="outlined"
              density="compact"
              hide-details
              @change="onDateInputChange"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="3" sm="6">
            <v-text-field
              label="End Date"
              type="date"
              v-model="endDateInput"
              variant="outlined"
              density="compact"
              hide-details
              @change="onDateInputChange"
            ></v-text-field>
          </v-col>
        </v-row>

        <v-row class="mt-4">
          <v-col cols="12" class="d-flex justify-end gap-2">
            <v-btn
              color="primary"
              @click="fetchReport"
              :loading="loading"
              :disabled="!isReportCriteriaMet"
            >
              <v-icon left>mdi-eye</v-icon>
              View Report
            </v-btn>
            <v-btn
              color="success"
              @click="exportData"
              :loading="loadingExport"
              :disabled="!isExportCriteriaMet"
            >
              <v-icon left>mdi-file-excel</v-icon>
              Export Excel
            </v-btn>
          </v-col>
        </v-row>

        <v-row v-if="loading" class="mt-8">
          <v-col cols="12" class="text-center">
            <v-progress-circular
              indeterminate
              color="primary"
              size="64"
            ></v-progress-circular>
            <p class="mt-4 text-h6 text-primary">Loading report...</p>
          </v-col>
        </v-row>

        <v-row v-else-if="errorMessage" class="mt-8">
          <v-col cols="12">
            <v-alert type="error" closable>{{ errorMessage }}</v-alert>
          </v-col>
        </v-row>

        <v-row v-else-if="reportData" class="mt-8">
          <v-col cols="12">
            <h3 class="report-section-title">
              Attendance Report: {{ reportType === 'employee' ? reportData.employee.full_name : reportData.department }}
            </h3>
            <p class="report-period">
              From: {{ reportData.period.start_date }} to: {{ reportData.period.end_date }}
            </p>

            <v-divider class="my-4"></v-divider>

            <div v-if="reportType === 'employee'">
              <v-row>
                <v-col cols="12"> <v-card class="summary-card" flat>
                    <v-card-title class="card-title">Attendance Overview</v-card-title>
                    <v-card-text>
                      <div class="summary-item">
                        <span>Required Work Days:</span>
                        <strong>{{ reportData.report.working_days_in_period }} days</strong>
                      </div>
                      <div class="summary-item">
                        <span>Actual Attendance Days:</span>
                        <strong>{{ reportData.report.total_attendance_days }} days</strong>
                      </div>
                      <div class="summary-item">
                        <span>Absent Days:</span>
                        <strong>{{ reportData.report.absent_days }} days</strong>
                      </div>
                      <div class="summary-item">
                        <span>Attendance Rate:</span>
                        <strong :class="getAttendanceRateClass(reportData.report.attendance_rate)">{{ reportData.report.attendance_rate }}%</strong>
                      </div>
                      <div class="summary-item">
                        <span>Total Work Hours:</span>
                        <strong>{{ reportData.report.total_work_hours }} hours</strong>
                      </div>
                      <div class="summary-item">
                        <span>Total Overtime Hours:</span>
                        <strong>{{ reportData.report.total_overtime_hours }} hours</strong>
                      </div>
                      <div class="summary-item">
                        <span>Total Undertim Hours:</span>
                        <strong>{{ reportData.report.total_undertime_hours }} hours</strong>
                      </div>
                      <div class="summary-item">
                        <span>Late Days:</span>
                        <strong>{{ reportData.report.late_days }} days</strong>
                      </div>
                      <div class="summary-item">
                        <span>Early Departure Days:</span>
                        <strong>{{ reportData.report.early_departure_days }} days</strong>
                      </div>
                      <div class="summary-item">
                        <span>Forgot Checkout Days:</span>
                        <strong>{{ reportData.report.forgot_checkout_days }} days</strong>
                      </div>
                       <div class="summary-item">
                        <span>Avg Check-in Time:</span>
                        <strong>{{ reportData.report.avg_checkin_time || 'N/A' }}</strong>
                      </div>
                       <div class="summary-item">
                        <span>Avg Check-out Time:</span>
                        <strong>{{ reportData.report.avg_checkout_time || 'N/A' }}</strong>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>

                <v-col cols="12" class="mt-4"> <v-card class="detail-card" flat>
                    <v-card-title class="card-title">Daily Details</v-card-title>
                    <v-card-text>
                      <v-data-table
                        :headers="employeeDailyHeaders"
                        :items="reportData.report.daily_records"
                        item-value="date"
                        class="elevation-1"
                        density="compact"
                        :items-per-page="10"
                      >
                        <template v-slot:item.date="{ item }">
                          {{ formatDate(item.date) }}
                        </template>
                        <template v-slot:item.work_hours="{ item }">
                          {{ item.work_hours.toFixed(1) }}
                        </template>
                         <template v-slot:item.late_minutes="{ item }">
                          <v-chip
                            :color="item.late_minutes > 15 ? 'red-lighten-4' : 'green-lighten-4'"
                            :text-color="item.late_minutes > 15 ? 'red-darken-4' : 'green-darken-4'"
                            size="small"
                            label
                          >
                            {{ item.late_minutes }}
                          </v-chip>
                        </template>
                        <template v-slot:item.early_minutes="{ item }">
                          <v-chip
                            :color="item.early_minutes > 15 ? 'orange-lighten-4' : 'green-lighten-4'"
                            :text-color="item.early_minutes > 15 ? 'orange-darken-4' : 'green-darken-4'"
                            size="small"
                            label
                          >
                            {{ item.early_minutes }}
                          </v-chip>
                        </template>
                        <template v-slot:item.overtime_hours="{ item }">
                          {{ item.overtime_hours.toFixed(1) }}
                        </template>
                        <template v-slot:item.undertime_hours="{ item }">
                          {{ item.undertime_hours.toFixed(1) }}
                        </template>
                        <template v-slot:item.status="{ item }">
                          <v-chip :color="item.status === 'absent' ? 'red' : 'green'" label size="small" variant="tonal">
                            {{ item.status === 'absent' ? 'Absent' : 'Present' }}
                          </v-chip>
                        </template>
                        <template v-slot:item.notes="{ item }">
                          <div class="d-flex flex-column">
                            <v-chip v-if="item.late_minutes > 15" color="red-lighten-5" text-color="red-darken-4" size="x-small" label class="mb-1">Late check-in</v-chip>
                            <v-chip v-if="item.early_minutes > 15" color="orange-lighten-5" text-color="orange-darken-4" size="x-small" label class="mb-1">Early check-out</v-chip>
                            <v-chip v-if="!item.checkout_time && item.checkin_time" color="blue-lighten-5" text-color="blue-darken-4" size="x-small" label class="mb-1">Forgot check-out</v-chip>
                             <v-chip v-if="item.attendance_type === 'half_day'" color="purple-lighten-5" text-color="purple-darken-4" size="x-small" label class="mb-1">Half day off</v-chip>
                             <span v-if="item.status === 'present' && item.late_minutes <= 15 && item.early_minutes <= 15 && item.checkout_time && item.attendance_type !== 'half_day'">Normal</span>
                          </div>
                        </template>
                        <template v-slot:no-data>
                          <v-alert :value="true" color="info" icon="mdi-information">
                            No attendance data for this period.
                          </v-alert>
                        </template>
                      </v-data-table>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </div>

            <div v-else-if="reportType === 'department'">
              <v-row>
                <v-col cols="12">
                  <v-card class="summary-card" flat>
                    <v-card-title class="card-title">Department Overview</v-card-title>
                    <v-card-text>
                       <div class="summary-item">
                        <span>Total Employees:</span>
                        <strong>{{ reportData.total_employees }}</strong>
                      </div>
                      <div class="summary-item">
                        <span>Total Attendance Days (All Employees):</span>
                        <strong>{{ reportData.report.total_attendance_days }} days</strong>
                      </div>
                      <div class="summary-item">
                        <span>Total Work Hours (All Employees):</span>
                        <strong>{{ reportData.report.total_work_hours }} hours</strong>
                      </div>
                      <div class="summary-item">
                        <span>Total Overtime Hours (All Employees):</span>
                        <strong>{{ reportData.report.total_overtime_hours }} hours</strong>
                      </div>
                      <div class="summary-item">
                        <span>Total Undertime Hours (All Employees):</span>
                        <strong>{{ reportData.report.total_undertime_hours }} hours</strong>
                      </div>
                       <div class="summary-item">
                        <span>Average Attendance Rate:</span>
                        <strong :class="getAttendanceRateClass(reportData.report.avg_attendance_rate)">{{ reportData.report.avg_attendance_rate }}%</strong>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
                 <v-col cols="12" class="mt-4">
                  <v-card class="detail-card" flat>
                    <v-card-title class="card-title">Employee Attendance Details</v-card-title>
                    <v-card-text>
                      <v-data-table
                        :headers="departmentEmployeeHeaders"
                        :items="reportData.report.employee_reports"
                        item-value="employee_id"
                        class="elevation-1"
                        density="comfortable"
                        :items-per-page="10"
                      >
                         <template v-slot:item.total_work_hours="{ item }">
                          {{ item.total_work_hours.toFixed(1) }}
                        </template>
                        <template v-slot:item.total_overtime_hours="{ item }">
                          {{ item.total_overtime_hours.toFixed(1) }}
                        </template>
                        <template v-slot:item.total_undertime_hours="{ item }">
                          {{ item.total_undertime_hours.toFixed(1) }}
                        </template>
                        <template v-slot:item.attendance_rate="{ item }">
                          <strong :class="getAttendanceRateClass(item.attendance_rate)">{{ item.attendance_rate }}%</strong>
                        </template>
                        <template v-slot:item.evaluation="{ item }">
                          <div class="d-flex flex-column">
                            <v-chip v-if="item.attendance_rate < 80" color="red-lighten-5" text-color="red-darken-4" size="x-small" label class="mb-1">Poor Attendance</v-chip>
                            <v-chip v-if="item.late_days > 5" color="orange-lighten-5" text-color="orange-darken-4" size="x-small" label class="mb-1">Frequent Late</v-chip>
                            <v-chip v-if="item.early_departure_days > 3" color="blue-lighten-5" text-color="blue-darken-4" size="x-small" label class="mb-1">Frequent Early Leave</v-chip>
                            <span v-if="item.attendance_rate >= 80 && item.late_days <= 5 && item.early_departure_days <= 3">Good</span>
                          </div>
                        </template>
                        <template v-slot:no-data>
                          <v-alert :value="true" color="info" icon="mdi-information">
                            No employee data for this department in the selected period.
                          </v-alert>
                        </template>
                      </v-data-table>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </div>
          </v-col>
        </v-row>
        <v-row v-else>
          <v-col cols="12" class="text-center placeholder-content mt-8">
            <v-icon size="64" color="grey-lighten-1" class="placeholder-icon">mdi-chart-bar</v-icon>
            <h3>No Report Available</h3>
            <p>Please select report type, details, and date range to view the attendance report.</p>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </div>
</template>

<script setup>
import '@/assets/css/AttendanceHistoryTab.css';
import { ref, computed, watch, onMounted } from 'vue';
import {
  getEmployeeReport,
  getDepartmentReport,
  exportReport,
  downloadReportFile,
  formatReportType
} from '@/services/api';

const reportType = ref('employee'); // 'employee' or 'department'
const employeeId = ref('');
const department = ref('IT'); // Default department
const startDateInput = ref(''); // Used for input type="date"
const endDateInput = ref('');   // Used for input type="date"

const reportData = ref(null);
const loading = ref(false);
const loadingExport = ref(false);
const errorMessage = ref('');

// Static data for departments - in a real app, you might fetch this from an API
const departments = ['IT', 'HR', 'Finance', 'Marketing', 'Operations'];
const reportTypes = [
  { title: 'Employee Report', value: 'employee' },
  { title: 'Department Report', value: 'department' }
];

// Watcher to set default dates to current month when component mounts
onMounted(() => {
  const today = new Date();
  const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
  const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);

  // Format dates to YYYY-MM-DD for input type="date"
  startDateInput.value = firstDayOfMonth.toISOString().split('T')[0];
  endDateInput.value = lastDayOfMonth.toISOString().split('T')[0];
});

// Watcher for reportType to clear relevant fields
watch(reportType, (newType) => {
  if (newType === 'employee') {
    department.value = departments[0]; // Reset department to default
  } else {
    employeeId.value = ''; // Clear employee ID
  }
  reportData.value = null; // Clear previous report data
  errorMessage.value = '';
});

// Handle change for date inputs
const onDateInputChange = () => {
  reportData.value = null; // Clear previous report data
  errorMessage.value = '';
};

const isReportCriteriaMet = computed(() => {
  if (!startDateInput.value || !endDateInput.value) {
    return false;
  }
  if (reportType.value === 'employee' && !employeeId.value) {
    return false;
  }
  if (reportType.value === 'department' && !department.value) {
    return false;
  }
  return true;
});

const isExportCriteriaMet = computed(() => {
  return isReportCriteriaMet.value;
});

const fetchReport = async () => {
  errorMessage.value = '';
  reportData.value = null;
  loading.value = true;

  // Use values from startDateInput and endDateInput directly
  const startDate = startDateInput.value;
  const endDate = endDateInput.value;

  try {
    if (reportType.value === 'employee') {
      reportData.value = await getEmployeeReport(employeeId.value.trim(), startDate, endDate); //
    } else {
      reportData.value = await getDepartmentReport(department.value, startDate, endDate); //
    }
    console.log('Report fetched:', reportData.value);
  } catch (error) {
    console.error('Error fetching report:', error);
    errorMessage.value = error.response?.data?.error || 'Failed to load report. Please try again.';
  } finally {
    loading.value = false;
  }
};

const exportData = async () => {
  errorMessage.value = '';
  loadingExport.value = true;

  // Use values from startDateInput and endDateInput directly
  const startDate = startDateInput.value;
  const endDate = endDateInput.value;
  let identifier = '';

  if (reportType.value === 'employee') {
    identifier = employeeId.value.trim();
    if (!identifier) {
      errorMessage.value = 'Please enter an Employee ID to export the report.';
      loadingExport.value = false;
      return;
    }
  } else if (reportType.value === 'department') {
    identifier = department.value;
     if (!identifier) {
      errorMessage.value = 'Please select a Department to export the report.';
      loadingExport.value = false;
      return;
    }
  }

  const formattedReportType = formatReportType(reportType.value, identifier); //

  try {
    const blob = await exportReport(formattedReportType, startDate, endDate); //
    const filename = `${reportType.value}_report_${identifier}_${new Date().toISOString().split('T')[0]}.xlsx`;
    downloadReportFile(blob, filename); //
    console.log('Report exported and downloaded successfully!');
  } catch (error) {
    console.error('Error exporting report:', error);
    errorMessage.value = error.response?.data?.error || 'Failed to export report. Please try again.';
  } finally {
    loadingExport.value = false;
  }
};

// Helper to format date for display in tables
const formatDate = (dateString) => {
  const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
  return new Date(dateString).toLocaleDateString('en-GB', options);
};

// Dynamic class for attendance rate based on value
const getAttendanceRateClass = (rate) => {
  if (rate >= 90) return 'text-success';
  if (rate >= 70) return 'text-warning';
  return 'text-error';
};

// Headers for employee daily report table
const employeeDailyHeaders = [
  { title: 'Date', key: 'date', sortable: true },
  { title: 'Check-in', key: 'checkin_time', sortable: false },
  { title: 'Check-out', key: 'checkout_time', sortable: false },
  { title: 'Work (h)', key: 'work_hours', sortable: true },
  { title: 'Late (min)', key: 'late_minutes', sortable: true },
  { title: 'Early (min)', key: 'early_minutes', sortable: true },
  { title: 'Overtime (h)', key: 'overtime_hours', sortable: true },
  { title: 'Undertime (h)', key: 'undertime_hours', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Notes', key: 'notes', sortable: false },
];

// Headers for department employee report table
const departmentEmployeeHeaders = [
  { title: 'Emp ID', key: 'employee_id', sortable: true },
  { title: 'Full Name', key: 'full_name', sortable: true },
  { title: 'Position', key: 'position', sortable: false },
  { title: 'Work Days', key: 'total_attendance_days', sortable: true },
  { title: 'Work Hours', key: 'total_work_hours', sortable: true },
  { title: 'Overtime', key: 'total_overtime_hours', sortable: true },
  { title: 'Undertime', key: 'total_undertime_hours', sortable: true },
  { title: 'Att. Rate', key: 'attendance_rate', sortable: true },
  { title: 'Late Days', key: 'late_days', sortable: true },
  { title: 'Early Days', key: 'early_departure_days', sortable: true },
  { title: 'Forgot CO', key: 'forgot_checkout_days', sortable: true },
  { title: 'Absent Days', key: 'absent_days', sortable: true },
  { title: 'Evaluation', key: 'evaluation', sortable: false },
];
</script>