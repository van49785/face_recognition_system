<template>
  <div>
    Home Page
  </div>
  <v-btn @click="logout">Logout</v-btn>
</template>

  <script setup>
    import { useAuthStore } from '../stores/auth';
    import { useRouter } from 'vue-router';
    const authStore = useAuthStore();
    const router = useRouter();
    async function logout() {
      await authStore.logout();
      router.push('/login');
}
  </script>