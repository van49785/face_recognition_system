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
          {{ isEditing ? 'Edit Employee Information' : (newlyAddedEmployeeId ? 'Finalize Employee Addition' : 'Add New Employee') }}
        </v-card-title>
        <v-card-text class="pt-4 pb-0">
          <p class="text-center text-medium-emphasis text-body-2" v-if="!newlyAddedEmployeeId">
            Please fill in the employee's basic information.
          </p>
          <p class="text-center text-medium-emphasis text-body-2" v-else>
            Employee basic information saved. Now, collect face data.
          </p>
          <v-container>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Employee ID"
                  variant="outlined"
                  density="compact"
                  required
                  :readonly="isEditing || newlyAddedEmployeeId"
                  v-model="editedEmployee.employee_id"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Full Name"
                  variant="outlined"
                  density="compact"
                  required
                  :readonly="newlyAddedEmployeeId"
                  v-model="editedEmployee.full_name"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Email"
                  variant="outlined"
                  density="compact"
                  :readonly="newlyAddedEmployeeId"
                  v-model="editedEmployee.email"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Phone Number"
                  variant="outlined"
                  density="compact"
                  :readonly="newlyAddedEmployeeId"
                  v-model="editedEmployee.phone"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  label="Department"
                  variant="outlined"
                  density="compact"
                  :items="['IT', 'HR', 'Marketing', 'Sales', 'Finance', 'Operations']"
                  :readonly="newlyAddedEmployeeId"
                  v-model="editedEmployee.department"
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Position"
                  variant="outlined"
                  density="compact"
                  :readonly="newlyAddedEmployeeId"
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
            @click="saveEmployee"
            :disabled="loading"
          >
            <span v-if="isEditing">Update</span>
            <span v-else-if="newlyAddedEmployeeId">Add New Employee</span>
            <span v-else>Save & Collect Face Data</span>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <FaceCapture
      v-if="showFaceCaptureDialog && newlyAddedEmployeeId"
      :userId="newlyAddedEmployeeId"
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

    const newlyAddedEmployeeId = ref(null);
    const showFaceCaptureDialog = ref(false); // New state for FaceCapture dialog

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
      newlyAddedEmployeeId.value = null; // Reset for new addition
      editedEmployee.value = { ...defaultEmployee };
      employeeDialog.value = true;
    };

    const openEditEmployeeDialog = (emp) => {
      isEditing.value = true;
      newlyAddedEmployeeId.value = null; // Ensure this is null for editing
      editedEmployee.value = { ...emp };
      employeeDialog.value = true;
    };

    const closeEmployeeDialog = () => {
      employeeDialog.value = false;
      editedEmployee.value = {};
      newlyAddedEmployeeId.value = null; // Also reset if dialog is closed
    };

    const saveEmployee = async () => {
      if (!editedEmployee.value.employee_id || !editedEmployee.value.full_name || !editedEmployee.value.department) {
        return showSnackbar('Missing required fields', 'warning');
      }

      loading.value = true; // Set loading state for the button

      try {
        const formData = new FormData();
        Object.keys(editedEmployee.value).forEach(key => {
          if (editedEmployee.value[key] !== null) {
            formData.append(key, editedEmployee.value[key]);
          }
        });

        if (isEditing.value) {
          // This path is for editing existing employee data
          await updateEmployee(editedEmployee.value.employee_id, formData);
          showSnackbar('Employee updated', 'success');
          closeEmployeeDialog();
          fetchEmployees();
        } else if (newlyAddedEmployeeId.value) {
          // This path is for finalizing the addition after face capture
          // The employee object already exists in the backend from the first step
          // We just need to close the dialog and refresh the list.
          // In a real scenario, you might have a separate API call here
          // to update the employee status to 'active' or similar after face data.
          // For now, we assume the employee is ready after face capture.
          showSnackbar('New employee added successfully!', 'success');
          closeEmployeeDialog();
          fetchEmployees();
        }
        else {
          // This path is for initially saving basic employee data before face capture
          const res = await addEmployee(formData);
          newlyAddedEmployeeId.value = res.employee_id || res.id || editedEmployee.value.employee_id;
          
          if (newlyAddedEmployeeId.value) {
            showSnackbar('Employee basic info saved. Now, collecting face data.', 'info');
            // Close the current dialog and open FaceCapture
            employeeDialog.value = false; 
            showFaceCaptureDialog.value = true; // Show face capture dialog
          } else {
            throw new Error('Failed to get employee ID after saving basic info.');
          }
        }
      } catch (error) {
        showSnackbar('Error saving employee: ' + (error.message || 'Unknown'), 'error');
      } finally {
        loading.value = false; // Reset loading state
      }
    };

    const onFaceCaptureCompleted = () => {
      showSnackbar('✅ Face data collected successfully!', 'success');
      showFaceCaptureDialog.value = false; // Hide face capture dialog
      // Re-open the employee dialog to finalize the addition
      // We pass the editedEmployee value so the ID is pre-filled
      employeeDialog.value = true; 
    };

    const onFaceCaptureCancelled = () => {
      showSnackbar('Face data collection cancelled. Employee not fully added.', 'warning');
      showFaceCaptureDialog.value = false; // Hide face capture dialog
      newlyAddedEmployeeId.value = null; // Clear the ID as the process was cancelled
      // You might want to delete the partially added employee from the backend here
      // or mark it as 'pending' with an incomplete status.
      closeEmployeeDialog(); // Close the initial employee dialog as well
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
      openAddEmployeeDialog, openEditEmployeeDialog, closeEmployeeDialog, saveEmployee,
      confirmDialog, selectedEmployee, actionType,
      confirmSoftDelete, confirmRestoreEmployee, executeConfirmedAction,
      snackbar, showSnackbar, updateOptions, debouncedSearch,
      newlyAddedEmployeeId, showFaceCaptureDialog, onFaceCaptureCompleted, onFaceCaptureCancelled,
      defaultAvatar
    };
  }
});
</script>

<style scoped>
.employee-management-content {
  padding: 30px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.employee-panel-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0;
}

/* Custom dialog titles */
.primary-title-dialog {
  background-color: #667eea;
  color: white;
  padding-left: 24px !important;
}

.red-title-dialog {
  background-color: #ef4444;
  color: white;
  padding-left: 24px !important;
}

/* Avatar styling */
.v-avatar {
  border: 1px solid #eee;
}

/* Adjust table styling */
.v-data-table-server {
  box-shadow: none !important;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

/* Table headers styling */
:deep(.v-data-table-server .v-data-table-header th) {
  background-color: #f8fafc !important;
  font-weight: 600 !important;
  color: #334155 !important;
  font-size: 0.875rem !important;
}

:deep(.v-data-table-server .v-data-table__td) {
  font-size: 0.9rem !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .employee-management-content {
    padding: 20px;
  }
  
  .employee-panel-title {
    font-size: 20px;
  }
  
  .d-flex.align-center.justify-space-between.mb-4 {
    flex-direction: column;
    align-items: flex-start !important;
    gap: 15px;
  }
  
  .v-btn {
    width: 100%;
  }
}
</style>