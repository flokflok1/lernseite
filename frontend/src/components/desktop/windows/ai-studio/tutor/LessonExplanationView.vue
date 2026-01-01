<!--
  LessonExplanationView - Lesson Step-by-Step Explanation Component

  Displays step-by-step explanations with:
  - Interactive whiteboard animations
  - Calculator hints
  - TTS speech
  - Progress tracking
-->

<template>
  <div class="lesson-explanation-view">
    <!-- Header -->
    <div class="view-header">
      <div class="header-icon">📝</div>
      <div class="header-info">
        <h2>Schritt-für-Schritt Erklärung</h2>
        <p>{{ lesson?.title }} • {{ course?.title }}</p>
      </div>
      <div class="header-stats">
        <div class="stat">
          <span class="stat-value">{{ explanations.length }}</span>
          <span class="stat-label">Vorhanden</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ currentExplanation ? steps.length : 0 }}</span>
          <span class="stat-label">Schritte</span>
        </div>
      </div>
    </div>

    <!-- Three-Column Layout -->
    <div class="main-layout">
      <!-- Left: Explanation List -->
      <div class="list-panel">
        <div class="panel-header">
          <span class="panel-icon">📝</span>
          <span class="panel-title">Erklärungen</span>
          <button @click="loadExplanations" class="refresh-btn" title="Aktualisieren">🔄</button>
        </div>

        <!-- Loading -->
        <div v-if="isLoading" class="list-loading">
          <div class="spinner"></div>
          <span>Lade...</span>
        </div>

        <!-- Explanation List -->
        <div v-else class="content-list">
          <div v-if="explanations.length === 0" class="list-empty">
            <span class="empty-icon-small">📝</span>
            <p>Noch keine Erklärungen</p>
          </div>
          <div
            v-for="expl in explanations"
            :key="expl.explanationId"
            class="list-item"
            :class="{ active: selectedExplanationId === expl.explanationId }"
            @click="onSelectExplanation(expl.explanationId)"
          >
            <div class="item-icon">📖</div>
            <div class="item-info">
              <span class="item-name">{{ expl.title }}</span>
              <span class="item-meta">{{ expl.stepCount }} Schritte • {{ formatDate(expl.createdAt) }}</span>
            </div>
            <div class="item-actions">
              <button @click.stop="onDeleteExplanation(expl.explanationId)" class="item-btn danger" title="Löschen">🗑️</button>
            </div>
          </div>
        </div>

        <!-- Create New Button -->
        <div class="list-actions">
          <button @click="showCreateForm = true" class="create-btn">
            ✨ Neu erstellen
          </button>
        </div>
      </div>

      <!-- Middle: Explanation View -->
      <div class="detail-panel">
        <!-- Create Form -->
        <div v-if="showCreateForm" class="create-form">
          <div class="panel-header">
            <span class="panel-icon">✨</span>
            <span class="panel-title">Neue Erklärung</span>
          </div>

          <div class="form-content">
            <div class="form-section">
              <label>Stil:</label>
              <select v-model="selectedStyle" class="form-select">
                <option value="adhs">🎯 ADHS-freundlich (kurz & visuell)</option>
                <option value="detailed">📚 Ausführlich</option>
                <option value="short">📋 Kurz & Kompakt</option>
                <option value="exam_focus">🎓 Prüfungsfokus</option>
              </select>
            </div>

            <div class="form-section">
              <label>Stimme:</label>
              <select v-model="tts.selectedVoice.value" class="form-select">
                <option v-for="voice in tts.voices.value" :key="voice.id" :value="voice.id">
                  {{ voice.name }}
                </option>
              </select>
            </div>

            <div class="form-section">
              <label class="checkbox-label">
                <input type="checkbox" v-model="generateWithAudio" />
                Audio direkt mitgenerieren
              </label>
            </div>

            <button
              @click="generateNewExplanation"
              class="generate-btn"
              :disabled="isGenerating"
            >
              <span v-if="isGenerating">⏳ Generiere...</span>
              <span v-else>✨ Erklärung generieren</span>
            </button>

            <button @click="showCreateForm = false" class="cancel-btn">
              Abbrechen
            </button>
          </div>
        </div>

        <!-- Explanation View -->
        <div v-else-if="currentExplanation && steps.length > 0" class="explanation-view">
          <!-- Tutor Header -->
          <div class="tutor-header">
            <div class="tutor-avatar">
              <span class="avatar-emoji">👨‍🏫</span>
            </div>
            <div class="tutor-info">
              <span class="tutor-name">{{ currentExplanation.title || 'Tutor erklärt' }}</span>
              <span class="tutor-status" :class="{ speaking: tts.isSpeaking.value }">
                {{ tts.isSpeaking.value ? '🔊 Spricht...' : '💬 Bereit' }}
              </span>
            </div>
            <div class="tutor-controls">
              <select v-model="tts.selectedVoice.value" class="tts-select" title="Stimme">
                <option v-for="voice in tts.voices.value" :key="voice.id" :value="voice.id">
                  {{ voice.name }}
                </option>
              </select>
              <select v-model="tts.selectedModel.value" class="tts-select" title="TTS Modell">
                <option value="browser">🔊 Browser (Free)</option>
                <option value="tts-1">TTS-1</option>
                <option value="tts-1-hd">TTS-1-HD</option>
              </select>
              <button @click="tts.toggleTTS(currentStepData?.speech)" class="tts-btn" :class="{ active: tts.ttsEnabled.value }">
                {{ tts.ttsEnabled.value ? '🔊' : '🔇' }}
              </button>
            </div>
          </div>

          <!-- Progress -->
          <div class="progress-section">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${((currentStep + 1) / steps.length) * 100}%` }"></div>
            </div>
            <span class="progress-text">Schritt {{ currentStep + 1 }} von {{ steps.length }}</span>
            <button
              v-if="currentStep === 0 && !tts.isSpeaking.value && !isAnimating"
              @click="startExplanation"
              class="start-btn"
            >
              ▶️ Start
            </button>
            <div v-if="isAnimating" class="animating-indicator">
              <span class="spinner-small"></span>
              <span>Zeichne...</span>
            </div>
          </div>

          <!-- Main Area: Whiteboard + Step Card -->
          <div class="tutor-main-area">
            <!-- Whiteboard (if step has whiteboard actions) -->
            <div v-if="currentStepData?.whiteboardActions?.length" class="whiteboard-container" :class="{ animating: isAnimating }">
              <InteractiveWhiteboard
                ref="whiteboardRef"
                :width="480"
                :height="320"
                :show-controls="true"
                background-color="transparent"
                text-color="#ffffff"
                @action-complete="onWhiteboardComplete"
              />
            </div>

            <!-- Step Card -->
            <div class="step-card" v-if="currentStepData">
              <div class="step-header">
                <span class="step-badge">Schritt {{ currentStep + 1 }}</span>
                <h3 class="step-title">{{ currentStepData.title || `Schritt ${currentStep + 1}` }}</h3>
              </div>

              <!-- Speech Bubble -->
              <div class="speech-bubble">
                <p>{{ currentStepData.speech }}</p>
              </div>

              <!-- Calculator Hint -->
              <div v-if="currentStepData.calculator" class="calculator-box">
                <div class="calc-header">
                  <span class="calc-icon">🔢</span>
                  <span class="calc-label">Taschenrechner-Eingabe:</span>
                </div>
                <div class="calc-input">
                  <code>{{ currentStepData.calculator }}</code>
                </div>
                <div v-if="currentStepData.result" class="calc-result">
                  <span class="equals">=</span>
                  <span class="result-value">{{ currentStepData.result }}</span>
                </div>
              </div>

              <!-- Schema Preview (fallback) -->
              <div v-if="currentStepData.schema && !currentStepData.whiteboardActions?.length" class="schema-preview">
                <table>
                  <tr v-for="(row, idx) in currentStepData.schema" :key="idx" :class="{ highlighted: row.highlight }">
                    <td class="schema-name">{{ row.name }}</td>
                    <td class="schema-op">{{ row.operator }}</td>
                    <td class="schema-value">{{ row.value }}</td>
                  </tr>
                </table>
              </div>
            </div>
          </div>

          <!-- Navigation -->
          <div class="step-navigation">
            <button @click="prevStep" :disabled="currentStep === 0" class="nav-btn">
              ◀ Zurück
            </button>
            <div class="step-dots">
              <span
                v-for="(_, idx) in steps"
                :key="idx"
                class="step-dot"
                :class="{ active: idx === currentStep, completed: idx < currentStep }"
                @click="goToStep(idx)"
              ></span>
            </div>
            <button @click="nextStep" :disabled="currentStep >= steps.length - 1" class="nav-btn">
              Weiter ▶
            </button>
          </div>
        </div>

        <!-- No Selection -->
        <div v-else class="no-selection">
          <span class="empty-icon">📝</span>
          <p>Wähle eine Erklärung aus oder erstelle eine neue</p>
        </div>
      </div>

      <!-- Right: Settings Panel -->
      <div class="settings-panel">
        <div class="panel-header">
          <span class="panel-icon">⚙️</span>
          <span class="panel-title">Einstellungen</span>
        </div>

        <div class="settings-content">
          <!-- TTS Settings -->
          <div class="settings-section">
            <h4>🔊 Sprachausgabe</h4>
            <div class="setting-row">
              <label>Auto-Play:</label>
              <button @click="autoPlayEnabled = !autoPlayEnabled" class="toggle-btn" :class="{ active: autoPlayEnabled }">
                {{ autoPlayEnabled ? 'An' : 'Aus' }}
              </button>
            </div>
            <div class="setting-row">
              <label>Geschwindigkeit:</label>
              <select v-model="playbackSpeed" class="setting-select">
                <option value="0.75">Langsam</option>
                <option value="1">Normal</option>
                <option value="1.25">Schnell</option>
              </select>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="settings-section">
            <h4>⚡ Schnellaktionen</h4>
            <button v-if="currentExplanation" @click="regenerateExplanation" class="quick-action-btn">
              🔄 Neu generieren
            </button>
            <button v-if="currentExplanation" @click="downloadPDF" class="quick-action-btn">
              📄 Als PDF
            </button>
            <button v-if="currentExplanation" @click="shareExplanation" class="quick-action-btn">
              📤 Teilen
            </button>
          </div>

          <!-- Info -->
          <div v-if="currentExplanation" class="settings-section">
            <h4>ℹ️ Info</h4>
            <div class="info-item">
              <span class="info-label">Erstellt:</span>
              <span class="info-value">{{ formatDate(currentExplanation.createdAt) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Schritte:</span>
              <span class="info-value">{{ steps.length }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="error-banner">
      <span>⚠️ {{ error }}</span>
      <button @click="error = null">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useTheoryManagement, type LessonExplanation, type TeachingStep } from '@/composables/useTheoryManagement'
import { useTTS } from '@/composables/useTTS'
import http from '@/api/http'
import InteractiveWhiteboard from '@/components/tutor/InteractiveWhiteboard.vue'

// ============================================================================
// Props & Emits
// ============================================================================

interface Course {
  course_id: string
  title: string
}

interface Lesson {
  lesson_id: string
  title: string
}

const props = defineProps<{
  course: Course | null
  lesson: Lesson | null
}>()

const emit = defineEmits<{
  (e: 'generated', explanationId: string): void
  (e: 'deleted', explanationId: string): void
}>()

// ============================================================================
// Composables
// ============================================================================

const theoryMgmt = useTheoryManagement()
const tts = useTTS()

// ============================================================================
// Local State
// ============================================================================

const showCreateForm = ref(false)
const selectedStyle = ref('adhs')
const generateWithAudio = ref(false)
const isGenerating = ref(false)
const error = ref<string | null>(null)

// Explanation state
const selectedExplanationId = ref<string | null>(null)
const currentExplanation = ref<LessonExplanation | null>(null)
const steps = ref<TeachingStep[]>([])
const currentStep = ref(0)
const isAnimating = ref(false)

// Settings
const autoPlayEnabled = ref(true)
const playbackSpeed = ref('1')

// Refs
const whiteboardRef = ref<InstanceType<typeof InteractiveWhiteboard> | null>(null)

// ============================================================================
// Computed
// ============================================================================

const explanations = computed(() => theoryMgmt.lessonExplanations.value)
const isLoading = computed(() => theoryMgmt.isLoading.value)

const currentStepData = computed(() => {
  if (steps.value.length === 0 || currentStep.value >= steps.value.length) return null
  return steps.value[currentStep.value]
})

// ============================================================================
// Methods
// ============================================================================

async function loadExplanations() {
  if (props.lesson?.lesson_id) {
    await theoryMgmt.loadLessonExplanations(props.lesson.lesson_id)
  }
}

async function onSelectExplanation(explanationId: string) {
  selectedExplanationId.value = explanationId
  showCreateForm.value = false
  currentStep.value = 0

  try {
    const response = await http.get(`/lesson-explanations/${explanationId}`)
    if (response.data.success) {
      const data = response.data.data
      currentExplanation.value = {
        explanationId: data.explanation_id || explanationId,
        title: data.title || 'Erklärung',
        steps: data.steps || [],
        createdAt: data.created_at
      }
      steps.value = data.steps || []
    }
  } catch (err: any) {
    console.error('Failed to load explanation:', err)
    error.value = err.message || 'Fehler beim Laden'
  }
}

async function onDeleteExplanation(explanationId: string) {
  if (!confirm('Möchtest du diese Erklärung wirklich löschen?')) return

  const success = await theoryMgmt.deleteExplanation(explanationId)
  if (success) {
    if (selectedExplanationId.value === explanationId) {
      selectedExplanationId.value = null
      currentExplanation.value = null
      steps.value = []
    }
    emit('deleted', explanationId)
  }
}

async function generateNewExplanation() {
  if (!props.lesson?.lesson_id) return

  isGenerating.value = true
  error.value = null

  try {
    const response = await http.post('/admin/ai/generate-lesson-explanation', {
      lesson_id: props.lesson.lesson_id,
      style: selectedStyle.value,
      generate_tts: generateWithAudio.value,
      voice: tts.selectedVoice.value
    })

    if (response.data.success) {
      await loadExplanations()
      showCreateForm.value = false

      const newId = response.data.data?.explanation_id
      if (newId) {
        await onSelectExplanation(newId)
        emit('generated', newId)
      }
    } else {
      throw new Error(response.data.error?.message || 'Generierung fehlgeschlagen')
    }
  } catch (err: any) {
    console.error('Explanation generation failed:', err)
    error.value = err.response?.data?.error?.message || err.message
  } finally {
    isGenerating.value = false
  }
}

function startExplanation() {
  currentStep.value = 0
  if (tts.ttsEnabled.value && currentStepData.value?.speech) {
    tts.speak(currentStepData.value.speech)
  }
  // Trigger whiteboard animation if present
  if (currentStepData.value?.whiteboardActions?.length && whiteboardRef.value) {
    isAnimating.value = true
    whiteboardRef.value.runActions(currentStepData.value.whiteboardActions)
  }
}

function nextStep() {
  if (currentStep.value < steps.value.length - 1) {
    tts.stopSpeaking()
    currentStep.value++
    if (autoPlayEnabled.value && tts.ttsEnabled.value && currentStepData.value?.speech) {
      tts.speak(currentStepData.value.speech)
    }
    // Trigger whiteboard animation
    if (currentStepData.value?.whiteboardActions?.length && whiteboardRef.value) {
      isAnimating.value = true
      whiteboardRef.value.clear()
      whiteboardRef.value.runActions(currentStepData.value.whiteboardActions)
    }
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    tts.stopSpeaking()
    currentStep.value--
    if (currentStepData.value?.whiteboardActions?.length && whiteboardRef.value) {
      isAnimating.value = true
      whiteboardRef.value.clear()
      whiteboardRef.value.runActions(currentStepData.value.whiteboardActions)
    }
  }
}

function goToStep(idx: number) {
  if (idx >= 0 && idx < steps.value.length) {
    tts.stopSpeaking()
    currentStep.value = idx
  }
}

function onWhiteboardComplete() {
  isAnimating.value = false
}

function regenerateExplanation() {
  selectedStyle.value = 'adhs'
  showCreateForm.value = true
}

function downloadPDF() {
  // TODO: Implement PDF export
  alert('PDF Export wird noch implementiert')
}

function shareExplanation() {
  // TODO: Implement sharing
  alert('Teilen wird noch implementiert')
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit'
    })
  } catch {
    return dateStr
  }
}

// ============================================================================
// Watchers & Lifecycle
// ============================================================================

watch(() => props.lesson, async (newLesson) => {
  theoryMgmt.reset()
  selectedExplanationId.value = null
  currentExplanation.value = null
  steps.value = []
  currentStep.value = 0
  showCreateForm.value = false

  if (newLesson?.lesson_id) {
    await loadExplanations()
  }
}, { immediate: true })

onMounted(() => {
  tts.loadModels()
})
</script>

<style scoped>
.lesson-explanation-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
}

/* Header */
.view-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.header-icon {
  font-size: 2rem;
}

.header-info h2 {
  margin: 0;
  font-size: 1.25rem;
}

.header-info p {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.header-stats {
  margin-left: auto;
  display: flex;
  gap: 1.5rem;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

/* Main Layout */
.main-layout {
  display: grid;
  grid-template-columns: 260px 1fr 260px;
  gap: 1px;
  flex: 1;
  min-height: 0;
  background: var(--color-border);
}

/* Panels */
.list-panel,
.detail-panel,
.settings-panel {
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
}

.refresh-btn:hover {
  opacity: 1;
}

/* List Panel */
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
}

.create-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Create Form */
.create-form {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.form-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-section label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-select {
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: var(--color-surface);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.generate-btn {
  padding: 0.875rem;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-weight: 500;
  cursor: pointer;
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancel-btn {
  padding: 0.625rem;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  color: var(--color-text-secondary);
  cursor: pointer;
}

/* Explanation View */
.explanation-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tutor-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: white;
}

.tutor-avatar {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-emoji {
  font-size: 1.5rem;
}

.tutor-info {
  flex: 1;
}

.tutor-name {
  display: block;
  font-weight: 600;
  font-size: 0.9375rem;
}

.tutor-status {
  font-size: 0.8125rem;
  opacity: 0.8;
}

.tutor-status.speaking {
  color: #22c55e;
}

.tutor-controls {
  display: flex;
  gap: 0.5rem;
}

.tts-select {
  padding: 0.375rem 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.25rem;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 0.75rem;
}

.tts-btn {
  padding: 0.375rem 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.25rem;
  color: white;
  cursor: pointer;
}

.tts-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

/* Progress */
.progress-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--color-border);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), #8b5cf6);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.start-btn {
  padding: 0.375rem 0.75rem;
  background: var(--color-primary);
  border: none;
  border-radius: 0.25rem;
  color: white;
  font-size: 0.8125rem;
  cursor: pointer;
}

.animating-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-text-tertiary);
}

.spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Main Area */
.tutor-main-area {
  flex: 1;
  display: flex;
  gap: 1rem;
  padding: 1rem;
  overflow-y: auto;
}

.whiteboard-container {
  flex: 1;
  max-width: 50%;
  background: #1e293b;
  border-radius: 0.5rem;
  overflow: hidden;
}

.whiteboard-container.animating {
  box-shadow: 0 0 0 2px var(--color-primary);
}

.step-card {
  flex: 1;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.step-badge {
  padding: 0.25rem 0.5rem;
  background: var(--color-primary);
  color: white;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.step-title {
  margin: 0;
  font-size: 1rem;
}

.speech-bubble {
  padding: 1rem;
  background: var(--color-surface);
  border-radius: 0.5rem;
  border-left: 3px solid var(--color-primary);
}

.speech-bubble p {
  margin: 0;
  line-height: 1.6;
}

.calculator-box {
  padding: 1rem;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(22, 163, 74, 0.1) 100%);
  border-radius: 0.5rem;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.calc-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.calc-icon {
  font-size: 1.25rem;
}

.calc-label {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.calc-input {
  padding: 0.5rem 0.75rem;
  background: var(--color-surface);
  border-radius: 0.25rem;
  font-family: monospace;
  font-size: 1.125rem;
}

.calc-result {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: #22c55e;
}

.schema-preview {
  overflow-x: auto;
}

.schema-preview table {
  width: 100%;
  border-collapse: collapse;
}

.schema-preview td {
  padding: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.schema-preview tr.highlighted {
  background: var(--color-primary-subtle);
}

.schema-name {
  font-weight: 500;
}

.schema-op {
  text-align: center;
  color: var(--color-text-tertiary);
}

.schema-value {
  text-align: right;
  font-family: monospace;
}

/* Navigation */
.step-navigation {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid var(--color-border);
}

.nav-btn {
  padding: 0.5rem 1rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-btn:hover:not(:disabled) {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.step-dots {
  display: flex;
  gap: 0.5rem;
}

.step-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-border);
  cursor: pointer;
  transition: all 0.15s;
}

.step-dot.active {
  background: var(--color-primary);
  transform: scale(1.2);
}

.step-dot.completed {
  background: #22c55e;
}

/* No Selection */
.no-selection {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

/* Settings Panel */
.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.settings-section {
  margin-bottom: 1.5rem;
}

.settings-section h4 {
  margin: 0 0 0.75rem;
  font-size: 0.875rem;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.setting-row label {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.setting-select {
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.8125rem;
  background: var(--color-surface);
}

.toggle-btn {
  padding: 0.375rem 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  font-size: 0.8125rem;
  cursor: pointer;
}

.toggle-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.quick-action-btn {
  width: 100%;
  padding: 0.625rem;
  margin-bottom: 0.5rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  cursor: pointer;
  text-align: left;
}

.quick-action-btn:hover {
  background: var(--color-border);
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.8125rem;
}

.info-label {
  color: var(--color-text-tertiary);
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  border-top: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  font-size: 0.875rem;
}

.error-banner button {
  background: none;
  border: none;
  color: currentColor;
  font-size: 1.25rem;
  cursor: pointer;
}
</style>
