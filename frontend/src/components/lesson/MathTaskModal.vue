<!--
  Math Task Modal - IHK Prüfungsstil

  Features:
  - Aufgabe wird angezeigt, Lösung ist versteckt
  - User muss erst selbst rechnen und Antwort eingeben
  - Nach Eingabe: Lösung prüfen oder aufdecken
  - Lösungsweg zum Aufklappen (nach Antwort)
  - Dark Mode Support
-->

<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content">
        <!-- Header -->
        <div class="modal-header">
          <div class="flex items-center gap-3">
            <span class="text-2xl">🧮</span>
            <div>
              <h2 class="modal-title">
                {{ taskData.title || 'Rechenaufgabe' }}
              </h2>
              <p v-if="methodName" class="modal-subtitle">
                {{ methodName }}
              </p>
            </div>
          </div>
          <button @click="$emit('close')" class="close-btn">
            ✕
          </button>
        </div>

        <!-- Body -->
        <div class="modal-body">
          <!-- Task Counter -->
          <div v-if="taskNumber" class="task-counter">
            Aufgabe {{ taskNumber }} von {{ totalTasks }}
          </div>

          <!-- Question Section -->
          <div class="task-section question-section">
            <div class="section-icon">📝</div>
            <div class="section-content">
              <h3 class="section-title">AUFGABENSTELLUNG</h3>
              <p class="question-text">{{ taskData.question }}</p>
            </div>
          </div>

          <!-- Answer Input Section (IHK Style) -->
          <div class="answer-section">
            <div class="answer-header">
              <span class="answer-icon">✏️</span>
              <label class="answer-label">Deine Antwort:</label>
            </div>

            <div class="answer-input-wrapper">
              <input
                v-model="userAnswer"
                type="text"
                class="answer-input"
                :placeholder="getPlaceholder()"
                :disabled="hasSubmitted"
                @keyup.enter="checkAnswer"
              />

              <button
                v-if="!hasSubmitted"
                @click="checkAnswer"
                class="check-btn"
                :disabled="!userAnswer.trim()"
              >
                Antwort prüfen
              </button>
            </div>

            <!-- Answer Feedback -->
            <div v-if="hasSubmitted" class="answer-feedback" :class="feedbackClass">
              <span class="feedback-icon">{{ isCorrect ? '✅' : '❌' }}</span>
              <span class="feedback-text">
                {{ isCorrect ? 'Richtig!' : 'Leider falsch. Schau dir die Lösung an.' }}
              </span>
            </div>
          </div>

          <!-- Solution Section (Hidden until answered or revealed) -->
          <div class="task-section solution-section" :class="{ 'locked': !canShowSolution }">
            <button
              @click="toggleSolution"
              class="toggle-btn"
              :disabled="!canShowSolution && !hasSubmitted"
            >
              <span class="section-icon">{{ canShowSolution ? '✅' : '🔒' }}</span>
              <span class="section-title">LÖSUNG</span>
              <span v-if="!canShowSolution && !hasSubmitted" class="lock-hint">
                (Erst Antwort eingeben)
              </span>
              <span class="toggle-icon" :class="{ rotated: showSolution }">▼</span>
            </button>

            <Transition name="slide">
              <div v-if="showSolution && canShowSolution" class="solution-content">
                <div class="solution-box" :class="{ 'correct': isCorrect, 'incorrect': hasSubmitted && !isCorrect }">
                  <strong>{{ taskData.solution }}</strong>
                </div>
              </div>
            </Transition>
          </div>

          <!-- Steps Section (Hidden until answered) -->
          <div class="task-section steps-section" :class="{ 'locked': !canShowSolution }">
            <button
              @click="toggleSteps"
              class="toggle-btn"
              :disabled="!canShowSolution"
            >
              <span class="section-icon">📋</span>
              <span class="section-title">LÖSUNGSWEG ({{ taskData.steps?.length || 0 }} Schritte)</span>
              <span class="toggle-icon" :class="{ rotated: showSteps }">▼</span>
            </button>

            <Transition name="slide">
              <div v-if="showSteps && canShowSolution" class="steps-content">
                <div
                  v-for="(step, index) in taskData.steps"
                  :key="index"
                  class="step-item"
                >
                  <div class="step-number">{{ step.step || index + 1 }}</div>
                  <div class="step-details">
                    <p class="step-description">{{ step.description }}</p>
                    <code v-if="step.calculation" class="step-calculation">
                      {{ step.calculation }}
                    </code>
                  </div>
                </div>
              </div>
            </Transition>
          </div>

          <!-- Explanation Section -->
          <div v-if="taskData.explanation && canShowSolution" class="task-section explanation-section">
            <button @click="showExplanation = !showExplanation" class="toggle-btn">
              <span class="section-icon">💡</span>
              <span class="section-title">ERKLÄRUNG</span>
              <span class="toggle-icon" :class="{ rotated: showExplanation }">▼</span>
            </button>

            <Transition name="slide">
              <div v-if="showExplanation" class="explanation-content">
                <p>{{ taskData.explanation }}</p>
              </div>
            </Transition>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <div class="footer-left">
            <span class="token-info">
              Token verbraucht: {{ tokensUsed }}
            </span>
          </div>
          <div class="footer-buttons">
            <button
              v-if="hasSubmitted"
              @click="resetTask"
              class="btn-outline"
            >
              🔄 Nochmal versuchen
            </button>
            <button @click="$emit('newTask')" class="btn-secondary">
              ➡️ Neue Aufgabe
            </button>
            <button @click="$emit('close')" class="btn-primary">
              Schließen
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface TaskStep {
  step?: number
  description: string
  calculation?: string
}

interface TaskData {
  title?: string
  question: string
  steps?: TaskStep[]
  solution: string
  explanation?: string
}

interface Props {
  taskData: TaskData
  methodName?: string
  tokensUsed?: number
  showInput?: boolean
  taskNumber?: number
  totalTasks?: number
}

const props = withDefaults(defineProps<Props>(), {
  tokensUsed: 0,
  showInput: true,
  taskNumber: 0,
  totalTasks: 0
})

defineEmits(['close', 'newTask'])

// State
const showSteps = ref(false)
const showSolution = ref(false)
const showExplanation = ref(false)
const userAnswer = ref('')
const hasSubmitted = ref(false)
const isCorrect = ref(false)

// Computed
const canShowSolution = computed(() => hasSubmitted.value)

const feedbackClass = computed(() => ({
  'feedback-correct': isCorrect.value,
  'feedback-incorrect': !isCorrect.value
}))

// Methods
const getPlaceholder = () => {
  // Analyze solution to suggest format
  const solution = props.taskData.solution?.toLowerCase() || ''
  if (solution.includes('euro') || solution.includes('€')) {
    return 'z.B. 2400 Euro oder 2400 €'
  }
  if (solution.includes('%')) {
    return 'z.B. 15% oder 15 Prozent'
  }
  return 'Deine Antwort eingeben...'
}

const normalizeAnswer = (answer: string): string => {
  return answer
    .toLowerCase()
    .replace(/\s+/g, '')
    .replace(/euro/g, '€')
    .replace(/prozent/g, '%')
    .replace(/,/g, '.')
    .replace(/[^\d.€%]/g, '')
}

const checkAnswer = () => {
  if (!userAnswer.value.trim()) return

  hasSubmitted.value = true

  // Normalize both answers for comparison
  const userNormalized = normalizeAnswer(userAnswer.value)
  const solutionNormalized = normalizeAnswer(props.taskData.solution)

  // Extract numbers for comparison
  const userNumbers = userNormalized.match(/[\d.]+/g) || []
  const solutionNumbers = solutionNormalized.match(/[\d.]+/g) || []

  // Check if main number matches
  if (userNumbers.length > 0 && solutionNumbers.length > 0) {
    const userNum = parseFloat(userNumbers[0])
    const solutionNum = parseFloat(solutionNumbers[0])
    // Allow small tolerance for rounding
    isCorrect.value = Math.abs(userNum - solutionNum) < 0.01
  } else {
    // Fallback to string comparison
    isCorrect.value = userNormalized === solutionNormalized
  }

  // Auto-show solution after submission
  showSolution.value = true
}

const toggleSolution = () => {
  if (canShowSolution.value) {
    showSolution.value = !showSolution.value
  }
}

const toggleSteps = () => {
  if (canShowSolution.value) {
    showSteps.value = !showSteps.value
  }
}

const resetTask = () => {
  userAnswer.value = ''
  hasSubmitted.value = false
  isCorrect.value = false
  showSolution.value = false
  showSteps.value = false
  showExplanation.value = false
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  backdrop-filter: blur(4px);
}

.modal-content {
  background-color: var(--color-surface, #ffffff);
  border-radius: 1rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--color-border, #e5e7eb);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background: linear-gradient(135deg, var(--color-primary-50, #eff6ff) 0%, var(--color-surface, #ffffff) 100%);
}

:root.dark .modal-header {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, var(--color-surface, #1f2937) 100%);
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
}

.modal-subtitle {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
}

.close-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--color-text-secondary, #6b7280);
  transition: all 0.2s;
  font-size: 1.25rem;
}

.close-btn:hover {
  background-color: var(--color-background, #f3f4f6);
  color: var(--color-text-primary, #111827);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.task-counter {
  text-align: center;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 1rem;
  padding: 0.5rem;
  background-color: var(--color-background, #f9fafb);
  border-radius: 0.5rem;
}

.task-section {
  margin-bottom: 1rem;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.75rem;
  overflow: hidden;
}

.task-section.locked {
  opacity: 0.6;
}

.question-section {
  display: flex;
  gap: 1rem;
  padding: 1.25rem;
  background-color: var(--color-primary-50, #eff6ff);
  border-color: var(--color-primary-200, #bfdbfe);
}

:root.dark .question-section {
  background-color: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
}

.section-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.section-content {
  flex: 1;
}

.section-title {
  font-weight: 600;
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.question-text {
  font-size: 1rem;
  color: var(--color-text-primary, #111827);
  line-height: 1.6;
}

/* Answer Section */
.answer-section {
  margin-bottom: 1rem;
  padding: 1.25rem;
  background-color: var(--color-surface, #ffffff);
  border: 2px solid var(--color-primary, #3b82f6);
  border-radius: 0.75rem;
}

.answer-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.answer-icon {
  font-size: 1.25rem;
}

.answer-label {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text-primary, #111827);
}

.answer-input-wrapper {
  display: flex;
  gap: 0.75rem;
}

.answer-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  background-color: var(--color-background, #f9fafb);
  color: var(--color-text-primary, #111827);
  font-size: 1rem;
  transition: all 0.2s;
}

.answer-input:focus {
  outline: none;
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.answer-input:disabled {
  background-color: var(--color-background, #f3f4f6);
  cursor: not-allowed;
}

.check-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, var(--color-primary, #3b82f6), #2563eb);
  color: white;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.2s;
  white-space: nowrap;
}

.check-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.check-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.answer-feedback {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
}

.feedback-correct {
  background-color: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.feedback-incorrect {
  background-color: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.feedback-icon {
  font-size: 1.25rem;
}

/* Toggle Buttons */
.toggle-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background-color: var(--color-background, #f9fafb);
  text-align: left;
  transition: background-color 0.2s;
  color: var(--color-text-primary, #111827);
}

.toggle-btn:hover:not(:disabled) {
  background-color: var(--color-surface-hover, rgba(0, 0, 0, 0.05));
}

.toggle-btn:disabled {
  cursor: not-allowed;
}

:root.dark .toggle-btn:hover:not(:disabled) {
  background-color: rgba(255, 255, 255, 0.05);
}

.lock-hint {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #9ca3af);
  font-style: italic;
}

.toggle-icon {
  margin-left: auto;
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  transition: transform 0.3s;
}

.toggle-icon.rotated {
  transform: rotate(180deg);
}

/* Solution Box */
.solution-content,
.steps-content,
.explanation-content {
  padding: 1.25rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-surface, #ffffff);
}

.solution-box {
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-radius: 0.5rem;
  font-size: 1.25rem;
  text-align: center;
  font-weight: 600;
}

.solution-box.correct {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.solution-box.incorrect {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

/* Steps */
.step-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px dashed var(--color-border, #e5e7eb);
}

.step-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.step-number {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--color-primary, #3b82f6), #2563eb);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.step-details {
  flex: 1;
}

.step-description {
  color: var(--color-text-primary, #111827);
  margin-bottom: 0.5rem;
}

.step-calculation {
  display: block;
  padding: 0.5rem 0.75rem;
  background-color: var(--color-background, #f3f4f6);
  border-radius: 0.5rem;
  font-family: 'Fira Code', 'Monaco', monospace;
  font-size: 0.875rem;
  color: var(--color-primary, #3b82f6);
  border: 1px solid var(--color-border, #e5e7eb);
}

.explanation-content p {
  color: var(--color-text-secondary, #6b7280);
  line-height: 1.7;
}

/* Footer */
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-background, #f9fafb);
}

.token-info {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
}

.footer-buttons {
  display: flex;
  gap: 0.75rem;
}

.btn-outline {
  padding: 0.625rem 1rem;
  border: 1px solid var(--color-border, #e5e7eb);
  color: var(--color-text-primary, #111827);
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s;
  background-color: transparent;
}

.btn-outline:hover {
  background-color: var(--color-surface, #ffffff);
  border-color: var(--color-text-secondary, #9ca3af);
}

.btn-secondary {
  padding: 0.625rem 1rem;
  border: 1px solid var(--color-border, #e5e7eb);
  color: var(--color-text-primary, #111827);
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s;
  background-color: var(--color-surface, #ffffff);
}

.btn-secondary:hover {
  background-color: var(--color-background, #f3f4f6);
  border-color: var(--color-text-secondary, #9ca3af);
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background: linear-gradient(135deg, var(--color-primary, #3b82f6), #2563eb);
  color: white;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* Slide Transition */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.slide-enter-to,
.slide-leave-from {
  max-height: 500px;
  opacity: 1;
}
</style>
