<!--
  Mini-Preview for Lesson Editor Window
  Shows lesson details
-->

<template>
  <div class="space-y-2">
    <div v-if="lesson.lesson_type" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Typ:</span>
      <span class="text-[var(--color-text-primary)]">{{ lessonTypeLabel }}</span>
    </div>

    <div v-if="lesson.duration_minutes" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Dauer:</span>
      <span class="text-[var(--color-text-primary)]">{{ lesson.duration_minutes }} Min.</span>
    </div>

    <div v-if="lesson.order_index" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Reihenfolge:</span>
      <span class="text-[var(--color-text-primary)]">{{ lesson.order_index }}</span>
    </div>

    <div v-if="lesson.description" class="pt-2 border-t border-[var(--color-border)]">
      <div class="text-[var(--color-text-secondary)] text-xs mb-1">Beschreibung:</div>
      <p class="text-[var(--color-text-primary)] text-xs line-clamp-2">
        {{ lesson.description }}
      </p>
    </div>

    <div v-if="!lesson.lesson_type" class="text-[var(--color-text-tertiary)] text-center py-2">
      Noch keine Details
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const lesson = computed(() => props.window.payload?.lesson || {})

const lessonTypeLabel = computed(() => {
  const types: Record<string, string> = {
    text: '📄 Text',
    video: '🎥 Video',
    quiz: '❓ Quiz',
    interactive: '🎮 Interaktiv',
    exercise: '💪 Übung',
    ai: '🤖 KI-Lektion',
    exam: '📝 Prüfung'
  }
  return types[lesson.value.lesson_type] || lesson.value.lesson_type
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
