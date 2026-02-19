<!--
  FilePreviewHeader.vue

  Header bar for file preview components.
  Shows icon, title, meta info, and action buttons.

  Used by: FilePreview.vue, FilePreviewPanel.vue, FilePreviewWindow.vue
-->

<template>
  <div class="preview-header">
    <div class="header-info">
      <span class="preview-icon">{{ icon }}</span>
      <div class="preview-details">
        <h3 class="preview-title">{{ title }}</h3>
        <span class="preview-meta">{{ meta }}</span>
      </div>
    </div>
    <div class="header-actions">
      <button
        v-if="showDownload"
        @click="$emit('download')"
        class="action-btn"
        :title="$t('filePreview.download')"
      >
        &#x2B07;&#xFE0F;
      </button>
      <button
        v-if="showEdit"
        @click="$emit('edit')"
        class="action-btn"
        :title="$t('filePreview.edit')"
      >
        &#x270F;&#xFE0F;
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  icon: string
  title: string
  meta: string
  showDownload: boolean
  showEdit: boolean
}

defineProps<Props>()

defineEmits<{
  download: []
  edit: []
}>()
</script>

<style scoped>
.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.preview-icon { font-size: 1.5rem; }

.preview-title {
  font-size: 0.9375rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-text-primary);
}

.preview-meta {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.375rem 0.625rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
}
</style>
