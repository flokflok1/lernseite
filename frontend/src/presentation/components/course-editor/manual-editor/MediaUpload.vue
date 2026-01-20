/**
 * MediaUpload.vue - Media file upload interface
 */

<script setup lang="ts">
interface Emits {
  (e: 'upload', file: File): void
}

defineEmits<Emits>()
</script>

<template>
  <div class="media-upload">Media Upload</div>
</template>

<style scoped>
.media-upload {
  padding: 16px;
}
</style>
