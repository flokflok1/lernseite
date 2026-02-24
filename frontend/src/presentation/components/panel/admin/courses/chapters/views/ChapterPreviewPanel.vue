<!--
  Admin Chapter Preview Panel

  Thin wrapper that extracts chapter data from an LsxPanel payload
  and delegates rendering to ChapterPreviewContent.

  Phase: D4 - AI Editor
-->

<template>
  <ChapterPreviewContent
    :chapter="chapter"
    @close="$emit('close')"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { LsxPanel } from '@/application/stores/modules/workspace'
import ChapterPreviewContent from '../ChapterPreviewContent.vue'

interface Props {
  panel: LsxPanel
}

const props = defineProps<Props>()

defineEmits<{
  (e: 'close'): void
}>()

const chapter = computed(() => props.panel.payload?.chapter as any)
</script>
