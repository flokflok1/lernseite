<!--
  FilesPanel - File browser for exam generation

  Displays course files with category filtering and selection.
-->

<template>
  <div class="files-panel">
    <div class="panel-header">
      <span class="panel-icon">📁</span>
      <span class="panel-title">{{ $t('aiEditorFiles.title') }}</span>
      <button @click="$emit('refresh')" class="refresh-btn" :title="$t('aiEditorFiles.refresh')">🔄</button>
    </div>

    <!-- File Categories -->
    <div class="file-categories">
      <button
        v-for="cat in categories"
        :key="cat.id"
        @click="$emit('category-change', cat.id)"
        class="category-btn"
        :class="{ active: selectedCategory === cat.id }"
      >
        <span class="cat-icon">{{ cat.icon }}</span>
        <span class="cat-name">{{ cat.name }}</span>
        <span class="cat-count">{{ getCategoryCount(cat.id) }}</span>
      </button>
    </div>

    <!-- File List -->
    <div class="file-list">
      <div v-if="isLoading" class="loading-files">
        <div class="spinner"></div>
        <span>{{ $t('aiEditorFiles.loading') }}</span>
      </div>

      <div v-else-if="filteredFiles.length === 0" class="no-files">
        <span class="no-files-icon">📭</span>
        <p>{{ $t('aiEditorFiles.noFiles') }}</p>
      </div>

      <div
        v-for="file in filteredFiles"
        :key="file.course_file_id"
        class="file-item"
        :class="{
          selected: selectedFileIds.includes(file.course_file_id),
          previewing: previewingFileId === file.course_file_id
        }"
      >
        <label class="file-checkbox">
          <input
            type="checkbox"
            :checked="selectedFileIds.includes(file.course_file_id)"
            @change="$emit('toggle-selection', file)"
          />
        </label>
        <div class="file-icon">{{ getFileIcon(file.file_type) }}</div>
        <div class="file-info" @click="$emit('preview', file)">
          <span class="file-name">{{ file.display_name || file.file_name }}</span>
          <span class="file-meta">
            {{ formatFileSize(file.file_size_bytes) }} • {{ file.file_category }}
          </span>
        </div>
        <button @click="$emit('preview', file)" class="preview-btn" :title="$t('aiEditorFiles.preview')">
          👁️
        </button>
      </div>
    </div>

    <!-- Select All / Clear -->
    <div class="file-actions">
      <button @click="$emit('select-all')" class="action-link">
        ✓ {{ $t('aiEditorFiles.selectAll') }}
      </button>
      <button @click="$emit('clear-selection')" class="action-link">
        ✗ {{ $t('aiEditorFiles.clearSelection') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Types
interface CourseFile {
  course_file_id: string
  file_name: string
  display_name?: string
  file_type: string
  file_size_bytes: number
  file_category: string
}

interface Category {
  id: string
  name: string
  icon: string
}

// Props
const props = defineProps<{
  files: CourseFile[]
  selectedFileIds: string[]
  selectedCategory: string
  previewingFileId?: string | null
  isLoading?: boolean
  categories: Category[]
}>()

// Emits
defineEmits<{
  (e: 'refresh'): void
  (e: 'category-change', categoryId: string): void
  (e: 'toggle-selection', file: CourseFile): void
  (e: 'select-all'): void
  (e: 'clear-selection'): void
  (e: 'preview', file: CourseFile): void
}>()

// Computed
const filteredFiles = computed(() => {
  if (props.selectedCategory === 'all') {
    return props.files
  }
  return props.files.filter(f => f.file_category === props.selectedCategory)
})

// Methods
function getCategoryCount(categoryId: string): number {
  if (categoryId === 'all') return props.files.length
  return props.files.filter(f => f.file_category === categoryId).length
}

function getFileIcon(type: string): string {
  const icons: Record<string, string> = {
    'application/pdf': '📕',
    'text/plain': '📝',
    'application/msword': '📘',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '📘',
    'application/vnd.ms-powerpoint': '📙',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '📙',
    'image/png': '🖼️',
    'image/jpeg': '🖼️',
    'image/gif': '🖼️'
  }
  return icons[type] || '📄'
}

function formatFileSize(bytes: number): string {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
</script>

<style scoped>
.files-panel {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.panel-icon {
  font-size: 1rem;
}

.panel-title {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 600;
}

.refresh-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  opacity: 0.7;
  transition: opacity 0.15s;
}

.refresh-btn:hover {
  opacity: 1;
}

/* Categories */
.file-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.category-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.5rem;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s;
}

.category-btn:hover {
  border-color: var(--color-primary);
}

.category-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.cat-icon {
  font-size: 0.875rem;
}

.cat-count {
  font-size: 0.625rem;
  padding: 0.125rem 0.25rem;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 0.25rem;
}

.category-btn.active .cat-count {
  background: rgba(255, 255, 255, 0.2);
}

/* File List */
.file-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.loading-files {
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
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-files {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  color: var(--color-text-tertiary);
  text-align: center;
}

.no-files-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.no-files p {
  margin: 0;
  font-size: 0.8125rem;
}

/* File Items */
.file-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 0.375rem;
  transition: all 0.15s;
}

.file-item:hover {
  background: var(--color-surface-secondary);
}

.file-item.selected {
  background: var(--color-primary-subtle);
}

.file-item.previewing {
  background: var(--color-warning-subtle);
  border: 1px solid var(--color-warning);
}

.file-checkbox {
  cursor: pointer;
}

.file-icon {
  font-size: 1.25rem;
}

.file-info {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.file-name {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  display: block;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

.preview-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  opacity: 0;
  transition: opacity 0.15s;
}

.file-item:hover .preview-btn {
  opacity: 0.7;
}

.preview-btn:hover {
  opacity: 1 !important;
}

/* File Actions */
.file-actions {
  display: flex;
  gap: 1rem;
  padding: 0.5rem 0.75rem;
  border-top: 1px solid var(--color-border);
}

.action-link {
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: 0.75rem;
  cursor: pointer;
}

.action-link:hover {
  text-decoration: underline;
}
</style>
