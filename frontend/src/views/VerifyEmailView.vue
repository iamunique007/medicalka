<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import api, { apiError } from '../api/client'

const route = useRoute()
const status = ref('loading') // loading | success | error
const message = ref('')

onMounted(async () => {
  const token = route.query.token
  if (!token) {
    status.value = 'error'
    message.value = 'Token topilmadi.'
    return
  }
  try {
    await api.get('/auth/verify-email', { params: { token } })
    status.value = 'success'
  } catch (e) {
    status.value = 'error'
    message.value = apiError(e)
  }
})
</script>

<template>
  <div class="max-w-sm mx-auto bg-white border border-slate-200 rounded-xl p-6 mt-8 text-center">
    <p v-if="status === 'loading'" class="text-slate-500">Tasdiqlanmoqda...</p>
    <div v-else-if="status === 'success'">
      <p class="text-emerald-600 font-medium text-lg">Email tasdiqlandi! ✅</p>
      <RouterLink to="/login" class="inline-block mt-4 text-emerald-600 hover:underline">Kirish</RouterLink>
    </div>
    <div v-else>
      <p class="text-red-500 font-medium">Tasdiqlashda xatolik</p>
      <p class="text-sm text-slate-500 mt-2">{{ message }}</p>
    </div>
  </div>
</template>
