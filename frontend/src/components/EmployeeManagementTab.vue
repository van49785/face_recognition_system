<template>
  <div class="employee-management-content">
    <div class="d-flex align-center justify-space-between mb-4">
      <h2 class="employee-panel-title">Employee Management</h2>
      <v-btn
        color="primary"
        prepend-icon="mdi-plus-circle"
        @click="openAddEmployeeDialog"
      >
        Add New Employee
      </v-btn>
    </div>

    <v-card class="elevation-4 pa-4 rounded-lg">
      <v-text-field
        v-model="searchQuery"
        label="Search by ID, Name, Email, or Department"
        prepend-inner-icon="mdi-magnify"
        variant="outlined"
        clearable
        hide-details
        class="mb-4"
        @input="debouncedSearch"
      ></v-text-field>

      <v-data-table-server
        :headers="headers"
        :items="employees"
        :items-length="totalEmployees"
        :loading="loading"
        :options.sync="options"
        @update:options="updateOptions"
        class="elevation-0"
        item-value="employee_id"
      >
        <template v-slot:item.full_name="{ item }">
          <div class="d-flex align-center py-2">
            <v-avatar size="40" class="mr-3">
              <v-img :src="(item.raw || item).image_url || defaultAvatar" alt="Avatar"></v-img>
            </v-avatar>
            <div>
              <div class="font-weight-bold">{{ (item.raw || item).full_name }}</div>
              <div class="text-caption text-medium-emphasis">{{ (item.raw || item).email }}</div>
            </div>
          </div>
        </template>

        <template v-slot:item.status="{ item }">
          <v-chip
            :color="(item.raw || item).status ? 'green' : 'red'"
            density="compact"
            label
          >
            {{ (item.raw || item).status ? 'Active' : 'Deleted' }}
          </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <div class="d-flex ga-2">
            <v-btn
              icon="mdi-pencil"
              size="small"
              variant="text"
              color="blue-darken-2"
              @click="openEditEmployeeDialog(item.raw || item)"
              title="Edit Info"
            ></v-btn>
            <v-btn
              v-if="(item.raw || item).status"
              icon="mdi-delete"
              size="small"
              variant="text"
              color="red-darken-2"
              @click="confirmSoftDelete(item.raw || item)"
              title="Delete Employee"
            ></v-btn>
            <v-btn
              v-else
              icon="mdi-restore"
              size="small"
              variant="text"
              color="orange-darken-2"
              @click="confirmRestoreEmployee(item.raw || item)"
              title="Restore Employee"
            ></v-btn>
          </div>
        </template>

        <template v-slot:no-data>
          <v-alert
            type="info"
            class="text-center my-4"
            variant="tonal"
            density="compact"
            icon="mdi-information-outline"
          >
            No employee data found
          </v-alert>
        </template>
      </v-data-table-server>
    </v-card>

    <v-dialog v-model="employeeDialog" max-width="800px">
      <v-card rounded="lg">
        <v-card-title class="headline text-h5 primary-title-dialog py-4">
          {{ isEditing ? 'Edit Employee Information' : 'Add New Employee' }}
        </v-card-title>
        <v-card-text class="pt-4 pb-0">
          <p class="text-center text-medium-emphasis text-body-2" v-if="!isEditing">
            Please fill in the employee information. Afterward, you will collect the facial data.
          </p>
          <v-container>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Employee ID"
                  variant="outlined"
                  density="compact"
                  required
                  :readonly="isEditing"
                  v-model="editedEmployee.employee_id"
                  :rules="[v => !!v || 'Employee ID is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Full Name"
                  variant="outlined"
                  density="compact"
                  required
                  v-model="editedEmployee.full_name"
                  :rules="[v => !!v || 'Full Name is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Email"
                  variant="outlined"
                  density="compact"
                  v-model="editedEmployee.email"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Phone Number"
                  variant="outlined"
                  density="compact"
                  v-model="editedEmployee.phone"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  label="Department"
                  variant="outlined"
                  density="compact"
                  :items="['IT', 'HR', 'Marketing', 'Sales', 'Finance', 'Operations']"
                  v-model="editedEmployee.department"
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Position"
                  variant="outlined"
                  density="compact"
                  v-model="editedEmployee.position"
                ></v-text-field>
              </v-col>
              <v-col cols="12" v-if="isEditing">
                <v-switch
                  v-model="editedEmployee.status"
                  color="primary"
                  :label="editedEmployee.status ? 'Status: Active' : 'Status: Deleted'"
                  hide-details
                ></v-switch>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions class="pa-4 pt-0 justify-end">
          <v-btn color="grey-darken-2" variant="text" @click="closeEmployeeDialog">Cancel</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            @click="processEmployeeAction"
            :disabled="loading"
          >
            <span v-if="isEditing">Update</span>
            <span v-else>Collect Face Data</span>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <FaceCapture
      v-if="showFaceCaptureDialog && pendingEmployeeData && pendingEmployeeData.employee_id"
      :userId="pendingEmployeeData.employee_id"
      @completed="onFaceCaptureCompleted"
      @cancelled="onFaceCaptureCancelled"
    />

    <v-dialog v-model="confirmDialog" max-width="500px">
      <v-card rounded="lg">
        <v-card-title class="headline text-h5 red-title-dialog py-4">
          Confirm Action
        </v-card-title>
        <v-card-text class="py-4">
          <v-icon size="48" color="warning" class="float-start me-3">mdi-alert-circle-outline</v-icon>
          <span v-if="actionType === 'delete'">
            Are you sure want to delete employee {{ selectedEmployee?.full_name }} (ID: {{ selectedEmployee?.employee_id }})?
            This employee will no longer be able to check in. You can restore them later.
          </span>
          <span v-else-if="actionType === 'restore'">
            Are you sure want to restore employee {{ selectedEmployee?.full_name }} (ID: {{ selectedEmployee?.employee_id }})?
          </span>
          <span v-else>Are you sure you want to perform this action?</span>
        </v-card-text>
        <v-card-actions class="pa-4 pt-0 justify-end">
          <v-btn color="grey-darken-2" variant="text" @click="confirmDialog = false">Cancel</v-btn>
          <v-btn
            :color="actionType === 'delete' ? 'red-darken-2' : 'primary'"
            variant="flat"
            @click="executeConfirmedAction"
          >
            {{ actionType === 'delete' ? 'Delete' : 'Restore' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      timeout="3000"
      bottom
      right
    >
      {{ snackbar.message }}
    </v-snackbar>
  </div>
</template>

<script>
import '@/assets/css/EmployeeManagementTab.css';
import { defineComponent, ref, onMounted } from 'vue';
import {
  getEmployees, deleteEmployee, restoreEmployee, addEmployee, updateEmployee
} from '../services/api';
import defaultAvatar from '../assets/image/user_placeholder.png';
import FaceCapture from './FaceCapture.vue';

export default defineComponent({
  name: 'EmployeeManagementTab',
  components: { FaceCapture },
  setup() {
    const employees = ref([]);
    const totalEmployees = ref(0);
    const loading = ref(true);
    const searchQuery = ref('');
    const options = ref({ page: 1, itemsPerPage: 10, sortBy: [], groupBy: [] });

    const employeeDialog = ref(false);
    const isEditing = ref(false);
    const editedEmployee = ref({});
    const defaultEmployee = {
      employee_id: '', full_name: '', email: '', phone: '',
      department: '', position: '', status: true
    };

    const confirmDialog = ref(false);
    const selectedEmployee = ref(null);
    const actionType = ref('');
    const snackbar = ref({ show: false, message: '', color: '' });
    const headers = ref([
      { title: 'ID', key: 'employee_id', sortable: true },
      { title: 'Full Name', key: 'full_name' },
      { title: 'Department', key: 'department' },
      { title: 'Email', key: 'email' },
      { title: 'Status', key: 'status' },
      { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
    ]);

    const pendingEmployeeData = ref(null); // NEW: Lưu trữ dữ liệu nhân viên tạm thời
    const showFaceCaptureDialog = ref(false);

    // Debounce search input
    let searchTimeout = null;
    const debouncedSearch = () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        fetchEmployees();
      }, 500); // 500ms delay
    };

    const fetchEmployees = async () => {
      loading.value = true;
      try {
        const { page, itemsPerPage, sortBy } = options.value;
        const sortField = sortBy[0]?.key || 'created_at';
        const sortOrder = sortBy[0]?.order === 'desc' ? 'desc' : 'desc';
        const params = { page, limit: itemsPerPage, sort_by: sortField, sort_order: sortOrder };
        if (searchQuery.value) params.search = searchQuery.value;
        const response = await getEmployees(params);
        employees.value = response.employees || [];
        totalEmployees.value = response.total || 0;
      } catch (error) {
        showSnackbar('Error loading employee list', 'error');
        employees.value = [];
      } finally {
        loading.value = false;
      }
    };

    const updateOptions = (newOptions) => {
      if (JSON.stringify(options.value) !== JSON.stringify(newOptions)) {
        options.value = { ...newOptions };
        fetchEmployees();
      }
    };

    const openAddEmployeeDialog = () => {
      isEditing.value = false;
      pendingEmployeeData.value = null; // Reset
      editedEmployee.value = { ...defaultEmployee };
      employeeDialog.value = true;
    };

    const openEditEmployeeDialog = (emp) => {
      isEditing.value = true;
      pendingEmployeeData.value = null; // Ensure this is null for editing
      editedEmployee.value = { ...emp };
      employeeDialog.value = true;
    };

    const closeEmployeeDialog = () => {
      employeeDialog.value = false;
      editedEmployee.value = {};
      pendingEmployeeData.value = null; // Clear pending data if dialog is closed
    };

    // NEW: Hàm này sẽ xử lý cả việc update và bắt đầu thu thập khuôn mặt
    const processEmployeeAction = async () => {
      if (isEditing.value) {
        // Logic chỉnh sửa nhân viên hiện có
        if (!editedEmployee.value.employee_id || !editedEmployee.value.full_name || !editedEmployee.value.department) {
          return showSnackbar('Missing required fields', 'warning');
        }
        loading.value = true;
        try {
          const formData = new FormData();
          Object.keys(editedEmployee.value).forEach(key => {
            if (editedEmployee.value[key] !== null) {
              formData.append(key, editedEmployee.value[key]);
            }
          });
          await updateEmployee(editedEmployee.value.employee_id, formData);
          showSnackbar('Employee updated', 'success');
          closeEmployeeDialog();
          fetchEmployees();
        } catch (error) {
          showSnackbar('Error updating employee: ' + (error.message || 'Unknown'), 'error');
        } finally {
          loading.value = false;
        }
      } else {
        // Logic cho việc thêm nhân viên mới (bước 1: điền thông tin và chuẩn bị chụp khuôn mặt)
        if (!editedEmployee.value.employee_id || !editedEmployee.value.full_name || !editedEmployee.value.department) {
          return showSnackbar('Missing required fields', 'warning');
        }
        
        // Lưu thông tin nhân viên vào biến tạm thời, chưa gọi API addEmployee
        pendingEmployeeData.value = { ...editedEmployee.value };
        
        showSnackbar('The employee information is ready. Please proceed to collect the facial data.', 'info');
        employeeDialog.value = false; // Đóng dialog thông tin nhân viên
        showFaceCaptureDialog.value = true; // Mở dialog FaceCapture
      }
    };

    // NEW: Hàm này chỉ được gọi khi FaceCapture hoàn thành thành công
    const onFaceCaptureCompleted = async () => {
      showSnackbar('Facial data has been successfully collected! Saving the employee...', 'info');
      showFaceCaptureDialog.value = false; // Ẩn dialog FaceCapture

      if (!pendingEmployeeData.value) {
        showSnackbar('Error: No employee data is waiting to be saved.', 'error');
        return;
      }

      loading.value = true;
      try {
        const formData = new FormData();
        Object.keys(pendingEmployeeData.value).forEach(key => {
          if (pendingEmployeeData.value[key] !== null) {
            formData.append(key, pendingEmployeeData.value[key]);
          }
        });
        
        // Gửi yêu cầu thêm nhân viên với đầy đủ thông tin (bao gồm cả dữ liệu khuôn mặt đã xử lý ở backend)
        await addEmployee(formData); 
        showSnackbar('New employee has been successfully added!', 'success');
        
        pendingEmployeeData.value = null; // Xóa dữ liệu tạm thời
        closeEmployeeDialog(); // Đóng dialog (nếu đang mở, mặc dù nó đã đóng ở bước trước)
        fetchEmployees(); // Tải lại danh sách nhân viên
      } catch (error) {
        showSnackbar('Error while adding the employee:' + (error.message || 'Unknown'), 'error');
        // Nếu thêm thất bại, bạn có thể cân nhắc xóa dữ liệu khuôn mặt vừa thu thập ở backend nếu cần
      } finally {
        loading.value = false;
      }
    };

    const onFaceCaptureCancelled = () => {
      showSnackbar('Face data collection has been cancelled. The employee will not be saved.', 'warning');
      showFaceCaptureDialog.value = false; // Ẩn FaceCapture
      pendingEmployeeData.value = null; // Xóa dữ liệu tạm thời vì quá trình bị hủy
      closeEmployeeDialog(); // Đóng dialog nhân viên nếu nó đang mở
    };

    const confirmSoftDelete = (e) => { selectedEmployee.value = e; actionType.value = 'delete'; confirmDialog.value = true; };
    const confirmRestoreEmployee = (e) => { selectedEmployee.value = e; actionType.value = 'restore'; confirmDialog.value = true; };

    const executeConfirmedAction = async () => {
      if (!selectedEmployee.value) return;
      try {
        if (actionType.value === 'delete') await deleteEmployee(selectedEmployee.value.employee_id);
        if (actionType.value === 'restore') await restoreEmployee(selectedEmployee.value.employee_id);
        showSnackbar(`Employee ${actionType.value}d`, 'success');
        fetchEmployees();
      } catch (err) {
        showSnackbar(`Error: ${err.message}`, 'error');
      }
      confirmDialog.value = false;
    };

    const showSnackbar = (message, color) => {
      snackbar.value = { show: true, message, color };
    };

    onMounted(fetchEmployees);

    return {
      employees, totalEmployees, loading, searchQuery, options,
      employeeDialog, isEditing, editedEmployee, headers,
      openAddEmployeeDialog, openEditEmployeeDialog, closeEmployeeDialog, processEmployeeAction, // Updated method name
      confirmDialog, selectedEmployee, actionType,
      confirmSoftDelete, confirmRestoreEmployee, executeConfirmedAction,
      snackbar, showSnackbar, updateOptions, debouncedSearch,
      pendingEmployeeData, showFaceCaptureDialog, onFaceCaptureCompleted, onFaceCaptureCancelled, // Updated state and methods
      defaultAvatar
    };
  }
});
</script>