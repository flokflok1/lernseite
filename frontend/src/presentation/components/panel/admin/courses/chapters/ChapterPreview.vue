<!--
  Admin Chapter Preview (Base Variant)

  Thin wrapper that extracts chapter data from an LsxWindow payload
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
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import ChapterPreviewContent from './ChapterPreviewContent.vue'

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

defineEmits<{
  (e: 'close'): void
}>()

const chapter = computed(() => props.window.payload?.chapter as any)
</script>
