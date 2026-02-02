<!--
  Admin AI Job Window Content

  Window content for monitoring AI course generation jobs.
  Phase: B24-06 - Admin Desktop OS
-->

<template>
  <div class="admin-ai-job-window">
    <p class="text-[var(--color-text-secondary)] p-8 text-center">
      AI Job Window - wird in Phase 5 implementiert
      <br />
      Job ID: {{ window.payload?.jobId }}
    </p>
  </div>
</template>

<script setup lang="ts">
import type { LsxWindow } from '@/application/stores/window.store'

interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>
