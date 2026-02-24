<!--
  LSX Pop-out Window Layout

  Minimal layout for pop-out windows: no sidebar, no taskbar.
  Handles auth initialization so the pop-out has access to user data.
-->

<template>
  <div class="popout-layout w-screen h-screen overflow-hidden bg-[var(--color-bg)]">
    <router-view v-if="isReady" />
    <div v-else class="flex items-center justify-center h-full">
      <div class="text-[var(--color-text-secondary)]">{{ $t('common.loading') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'

const authStore = useAuthStore()
const isReady = ref(false)

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    try {
      await authStore.checkAuth()
    } catch {
      // Auth failed — pop-out will show content without auth
    }
  }
  isReady.value = true
})
</script>
