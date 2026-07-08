<script setup>
import NavBar from './components/NavBar.vue'
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <NavBar />
    <main class="max-w-3xl mx-auto px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>
