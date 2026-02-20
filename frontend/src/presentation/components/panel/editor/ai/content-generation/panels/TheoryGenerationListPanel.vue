<!--
  TheoryGenerationListPanel - List of chapter theories (left panel)

  Displays list of chapter theories with search, filter, and action buttons.
  Emits events for selection and deletion.
  Max 200 lines = focused responsibility.
-->

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChapterTheory } from '../types/theory.types'

interface Props {
  theories: ChapterTheory[]
  isLoading: boolean
  selectedId: string | null
}

interface Emits {
  (e: 'select', id: string): void
  (e: 'delete', id: string): void
  (e: 'refresh'): void
  (e: 'create'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

// Local state
const searchQuery = ref('')

// Computed
const filteredTheories = computed(() => {
  if (!searchQuery.value) return props.theories

  const query = searchQuery.value.toLowerCase()
  return props.theories.filter(theory =>
    theory.title.toLowerCase().includes(query)
  )
})

// Methods
const handleSelect = (theoryId: string) => {
  emit('select', theoryId)
}

const handleDelete = (theoryId: string) => {
  if (confirm(t('course-editor.theory.confirmDelete'))) {
    emit('delete', theoryId)
  }
}

const getStyleEmoji = (style: string): string => {
  const emojis: Record<string, string> = {
    standard: '📚',
    compact: '📋',
    detailed: '📖',
    visual: '🎨',
    exam: '📝'
  }
  return emojis[style] || '📚'
}

const formatDate = (date: Date): string => {
  return new Date(date).toLocaleDateString()
}
</script>

<template>
  <div class="theory-list-panel">
    <!-- Header -->
    <div class="panel-header">
      <span class="panel-icon">📚</span>
      <span class="panel-title">{{ $t('course-editor.theory.list.title') }}</span>
      <button @click="$emit('refresh')" class="refresh-btn" :title="$t('course-editor.theory.list.refresh')">
        🔄
      </button>
    </div>

    <!-- Search -->
    <div class="search-container">
      <input
        v-model="searchQuery"
        type="text"
        class="search-input"
        :placeholder="$t('course-editor.theory.list.search')"
      />
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="list-loading">
      <div class="spinner"></div>
      <span>{{ $t('course-editor.theory.list.loading') }}</span>
    </div>

    <!-- List -->
    <div v-else class="content-list">
      <!-- Empty -->
      <div v-if="filteredTheories.length === 0" class="list-empty">
        <span class="empty-icon">📝</span>
        <p>{{ $t('course-editor.theory.list.empty') }}</p>
      </div>

      <!-- Items -->
      <div
        v-for="theory in filteredTheories"
        :key="theory.theoryId"
        class="list-item"
        :class="{ active: selectedId === theory.theoryId }"
        @click="handleSelect(theory.theoryId)"
      >
        <div class="item-icon">{{ getStyleEmoji(theory.style) }}</div>
        <div class="item-info">
          <span class="item-name">{{ theory.title }}</span>
          <span class="item-meta">{{ formatDate(theory.createdAt) }}</span>
        </div>
        <div class="item-actions">
          <button
            v-if="theory.audioUrl"
            @click.stop
            class="item-btn"
            :title="$t('course-editor.theory.list.playAudio')"
          >
            🔊
          </button>
          <button
            @click.stop="handleDelete(theory.theoryId)"
            class="item-btn danger"
            :title="$t('course-editor.theory.list.delete')"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>

    <!-- Create Button -->
    <div class="list-actions">
      <button @click="$emit('create')" class="create-btn">
        {{ $t('course-editor.theory.list.createNew') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.theory-list-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
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

.search-container {
  padding: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.search-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: var(--color-surface);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
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

.empty-icon {
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
  min-width: 1.5rem;
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
