<script setup>
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <header class="bg-white border-b border-slate-200">
    <nav class="max-w-3xl mx-auto px-4 h-14 flex items-center justify-between">
      <RouterLink to="/" class="text-lg font-bold text-emerald-600">Medicalka</RouterLink>

      <div class="flex items-center gap-4 text-sm">
        <RouterLink to="/" class="text-slate-600 hover:text-emerald-600">Barcha postlar</RouterLink>

        <template v-if="auth.isAuthenticated">
          <RouterLink to="/posts/new" class="text-slate-600 hover:text-emerald-600">Post yozish</RouterLink>
          <RouterLink to="/profile" class="text-slate-600 hover:text-emerald-600">
            {{ auth.user?.username || 'Profil' }}
          </RouterLink>
          <button @click="logout" class="text-red-500 hover:text-red-600">Chiqish</button>
        </template>
        <template v-else>
          <RouterLink to="/login" class="text-slate-600 hover:text-emerald-600">Kirish</RouterLink>
          <RouterLink to="/register" class="px-3 py-1.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700">
            Ro'yxatdan o'tish
          </RouterLink>
        </template>
      </div>
    </nav>
  </header>
</template>
