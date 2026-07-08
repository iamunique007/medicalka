<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { apiError } from '../api/client'

const auth = useAuthStore()
const form = ref({ username: '', full_name: '' })
const error = ref('')
const success = ref('')
const loading = ref(false)

onMounted(() => {
  if (auth.user) {
    form.value.username = auth.user.username
    form.value.full_name = auth.user.full_name
  }
})

async function submit() {
  error.value = ''
  success.value = ''
  const payload = {}
  if (form.value.username !== auth.user.username) payload.username = form.value.username
  if (form.value.full_name !== auth.user.full_name) payload.full_name = form.value.full_name
  if (Object.keys(payload).length === 0) {
    error.value = "O'zgartirish kiritilmadi."
    return
  }
  loading.value = true
  try {
    await auth.updateMe(payload)
    success.value = 'Profil yangilandi.'
  } catch (e) {
    error.value = apiError(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-sm mx-auto bg-white border border-slate-200 rounded-xl p-6 mt-4">
    <h1 class="text-xl font-bold mb-1">Profil</h1>
    <p class="text-sm text-slate-500 mb-4">
      {{ auth.user?.email }}
      <span v-if="auth.user?.is_verified" class="text-emerald-600">• tasdiqlangan</span>
      <span v-else class="text-amber-600">• tasdiqlanmagan</span>
    </p>

    <form @submit.prevent="submit" class="space-y-3">
      <div>
        <label class="text-sm text-slate-600">Username</label>
        <input
          v-model="form.username"
          type="text"
          minlength="3"
          maxlength="32"
          class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
        />
      </div>
      <div>
        <label class="text-sm text-slate-600">To'liq ism</label>
        <input
          v-model="form.full_name"
          type="text"
          minlength="2"
          maxlength="100"
          class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
        />
      </div>
      <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
      <p v-if="success" class="text-sm text-emerald-600">{{ success }}</p>
      <button
        type="submit"
        :disabled="loading"
        class="w-full py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50"
      >
        {{ loading ? 'Saqlanmoqda...' : 'Saqlash' }}
      </button>
    </form>
  </div>
</template>
