<!--
  Mini-Preview for Course Editor Window
  Shows course metadata
-->

<template>
  <div class="space-y-2">
    <div v-if="course.status" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Status:</span>
      <span :class="statusClass">{{ statusLabel }}</span>
    </div>

    <div v-if="course.category" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Kategorie:</span>
      <span class="text-[var(--color-text-primary)]">{{ course.category }}</span>
    </div>

    <div v-if="course.level" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Level:</span>
      <span class="text-[var(--color-text-primary)]">{{ levelLabel }}</span>
    </div>

    <div class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Module:</span>
      <span class="text-[var(--color-text-primary)]">{{ course.module_count || 0 }}</span>
    </div>

    <div v-if="course.enrollment_count !== undefined" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Einschreibungen:</span>
      <span class="text-[var(--color-text-primary)]">{{ course.enrollment_count }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { LsxWindow } from '@/store/modules/desktop'

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const course = computed(() => props.window.payload?.course || {})

const statusLabel = computed(() => {
  const labels: Record<string, string> = {
    draft: 'Entwurf',
    published: 'Veröffentlicht',
    archived: 'Archiviert'
  }
  return labels[course.value.status] || course.value.status
})

const statusClass = computed(() => {
  const status = course.value.status
  if (status === 'published') return 'text-green-600'
  if (status === 'archived') return 'text-orange-600'
  return 'text-[var(--color-text-primary)]'
})

const levelLabel = computed(() => {
  const levels: Record<string, string> = {
    beginner: 'Anfänger',
    intermediate: 'Fortgeschritten',
    advanced: 'Experte',
    expert: 'Meister'
  }
  return levels[course.value.level] || course.value.level
})
</script>
