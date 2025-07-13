<!-- src/components/EmployeeManagementTab.vue -->
<template>
  <div class="employee-management-content">
    <div class="d-flex align-center justify-space-between mb-4">
      <h2 class="employee-panel-title">Quản lý Nhân viên</h2>
      <v-btn
        color="primary"
        prepend-icon="mdi-plus-circle"
        @click="openAddEmployeeDialog"
      >
        Thêm Nhân viên mới
      </v-btn>
    </div>

    <v-card class="elevation-4 pa-4 rounded-lg">
      <v-text-field
        v-model="searchQuery"
        label="Tìm kiếm theo ID, Tên, Email hoặc Phòng ban"
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
            {{ (item.raw || item).status ? 'Đang hoạt động' : 'Đã xóa mềm' }}
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
              title="Sửa thông tin"
            ></v-btn>
            <v-btn
              v-if="(item.raw || item).status"
              icon="mdi-delete"
              size="small"
              variant="text"
              color="red-darken-2"
              @click="confirmSoftDelete(item.raw || item)"
              title="Xóa mềm nhân viên"
            ></v-btn>
            <v-btn
              v-else
              icon="mdi-restore"
              size="small"
              variant="text"
              color="orange-darken-2"
              @click="confirmRestoreEmployee(item.raw || item)"
              title="Khôi phục nhân viên"
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
            Không có dữ liệu nhân viên nào được tìm thấy.
          </v-alert>
        </template>
      </v-data-table-server>
    </v-card>

    <v-dialog v-model="employeeDialog" max-width="800px">
      <v-card rounded="lg">
        <v-card-title class="headline text-h5 primary-title-dialog py-4">
          {{ isEditing ? 'Chỉnh sửa Thông tin Nhân viên' : 'Thêm Nhân viên Mới' }}
        </v-card-title>
        <v-card-text class="pt-4 pb-0">
          <p class="text-center text-medium-emphasis text-body-2">
            Form thêm/sửa nhân viên sẽ được tạo ở đây. Sau khi tạo/sửa, sẽ có bước huấn luyện khuôn mặt.
          </p>
          <v-container>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Mã nhân viên (Employee ID)"
                  variant="outlined"
                  density="compact"
                  required
                  :readonly="isEditing"
                  v-model="editedEmployee.employee_id"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Họ và tên"
                  variant="outlined"
                  density="compact"
                  required
                  v-model="editedEmployee.full_name"
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
                  label="Số điện thoại"
                  variant="outlined"
                  density="compact"
                  v-model="editedEmployee.phone"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  label="Phòng ban"
                  variant="outlined"
                  density="compact"
                  :items="['IT', 'HR', 'Marketing', 'Sales', 'Finance', 'Operations']"
                  v-model="editedEmployee.department"
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Vị trí"
                  variant="outlined"
                  density="compact"
                  v-model="editedEmployee.position"
                ></v-text-field>
              </v-col>
              <v-col cols="12" v-if="isEditing">
                <v-switch
                  v-model="editedEmployee.status"
                  color="primary"
                  :label="editedEmployee.status ? 'Trạng thái: Đang hoạt động' : 'Trạng thái: Đã xóa mềm'"
                  hide-details
                ></v-switch>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions class="pa-4 pt-0 justify-end">
          <v-btn color="grey-darken-2" variant="text" @click="closeEmployeeDialog">Hủy</v-btn>
          <v-btn color="primary" variant="flat" @click="saveEmployee">
            {{ isEditing ? 'Cập nhật' : 'Thêm mới' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirmDialog" max-width="500px">
      <v-card rounded="lg">
        <v-card-title class="headline text-h5 red-title-dialog py-4">
          Xác nhận Hành động
        </v-card-title>
        <v-card-text class="py-4">
          <v-icon size="48" color="warning" class="float-start me-3">mdi-alert-circle-outline</v-icon>
          <span v-if="actionType === 'delete'">
            Bạn có chắc chắn muốn **xóa mềm** nhân viên **{{ selectedEmployee?.full_name }}** (ID: {{ selectedEmployee?.employee_id }}) không?
            Nhân viên này sẽ không thể chấm công. Bạn có thể khôi phục sau.
          </span>
          <span v-else-if="actionType === 'restore'">
            Bạn có chắc chắn muốn **khôi phục** nhân viên **{{ selectedEmployee?.full_name }}** (ID: {{ selectedEmployee?.employee_id }}) không?
          </span>
          <span v-else>Bạn có chắc chắn muốn thực hiện hành động này không?</span>
        </v-card-text>
        <v-card-actions class="pa-4 pt-0 justify-end">
          <v-btn color="grey-darken-2" variant="text" @click="confirmDialog = false">Hủy</v-btn>
          <v-btn
            :color="actionType === 'delete' ? 'red-darken-2' : 'primary'"
            variant="flat"
            @click="executeConfirmedAction"
          >
            {{ actionType === 'delete' ? 'Xóa mềm' : 'Khôi phục' }}
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
import { defineComponent, ref, onMounted, watch } from 'vue';
import { getEmployees, deleteEmployee, restoreEmployee, addEmployee, updateEmployee } from '../services/api';
import defaultAvatar from '../assets/user_placeholder.png';

export default defineComponent({
  name: 'EmployeeManagementTab',
  setup() {
    const employees = ref([]);
    const totalEmployees = ref(0);
    const loading = ref(true);
    const searchQuery = ref('');
    const options = ref({
      page: 1,
      itemsPerPage: 10,
      sortBy: [],
      groupBy: [],
      search: undefined,
    });

    const employeeDialog = ref(false);
    const isEditing = ref(false);
    const editedEmployee = ref({});
    const defaultEmployee = {
      employee_id: '',
      full_name: '',
      email: '',
      phone: '',
      department: '',
      position: '',
      status: true,
    };

    const confirmDialog = ref(false);
    const selectedEmployee = ref(null);
    const actionType = ref('');

    const snackbar = ref({
      show: false,
      message: '',
      color: '',
    });

    const headers = ref([
      { title: 'ID', key: 'employee_id', sortable: true },
      { title: 'Họ và tên', key: 'full_name', sortable: true },
      { title: 'Phòng ban', key: 'department', sortable: true },
      { title: 'Email', key: 'email', sortable: true },
      { title: 'Trạng thái', key: 'status', sortable: true },
      { title: 'Hành động', key: 'actions', sortable: false, align: 'center' },
    ]);

    const fetchEmployees = async () => {
      loading.value = true;
      try {
        const { page, itemsPerPage, sortBy } = options.value;
        const sortField = sortBy.length > 0 ? sortBy[0].key : 'created_at';
        const sortOrder = sortBy.length > 0 && sortBy[0].order === 'desc' ? 'desc' : 'desc';

        const params = {
          page,
          limit: itemsPerPage,
          sort_by: sortField,
          sort_order: sortOrder
        };

        if (searchQuery.value) {
          params.search = searchQuery.value;
        }

        const response = await getEmployees(params);
        
        employees.value = response.employees || [];
        totalEmployees.value = response.total || 0;

      } catch (error) {
        console.error('Error fetching employees:', error);
        showSnackbar('Lỗi khi tải danh sách nhân viên.', 'error');
        employees.value = [];
        totalEmployees.value = 0;
      } finally {
        loading.value = false;
      }
    };

    const updateOptions = (newOptions) => {
      // Chỉ gọi API nếu thực sự có thay đổi
      if (JSON.stringify(options.value) !== JSON.stringify(newOptions)) {
        options.value = { ...newOptions };
        fetchEmployees();
      }
    };

    let searchTimeout = null;
    const debouncedSearch = () => {
      if (searchTimeout) clearTimeout(searchTimeout);
      searchTimeout = setTimeout(fetchEmployees, 300);
    };

    const openAddEmployeeDialog = () => {
      isEditing.value = false;
      editedEmployee.value = { ...defaultEmployee };
      employeeDialog.value = true;
    };

    const openEditEmployeeDialog = (employee) => {
      isEditing.value = true;
      editedEmployee.value = { ...employee };
      employeeDialog.value = true;
    };

    const closeEmployeeDialog = () => {
      employeeDialog.value = false;
      editedEmployee.value = {};
    };

    const saveEmployee = async () => {
      if (!editedEmployee.value.employee_id || !editedEmployee.value.full_name || !editedEmployee.value.department) {
        showSnackbar('Vui lòng điền đầy đủ các trường bắt buộc (Mã NV, Họ tên, Phòng ban).', 'warning');
        return;
      }

      try {
        const formData = new FormData();
        
        // Thêm các trường dữ liệu
        Object.keys(editedEmployee.value).forEach(key => {
          if (editedEmployee.value[key] !== null && editedEmployee.value[key] !== undefined) {
            formData.append(key, editedEmployee.value[key]);
          }
        });

        if (isEditing.value) {
          await updateEmployee(editedEmployee.value.employee_id, formData);
          showSnackbar('Cập nhật nhân viên thành công!', 'success');
        } else {
          await addEmployee(formData);
          showSnackbar('Thêm nhân viên thành công! (Cần huấn luyện khuôn mặt)', 'success');
        }
        closeEmployeeDialog();
        fetchEmployees();
      } catch (error) {
        console.error('Error saving employee:', error);
        showSnackbar(`Lỗi khi ${isEditing.value ? 'cập nhật' : 'thêm'} nhân viên: ${error.response?.data?.error || error.message}`, 'error');
      }
    };

    const confirmSoftDelete = (employee) => {
      selectedEmployee.value = employee;
      actionType.value = 'delete';
      confirmDialog.value = true;
    };

    const confirmRestoreEmployee = (employee) => {
      selectedEmployee.value = employee;
      actionType.value = 'restore';
      confirmDialog.value = true;
    };

    const executeConfirmedAction = async () => {
      if (!selectedEmployee.value) return;

      try {
        if (actionType.value === 'delete') {
          await deleteEmployee(selectedEmployee.value.employee_id);
          showSnackbar(`Đã xóa mềm nhân viên ${selectedEmployee.value.full_name}.`, 'success');
        } else if (actionType.value === 'restore') {
          await restoreEmployee(selectedEmployee.value.employee_id);
          showSnackbar(`Đã khôi phục nhân viên ${selectedEmployee.value.full_name}.`, 'success');
        }
        confirmDialog.value = false;
        selectedEmployee.value = null;
        fetchEmployees();
      } catch (error) {
        console.error(`Error ${actionType.value}ing employee:`, error);
        showSnackbar(`Lỗi khi ${actionType.value === 'delete' ? 'xóa mềm' : 'khôi phục'} nhân viên: ${error.response?.data?.error || error.message}`, 'error');
      }
    };

    const showSnackbar = (message, color) => {
      snackbar.value.message = message;
      snackbar.value.color = color;
      snackbar.value.show = true;
    };

    onMounted(fetchEmployees);

    return {
      employees,
      totalEmployees,
      loading,
      searchQuery,
      options,
      employeeDialog,
      isEditing,
      editedEmployee,
      headers,
      openAddEmployeeDialog,
      openEditEmployeeDialog,
      closeEmployeeDialog,
      saveEmployee,
      confirmDialog,
      selectedEmployee,
      actionType,
      confirmSoftDelete,
      confirmRestoreEmployee,
      executeConfirmedAction,
      showSnackbar,
      snackbar,
      debouncedSearch,
      updateOptions,
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