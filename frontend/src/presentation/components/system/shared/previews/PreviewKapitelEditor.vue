<!--
  Mini-Preview for Kapitel Editor Window
  Shows chapter details
  Refactored: modules → chapters (2025-11-27)
-->

<template>
  <div class="space-y-2">
    <div v-if="chapter.duration_minutes" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Dauer:</span>
      <span class="text-[var(--color-text-primary)]">{{ chapter.duration_minutes }} Min.</span>
    </div>

    <div v-if="chapter.lesson_count !== undefined" class="flex justify-between">
      <span class="text-[var(--color-text-secondary)]">Lektionen:</span>
      <span class="text-[var(--color-text-primary)]">{{ chapter.lesson_count }}</span>
    </div>

    <!-- Flags -->
    <div v-if="hasFlags" class="pt-2 border-t border-[var(--color-border)]">
      <div class="text-[var(--color-text-secondary)] mb-1">Enthält:</div>
      <div class="flex flex-wrap gap-1">
        <span v-if="chapter.has_video" class="px-2 py-0.5 bg-blue-500/20 text-blue-700 rounded text-xs">
          🎥 Video
        </span>
        <span v-if="chapter.has_quiz" class="px-2 py-0.5 bg-purple-500/20 text-purple-700 rounded text-xs">
          ❓ Quiz
        </span>
        <span v-if="chapter.has_exam" class="px-2 py-0.5 bg-red-500/20 text-red-700 rounded text-xs">
          📝 Prüfung
        </span>
      </div>
    </div>

    <div v-if="!chapter.duration_minutes && !hasFlags" class="text-[var(--color-text-tertiary)] text-center py-2">
      Noch keine Details
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { LsxWindow } from '@/application/stores/window.store'

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const chapter = computed(() => props.window.payload?.chapter || {})

const hasFlags = computed(() =>
  chapter.value.has_video || chapter.value.has_quiz || chapter.value.has_exam
)
</script>
