<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { apiError } from '../api/client'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const isEdit = computed(() => route.name === 'post-edit')
const form = ref({ title: '', content: '' })
const error = ref('')
const loading = ref(false)

onMounted(async () => {
  if (isEdit.value) {
    try {
      const { data } = await api.get(`/posts/${route.params.id}`)
      form.value = { title: data.title, content: data.content }
    } catch (e) {
      error.value = apiError(e)
    }
  }
})

async function submit() {
  error.value = ''
  if (!auth.isVerified) {
    error.value = "Post yozish uchun emailingiz tasdiqlangan bo'lishi kerak."
    return
  }
  loading.value = true
  try {
    if (isEdit.value) {
      await api.patch(`/posts/${route.params.id}`, form.value)
      router.push({ name: 'post-detail', params: { id: route.params.id } })
    } else {
      const { data } = await api.post('/posts', form.value)
      router.push({ name: 'post-detail', params: { id: data.id } })
    }
  } catch (e) {
    error.value = apiError(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto bg-white border border-slate-200 rounded-xl p-6 mt-4">
    <h1 class="text-xl font-bold mb-4">{{ isEdit ? 'Postni tahrirlash' : 'Yangi post' }}</h1>
    <form @submit.prevent="submit" class="space-y-3">
      <input
        v-model="form.title"
        type="text"
        placeholder="Sarlavha (5-255 belgi)"
        required
        minlength="5"
        maxlength="255"
        class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
      />
      <textarea
        v-model="form.content"
        placeholder="Matn..."
        required
        rows="10"
        maxlength="10000"
        class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
      ></textarea>
      <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
      <div class="flex gap-2">
        <button
          type="submit"
          :disabled="loading"
          class="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50"
        >
          {{ loading ? 'Saqlanmoqda...' : 'Saqlash' }}
        </button>
        <button
          type="button"
          @click="router.back()"
          class="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50"
        >
          Bekor qilish
        </button>
      </div>
    </form>
  </div>
</template>
