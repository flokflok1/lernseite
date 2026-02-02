<!--
  ChapterEditor Module - Refactored

  This is a re-export from the refactored ChapterEditor module.
  The actual implementation is in ./ChapterEditor/
-->

<script setup lang="ts">
// Re-export from refactored module
import ChapterEditorComponent from './ChapterEditor/ChapterEditorMain.vue'

interface Props {
  panel: any
}

withDefaults(defineProps<Props>(), {})
</script>

<template>
  <!-- Render the refactored component -->
  <ChapterEditorComponent :panel="panel" />
</template>
