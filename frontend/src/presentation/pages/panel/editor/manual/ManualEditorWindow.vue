/**
 * ManualEditorWindow.vue
 *
 * Thin window wrapper for ManualEditorContainerView.
 * Receives window prop from DesktopLayer and extracts payload data.
 */

<template>
  <ManualEditorContainerView
    :project-id="(window?.payload?.projectId as string) || ''"
    :course-id="(window?.payload?.courseId as string) || null"
  />
</template>

<script setup lang="ts">
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import ManualEditorContainerView from '@/presentation/components/panel/editor/manual/core/ManualEditorContainerView.vue'

defineProps<{ window: LsxWindow }>()
</script>
