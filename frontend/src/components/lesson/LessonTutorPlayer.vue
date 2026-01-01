<!--
  LessonTutorPlayer - Interaktiver Tutor mit TTS und Whiteboard

  Features:
  - Schritt-fur-Schritt Erklarungen (mit Liste wie Chapter Theory)
  - Text-to-Speech (OpenAI TTS / Browser)
  - Interaktives Whiteboard mit Animationen
  - Taschenrechner-Anleitungen
  - Schema-Aufbau
  - Liste der erstellten Erklarungen mit Edit/Delete

  Usage:
  <LessonTutorPlayer
    :lesson-id="lesson.lesson_id"
    :lesson-title="lesson.title"
    :chapter-title="chapter.title"
    :course-title="course.title"
    @close="closeModal"
    @completed="onCompleted"
  />
-->

<template>
  <div class="lesson-tutor-player">
    <!-- TTS Error Banner -->
    <div v-if="ttsError" class="tts-error-banner">
      <span class="error-icon">!!</span>
      <span class="error-text">{{ ttsError }}</span>
      <button @click="ttsError = null" class="error-close">x</button>
    </div>

    <!-- Two Column Layout: List + Content -->
    <div class="tutor-layout">
      <!-- Left: Explanation List -->
      <div class="explanation-list-panel">
        <div class="list-header">
          <h3>Erklarungen</h3>
          <button @click="showNewForm = true" class="new-btn" title="Neue Erklarung erstellen">
            + Neu
          </button>
        </div>

        <!-- Loading List -->
        <div v-if="isLoadingList" class="list-loading">
          <div class="small-spinner"></div>
          <span>Lade...</span>
        </div>

        <!-- Empty List -->
        <div v-else-if="explanationList.length === 0 && !showNewForm" class="list-empty">
          <p>Noch keine Erklarungen</p>
          <button @click="showNewForm = true" class="create-first-btn">
            Erste Erklarung erstellen
          </button>
        </div>

        <!-- List Items -->
        <div v-else class="list-items">
          <div
            v-for="expl in explanationList"
            :key="expl.explanationId"
            class="list-item"
            :class="{ active: selectedExplanationId === expl.explanationId }"
            @click="selectExplanation(expl.explanationId)"
          >
            <div class="item-main">
              <span class="item-title">{{ expl.title }}</span>
              <span class="item-meta">
                {{ expl.style }} | {{ formatDate(expl.createdAt) }}
              </span>
            </div>
            <div class="item-actions">
              <button @click.stop="startEditTitle(expl)" class="item-btn" title="Umbenennen">
                E
              </button>
              <button @click.stop="confirmDelete(expl)" class="item-btn delete" title="Loschen">
                X
              </button>
            </div>
          </div>
        </div>

        <!-- Edit Title Form -->
        <div v-if="editingExplanation" class="edit-form">
          <input
            v-model="editTitle"
            type="text"
            class="edit-input"
            placeholder="Neuer Titel"
            @keyup.enter="saveTitle"
            @keyup.esc="cancelEdit"
          />
          <div class="edit-buttons">
            <button @click="saveTitle" class="save-btn">Speichern</button>
            <button @click="cancelEdit" class="cancel-btn">Abbrechen</button>
          </div>
        </div>
      </div>

      <!-- Right: Content Area -->
      <div class="content-panel">
        <!-- Loading State -->
        <div v-if="isGenerating" class="generating-state">
          <div class="generating-spinner"></div>
          <p>KI generiert Erklarung...</p>
          <p class="generating-hint">Das kann 10-30 Sekunden dauern</p>
        </div>

        <!-- New Explanation Form -->
        <div v-else-if="showNewForm" class="no-content-state">
          <div class="no-content-icon">Lehrer</div>
          <h3>Neue Erklarung erstellen</h3>
          <p>Lass die KI eine Schritt-fur-Schritt Erklarung erstellen.</p>

          <!-- Generation Options -->
          <div class="generation-options">
            <div class="option-row">
              <label class="option-label">Stil:</label>
              <select v-model="selectedStyle" class="option-select">
                <option value="adhs">ADHS-freundlich (kurz & visuell)</option>
                <option value="detailed">Ausfuhrlich</option>
                <option value="short">Kurz & Kompakt</option>
                <option value="exam_focus">Prufungsfokus (IHK)</option>
              </select>
            </div>

            <div class="option-row">
              <label class="option-label">Stimme:</label>
              <select v-model="selectedVoice" class="option-select">
                <option value="nova">Nova (weiblich)</option>
                <option value="alloy">Alloy (neutral)</option>
                <option value="echo">Echo (mannlich)</option>
                <option value="onyx">Onyx (tief)</option>
                <option value="shimmer">Shimmer (warm)</option>
              </select>
            </div>

            <div class="option-row">
              <label class="option-checkbox">
                <input type="checkbox" v-model="generateWithTTS" />
                <span>Audio direkt mitgenerieren</span>
              </label>
            </div>
          </div>

          <div class="form-buttons">
            <button @click="generateSteps" class="generate-btn">
              Erklarung mit KI generieren
            </button>
            <button v-if="explanationList.length > 0" @click="showNewForm = false" class="cancel-form-btn">
              Abbrechen
            </button>
          </div>
        </div>

        <!-- No Selection (has list but nothing selected) -->
        <div v-else-if="!hasContent && explanationList.length > 0" class="select-prompt">
          <p>Wahle eine Erklarung aus der Liste</p>
          <p class="or-text">oder</p>
          <button @click="showNewForm = true" class="new-explanation-btn">
            Neue Erklarung erstellen
          </button>
        </div>

        <!-- Explanation View -->
        <div v-else-if="hasContent" class="explanation-view">
      <!-- Tutor Header -->
      <div class="tutor-header">
        <div class="tutor-avatar">
          <span class="avatar-emoji">Lehrer</span>
        </div>
        <div class="tutor-info">
          <span class="tutor-name">Tutor erklart: {{ lessonTitle }}</span>
          <span class="tutor-status" :class="{ speaking: isSpeaking }">
            {{ isSpeaking ? 'Spricht...' : 'Bereit' }}
          </span>
        </div>
        <div class="tutor-controls">
          <!-- Voice Select -->
          <select v-model="selectedVoice" class="tts-select voice-select" title="Stimme">
            <option value="nova">Nova</option>
            <option value="alloy">Alloy</option>
            <option value="echo">Echo</option>
            <option value="onyx">Onyx</option>
            <option value="shimmer">Shimmer</option>
          </select>
          <!-- Model Select -->
          <select v-model="selectedTTSModel" class="tts-select model-select" title="TTS Modell">
            <option value="browser">Browser (Free)</option>
            <option value="tts-1">TTS-1 Standard</option>
            <option value="tts-1-hd">TTS-1-HD High Quality</option>
          </select>
          <button @click="toggleTTS" class="tts-btn" :class="{ active: ttsEnabled }" title="Sprachausgabe">
            {{ ttsEnabled ? 'Audio An' : 'Audio Aus' }}
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
          v-if="currentStep === 0 && !isSpeaking && !isAnimatingWhiteboard"
          @click="startExplanation"
          class="start-explanation-btn"
        >
          Erklarung starten
        </button>
        <div v-if="isAnimatingWhiteboard" class="animating-indicator">
          <span class="spinner"></span>
          <span>Zeichne auf Whiteboard...</span>
        </div>
      </div>

      <!-- Whiteboard + Step Card Layout -->
      <div class="tutor-main-area">
        <!-- Interactive Whiteboard -->
        <div v-if="hasWhiteboardActions" class="whiteboard-container" :class="{ animating: isAnimatingWhiteboard }">
          <div class="whiteboard-label">Whiteboard</div>
          <InteractiveWhiteboard
            ref="whiteboardRef"
            :width="480"
            :height="320"
            :show-controls="true"
            background-color="#1e293b"
            text-color="#f1f5f9"
            title=""
            @action-complete="onWhiteboardActionComplete"
          />
        </div>

        <!-- Current Step Card -->
        <div class="step-card" v-if="currentStepData">
          <div class="step-header">
            <span class="step-badge">Schritt {{ currentStep + 1 }}</span>
            <h3 class="step-title">{{ currentStepData.title }}</h3>
          </div>

          <!-- Speech Bubble -->
          <div class="speech-bubble">
            <p>{{ currentStepData.speech }}</p>
          </div>

          <!-- Calculator Hint -->
          <div v-if="currentStepData.calculator" class="calculator-box">
            <div class="calc-header">
              <span class="calc-icon">Rechner</span>
              <span class="calc-label">So tippst du es im Taschenrechner ein:</span>
            </div>
            <div class="calc-input">
              <code>{{ currentStepData.calculator }}</code>
            </div>
            <div v-if="currentStepData.result" class="calc-result">
              <span class="equals">=</span>
              <span class="result-value">{{ currentStepData.result }}</span>
            </div>
          </div>

          <!-- Schema Preview -->
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
      <div class="nav-buttons">
        <button @click="prevStep" class="nav-btn nav-prev" :disabled="currentStep === 0">
          Zuruck
        </button>
        <button v-if="currentStep < steps.length - 1" @click="nextStep" class="nav-btn nav-next">
          Weiter
        </button>
        <button v-else @click="finishTutorial" class="nav-btn nav-finish">
          Fertig!
        </button>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <button @click="$emit('back-to-theory')" class="action-btn">
          Zuruck zum Theorieblatt
        </button>
        <button @click="restartTutorial" class="action-btn">
          Von vorne
        </button>
        <button @click="$emit('practice')" class="action-btn primary">
          Jetzt selbst uben
        </button>
      </div>
        </div>
        <!-- /explanation-view -->

        <!-- Delete Confirmation Modal -->
        <div v-if="deleteConfirm" class="delete-modal">
          <div class="delete-modal-content">
            <h4>Erklarung loschen?</h4>
            <p>{{ deleteConfirm.title }}</p>
            <div class="modal-buttons">
              <button @click="executeDelete" class="confirm-delete-btn">Loschen</button>
              <button @click="deleteConfirm = null" class="cancel-delete-btn">Abbrechen</button>
            </div>
          </div>
        </div>
      </div>
      <!-- /content-panel -->
    </div>
    <!-- /tutor-layout -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted, onMounted } from 'vue'
import http from '@/api/http'
import InteractiveWhiteboard from '@/components/tutor/InteractiveWhiteboard.vue'

// ============================================================================
// Types
// ============================================================================

interface SchemaRow {
  name: string
  operator: string
  value: string
  highlight?: boolean
}

interface WhiteboardAction {
  type: 'write' | 'draw' | 'highlight' | 'arrow' | 'underline' | 'box' | 'clear' | 'schema'
  content?: string
  position?: { x: number, y: number }
  endPosition?: { x: number, y: number }
  duration?: number
  color?: string
  fontSize?: number
  schema?: SchemaRow[]
}

interface TutorialStep {
  title: string
  speech: string
  calculator?: string
  result?: string
  schema?: SchemaRow[]
  whiteboardActions?: WhiteboardAction[]
}

interface ExplanationListItem {
  explanationId: string
  title: string
  style: string
  hasAudio: boolean
  tokensUsed: number
  createdAt: string
  updatedAt: string
}

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  lessonId: string
  lessonTitle: string
  chapterTitle?: string
  courseTitle?: string
  lmType?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'completed'): void
  (e: 'back-to-theory'): void
  (e: 'practice'): void
}>()

// ============================================================================
// State
// ============================================================================

const currentStep = ref(0)
const ttsEnabled = ref(false)
const isSpeaking = ref(false)
const isGenerating = ref(false)
const selectedTTSModel = ref<string>('tts-1')
const selectedVoice = ref<string>('nova')
const selectedStyle = ref<string>('adhs')
const generateWithTTS = ref<boolean>(false)
const audioElement = ref<HTMLAudioElement | null>(null)
const ttsError = ref<string | null>(null)

// Whiteboard
const whiteboardRef = ref<InstanceType<typeof InteractiveWhiteboard> | null>(null)
const isAnimatingWhiteboard = ref(false)

// Lesson Steps
const lessonSteps = ref<TutorialStep[]>([])

// Explanation List
const explanationList = ref<ExplanationListItem[]>([])
const selectedExplanationId = ref<string | null>(null)
const isLoadingList = ref(false)
const showNewForm = ref(false)

// Edit/Delete
const editingExplanation = ref<ExplanationListItem | null>(null)
const editTitle = ref('')
const deleteConfirm = ref<ExplanationListItem | null>(null)

// ============================================================================
// Computed
// ============================================================================

const hasContent = computed(() => lessonSteps.value.length > 0)
const steps = computed(() => lessonSteps.value)
const currentStepData = computed(() => steps.value[currentStep.value])

// Check if any step has whiteboard actions
const hasWhiteboardActions = computed(() => {
  return lessonSteps.value.some(step => step.whiteboardActions && step.whiteboardActions.length > 0)
})

// ============================================================================
// Methods
// ============================================================================

// Load explanation list
async function loadExplanationList() {
  isLoadingList.value = true
  try {
    const response = await http.get(`/lessons/${props.lessonId}/explanations`)
    if (response.data.success) {
      explanationList.value = response.data.data.explanations || []
      // Auto-select the first (most recent) if available
      if (explanationList.value.length > 0 && !selectedExplanationId.value) {
        selectExplanation(explanationList.value[0].explanationId)
      } else if (explanationList.value.length === 0) {
        showNewForm.value = true
      }
    }
  } catch (error) {
    console.error('Failed to load explanation list:', error)
  } finally {
    isLoadingList.value = false
  }
}

// Select and load an explanation
async function selectExplanation(explanationId: string) {
  selectedExplanationId.value = explanationId
  showNewForm.value = false
  lessonSteps.value = []

  try {
    const response = await http.get(`/lesson-explanation/${explanationId}`)
    if (response.data.success) {
      lessonSteps.value = response.data.data.steps || []
      currentStep.value = 0
      if (whiteboardRef.value) {
        whiteboardRef.value.clearBoard()
      }
    }
  } catch (error) {
    console.error('Failed to load explanation:', error)
    ttsError.value = 'Fehler beim Laden der Erklarung'
  }
}

// Generate new steps
async function generateSteps() {
  isGenerating.value = true
  lessonSteps.value = []

  try {
    const response = await http.post('/admin/ai/generate-lesson-steps', {
      lesson_id: props.lessonId,
      lesson_title: props.lessonTitle,
      lm_type: props.lmType,
      chapter_title: props.chapterTitle,
      style: selectedStyle.value,
      generate_tts: generateWithTTS.value,
      tts_voice: selectedVoice.value
    })

    if (response.data.success) {
      lessonSteps.value = response.data.data.steps || []
      currentStep.value = 0
      showNewForm.value = false

      // Set the new explanation as selected
      if (response.data.explanationId) {
        selectedExplanationId.value = response.data.explanationId
      }

      // Reload list to show new entry
      await loadExplanationList()

      if (response.data.audio) {
        ttsEnabled.value = true
      }
    } else {
      throw new Error(response.data.error?.message || 'Generierung fehlgeschlagen')
    }
  } catch (error: any) {
    console.error('Lesson steps generation failed:', error)
    ttsError.value = `Fehler: ${error.response?.data?.error?.message || error.message}`
  } finally {
    isGenerating.value = false
  }
}

// Edit title
function startEditTitle(expl: ExplanationListItem) {
  editingExplanation.value = expl
  editTitle.value = expl.title
}

function cancelEdit() {
  editingExplanation.value = null
  editTitle.value = ''
}

async function saveTitle() {
  if (!editingExplanation.value || !editTitle.value.trim()) return

  try {
    const response = await http.patch(`/lesson-explanation/${editingExplanation.value.explanationId}`, {
      title: editTitle.value.trim()
    })
    if (response.data.success) {
      // Update in list
      const idx = explanationList.value.findIndex(e => e.explanationId === editingExplanation.value?.explanationId)
      if (idx >= 0) {
        explanationList.value[idx].title = editTitle.value.trim()
      }
    }
  } catch (error) {
    console.error('Failed to update title:', error)
    ttsError.value = 'Fehler beim Speichern des Titels'
  } finally {
    cancelEdit()
  }
}

// Delete
function confirmDelete(expl: ExplanationListItem) {
  deleteConfirm.value = expl
}

async function executeDelete() {
  if (!deleteConfirm.value) return

  try {
    const response = await http.delete(`/lesson-explanation/${deleteConfirm.value.explanationId}`)
    if (response.data.success) {
      // Remove from list
      explanationList.value = explanationList.value.filter(e => e.explanationId !== deleteConfirm.value?.explanationId)

      // Clear selection if deleted
      if (selectedExplanationId.value === deleteConfirm.value.explanationId) {
        selectedExplanationId.value = null
        lessonSteps.value = []
        // Select next if available
        if (explanationList.value.length > 0) {
          selectExplanation(explanationList.value[0].explanationId)
        } else {
          showNewForm.value = true
        }
      }
    }
  } catch (error) {
    console.error('Failed to delete explanation:', error)
    ttsError.value = 'Fehler beim Loschen'
  } finally {
    deleteConfirm.value = null
  }
}

// Format date
function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function nextStep() {
  if (currentStep.value < steps.value.length - 1) {
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    stopSpeaking()
    currentStep.value--
  }
}

function restartTutorial() {
  currentStep.value = 0
  if (whiteboardRef.value) {
    whiteboardRef.value.clearBoard()
  }
}

function finishTutorial() {
  emit('completed')
}

// ============================================================================
// TTS
// ============================================================================

function toggleTTS() {
  ttsEnabled.value = !ttsEnabled.value
  if (ttsEnabled.value && currentStepData.value) {
    speak(currentStepData.value.speech)
  } else {
    stopSpeaking()
  }
}

function stopSpeaking() {
  window.speechSynthesis?.cancel()
  if (audioElement.value) {
    audioElement.value.pause()
    audioElement.value = null
  }
  isSpeaking.value = false
}

async function speak(text: string) {
  stopSpeaking()
  isSpeaking.value = true
  ttsError.value = null

  const model = selectedTTSModel.value

  if (model === 'browser') {
    speakWithBrowser(text)
    return
  }

  try {
    const response = await http.post('/tts/speak', {
      text,
      voice: selectedVoice.value,
      provider: 'openai',
      model: model,
      language: 'de'
    })

    if (response.data.success && response.data.data.audio_path) {
      const audio = new Audio()
      audioElement.value = audio

      const audioUrl = `/api/v1/tts/audio/${response.data.data.audio_url.split('/').pop()}?path=${encodeURIComponent(response.data.data.audio_path)}`
      audio.src = audioUrl

      audio.onended = () => {
        isSpeaking.value = false
        audioElement.value = null
      }
      audio.onerror = () => {
        isSpeaking.value = false
        audioElement.value = null
        ttsError.value = 'Fehler beim Abspielen der Audio-Datei'
      }

      await audio.play()
    } else {
      throw new Error(response.data.error?.message || 'TTS failed')
    }
  } catch (error: any) {
    console.error('TTS API error:', error)
    ttsError.value = `TTS-Fehler: ${error?.response?.data?.error?.message || error?.message || 'Unbekannt'}`
    speakWithBrowser(text)
  }
}

function speakWithBrowser(text: string) {
  if (!window.speechSynthesis) {
    isSpeaking.value = false
    return
  }

  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'de-DE'
  utterance.rate = 0.9

  utterance.onend = () => { isSpeaking.value = false }
  utterance.onerror = () => { isSpeaking.value = false }

  window.speechSynthesis.speak(utterance)
}

// ============================================================================
// Whiteboard
// ============================================================================

function onWhiteboardActionComplete(action: WhiteboardAction) {
  console.log('Whiteboard action complete:', action.type)
}

async function startExplanation() {
  // Stop any current speech first
  stopSpeaking()

  // Enable TTS - the watch on currentStep will handle speaking
  ttsEnabled.value = true

  // If already at step 0, manually trigger whiteboard + speech
  // (watch won't fire if value doesn't change)
  if (currentStep.value === 0) {
    const stepData = steps.value[0]
    if (stepData?.whiteboardActions?.length && whiteboardRef.value) {
      isAnimatingWhiteboard.value = true
      whiteboardRef.value.clearBoard()
      await new Promise(resolve => setTimeout(resolve, 100))
      await whiteboardRef.value.executeActions(stepData.whiteboardActions)
      isAnimatingWhiteboard.value = false
    }

    if (stepData?.speech) {
      speak(stepData.speech)
    }
  } else {
    // Setting to 0 will trigger the watch which handles TTS
    currentStep.value = 0
  }
}

// ============================================================================
// Watchers
// ============================================================================

watch(currentStep, async (newStep, oldStep) => {
  const stepData = steps.value[newStep]
  if (!stepData) return

  if (oldStep !== undefined) {
    stopSpeaking()
  }

  // Execute whiteboard animations if available
  if (stepData.whiteboardActions?.length && whiteboardRef.value) {
    isAnimatingWhiteboard.value = true
    try {
      whiteboardRef.value.clearBoard()
      await new Promise(resolve => setTimeout(resolve, 100))
      await whiteboardRef.value.executeActions(stepData.whiteboardActions)
    } catch (err) {
      console.error('Whiteboard animation error:', err)
    } finally {
      isAnimatingWhiteboard.value = false
    }
  }

  // Speak if TTS enabled
  if (ttsEnabled.value && stepData.speech) {
    speak(stepData.speech)
  }
})

// ============================================================================
// Lifecycle
// ============================================================================

onUnmounted(() => {
  stopSpeaking()
})

// Load explanation list on mount
onMounted(async () => {
  await loadExplanationList()
})
</script>

<style scoped>
.lesson-tutor-player {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  height: 100%;
  overflow: hidden;
}

/* Two Column Layout */
.tutor-layout {
  display: flex;
  gap: 1rem;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* Left Panel - Explanation List */
.explanation-list-panel {
  width: 280px;
  min-width: 280px;
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border, #334155);
}

.list-header h3 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary, #f1f5f9);
}

.new-btn {
  padding: 0.375rem 0.75rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}

.list-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: var(--color-text-tertiary, #64748b);
}

.small-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border, #334155);
  border-top-color: var(--color-primary, #6366f1);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.list-empty {
  padding: 2rem 1rem;
  text-align: center;
}

.list-empty p {
  color: var(--color-text-tertiary, #64748b);
  margin: 0 0 1rem;
  font-size: 0.875rem;
}

.create-first-btn {
  padding: 0.5rem 1rem;
  background: var(--color-surface-secondary, #0f172a);
  border: 1px dashed var(--color-border, #334155);
  border-radius: 0.5rem;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.8125rem;
  cursor: pointer;
}

.list-items {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  margin-bottom: 0.25rem;
  transition: all 0.2s;
}

.list-item:hover {
  background: var(--color-surface-secondary, #0f172a);
}

.list-item.active {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.item-main {
  flex: 1;
  min-width: 0;
}

.item-title {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-primary, #f1f5f9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-meta {
  display: block;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary, #64748b);
  margin-top: 0.25rem;
}

.item-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.list-item:hover .item-actions {
  opacity: 1;
}

.item-btn {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 0.25rem;
  background: var(--color-surface, #1e293b);
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.625rem;
  cursor: pointer;
}

.item-btn:hover {
  background: var(--color-surface-secondary, #0f172a);
}

.item-btn.delete:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

/* Edit Form */
.edit-form {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border, #334155);
}

.edit-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.375rem;
  background: var(--color-surface-secondary, #0f172a);
  color: var(--color-text-primary, #f1f5f9);
  font-size: 0.8125rem;
  margin-bottom: 0.5rem;
}

.edit-buttons {
  display: flex;
  gap: 0.5rem;
}

.save-btn, .cancel-btn {
  flex: 1;
  padding: 0.375rem;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
}

.save-btn {
  background: #10b981;
  color: white;
}

.cancel-btn {
  background: var(--color-surface, #1e293b);
  color: var(--color-text-secondary, #94a3b8);
  border: 1px solid var(--color-border, #334155);
}

/* Right Panel - Content */
.content-panel {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
}

/* Select Prompt */
.select-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: var(--color-text-tertiary, #64748b);
}

.select-prompt p {
  margin: 0;
}

.or-text {
  margin: 0.75rem 0 !important;
  font-size: 0.75rem;
}

.new-explanation-btn {
  padding: 0.5rem 1rem;
  background: var(--color-surface, #1e293b);
  border: 1px dashed var(--color-border, #334155);
  border-radius: 0.5rem;
  color: var(--color-text-secondary, #94a3b8);
  cursor: pointer;
}

/* Form Buttons */
.form-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.cancel-form-btn {
  padding: 1rem 2rem;
  background: transparent;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.75rem;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 1rem;
  cursor: pointer;
}

/* Delete Modal */
.delete-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.delete-modal-content {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.75rem;
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
}

.delete-modal-content h4 {
  margin: 0 0 0.5rem;
  color: var(--color-text-primary, #f1f5f9);
}

.delete-modal-content p {
  margin: 0 0 1.5rem;
  color: var(--color-text-secondary, #94a3b8);
}

.modal-buttons {
  display: flex;
  gap: 0.75rem;
}

.confirm-delete-btn {
  flex: 1;
  padding: 0.75rem;
  background: #ef4444;
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.cancel-delete-btn {
  flex: 1;
  padding: 0.75rem;
  background: var(--color-surface-secondary, #0f172a);
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.5rem;
  color: var(--color-text-secondary, #94a3b8);
  cursor: pointer;
}

/* TTS Error Banner */
.tts-error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 0.5rem;
}

.tts-error-banner .error-icon {
  font-size: 1.25rem;
  color: #ef4444;
}

.tts-error-banner .error-text {
  flex: 1;
  color: #ef4444;
  font-size: 0.875rem;
}

.tts-error-banner .error-close {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: #ef4444;
  font-size: 1.25rem;
  cursor: pointer;
  border-radius: 4px;
}

/* Generating State */
.generating-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.generating-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-border, #334155);
  border-top-color: var(--color-primary, #6366f1);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.generating-hint {
  color: var(--color-text-tertiary, #64748b);
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

/* No Content State */
.no-content-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  background: var(--color-surface, #1e293b);
  border: 2px dashed var(--color-border, #334155);
  border-radius: 1rem;
}

.no-content-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.no-content-state h3 {
  color: var(--color-text-primary, #f1f5f9);
  margin: 0 0 0.5rem;
}

.no-content-state p {
  color: var(--color-text-secondary, #94a3b8);
  margin: 0 0 1.5rem;
}

/* Generation Options */
.generation-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--color-surface-secondary, #0f172a);
  border-radius: 0.5rem;
  width: 100%;
  max-width: 400px;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.option-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
  min-width: 60px;
}

.option-select {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.375rem;
  background: var(--color-surface, #1e293b);
  color: var(--color-text-primary, #f1f5f9);
  font-size: 0.875rem;
}

.option-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
  cursor: pointer;
}

.generate-btn {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Explanation View */
.explanation-view {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Tutor Header */
.tutor-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.75rem;
}

.tutor-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: white;
}

.tutor-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.tutor-name {
  font-weight: 600;
  color: var(--color-text-primary, #f1f5f9);
}

.tutor-status {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #64748b);
}

.tutor-status.speaking {
  color: #10b981;
}

.tutor-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tts-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.5rem;
  background: var(--color-surface, #1e293b);
  color: var(--color-text-primary, #f1f5f9);
  font-size: 0.75rem;
}

.voice-select {
  min-width: 90px;
}

.model-select {
  min-width: 140px;
}

.tts-btn {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.5rem;
  background: transparent;
  font-size: 0.75rem;
  cursor: pointer;
  color: var(--color-text-secondary, #94a3b8);
}

.tts-btn.active {
  background: rgba(16, 185, 129, 0.15);
  border-color: #10b981;
  color: #10b981;
}

/* Progress */
.progress-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--color-surface-secondary, #0f172a);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #64748b);
  white-space: nowrap;
}

.start-explanation-btn {
  margin-left: auto;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
}

.animating-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 0.375rem;
  font-size: 0.75rem;
  color: #8b5cf6;
}

.animating-indicator .spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(139, 92, 246, 0.3);
  border-top-color: #8b5cf6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Tutor Main Area */
.tutor-main-area {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 900px) {
  .tutor-main-area {
    flex-direction: row;
    align-items: flex-start;
  }

  .tutor-main-area .whiteboard-container {
    flex: 0 0 500px;
  }

  .tutor-main-area .step-card {
    flex: 1;
  }
}

/* Whiteboard Container */
.whiteboard-container {
  background: linear-gradient(145deg, #1e293b, #0f172a);
  border-radius: 0.75rem;
  padding: 1rem;
  border: 1px solid rgba(99, 102, 241, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.whiteboard-container.animating {
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow: 0 4px 20px rgba(139, 92, 246, 0.2);
}

.whiteboard-label {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #64748b);
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* Step Card */
.step-card {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.75rem;
  overflow: hidden;
}

.step-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border, #334155);
  background: var(--color-surface-secondary, #0f172a);
}

.step-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
}

.step-title {
  margin: 0;
  font-size: 1rem;
  color: var(--color-text-primary, #f1f5f9);
}

/* Speech Bubble */
.speech-bubble {
  padding: 1.25rem;
  background: rgba(99, 102, 241, 0.05);
  border-left: 3px solid #6366f1;
  margin: 1rem;
  border-radius: 0 0.5rem 0.5rem 0;
}

.speech-bubble p {
  margin: 0;
  color: var(--color-text-primary, #f1f5f9);
  line-height: 1.6;
}

/* Calculator Box */
.calculator-box {
  margin: 0 1rem 1rem;
  padding: 1rem;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 0.5rem;
}

.calc-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.calc-icon {
  font-size: 1rem;
}

.calc-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
}

.calc-input {
  background: rgba(0, 0, 0, 0.2);
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  margin-bottom: 0.5rem;
}

.calc-input code {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 1.125rem;
  color: #10b981;
}

.calc-result {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-left: 0.5rem;
}

.equals {
  color: var(--color-text-tertiary, #64748b);
  font-size: 1.25rem;
}

.result-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #10b981;
}

/* Schema Preview */
.schema-preview {
  margin: 0 1rem 1rem;
  overflow-x: auto;
}

.schema-preview table {
  width: 100%;
  border-collapse: collapse;
}

.schema-preview tr {
  border-bottom: 1px solid var(--color-border, #334155);
}

.schema-preview tr.highlighted {
  background: rgba(139, 92, 246, 0.1);
}

.schema-preview tr.highlighted td {
  color: #8b5cf6;
  font-weight: 600;
}

.schema-preview td {
  padding: 0.5rem 0.75rem;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.875rem;
}

.schema-name {
  text-align: left;
}

.schema-op {
  text-align: center;
  width: 30px;
}

.schema-value {
  text-align: right;
  font-family: 'Monaco', 'Menlo', monospace;
}

/* Navigation */
.nav-buttons {
  display: flex;
  gap: 1rem;
  justify-content: space-between;
}

.nav-btn {
  flex: 1;
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-prev {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  color: var(--color-text-secondary, #94a3b8);
}

.nav-prev:hover:not(:disabled) {
  background: var(--color-surface-secondary, #0f172a);
}

.nav-prev:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-next {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.nav-next:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.nav-finish {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  padding-top: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.375rem;
  background: transparent;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--color-surface-secondary, #0f172a);
  color: var(--color-text-primary, #f1f5f9);
}

.action-btn.primary {
  background: var(--color-primary, #6366f1);
  border-color: var(--color-primary, #6366f1);
  color: white;
}

.action-btn.primary:hover {
  filter: brightness(1.1);
}
</style>
