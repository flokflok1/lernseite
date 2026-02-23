<script setup lang="ts">
/**
 * UnifiedAIEditorWindow — Window wrapper for the desktop window system
 *
 * Receives window prop from FloatingWindow and extracts payload data.
 * Replaces AiStudioProWindow and AIEditorWindow.
 */
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import UnifiedAIEditor from './UnifiedAIEditor.vue'

defineProps<{ window: LsxWindow }>()
</script>

<template>
  <div class="w-full h-full">
    <UnifiedAIEditor
      :initial-course-id="(window?.payload?.courseId as string) || undefined"
    />
  </div>
</template>
