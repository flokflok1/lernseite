<!--
  TypesPanel - Content Types Selection
  Sub-component of ContentTab
-->

<template>
  <div class="types-panel">
    <div class="panel-header">
      <span class="panel-icon">📚</span>
      <span class="panel-title">{{ $t('features.aiEditorContent.contentTypes') }}</span>
    </div>

    <div class="type-list">
      <div
        v-for="type in contentTypes"
        :key="type.id"
        class="type-item"
        :class="{ active: selectedType === type.id }"
        @click="$emit('update:selectedType', type.id)"
      >
        <span class="type-emoji">{{ type.emoji }}</span>
        <span class="type-name">{{ type.name }}</span>
      </div>
    </div>

    <div class="panel-divider"></div>

    <!-- Lesson Info -->
    <div class="info-section">
      <h4>{{ $t('features.aiEditorContent.lesson') }}</h4>
      <div class="info-item">
        <span class="info-label">{{ $t('features.aiEditorContent.type') }}</span>
        <span class="info-value">{{ lessonType }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">{{ $t('features.aiEditorContent.status') }}</span>
        <span class="info-value status-badge" :class="hasContent ? 'saved' : 'draft'">
          {{ hasContent ? $t('features.aiEditorContent.saved') : $t('features.aiEditorContent.draft') }}
        </span>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <button @click="$emit('back')" class="action-btn">
        {{ $t('features.aiEditorContent.backToChapter') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ContentType {
  id: string
  name: string
  emoji: string
}

defineProps<{
  contentTypes: ContentType[]
  selectedType: string
  lessonType: string
  hasContent: boolean
}>()

defineEmits<{
  (e: 'update:selectedType', value: string): void
  (e: 'back'): void
}>()
</script>

<style scoped>
.types-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.panel-icon { font-size: 1rem; }

.panel-title {
  flex: 1;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.panel-divider {
  height: 1px;
  background: var(--color-border);
  margin: 0.5rem 0;
}

.type-list { padding: 0.5rem; }

.type-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.15s;
}

.type-item:hover { background: var(--color-surface-secondary); }

.type-item.active {
  background: rgba(var(--color-primary-rgb, 59, 130, 246), 0.1);
  border: 1px solid var(--color-primary);
}

.type-emoji { font-size: 1.125rem; }

.type-name {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.info-section { padding: 1rem; }

.info-section h4 {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.info-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.info-value {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.status-badge {
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
}

.status-badge.saved {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.draft {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.quick-actions {
  padding: 0.75rem;
  margin-top: auto;
  border-top: 1px solid var(--color-border);
}

.action-btn {
  width: 100%;
  padding: 0.5rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}
</style>
