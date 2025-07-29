<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>Employee Dashboard</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn text @click="handleLogout">
        <v-icon left>mdi-logout</v-icon>
        Đăng xuất
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <v-row>
          <v-col cols="12">
            <v-card class="pa-4">
              <v-card-title class="headline">Chào mừng đến với trang Nhân viên!</v-card-title>
              <v-card-text>
                Đây là giao diện chính dành cho nhân viên. Các chức năng của bạn sẽ được hiển thị ở đây.
              </v-card-text>
              <v-card-actions>
                <v-btn color="success" @click="goToAttendance">
                  <v-icon left>mdi-calendar-check</v-icon>
                  Chấm công
                </v-btn>
                <v-btn color="info" @click="goToProfile">
                  <v-icon left>mdi-account</v-icon>
                  Hồ sơ của tôi
                </v-btn>
                </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth'; // Đảm bảo đường dẫn đúng đến auth store

const router = useRouter();
const authStore = useAuthStore();

const handleLogout = async () => {
  console.log('Attempting to log out...');
  await authStore.logout(); // Gọi action logout từ Pinia store
  console.log('Logged out. Redirecting to login page...');
  router.push('/login'); // Chuyển hướng về trang đăng nhập
};

const goToAttendance = () => {
  router.push('/attendance'); // Giả sử có trang chấm công
};

const goToProfile = () => {
  // TODO: Implement navigation to employee profile page
  alert('Chức năng Hồ sơ đang phát triển!');
};

// Có thể thêm các logic khác liên quan đến trang nhân viên ở đây
</script>

<style scoped>
/* Có thể thêm CSS riêng cho Employee Page nếu cần */
</style>