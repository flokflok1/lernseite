<!--
  Mini-Preview for Course Create Window
  Shows current course draft data
-->

<template>
  <div class="space-y-2">
    <div v-if="courseDraft.title" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Titel:</span>
      <span class="text-[var(--color-text-primary)] font-medium truncate ml-2">
        {{ courseDraft.title }}
      </span>
    </div>

    <div v-if="courseDraft.category" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Kategorie:</span>
      <span class="text-[var(--color-text-primary)]">{{ courseDraft.category }}</span>
    </div>

    <div v-if="courseDraft.level" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Level:</span>
      <span class="text-[var(--color-text-primary)]">{{ levelLabel }}</span>
    </div>

    <div v-if="moduleCount > 0" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Module:</span>
      <span class="text-[var(--color-text-primary)]">{{ moduleCount }}</span>
    </div>

    <div v-if="lessonCount > 0" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Lektionen:</span>
      <span class="text-[var(--color-text-primary)]">{{ lessonCount }}</span>
    </div>

    <div v-if="!courseDraft.title" class="text-[var(--color-text-tertiary)] text-center py-2">
      Noch keine Daten eingegeben
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/desktop'

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const courseDraft = computed(() => props.window.payload?.courseDraft || {})
const moduleCount = computed(() => props.window.payload?.modules?.length || 0)
const lessonCount = computed(() => {
  const modules = props.window.payload?.modules || []
  return modules.reduce((total: number, mod: any) => total + (mod.lessons?.length || 0), 0)
})

const levelLabel = computed(() => {
  const levels: Record<string, string> = {
    beginner: 'Anfänger',
    intermediate: 'Fortgeschritten',
    advanced: 'Experte',
    expert: 'Meister'
  }
  return levels[courseDraft.value.level] || courseDraft.value.level
})
</script>
