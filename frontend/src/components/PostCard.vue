<script setup>
import { RouterLink } from 'vue-router'

defineProps({ post: Object })

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('uz-UZ', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>

<template>
  <RouterLink
    :to="{ name: 'post-detail', params: { id: post.id } }"
    class="block bg-white border border-slate-200 rounded-xl p-4 hover:border-emerald-400 transition"
  >
    <h2 class="font-semibold text-lg text-slate-900">{{ post.title }}</h2>
    <p class="text-slate-600 text-sm mt-1 line-clamp-2">{{ post.content }}</p>
    <p class="text-xs text-slate-400 mt-2">{{ formatDate(post.created_at) }}</p>
  </RouterLink>
</template>
