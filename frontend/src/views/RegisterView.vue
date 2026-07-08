<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { apiError } from '../api/client'

const auth = useAuthStore()
const form = ref({ email: '', username: '', full_name: '', password: '' })
const error = ref('')
const success = ref(false)
const verifyToken = ref('')
const loading = ref(false)

// Backend xoh xom token, xoh to'liq URL (…?token=abc) qaytarsa ham tokenni ajratib oladi
function extractToken(v) {
  if (!v) return ''
  const m = String(v).match(/token=([^&]+)/)
  return m ? decodeURIComponent(m[1]) : String(v)
}

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const data = await auth.register(form.value)
    verifyToken.value = extractToken(data.verification_token)
    success.value = true
  } catch (e) {
    error.value = apiError(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-sm mx-auto bg-white border border-slate-200 rounded-xl p-6 mt-8">
    <h1 class="text-xl font-bold mb-4">Ro'yxatdan o'tish</h1>

    <div v-if="success" class="text-center">
      <p class="text-emerald-600 font-medium">Ro'yxatdan o'tdingiz! 🎉</p>

      <template v-if="verifyToken">
        <p class="text-sm text-slate-500 mt-2">
          Akkountingizni hoziroq tasdiqlashingiz yoki keyinroq kirishingiz mumkin:
        </p>
        <div class="flex flex-col gap-2 mt-4">
          <RouterLink
            :to="{ name: 'verify-email', query: { token: verifyToken } }"
            class="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
          >
            Akkountni tasdiqlash
          </RouterLink>
          <RouterLink to="/login" class="text-sm text-slate-500 hover:text-emerald-600">
            Tasdiqlamasdan kirish sahifasiga o'tish
          </RouterLink>
        </div>
        <p class="text-[11px] text-slate-400 mt-3 break-all">token: {{ verifyToken }}</p>
      </template>

      <template v-else>
        <p class="text-sm text-slate-500 mt-2">
          Emailingizga tasdiqlash havolasi yuborildi. Uni ochib akkountingizni tasdiqlang, keyin kiring.
        </p>
        <RouterLink to="/login" class="inline-block mt-4 text-emerald-600 hover:underline">Kirish sahifasiga</RouterLink>
      </template>
    </div>

    <form v-else @submit.prevent="submit" class="space-y-3">
      <input
        v-model="form.email"
        type="email"
        placeholder="Email"
        required
        class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
      />
      <input
        v-model="form.username"
        type="text"
        placeholder="Username (3-32, a-z 0-9 _)"
        required
        class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
      />
      <input
        v-model="form.full_name"
        type="text"
        placeholder="To'liq ism"
        required
        class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
      />
      <input
        v-model="form.password"
        type="password"
        placeholder="Parol (kamida 6 belgi)"
        required
        minlength="6"
        class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
      />
      <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
      <button
        type="submit"
        :disabled="loading"
        class="w-full py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50"
      >
        {{ loading ? 'Yuborilmoqda...' : "Ro'yxatdan o'tish" }}
      </button>
    </form>

    <p v-if="!success" class="text-sm text-slate-500 mt-4 text-center">
      Akkountingiz bormi?
      <RouterLink to="/login" class="text-emerald-600 hover:underline">Kiring</RouterLink>
    </p>
  </div>
</template>
