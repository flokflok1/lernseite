<template>
  <div class="preview-tab">
    <div class="preview-placeholder">
      <div class="preview-icon">&#x1f441;&#xfe0f;</div>
      <p>{{ $t('panel.plugins.previewPlaceholder') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.preview-tab {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.preview-placeholder {
  text-align: center;
  color: var(--color-text-secondary, #6b7280);
}

.preview-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}
</style>
