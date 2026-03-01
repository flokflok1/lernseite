<script setup lang="ts">
/**
 * ComparisonItemRow Component
 *
 * Displays a single comparison item with expandable details.
 * Shows item header, values comparison, conflict info, and resolution actions.
 */

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface ComparisonItem {
  key_path: string
  namespace_code: string
  language: string
  similarity: number
  action: string
  resolution_status: string
  frontend_value?: string | null
  database_value?: string | null
  conflict_reason?: string | null
}

interface Props {
  item: ComparisonItem
  index: number
  isExpanded: boolean
  selectedMode: 'AUTO' | 'MANUAL'
  resolutionStatus: (key: string) => string
}

interface Emits {
  (e: 'toggle-expanded'): void
  (e: 'set-resolution', action: string): void
  (e: 'clear-resolution'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { t } = useI18n()

const itemKey = computed(() => `${props.item.key_path}-${props.item.language}`)

const actionIcon = computed(() => {
  switch (props.item.action) {
    case 'SKIP': return '⏭️'
    case 'ADD': return '➕'
    case 'UPDATE': return '✏️'
    case 'DELETE': return '🗑️'
    default: return '📌'
  }
})

const resolutionStatusLocal = computed(() => {
  return props.resolutionStatus(itemKey.value)
})

const isResolved = computed(() => {
  return resolutionStatusLocal.value === 'resolved'
})

const similarityColor = computed(() => {
  const score = props.item.similarity
  if (score >= 0.95) return 'similarity-high'
  if (score >= 0.80) return 'similarity-medium'
  return 'similarity-low'
})

function handleToggleExpand(): void {
  emit('toggle-expanded')
}

function handleSetResolution(action: string): void {
  emit('set-resolution', action)
}

function handleClearResolution(): void {
  emit('clear-resolution')
}
</script>

<template>
  <div
    class="comparison-item"
    :class="{
      expanded: isExpanded,
      resolved: isResolved
    }"
  >
    <!-- Item Header -->
    <div class="item-header" @click="handleToggleExpand">
      <div class="item-info">
        <div class="key-path">{{ item.key_path }}</div>
        <div class="meta-info">
          <span class="namespace">{{ item.namespace_code }}</span>
          <span class="language-badge">{{ item.language.toUpperCase() }}</span>
          <span
            v-if="item.similarity < 1"
            class="similarity"
            :class="similarityColor"
          >
            {{ Math.round(item.similarity * 100) }}% {{ $t('panel.i18n.similar') }}
          </span>
        </div>
      </div>

      <div class="item-action">
        <span class="action-icon">{{ actionIcon }}</span>
        <span v-if="isResolved" class="resolved-badge">
          ✓ {{ $t('panel.i18n.resolved') }}
        </span>
        <span v-else-if="item.resolution_status === 'PENDING'" class="pending-badge">
          ⏳ {{ $t('panel.i18n.pending') }}
        </span>
      </div>

      <button class="expand-toggle">
        {{ isExpanded ? '▼' : '▶' }}
      </button>
    </div>

    <!-- Item Details (Expanded) -->
    <div v-if="isExpanded" class="item-details">
      <!-- Values Comparison -->
      <div class="values-comparison">
        <div class="value-column">
          <div class="column-header">
            📱 {{ $t('panel.i18n.frontend_value') }}
          </div>
          <div v-if="item.frontend_value" class="value-content">
            {{ item.frontend_value }}
          </div>
          <div v-else class="value-empty">
            {{ $t('panel.i18n.no_value') }}
          </div>
        </div>

        <div class="value-column">
          <div class="column-header">
            💾 {{ $t('panel.i18n.database_value') }}
          </div>
          <div v-if="item.database_value" class="value-content">
            {{ item.database_value }}
          </div>
          <div v-else class="value-empty">
            {{ $t('panel.i18n.no_value') }}
          </div>
        </div>
      </div>

      <!-- Conflict Info -->
      <div v-if="item.conflict_reason" class="conflict-info">
        <span class="conflict-icon">⚠️</span>
        <div class="conflict-details">
          <div class="conflict-title">{{ $t('panel.i18n.conflict') }}</div>
          <div class="conflict-reason">{{ item.conflict_reason }}</div>
        </div>
      </div>

      <!-- Resolution Actions (MANUAL mode only) -->
      <div v-if="selectedMode === 'MANUAL'" class="resolution-actions">
        <div class="actions-label">{{ $t('panel.i18n.select_action') }}:</div>
        <div class="action-buttons">
          <button
            class="action-button"
            @click="handleSetResolution('ADD')"
          >
            ➕ {{ $t('panel.i18n.action_add') }}
          </button>
          <button
            class="action-button"
            @click="handleSetResolution('UPDATE')"
          >
            ✏️ {{ $t('panel.i18n.action_update') }}
          </button>
          <button
            class="action-button"
            @click="handleSetResolution('DELETE')"
          >
            🗑️ {{ $t('panel.i18n.action_delete') }}
          </button>
          <button
            class="action-button"
            @click="handleSetResolution('SKIP')"
          >
            ⏭️ {{ $t('panel.i18n.action_skip') }}
          </button>
          <button
            v-if="isResolved"
            class="action-button clear"
            @click="handleClearResolution"
          >
            ✗ {{ $t('panel.i18n.clear') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.comparison-item {
  border: 1px solid var(--color-border, #e0e0e0);
  border-radius: 6px;
  background: white;
  margin-bottom: 12px;
  transition: all 0.2s ease;
}

.comparison-item.expanded {
  border-color: var(--color-primary, #2196f3);
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.1);
}

.comparison-item.resolved {
  background-color: var(--color-success-bg, #f1f8e9);
  border-color: var(--color-success, #4caf50);
}

/* Item Header */
.item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
}

.item-header:hover {
  background-color: var(--color-hover-bg, #f9f9f9);
}

.item-info {
  flex: 1;
}

.key-path {
  font-weight: 600;
  color: var(--color-text-primary, #333);
  font-size: 14px;
  margin-bottom: 6px;
  word-break: break-word;
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.namespace,
.language-badge {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 3px;
  background-color: var(--color-surface, #f5f5f5);
  color: var(--color-text-secondary, #666);
}

.language-badge {
  font-weight: 600;
}

.similarity {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 500;
}

.similarity-high {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.similarity-medium {
  background-color: #fff3e0;
  color: #f57c00;
}

.similarity-low {
  background-color: #ffebee;
  color: #c62828;
}

/* Item Action */
.item-action {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
}

.action-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.resolved-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 3px;
  background-color: var(--color-success-bg, #f1f8e9);
  color: var(--color-success, #4caf50);
  font-weight: 600;
}

.pending-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 3px;
  background-color: var(--color-warning-bg, #fff3e0);
  color: var(--color-warning, #ff9800);
  font-weight: 600;
}

/* Expand Toggle */
.expand-toggle {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text-secondary, #666);
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.expand-toggle:hover {
  color: var(--color-primary, #2196f3);
}

/* Item Details */
.item-details {
  border-top: 1px solid var(--color-border, #e0e0e0);
  padding: 16px;
  background-color: var(--color-surface, #f5f5f5);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Values Comparison */
.values-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.value-column {
  background: white;
  border: 1px solid var(--color-border, #e0e0e0);
  border-radius: 4px;
  overflow: hidden;
}

.column-header {
  padding: 8px 12px;
  background-color: var(--color-surface, #f5f5f5);
  border-bottom: 1px solid var(--color-border, #e0e0e0);
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary, #666);
}

.value-content {
  padding: 12px;
  font-size: 13px;
  color: var(--color-text-primary, #333);
  word-break: break-word;
  white-space: pre-wrap;
}

.value-empty {
  padding: 12px;
  font-size: 13px;
  color: var(--color-text-secondary, #666);
  font-style: italic;
}

/* Conflict Info */
.conflict-info {
  display: flex;
  gap: 12px;
  padding: 12px;
  background-color: var(--color-warning-bg, #fff3e0);
  border: 1px solid var(--color-warning, #ff9800);
  border-radius: 4px;
}

.conflict-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.conflict-details {
  flex: 1;
}

.conflict-title {
  font-weight: 600;
  font-size: 13px;
  color: var(--color-warning, #ff9800);
  margin-bottom: 4px;
}

.conflict-reason {
  font-size: 13px;
  color: var(--color-text-primary, #333);
}

/* Resolution Actions */
.resolution-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.actions-label {
  font-weight: 600;
  font-size: 13px;
  color: var(--color-text-primary, #333);
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.action-button {
  padding: 8px 12px;
  border: 1px solid var(--color-border, #e0e0e0);
  background-color: white;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--color-text-primary, #333);
}

.action-button:hover {
  border-color: var(--color-primary, #2196f3);
  background-color: var(--color-primary-light, #e3f2fd);
  color: var(--color-primary, #2196f3);
}

.action-button.clear {
  border-color: var(--color-error, #dc2626);
  color: var(--color-error, #dc2626);
}

.action-button.clear:hover {
  background-color: var(--color-error-bg, #ffebee);
}

/* Responsive */
@media (max-width: 768px) {
  .item-header {
    flex-wrap: wrap;
    gap: 8px;
  }

  .values-comparison {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-button {
    width: 100%;
  }
}
</style>
