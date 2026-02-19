/**
 * AIEditorWindow.vue
 *
 * Thin window wrapper for AIEditorContainer.
 * Receives window prop from DesktopLayer and extracts payload data.
 */

<template>
  <AIEditorContainer
    :project-id="(window?.payload?.projectId as string) || ''"
    :course-id="(window?.payload?.courseId as string) || null"
  />
</template>

<script setup lang="ts">
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import AIEditorContainer from './AIEditorContainer.vue'

defineProps<{ window: LsxWindow }>()
</script>
