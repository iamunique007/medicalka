<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import api, { apiError } from '../api/client'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const post = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref('')
const newComment = ref('')
const commentError = ref('')
const liked = ref(false)
const likesCount = ref(0)
const likeBusy = ref(false)
const postId = route.params.id

const isAuthor = computed(() => auth.user && post.value && auth.user.id === post.value.author_id)

function formatDate(iso) {
  return new Date(iso).toLocaleString('uz-UZ', { dateStyle: 'medium', timeStyle: 'short' })
}

async function loadComments() {
  const { data } = await api.get(`/posts/${postId}/comments`)
  comments.value = data
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [postRes] = await Promise.all([api.get(`/posts/${postId}`), loadComments()])
    post.value = postRes.data
    liked.value = !!postRes.data.is_liked
    likesCount.value = postRes.data.likes_count ?? 0
  } catch (e) {
    error.value = apiError(e)
  } finally {
    loading.value = false
  }
}

async function toggleLike() {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  likeBusy.value = true
  try {
    if (liked.value) {
      await api.delete(`/posts/${postId}/like`)
      liked.value = false
      likesCount.value = Math.max(0, likesCount.value - 1)
    } else {
      await api.post(`/posts/${postId}/like`)
      liked.value = true
      likesCount.value += 1
    }
  } catch (e) {
    const s = e.response?.status
    if (s === 409) liked.value = true // allaqachon like bosilgan
    else if (s === 404) liked.value = false // like bosilmagan
    else alert(apiError(e))
  } finally {
    likeBusy.value = false
  }
}

async function addComment() {
  commentError.value = ''
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  try {
    await api.post(`/posts/${postId}/comments`, { content: newComment.value })
    newComment.value = ''
    await loadComments()
  } catch (e) {
    commentError.value = apiError(e)
  }
}

async function deleteComment(id) {
  if (!confirm("Izohni o'chirishni tasdiqlaysizmi?")) return
  try {
    await api.delete(`/posts/${postId}/comments/${id}`)
    comments.value = comments.value.filter((c) => c.id !== id)
  } catch (e) {
    alert(apiError(e))
  }
}

async function deletePost() {
  if (!confirm("Postni o'chirishni tasdiqlaysizmi?")) return
  try {
    await api.delete(`/posts/${postId}`)
    router.push({ name: 'home' })
  } catch (e) {
    alert(apiError(e))
  }
}

onMounted(load)
</script>

<template>
  <div>
    <p v-if="loading" class="text-slate-500">Yuklanmoqda...</p>
    <p v-else-if="error" class="text-red-500">{{ error }}</p>

    <div v-else-if="post">
      <article class="bg-white border border-slate-200 rounded-xl p-6">
        <div class="flex items-start justify-between gap-4">
          <h1 class="text-2xl font-bold">{{ post.title }}</h1>
          <div v-if="isAuthor" class="flex gap-2 shrink-0">
            <RouterLink
              :to="{ name: 'post-edit', params: { id: post.id } }"
              class="text-sm text-slate-500 hover:text-emerald-600"
              >Tahrirlash</RouterLink
            >
            <button @click="deletePost" class="text-sm text-red-500 hover:text-red-600">O'chirish</button>
          </div>
        </div>
        <p class="text-xs text-slate-400 mt-1">{{ formatDate(post.created_at) }}</p>
        <p class="mt-4 whitespace-pre-wrap text-slate-700">{{ post.content }}</p>

        <button
          @click="toggleLike"
          :disabled="likeBusy"
          class="mt-6 inline-flex items-center gap-2 px-4 py-2 rounded-lg border transition"
          :class="
            liked
              ? 'bg-rose-50 border-rose-300 text-rose-600'
              : 'border-slate-300 text-slate-600 hover:border-rose-300'
          "
        >
          <span>{{ liked ? '♥' : '♡' }}</span>
          <span>{{ liked ? 'Yoqdi' : 'Like' }}</span>
          <span class="text-sm opacity-70">· {{ likesCount }}</span>
        </button>
      </article>

      <section class="mt-6">
        <h2 class="font-semibold text-lg mb-3">Izohlar ({{ comments.length }})</h2>

        <div v-if="auth.isAuthenticated" class="mb-4">
          <textarea
            v-model="newComment"
            rows="2"
            placeholder="Izoh yozing (kamida 2 belgi)..."
            class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
          ></textarea>
          <p v-if="commentError" class="text-sm text-red-500 mt-1">{{ commentError }}</p>
          <button
            @click="addComment"
            :disabled="newComment.trim().length < 2"
            class="mt-2 px-4 py-1.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50"
          >
            Yuborish
          </button>
        </div>
        <p v-else class="text-sm text-slate-500 mb-4">
          Izoh qoldirish uchun <RouterLink to="/login" class="text-emerald-600 hover:underline">kiring</RouterLink>.
        </p>

        <div class="space-y-3">
          <div v-for="c in comments" :key="c.id" class="bg-white border border-slate-200 rounded-lg p-3">
            <div class="flex items-center justify-between">
              <span class="font-medium text-sm">
                {{ c.author.full_name }} <span class="text-slate-400">@{{ c.author.username }}</span>
              </span>
              <button
                v-if="auth.user && auth.user.id === c.author.id"
                @click="deleteComment(c.id)"
                class="text-xs text-red-500 hover:text-red-600"
              >
                o'chirish
              </button>
            </div>
            <p class="text-slate-700 text-sm mt-1 whitespace-pre-wrap">{{ c.content }}</p>
            <p class="text-xs text-slate-400 mt-1">{{ formatDate(c.created_at) }}</p>
          </div>
          <p v-if="comments.length === 0" class="text-sm text-slate-500">Hali izoh yo'q.</p>
        </div>
      </section>
    </div>
  </div>
</template>
