<!--
  TheoryListPanel - Left column displaying the list of chapter theories.

  Handles loading state, empty state, theory selection, and delete actions.
-->

<template>
  <div class="list-panel">
    <div class="panel-header">
      <span class="panel-icon">📚</span>
      <span class="panel-title">{{ $t('chapterTheoryView.theories') }}</span>
      <button @click="$emit('refresh')" class="refresh-btn" :title="$t('chapterTheoryView.refresh')">🔄</button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="list-loading">
      <div class="spinner"></div>
      <span>{{ $t('chapterTheoryView.loading') }}</span>
    </div>

    <!-- Theory List -->
    <div v-else class="content-list">
      <div v-if="theories.length === 0" class="list-empty">
        <span class="empty-icon-small">📝</span>
        <p>{{ $t('chapterTheoryView.noTheories') }}</p>
      </div>
      <div
        v-for="theory in theories"
        :key="theory.theoryId"
        class="list-item"
        :class="{ active: selectedTheoryId === theory.theoryId }"
        @click="$emit('select', theory.theoryId)"
      >
        <div class="item-icon">{{ getStyleEmoji(theory.style) }}</div>
        <div class="item-info">
          <span class="item-name">{{ theory.title }}</span>
          <span class="item-meta">{{ formatDate(theory.createdAt) }}</span>
        </div>
        <div class="item-actions">
          <button
            v-if="theory.audioUrl"
            @click.stop="$emit('playAudio', theory.audioUrl)"
            class="item-btn"
            :title="$t('chapterTheoryView.playAudio')"
          >
            🔊
          </button>
          <button
            @click.stop="$emit('delete', theory.theoryId)"
            class="item-btn danger"
            :title="$t('chapterTheoryView.delete')"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>

    <!-- Create New Button -->
    <div class="list-actions">
      <button @click="$emit('create')" class="create-btn">
        {{ $t('chapterTheoryView.createNew') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TheoryListItem } from './chapter-theory.types'

interface Props {
  theories: TheoryListItem[]
  selectedTheoryId: string | null
  isLoading: boolean
  getStyleEmoji: (style: string) => string
  formatDate: (dateStr: string) => string
}

defineProps<Props>()

defineEmits<{
  (e: 'select', theoryId: string): void
  (e: 'delete', theoryId: string): void
  (e: 'playAudio', url: string): void
  (e: 'refresh'): void
  (e: 'create'): void
}>()
</script>

<style scoped>
.list-panel {
  background: var(--color-surface);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.panel-icon {
  font-size: 1rem;
}

.panel-title {
  font-weight: 600;
  font-size: 0.875rem;
  flex: 1;
}

.refresh-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.refresh-btn:hover {
  opacity: 1;
}

.list-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: var(--color-text-tertiary);
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.content-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.list-empty {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-tertiary);
}

.empty-icon-small {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.5rem;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.15s;
}

.list-item:hover {
  background: var(--color-surface-secondary);
}

.list-item.active {
  background: var(--color-primary-subtle);
}

.item-icon {
  font-size: 1.25rem;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-meta {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.item-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.15s;
}

.list-item:hover .item-actions {
  opacity: 1;
}

.item-btn {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
  opacity: 0.7;
  transition: opacity 0.15s;
}

.item-btn:hover {
  opacity: 1;
}

.item-btn.danger:hover {
  color: #ef4444;
}

.list-actions {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.create-btn {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, var(--color-primary) 0%, #8b5cf6 100%);
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}

.create-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}
</style>
