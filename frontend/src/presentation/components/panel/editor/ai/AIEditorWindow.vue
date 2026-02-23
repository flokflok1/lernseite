/**
 * AIEditorWindow.vue
 *
 * DEPRECATED: Redirects to UnifiedAIEditorWindow.
 * Kept for backward compatibility with existing panel/window references.
 */

<template>
  <UnifiedAIEditorWindow :window="window" />
</template>

<script setup lang="ts">
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import UnifiedAIEditorWindow from './unified/UnifiedAIEditorWindow.vue'

defineProps<{ window: LsxWindow }>()
</script>
