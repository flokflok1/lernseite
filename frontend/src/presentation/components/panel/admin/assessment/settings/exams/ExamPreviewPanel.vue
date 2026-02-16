<!--
  ExamPreviewPanel - Preview and edit generated exam

  Displays the generated exam with questions, allows editing,
  regenerating, and saving.
-->

<template>
  <div v-if="exam" class="exam-preview">
    <div class="preview-header">
      <div class="preview-title">
        <span class="preview-icon">📋</span>
        <div>
          <h3>{{ exam.title || 'Generierte Prüfung' }}</h3>
          <p>{{ exam.questions?.length || 0 }} Fragen • {{ exam.duration || 30 }} Minuten</p>
        </div>
      </div>
      <div class="preview-actions">
        <button @click="$emit('edit')" class="action-btn">✏️ Bearbeiten</button>
        <button @click="$emit('regenerate')" class="action-btn">🔄 Neu generieren</button>
        <button @click="$emit('save')" class="action-btn primary">💾 Speichern</button>
        <button @click="$emit('close')" class="action-btn">✕ Schließen</button>
      </div>
    </div>

    <!-- Questions List -->
    <div class="questions-list">
      <div
        v-for="(question, qIdx) in exam.questions"
        :key="qIdx"
        class="question-card"
        :class="{ expanded: expandedQuestions.has(qIdx) }"
      >
        <div class="question-header" @click="toggleQuestion(qIdx)">
          <span class="question-number">{{ qIdx + 1 }}</span>
          <span class="question-type" :class="question.type">{{ getQuestionTypeLabel(question.type) }}</span>
          <span class="question-text">{{ truncateText(question.question, 80) }}</span>
          <span class="question-points">{{ question.points || 1 }} Pkt.</span>
          <svg class="expand-icon" :class="{ rotated: expandedQuestions.has(qIdx) }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>

        <!-- Expanded Content -->
        <div v-if="expandedQuestions.has(qIdx)" class="question-body">
          <div class="question-full-text">{{ question.question }}</div>

          <!-- MC Options -->
          <div v-if="question.type === 'mc' && question.options" class="mc-options">
            <div
              v-for="(opt, oIdx) in question.options"
              :key="oIdx"
              class="mc-option"
              :class="{ correct: isCorrectAnswer(question, oIdx) }"
            >
              <span class="option-letter">{{ String.fromCharCode(65 + oIdx) }}</span>
              <span class="option-text">{{ opt }}</span>
              <span v-if="isCorrectAnswer(question, oIdx)" class="correct-badge">✓</span>
            </div>
          </div>

          <!-- Free Text Answer -->
          <div v-if="question.type === 'free_text' && question.sample_answer" class="sample-answer">
            <strong>Musterantwort:</strong>
            <p>{{ question.sample_answer }}</p>
          </div>

          <!-- Source Reference -->
          <div v-if="question.source_file" class="question-source">
            📄 Quelle: {{ question.source_file }}
          </div>

          <!-- Question Actions -->
          <div class="question-actions">
            <button @click="$emit('edit-question', qIdx)" class="q-action-btn">✏️ Bearbeiten</button>
            <button @click="$emit('regenerate-question', qIdx)" class="q-action-btn">🔄 Neu</button>
            <button @click="$emit('delete-question', qIdx)" class="q-action-btn danger">🗑️ Löschen</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Types
interface Question {
  type: 'mc' | 'free_text' | 'matching' | 'fill_blank'
  question: string
  options?: string[]
  correct_answer?: number | number[] | string
  sample_answer?: string
  points?: number
  difficulty?: string
  source_file?: string
}

interface Exam {
  exam_id?: string
  title: string
  description?: string
  duration: number
  questions: Question[]
  chapter_id?: string
  created_at?: string
}

// Props
defineProps<{
  exam: Exam | null
}>()

// Emits
defineEmits<{
  (e: 'edit'): void
  (e: 'regenerate'): void
  (e: 'save'): void
  (e: 'close'): void
  (e: 'edit-question', index: number): void
  (e: 'regenerate-question', index: number): void
  (e: 'delete-question', index: number): void
}>()

// Local state
const expandedQuestions = ref<Set<number>>(new Set())

// Methods
function toggleQuestion(idx: number) {
  if (expandedQuestions.value.has(idx)) {
    expandedQuestions.value.delete(idx)
  } else {
    expandedQuestions.value.add(idx)
  }
}

function getQuestionTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    mc: 'Multiple Choice',
    free_text: 'Freitext',
    matching: 'Zuordnung',
    fill_blank: 'Lückentext'
  }
  return labels[type] || type
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

function isCorrectAnswer(question: Question, optionIndex: number): boolean {
  const correct = question.correct_answer
  if (typeof correct === 'number') {
    return correct === optionIndex
  }
  if (Array.isArray(correct)) {
    return correct.includes(optionIndex)
  }
  return false
}
</script>

<style scoped>
.exam-preview {
  background: var(--color-surface);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  margin-top: 1rem;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.preview-icon {
  font-size: 1.5rem;
}

.preview-title h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.preview-title p {
  margin: 0;
  font-size: 0.75rem;
  opacity: 0.8;
}

.preview-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 0.375rem;
  color: white;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.action-btn.primary {
  background: #22c55e;
}

.action-btn.primary:hover {
  background: #16a34a;
}

/* Questions List */
.questions-list {
  max-height: 500px;
  overflow-y: auto;
  padding: 0.75rem;
}

.question-card {
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  overflow: hidden;
}

.question-card:last-child {
  margin-bottom: 0;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  cursor: pointer;
  transition: background 0.15s;
}

.question-header:hover {
  background: var(--color-surface-secondary);
}

.question-number {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
}

.question-type {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 500;
  text-transform: uppercase;
}

.question-type.mc {
  background: #dbeafe;
  color: #1d4ed8;
}

.question-type.free_text {
  background: #dcfce7;
  color: #166534;
}

.question-type.matching {
  background: #fef3c7;
  color: #92400e;
}

.question-type.fill_blank {
  background: #f3e8ff;
  color: #7c3aed;
}

.question-text {
  flex: 1;
  font-size: 0.8125rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.question-points {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  white-space: nowrap;
}

.expand-icon {
  width: 16px;
  height: 16px;
  color: var(--color-text-tertiary);
  transition: transform 0.2s;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

/* Question Body */
.question-body {
  padding: 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.question-full-text {
  font-size: 0.875rem;
  line-height: 1.6;
  margin-bottom: 1rem;
}

/* MC Options */
.mc-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.mc-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
}

.mc-option.correct {
  background: #dcfce7;
  border-color: #22c55e;
}

.option-letter {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-secondary);
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
}

.mc-option.correct .option-letter {
  background: #22c55e;
  color: white;
}

.option-text {
  flex: 1;
  font-size: 0.8125rem;
}

.correct-badge {
  color: #22c55e;
  font-weight: 600;
}

/* Sample Answer */
.sample-answer {
  padding: 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  margin-bottom: 1rem;
}

.sample-answer strong {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.25rem;
}

.sample-answer p {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.5;
}

/* Source Reference */
.question-source {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  margin-bottom: 1rem;
}

/* Question Actions */
.question-actions {
  display: flex;
  gap: 0.5rem;
}

.q-action-btn {
  padding: 0.375rem 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s;
}

.q-action-btn:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.q-action-btn.danger:hover {
  border-color: #ef4444;
  background: #fef2f2;
  color: #ef4444;
}
</style>
