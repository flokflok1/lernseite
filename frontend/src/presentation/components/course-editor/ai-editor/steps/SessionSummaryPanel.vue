/**
 * SessionSummaryPanel.vue
 *
 * Step 3: Review & Confirmation
 * - Display PDF analysis summary
 * - Show AI recommendations
 * - Confirm session creation
 */

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { PDFUploadResponse, SourceType } from '@/application/services/api/learning'

interface Props {
  sourceType: SourceType | null
  uploadedFile: File | null
  pdfAnalysis: PDFUploadResponse | null
  isLoading: boolean
  error?: string | null
}

interface Emits {
  (e: 'confirm'): void
  (e: 'back'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const { t } = useI18n()

// Computed
const hasValidData = computed(() => {
  return props.sourceType && (props.pdfAnalysis || props.sourceType !== 'pdf')
})

const recommendedChapters = computed(() => {
  return props.pdfAnalysis?.recommendations?.suggested_chapters || 1
})

const lessonsPerChapter = computed(() => {
  return props.pdfAnalysis?.recommendations?.suggested_lessons_per_chapter || 3
})

const estimatedTotalLessons = computed(() => {
  return recommendedChapters.value * lessonsPerChapter.value
})

const learningMethods = computed(() => {
  const methodIds = props.pdfAnalysis?.recommendations?.suitable_methods || []
  const methodNames: Record<number, string> = {
    0: 'Theory (LM00)',
    1: 'Explanation (LM01)',
    2: 'Tutorial (LM02)',
    3: 'Interactive Lesson (LM03)',
    4: 'Case Study (LM04)',
    5: 'Exercise (LM05)',
    6: 'Simulation (LM06)',
    7: 'Project (LM07)',
    8: 'Lab Work (LM08)',
    9: 'Quiz (LM09)',
    10: 'Exam (LM10)',
    11: 'Assessment (LM11)'
  }
  return methodIds.map(id => methodNames[id] || `Learning Method ${id}`)
})

const complexityLevel = computed(() => {
  return props.pdfAnalysis?.recommendations?.complexity_level || 'medium'
})

const estimatedTimeMinutes = computed(() => {
  return props.pdfAnalysis?.estimated_reading_time || 0
})

const estimatedTimeFormatted = computed(() => {
  const hours = Math.floor(estimatedTimeMinutes.value / 60)
  const mins = estimatedTimeMinutes.value % 60
  if (hours > 0) {
    return `${hours}h ${mins}min`
  }
  return `${mins}min`
})
</script>

<template>
  <div class="session-summary-panel">
    <h3>{{ $t('courses.editor.reviewSession') }}</h3>
    <p class="description">{{ $t('courses.editor.reviewDescription') }}</p>

    <!-- Summary Cards -->
    <div class="summary-grid">
      <!-- Source Info -->
      <div class="summary-card">
        <div class="card-header">📚 {{ $t('courses.editor.sourceInformation') }}</div>
        <div class="card-content">
          <div v-if="sourceType === 'pdf'" class="info-row">
            <span class="label">{{ $t('courses.editor.fileName') }}:</span>
            <span class="value">{{ uploadedFile?.name }}</span>
          </div>
          <div v-if="sourceType === 'pdf'" class="info-row">
            <span class="label">{{ $t('courses.editor.fileSize') }}:</span>
            <span class="value">{{ (uploadedFile?.size! / 1024 / 1024).toFixed(2) }} MB</span>
          </div>
          <div class="info-row">
            <span class="label">{{ $t('courses.editor.sourceType') }}:</span>
            <span class="value capitalize">{{ sourceType }}</span>
          </div>
        </div>
      </div>

      <!-- Content Analysis (if Document) -->
      <div v-if="sourceType === 'pdf' && pdfAnalysis" class="summary-card">
        <div class="card-header">🔍 {{ $t('courses.editor.documentAnalysis') }}</div>
        <div class="card-content">
          <div class="info-row">
            <span class="label">{{ $t('courses.editor.wordCount') }}:</span>
            <span class="value">{{ pdfAnalysis.word_count?.toLocaleString() || 0 }}</span>
          </div>
          <div class="info-row">
            <span class="label">{{ $t('courses.editor.paragraphCount') }}:</span>
            <span class="value">{{ pdfAnalysis.structure_analysis?.paragraph_count || 0 }}</span>
          </div>
          <div class="info-row">
            <span class="label">{{ $t('courses.editor.estimatedReadingTime') }}:</span>
            <span class="value">{{ estimatedTimeFormatted }}</span>
          </div>
          <div class="info-row">
            <span class="label">{{ $t('courses.editor.complexity') }}:</span>
            <span class="value capitalize">{{ complexityLevel }}</span>
          </div>
        </div>
      </div>

      <!-- AI Recommendations -->
      <div v-if="sourceType === 'pdf' && pdfAnalysis" class="summary-card">
        <div class="card-header">⚡ {{ $t('courses.editor.aiRecommendations') }}</div>
        <div class="card-content">
          <div class="info-row">
            <span class="label">{{ $t('courses.editor.suggestedChapters') }}:</span>
            <span class="value">{{ recommendedChapters }}</span>
          </div>
          <div class="info-row">
            <span class="label">{{ $t('courses.editor.lessonsPerChapter') }}:</span>
            <span class="value">{{ lessonsPerChapter }}</span>
          </div>
          <div class="info-row">
            <span class="label">{{ $t('courses.editor.estimatedTotal') }}:</span>
            <span class="value">{{ estimatedTotalLessons }} {{ $t('courses.editor.lessons') }}</span>
          </div>
        </div>
      </div>

      <!-- Suitable Learning Methods -->
      <div v-if="sourceType === 'pdf' && learningMethods.length > 0" class="summary-card">
        <div class="card-header">📖 {{ $t('courses.editor.suitableLearningMethods') }}</div>
        <div class="card-content">
          <div class="method-tags">
            <span v-for="method in learningMethods" :key="method" class="method-tag">
              {{ method }}
            </span>
          </div>
        </div>
      </div>

      <!-- Key Topics (if available) -->
      <div v-if="sourceType === 'pdf' && pdfAnalysis?.structure_analysis?.key_topics?.length" class="summary-card">
        <div class="card-header">🏷️ {{ $t('courses.editor.keyTopics') }}</div>
        <div class="card-content">
          <div class="topic-list">
            <div v-for="topic in pdfAnalysis.structure_analysis.key_topics.slice(0, 5)" :key="topic.topic" class="topic-item">
              <span class="topic-name">{{ topic.topic }}</span>
              <span class="topic-count">({{ topic.count }})</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Next Steps Info -->
    <div class="next-steps-box">
      <div class="next-steps-header">📝 {{ $t('courses.editor.whatNext') }}</div>
      <ol class="next-steps-list">
        <li>{{ $t('courses.editor.nextStep1') }}</li>
        <li>{{ $t('courses.editor.nextStep2') }}</li>
        <li>{{ $t('courses.editor.nextStep3') }}</li>
      </ol>
    </div>

    <!-- Action Buttons -->
    <div class="panel-actions">
      <button
        class="btn btn-secondary"
        @click="$emit('back')"
        :disabled="isLoading"
      >
        {{ $t('common.back') }}
      </button>
      <button
        class="btn btn-primary"
        @click="$emit('confirm')"
        :disabled="!hasValidData || isLoading"
      >
        <span v-if="isLoading">⏳ {{ $t('courses.editor.creating') }}</span>
        <span v-else>{{ $t('courses.editor.createSession') }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.session-summary-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

/* Summary Grid */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.summary-card {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: white;
  overflow: hidden;
}

.card-header {
  padding: 12px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  font-weight: 500;
  font-size: 13px;
  color: #333;
}

.card-content {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  gap: 12px;
}

.label {
  font-weight: 500;
  color: #666;
  flex-shrink: 0;
}

.value {
  color: #333;
  text-align: right;
  flex-shrink: 0;
  max-width: 60%;
  word-break: break-word;
}

.capitalize {
  text-transform: capitalize;
}

/* Method Tags */
.method-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.method-tag {
  display: inline-block;
  padding: 4px 10px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

/* Topic List */
.topic-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.topic-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
}

.topic-item:last-child {
  border-bottom: none;
}

.topic-name {
  color: #333;
  flex: 1;
}

.topic-count {
  color: #999;
  font-size: 11px;
  margin-left: 8px;
}

/* Next Steps */
.next-steps-box {
  padding: 16px;
  background: #f0f7ff;
  border: 1px solid #b3e5fc;
  border-radius: 6px;
}

.next-steps-header {
  font-size: 13px;
  font-weight: 600;
  color: #0277bd;
  margin-bottom: 12px;
}

.next-steps-list {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: #555;
  line-height: 1.6;
}

.next-steps-list li {
  margin-bottom: 6px;
}

.next-steps-list li:last-child {
  margin-bottom: 0;
}

/* Actions */
.panel-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1976d2;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover:not(:disabled) {
  background: #eeeeee;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .session-summary-panel {
    padding: 16px;
    gap: 16px;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .panel-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .info-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .value {
    text-align: left;
    max-width: 100%;
  }
}
</style>
