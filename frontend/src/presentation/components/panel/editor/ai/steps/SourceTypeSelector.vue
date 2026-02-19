/**
 * SourceTypeSelector.vue
 *
 * Step 1: Select source type for course creation
 * - PDF Upload
 * - Manual Entry
 * - From Template
 */

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

interface Props {
  isLoading: boolean
}

interface Emits {
  (e: 'select', type: 'pdf' | 'manual' | 'template'): void
}

defineProps<Props>()
defineEmits<Emits>()

const { t } = useI18n()
</script>

<template>
  <div class="source-type-selector">
    <h3>{{ $t('courses.editor.chooseSourceType') }}</h3>
    <p class="description">{{ $t('courses.editor.sourceTypeDescription') }}</p>

    <div class="source-options">
      <!-- PDF Upload Option -->
      <button
        class="source-option"
        @click="$emit('select', 'pdf')"
        :disabled="isLoading"
      >
        <div class="option-icon">📄</div>
        <div class="option-content">
          <h4>{{ $t('courses.editor.uploadPdf') }}</h4>
          <p>{{ $t('courses.editor.uploadPdfDescription') }}</p>
        </div>
        <div class="option-arrow">→</div>
      </button>

      <!-- Manual Entry Option -->
      <button
        class="source-option"
        @click="$emit('select', 'manual')"
        :disabled="isLoading"
      >
        <div class="option-icon">✍️</div>
        <div class="option-content">
          <h4>{{ $t('courses.editor.manualEntry') }}</h4>
          <p>{{ $t('courses.editor.manualEntryDescription') }}</p>
        </div>
        <div class="option-arrow">→</div>
      </button>

      <!-- Template Option -->
      <button
        class="source-option"
        @click="$emit('select', 'template')"
        :disabled="isLoading"
      >
        <div class="option-icon">📋</div>
        <div class="option-content">
          <h4>{{ $t('courses.editor.fromTemplate') }}</h4>
          <p>{{ $t('courses.editor.fromTemplateDescription') }}</p>
        </div>
        <div class="option-arrow">→</div>
      </button>
    </div>

    <!-- Info Box -->
    <div class="info-box">
      <span class="info-icon">ℹ️</span>
      <div>
        <strong>{{ $t('courses.editor.tip') }}</strong>
        <p>{{ $t('courses.editor.sourceTypeHint') }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.source-type-selector {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 20px;
}

h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.description {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.source-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.source-option {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.source-option:hover:not(:disabled) {
  border-color: #2196f3;
  background: #f5f9ff;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.1);
}

.source-option:active:not(:disabled) {
  transform: translateY(1px);
}

.source-option:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.option-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.option-content {
  flex: 1;
}

.option-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 4px 0;
}

.option-content p {
  font-size: 13px;
  color: #666;
  margin: 0;
  line-height: 1.4;
}

.option-arrow {
  font-size: 20px;
  color: #bbb;
  transition: all 0.2s;
}

.source-option:hover:not(:disabled) .option-arrow {
  color: #2196f3;
  transform: translateX(4px);
}

/* Info Box */
.info-box {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  border-radius: 4px;
}

.info-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.info-box strong {
  display: block;
  font-size: 13px;
  color: #1976d2;
  margin-bottom: 4px;
}

.info-box p {
  font-size: 13px;
  color: #555;
  margin: 0;
  line-height: 1.4;
}

/* Responsive */
@media (max-width: 768px) {
  .source-options {
    grid-template-columns: 1fr;
  }

  .source-option {
    padding: 16px;
    gap: 12px;
  }

  .option-icon {
    font-size: 24px;
  }
}
</style>
