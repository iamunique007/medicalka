<script setup>
import { ref, onMounted, watch } from 'vue'
import api, { apiError } from '../api/client'
import PostCard from '../components/PostCard.vue'

const posts = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const search = ref('')
const loading = ref(false)
const error = ref('')
let searchTimer = null

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/posts', {
      params: { page: page.value, page_size: pageSize, search: search.value || undefined },
    })
    posts.value = data.items
    total.value = data.total
  } catch (e) {
    error.value = apiError(e)
  } finally {
    loading.value = false
  }
}

const totalPages = () => Math.max(1, Math.ceil(total.value / pageSize))
function nextPage() {
  if (page.value < totalPages()) {
    page.value++
    load()
  }
}
function prevPage() {
  if (page.value > 1) {
    page.value--
    load()
  }
}

watch(search, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    load()
  }, 400)
})

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-4">
      <input
        v-model="search"
        type="text"
        placeholder="Postlarni qidirish..."
        class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
      />
    </div>

    <p v-if="loading" class="text-slate-500">Yuklanmoqda...</p>
    <p v-else-if="error" class="text-red-500">{{ error }}</p>
    <p v-else-if="posts.length === 0" class="text-slate-500">Post topilmadi.</p>

    <div v-else class="space-y-3">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </div>

    <div v-if="total > pageSize" class="flex items-center justify-between mt-6">
      <button @click="prevPage" :disabled="page === 1" class="px-3 py-1.5 border rounded-lg disabled:opacity-40">
        Oldingi
      </button>
      <span class="text-sm text-slate-500">{{ page }} / {{ totalPages() }}</span>
      <button @click="nextPage" :disabled="page >= totalPages()" class="px-3 py-1.5 border rounded-lg disabled:opacity-40">
        Keyingi
      </button>
    </div>
  </div>
</template>
