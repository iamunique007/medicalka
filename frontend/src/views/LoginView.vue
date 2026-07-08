<script setup>
import { ref } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { apiError } from '../api/client'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const form = ref({ username_or_email: '', password: '' })
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.value.username_or_email, form.value.password)
    router.push(route.query.redirect || { name: 'home' })
  } catch (e) {
    error.value = apiError(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-sm mx-auto bg-white border border-slate-200 rounded-xl p-6 mt-8">
    <h1 class="text-xl font-bold mb-4">Kirish</h1>
    <form @submit.prevent="submit" class="space-y-3">
      <input
        v-model="form.username_or_email"
        type="text"
        placeholder="Email yoki username"
        required
        class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
      />
      <input
        v-model="form.password"
        type="password"
        placeholder="Parol"
        required
        class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
      />
      <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
      <button
        type="submit"
        :disabled="loading"
        class="w-full py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50"
      >
        {{ loading ? 'Kirilmoqda...' : 'Kirish' }}
      </button>
    </form>
    <p class="text-sm text-slate-500 mt-4 text-center">
      Akkountingiz yo'qmi?
      <RouterLink to="/register" class="text-emerald-600 hover:underline">Ro'yxatdan o'ting</RouterLink>
    </p>
  </div>
</template>
