/**
 * ManualEditorWindow.vue
 *
 * Thin window wrapper for ManualEditorContainer.
 * Receives window prop from DesktopLayer and extracts payload data.
 */

<template>
  <ManualEditorContainer
    :project-id="(window?.payload?.projectId as string) || ''"
    :course-id="(window?.payload?.courseId as string) || null"
  />
</template>

<script setup lang="ts">
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import ManualEditorContainer from './ManualEditorContainer.vue'

defineProps<{ window: LsxWindow }>()
</script>
