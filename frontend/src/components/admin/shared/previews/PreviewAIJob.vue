<!--
  Mini-Preview for AI Job Window
  Shows job status and progress
-->

<template>
  <div class="space-y-3">
    <!-- Status -->
    <div class="flex justify-between items-center">
      <span class="text-[var(--color-text-secondary)]">Status:</span>
      <span :class="statusClass" class="font-medium">{{ statusLabel }}</span>
    </div>

    <!-- Progress Bar -->
    <div v-if="job.status === 'processing' || job.status === 'pending'" class="space-y-1">
      <div class="flex justify-between text-xs">
        <span class="text-[var(--color-text-secondary)]">Fortschritt</span>
        <span class="text-[var(--color-text-primary)] font-medium">{{ progress }}%</span>
      </div>
      <div class="w-full bg-[var(--color-border)] rounded-full h-2 overflow-hidden">
        <div
          class="bg-blue-500 h-full transition-all duration-300"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
    </div>

    <!-- Course Name (if available) -->
    <div v-if="courseName" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Kurs:</span>
      <span class="text-[var(--color-text-primary)] font-medium truncate ml-2">
        {{ courseName }}
      </span>
    </div>

    <!-- Module/Lesson Count -->
    <div v-if="job.status === 'completed' && outputData" class="pt-2 border-t border-[var(--color-border)] space-y-1">
      <div v-if="outputData.modules" class="flex justify-between text-xs">
        <span class="text-[var(--color-text-secondary)]">Module:</span>
        <span class="text-[var(--color-text-primary)]">{{ outputData.modules.length }}</span>
      </div>
      <div v-if="totalLessons > 0" class="flex justify-between text-xs">
        <span class="text-[var(--color-text-secondary)]">Lektionen:</span>
        <span class="text-[var(--color-text-primary)]">{{ totalLessons }}</span>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="job.status === 'failed' && job.error_message" class="pt-2 border-t border-red-500/20">
      <p class="text-xs text-red-600 truncate">{{ job.error_message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { LsxWindow } from '@/store/window.store'

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const job = computed(() => props.window.payload?.job || {})
const outputData = computed(() => job.value.output_data || null)

const progress = computed(() => {
  return Math.min(Math.max(job.value.progress || 0, 0), 100)
})

const statusLabel = computed(() => {
  const labels: Record<string, string> = {
    pending: 'Warten...',
    processing: 'Verarbeitung läuft',
    completed: 'Abgeschlossen',
    failed: 'Fehler',
    cancelled: 'Abgebrochen'
  }
  return labels[job.value.status] || job.value.status
})

const statusClass = computed(() => {
  const status = job.value.status
  if (status === 'processing') return 'text-blue-600'
  if (status === 'completed') return 'text-green-600'
  if (status === 'failed') return 'text-red-600'
  if (status === 'cancelled') return 'text-orange-600'
  return 'text-[var(--color-text-primary)]'
})

const courseName = computed(() => {
  return outputData.value?.course?.title || props.window.payload?.fileName || null
})

const totalLessons = computed(() => {
  if (!outputData.value?.modules) return 0
  return outputData.value.modules.reduce(
    (total: number, mod: any) => total + (mod.lessons?.length || 0),
    0
  )
})
</script>
