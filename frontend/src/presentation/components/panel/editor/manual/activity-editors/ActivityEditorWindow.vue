/**
 * ActivityEditorWindow.vue
 *
 * Thin FloatingWindow wrapper. Extracts activity from window payload
 * and delegates to ActivityEditorContainerView.
 * Pattern: same as ManualEditorWindow.vue
 */
<template>
  <ActivityEditorContainerView
    v-if="(window?.payload?.activity as any)"
    :activity="(window.payload.activity as any)"
  />
</template>

<script setup lang="ts">
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import ActivityEditorContainerView from './ActivityEditorContainerView.vue'

defineProps<{ window: LsxWindow }>()
</script>
