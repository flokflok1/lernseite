<script setup lang="ts">
/**
 * UnifiedAIEditorWindow — Window wrapper for the desktop window system
 *
 * Receives window prop from FloatingWindow and extracts payload data.
 * Single entry point for AI Editor in window system.
 */
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import UnifiedAIEditor from './UnifiedAIEditor.vue'

defineProps<{ window: LsxWindow }>()
</script>

<template>
  <div class="w-full h-full">
    <UnifiedAIEditor
      :course-id="(window?.payload?.courseId as string) || undefined"
    />
  </div>
</template>
