<!--
  Admin AI Job Window Content

  Window content for monitoring AI course generation jobs.
  Phase: B24-06 - Admin Desktop OS
-->

<template>
  <div class="admin-ai-job-window">
    <p class="text-[var(--color-text-secondary)] p-8 text-center">
      {{ $t('windows.aiJob.placeholder') }}
      <br />
      Job ID: {{ window.payload?.jobId }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { LsxWindow } from '@/application/stores/window.store'

const { t } = useI18n()

interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>
