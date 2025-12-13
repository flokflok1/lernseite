<!--
  Tutor Tab - ADHS-freundliche Lernerklärungen

  Flow:
  1. Theorieblatt anzeigen (kompakte Übersicht)
  2. "Erklärung starten" → Schritt-für-Schritt mit TTS
  3. "Jetzt üben" → Interaktive Übung

  Features:
  - Kurze, visuelle Erklärungen
  - TTS Sprachausgabe (optional)
  - Taschenrechner-Tipps
  - Kein langes Video - alles interaktiv
-->

<template>
  <div class="tutor-tab">
    <!-- Main Content -->
    <div class="tab-content">
      <!-- Nothing Selected -->
      <div v-if="!chapter && !lesson" class="empty-state">
        <div class="empty-icon">👨‍🏫</div>
        <h3>Kapitel oder Lektion auswählen</h3>
        <p>Wähle links ein <strong>Kapitel</strong> für das Theorieblatt oder eine <strong>Lektion</strong> für die Schritt-für-Schritt Erklärung.</p>
      </div>

      <!-- ============================================ -->
      <!-- CHAPTER VIEW - Theorieblatt für ganzes Kapitel -->
      <!-- ============================================ -->
      <div v-else-if="showChapterView" class="chapter-theory-section">
        <div class="chapter-header">
          <div class="chapter-icon">📖</div>
          <div>
            <h2 class="chapter-title">{{ chapter?.title }}</h2>
            <p class="chapter-subtitle">Theorieblatt • {{ course?.title }}</p>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isGeneratingChapter" class="generating-state">
          <div class="generating-spinner"></div>
          <p>KI generiert Theorieblatt...</p>
          <p class="generating-hint">Das kann 10-30 Sekunden dauern</p>
        </div>

        <!-- No Content Yet -->
        <div v-else-if="!chapterTheory" class="no-theory-state">
          <div class="no-theory-icon">📝</div>
          <h3>Noch kein Theorieblatt vorhanden</h3>
          <p>Lass die KI ein umfangreiches Theorieblatt fuer dieses Kapitel erstellen.</p>

          <!-- Generation Options -->
          <div class="generation-options">
            <div class="option-row">
              <label class="option-label">Stil:</label>
              <select v-model="selectedStyle" class="option-select">
                <option value="adhs">ADHS-freundlich (kurz & visuell)</option>
                <option value="detailed">Ausfuehrlich (mit Hintergrund)</option>
                <option value="short">Kurz & Kompakt</option>
                <option value="exam_focus">Pruefungsfokus (IHK)</option>
                <option value="standard">Standard</option>
              </select>
            </div>

            <div class="option-row">
              <label class="option-label">Stimme:</label>
              <select v-model="selectedVoice" class="option-select">
                <option value="nova">Nova (weiblich, freundlich)</option>
                <option value="alloy">Alloy (neutral)</option>
                <option value="echo">Echo (maennlich, warm)</option>
                <option value="onyx">Onyx (maennlich, tief)</option>
                <option value="shimmer">Shimmer (weiblich, sanft)</option>
              </select>
            </div>

            <div class="option-row">
              <label class="option-checkbox">
                <input type="checkbox" v-model="generateWithTTS" />
                <span>Audio direkt mitgenerieren (Vorlesen)</span>
              </label>
            </div>
          </div>

          <button @click="generateChapterTheory" class="generate-chapter-btn">
            ✨ Theorieblatt mit KI generieren
          </button>
        </div>

        <!-- Chapter Theory Content -->
        <div v-else class="chapter-theory-content">
          <!-- Übersicht -->
          <div class="theory-section">
            <h3 class="section-title">📋 Übersicht</h3>
            <div class="section-content" v-html="chapterTheory.overview"></div>
          </div>

          <!-- Lernziele -->
          <div class="theory-section">
            <h3 class="section-title">🎯 Lernziele</h3>
            <ul class="learning-goals">
              <li v-for="(goal, idx) in chapterTheory.learningGoals" :key="idx">{{ goal }}</li>
            </ul>
          </div>

          <!-- Kernkonzepte -->
          <div class="theory-section">
            <h3 class="section-title">💡 Kernkonzepte</h3>
            <div class="concepts-grid">
              <div v-for="(concept, idx) in chapterTheory.concepts" :key="idx" class="concept-card">
                <h4 class="concept-title">{{ concept.title }}</h4>
                <p class="concept-description">{{ concept.description }}</p>
                <div v-if="concept.formula" class="concept-formula">
                  <code>{{ concept.formula }}</code>
                </div>
              </div>
            </div>
          </div>

          <!-- Wichtige Begriffe -->
          <div class="theory-section" v-if="chapterTheory.terms?.length">
            <h3 class="section-title">📚 Wichtige Begriffe</h3>
            <div class="terms-list">
              <div v-for="(term, idx) in chapterTheory.terms" :key="idx" class="term-item">
                <strong>{{ term.term }}:</strong> {{ term.definition }}
              </div>
            </div>
          </div>

          <!-- Prüfungsrelevanz -->
          <div class="theory-section exam-relevance" v-if="chapterTheory.examRelevance">
            <h3 class="section-title">⚠️ Prüfungsrelevanz</h3>
            <div class="section-content" v-html="chapterTheory.examRelevance"></div>
          </div>

          <!-- Actions -->
          <div class="chapter-actions">
            <button @click="generateChapterTheory" class="action-btn secondary">
              🔄 Neu generieren
            </button>
            <button @click="printTheory" class="action-btn secondary">
              🖨️ Drucken
            </button>
          </div>
        </div>
      </div>

      <!-- ============================================ -->
      <!-- LESSON VIEW - Schritt-für-Schritt Erklärung -->
      <!-- ============================================ -->
      <div v-else-if="lesson" class="lesson-section">
        <!-- TTS Error Message -->
        <div v-if="ttsError" class="tts-error-banner">
          <span class="error-icon">⚠️</span>
          <span class="error-text">{{ ttsError }}</span>
          <button @click="ttsError = null" class="error-close">×</button>
        </div>

        <!-- Lesson Header -->
        <div class="lesson-header">
          <div class="lesson-icon">📝</div>
          <div>
            <h2 class="lesson-title">{{ lesson.title }}</h2>
            <p class="lesson-subtitle">
              <span v-if="lesson.lm_type" class="lm-badge">{{ lesson.lm_type }}</span>
              {{ chapter?.title }}
            </p>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isGeneratingLesson" class="generating-state">
          <div class="generating-spinner"></div>
          <p>KI generiert Erklärung...</p>
          <p class="generating-hint">Das kann 10-30 Sekunden dauern</p>
        </div>

        <!-- No Steps Yet - Generate Button with Options -->
        <div v-else-if="!hasLessonContent" class="no-content-state">
          <div class="no-content-icon">👨‍🏫</div>
          <h3>Noch keine Erklaerung vorhanden</h3>
          <p>Lass die KI eine Schritt-fuer-Schritt Erklaerung fuer diese Lektion erstellen.</p>

          <!-- Generation Options -->
          <div class="generation-options">
            <div class="option-row">
              <label class="option-label">Stil:</label>
              <select v-model="selectedStyle" class="option-select">
                <option value="adhs">ADHS-freundlich (kurz & visuell)</option>
                <option value="detailed">Ausfuehrlich (mit Hintergrund)</option>
                <option value="short">Kurz & Kompakt</option>
                <option value="exam_focus">Pruefungsfokus (IHK)</option>
                <option value="standard">Standard</option>
              </select>
            </div>

            <div class="option-row">
              <label class="option-label">Stimme:</label>
              <select v-model="selectedVoice" class="option-select">
                <option value="nova">Nova (weiblich, freundlich)</option>
                <option value="alloy">Alloy (neutral)</option>
                <option value="echo">Echo (maennlich, warm)</option>
                <option value="onyx">Onyx (maennlich, tief)</option>
                <option value="shimmer">Shimmer (weiblich, sanft)</option>
              </select>
            </div>

            <div class="option-row">
              <label class="option-checkbox">
                <input type="checkbox" v-model="generateWithTTS" />
                <span>Audio direkt mitgenerieren</span>
              </label>
            </div>
          </div>

          <button @click="generateLessonSteps" class="generate-lesson-btn">
            ✨ Erklaerung mit KI generieren
          </button>
        </div>

        <!-- Has Content - Show Explanation -->
        <div v-else class="explanation-view">
          <!-- Tutor Header -->
          <div class="tutor-header">
            <div class="tutor-avatar">
              <span class="avatar-emoji">👨‍🏫</span>
            </div>
            <div class="tutor-info">
              <span class="tutor-name">Tutor erklärt: {{ lesson.title }}</span>
              <span class="tutor-status" :class="{ speaking: isSpeaking }">
                {{ isSpeaking ? '🔊 Spricht...' : '💬 Bereit' }}
              </span>
            </div>
            <div class="tutor-controls">
              <!-- Voice Select -->
              <select v-model="selectedVoice" class="tts-select voice-select" title="Stimme">
                <option value="nova">👩 Nova</option>
                <option value="alloy">🎭 Alloy</option>
                <option value="echo">🎤 Echo</option>
                <option value="onyx">👨 Onyx</option>
                <option value="shimmer">✨ Shimmer</option>
              </select>
              <!-- Model Select -->
              <select v-model="selectedTTSModel" class="tts-select model-select" title="TTS Modell" @change="onModelChange">
                <option value="browser">🔊 Browser (Free)</option>
                <optgroup label="OpenAI TTS">
                  <option value="tts-1">TTS-1 Standard</option>
                  <option value="tts-1-hd">TTS-1-HD High Quality</option>
                </optgroup>
                <optgroup label="Aus DB" v-if="openaiTTSModels.length > 0">
                  <option v-for="model in openaiTTSModels" :key="model.model_name" :value="model.model_name">
                    {{ model.display_name }}
                  </option>
                </optgroup>
              </select>
              <button @click="toggleTTS" class="tts-btn" :class="{ active: ttsEnabled }" title="Sprachausgabe">
                {{ ttsEnabled ? '🔊' : '🔇' }}
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
              ▶️ Erklärung starten
            </button>
            <div v-if="isAnimatingWhiteboard" class="animating-indicator">
              <span class="spinner"></span>
              <span>Zeichne auf Whiteboard...</span>
            </div>
          </div>

          <!-- Whiteboard + Step Card Layout -->
          <div class="tutor-main-area">
            <!-- Interactive Whiteboard (for ADHS style with animations) -->
            <div v-if="currentStepData?.whiteboardActions?.length" class="whiteboard-container" :class="{ animating: isAnimatingWhiteboard }">
              <InteractiveWhiteboard
                ref="whiteboardRef"
                :width="500"
                :height="350"
                :show-controls="true"
                background-color="transparent"
                text-color="#ffffff"
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
                  <span class="calc-icon">🔢</span>
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

              <!-- Formula/Schema Preview (fallback if no whiteboard) -->
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
              ← Zurück
            </button>
            <button v-if="currentStep < steps.length - 1" @click="nextStep" class="nav-btn nav-next">
              Weiter →
            </button>
            <button v-else @click="finishTutorial" class="nav-btn nav-finish">
              Fertig! 🎉
            </button>
          </div>

          <!-- Quick Actions -->
          <div class="quick-actions">
            <button @click="currentView = 'theory'" class="action-btn">
              📋 Zurück zum Theorieblatt
            </button>
            <button @click="restartTutorial" class="action-btn">
              🔄 Von vorne
            </button>
            <button @click="openPracticeMode" class="action-btn primary">
              🎯 Jetzt selbst üben
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted, onMounted, nextTick } from 'vue'
import http from '@/api/http'
import InteractiveWhiteboard from '@/components/tutor/InteractiveWhiteboard.vue'

interface Lesson {
  lesson_id: string
  title: string
  lm_type?: string
  content?: Record<string, unknown>
}

interface Chapter {
  chapter_id: string
  title: string
}

interface Course {
  course_id: string
  title: string
}

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
  schema?: Array<{
    name: string
    operator: string
    value: string
    highlight?: boolean
  }>
  whiteboardActions?: WhiteboardAction[]
}

interface Props {
  lesson?: Lesson | null
  chapter?: Chapter | null
  course?: Course | null
}

const props = withDefaults(defineProps<Props>(), {
  lesson: null,
  chapter: null,
  course: null
})

// Computed: Show chapter view when chapter selected but no lesson
const showChapterView = computed(() => props.chapter && !props.lesson)

const emit = defineEmits<{
  (e: 'open-practice'): void
}>()

// TTS Model interface
interface TTSModel {
  model_id?: number
  model_name: string
  display_name: string
  provider_name?: string
  provider?: string
  input_price_per_1k?: number
  output_price_per_1k?: number
  category?: string
  subcategory?: string
  active?: boolean
}

// State
const currentView = ref<'theory' | 'explanation'>('theory') // Default: Theorieblatt zuerst
const currentStep = ref(0)
const ttsEnabled = ref(false)
const isSpeaking = ref(false)
const isGenerating = ref(false)
const selectedTTSModel = ref<string>('tts-1') // 'browser', 'tts-1', 'tts-1-hd', or DB model
const selectedVoice = ref<string>('nova') // 'nova', 'alloy', 'onyx', 'shimmer', 'fable', 'echo'
const selectedStyle = ref<string>('adhs') // 'adhs', 'detailed', 'short', 'exam_focus', 'standard'
const generateWithTTS = ref<boolean>(false) // Generate TTS audio with content
const audioElement = ref<HTMLAudioElement | null>(null)
const availableModels = ref<TTSModel[]>([])
const ttsError = ref<string | null>(null)

// Whiteboard
const whiteboardRef = ref<InstanceType<typeof InteractiveWhiteboard> | null>(null)
const isAnimatingWhiteboard = ref(false)

// Chapter Theory (KI-generated)
interface ChapterTheory {
  overview: string
  learningGoals: string[]
  concepts: Array<{
    title: string
    description: string
    formula?: string
  }>
  terms?: Array<{
    term: string
    definition: string
  }>
  examRelevance?: string
}

const isGeneratingChapter = ref(false)
const chapterTheory = ref<ChapterTheory | null>(null)

// Lesson Steps (KI-generated)
const isGeneratingLesson = ref(false)
const lessonSteps = ref<TutorialStep[]>([])
const hasLessonContent = computed(() => lessonSteps.value.length > 0)

// Computed: Only REAL TTS models from DB (subcategory = 'tts')
// NOT gpt-audio-* (those are chat models with audio output, different API endpoint!)
const openaiTTSModels = computed(() => {
  return availableModels.value.filter(m => {
    const name = (m.model_name || '').toLowerCase()
    const subcategory = (m.subcategory || '').toLowerCase()
    // Only show models with subcategory='tts' OR model name starts with 'tts-'
    return subcategory === 'tts' || name.startsWith('tts-')
  })
})

// Load TTS models from Database
async function loadTTSModels() {
  try {
    // First try to load from models endpoint (includes all DB models)
    const response = await http.get('/admin/ai/models', {
      params: { category: 'audio' }
    })
    if (response.data.success && response.data.data.models) {
      availableModels.value = response.data.data.models.filter((m: TTSModel) => m.active)
      console.log('TTS models loaded from DB:', availableModels.value.length)
      return
    }
  } catch (error) {
    console.log('Could not load from admin endpoint, trying TTS voices...')
  }

  // Fallback: Try TTS voices endpoint
  try {
    const response = await http.get('/tts/voices')
    if (response.data.success) {
      availableModels.value = response.data.data.tts_models || []
      console.log('TTS models loaded from voices endpoint:', availableModels.value.length)
    }
  } catch (error) {
    console.log('TTS models not available, using defaults')
  }
}

// Handle model change
function onModelChange() {
  console.log('TTS model changed to:', selectedTTSModel.value)
}

// Load on mount
onMounted(() => {
  loadTTSModels()
})

// Steps are now KI-generated, not hardcoded
const steps = computed(() => lessonSteps.value)

// Current step data
const currentStepData = computed(() => steps.value[currentStep.value])

// Navigation - TTS and whiteboard are handled by watch on currentStep
function nextStep() {
  if (currentStep.value < steps.value.length - 1) {
    currentStep.value++
    // TTS and whiteboard animation are triggered by the currentStep watch
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    stopSpeaking() // Stop current speech before going back
    currentStep.value--
    // TTS and whiteboard animation are triggered by the currentStep watch
  }
}

function restartTutorial() {
  currentStep.value = 0
}

// Generate Chapter Theory via KI
async function generateChapterTheory() {
  if (!props.chapter) return

  isGeneratingChapter.value = true
  chapterTheory.value = null

  try {
    const response = await http.post('/admin/ai/generate-chapter-theory', {
      chapter_id: props.chapter.chapter_id,
      chapter_title: props.chapter.title,
      course_title: props.course?.title,
      // New: Style and TTS options
      style: selectedStyle.value,
      generate_tts: generateWithTTS.value,
      tts_voice: selectedVoice.value
    })

    if (response.data.success) {
      chapterTheory.value = response.data.data

      // Store audio info if generated
      if (response.data.audio) {
        console.log('TTS audio generated for theory:', response.data.audio)
        // Could store for playback
      }
    } else {
      throw new Error(response.data.error?.message || 'Generierung fehlgeschlagen')
    }
  } catch (error: any) {
    console.error('Chapter theory generation failed:', error)
    ttsError.value = `Fehler: ${error.response?.data?.error?.message || error.message}`
  } finally {
    isGeneratingChapter.value = false
  }
}

// Generate Lesson Steps via KI
async function generateLessonSteps() {
  if (!props.lesson) return

  isGeneratingLesson.value = true
  lessonSteps.value = []

  try {
    const response = await http.post('/admin/ai/generate-lesson-steps', {
      lesson_id: props.lesson.lesson_id,
      lesson_title: props.lesson.title,
      lm_type: props.lesson.lm_type,
      chapter_title: props.chapter?.title,
      // New: Style and TTS options
      style: selectedStyle.value,
      generate_tts: generateWithTTS.value,
      tts_voice: selectedVoice.value
    })

    if (response.data.success) {
      lessonSteps.value = response.data.data.steps || []
      // Start at first step
      currentStep.value = 0

      // Enable TTS if audio was generated
      if (response.data.audio) {
        ttsEnabled.value = true
        console.log('TTS audio generated:', response.data.audio)
      }
    } else {
      throw new Error(response.data.error?.message || 'Generierung fehlgeschlagen')
    }
  } catch (error: any) {
    console.error('Lesson steps generation failed:', error)
    ttsError.value = `Fehler: ${error.response?.data?.error?.message || error.message}`
  } finally {
    isGeneratingLesson.value = false
  }
}

// Print Theory
function printTheory() {
  window.print()
}

function finishTutorial() {
  // Could emit event or show completion modal
  alert('Glückwunsch! Du hast die Erklärung abgeschlossen. Jetzt kannst du selbst üben!')
}

function openPracticeMode() {
  emit('open-practice')
}

// TTS
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

  // Browser TTS (free, instant, no API call)
  if (model === 'browser') {
    speakWithBrowser(text)
    return
  }

  // OpenAI TTS via API
  try {
    const voice = selectedVoice.value
    console.log(`TTS: Using OpenAI ${model} with voice ${voice}`)

    const response = await http.post('/tts/speak', {
      text,
      voice: voice,
      provider: 'openai',
      model: model,
      language: 'de'
    })

    if (response.data.success && response.data.data.audio_path) {
      // Play audio
      const audio = new Audio()
      audioElement.value = audio

      // Use direct path for development
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
        console.error('Audio playback error')
      }

      await audio.play()
    } else {
      throw new Error(response.data.error?.message || 'TTS failed')
    }
  } catch (error: any) {
    console.error('TTS API error:', error)

    // Extract error details
    const errorMsg = error?.response?.data?.error?.message
      || error?.response?.data?.error?.details
      || error?.message
      || 'Unbekannter Fehler'

    // Check if it's an API key issue
    if (error?.response?.status === 503 || errorMsg.includes('API key')) {
      ttsError.value = `TTS-Fehler: ${errorMsg}. Prüfe die OpenAI API-Key Konfiguration im KI Studio > Modelle Tab.`
      console.error('TTS API Key issue - check admin panel configuration')
    } else {
      ttsError.value = `TTS-Fehler: ${errorMsg}`
    }

    // Fallback to browser TTS
    console.log('Falling back to browser TTS...')
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

// Cleanup
onUnmounted(() => {
  stopSpeaking()
})

// Watch for lesson changes - reset step
watch(() => props.lesson, () => {
  currentStep.value = 0
  // Clear whiteboard when lesson changes
  if (whiteboardRef.value) {
    whiteboardRef.value.clearBoard()
  }
})

// Watch for step changes - execute whiteboard animations and TTS
watch(currentStep, async (newStep, oldStep) => {
  const stepData = steps.value[newStep]
  if (!stepData) return

  // Stop any current speech when step changes
  if (oldStep !== undefined) {
    stopSpeaking()
  }

  // If this step has whiteboard actions, execute them
  if (stepData.whiteboardActions?.length && whiteboardRef.value) {
    isAnimatingWhiteboard.value = true

    // Clear board before new step animations
    whiteboardRef.value.clearBoard()

    // Wait a moment for clear to finish
    await new Promise(resolve => setTimeout(resolve, 100))

    // Execute all whiteboard actions for this step
    await whiteboardRef.value.executeActions(stepData.whiteboardActions)

    isAnimatingWhiteboard.value = false
  }

  // After whiteboard animation completes (or if none), speak if TTS enabled
  if (ttsEnabled.value && stepData.speech) {
    speak(stepData.speech)
  }
})

// Handler for when a whiteboard action completes
function onWhiteboardActionComplete(action: WhiteboardAction) {
  console.log('Whiteboard action complete:', action.type, action.content?.slice(0, 20))
}

// Start explanation with TTS and whiteboard for first step
async function startExplanation() {
  currentStep.value = 0
  ttsEnabled.value = true

  // Trigger the watch manually for the first step
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
}
</script>

<style scoped>
.tutor-tab {
  height: 100%;
  overflow-y: auto;
}

.tab-content {
  padding: 1.5rem;
  max-width: 700px;
  margin: 0 auto;
}

/* Header */
.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.tab-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.tab-subtitle {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  margin: 0.25rem 0 0;
}

.badge {
  padding: 0.375rem 0.75rem;
  border-radius: 2rem;
  font-size: 0.75rem;
  font-weight: 500;
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-text-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: var(--color-text-primary);
  margin: 0 0 0.5rem;
}

.empty-state p {
  margin: 0;
}

/* ============================================ */
/* CHAPTER THEORY SECTION */
/* ============================================ */
.chapter-theory-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chapter-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.chapter-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
}

.chapter-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.chapter-subtitle {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  margin: 0.25rem 0 0;
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
  border: 4px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.generating-state p {
  color: var(--color-text-primary);
  font-weight: 500;
  margin: 0;
}

.generating-hint {
  color: var(--color-text-tertiary) !important;
  font-size: 0.875rem;
  font-weight: 400 !important;
  margin-top: 0.5rem !important;
}

/* No Theory State */
.no-theory-state, .no-content-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  background: var(--color-surface);
  border: 2px dashed var(--color-border);
  border-radius: 1rem;
}

.no-theory-icon, .no-content-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.no-theory-state h3, .no-content-state h3 {
  color: var(--color-text-primary);
  margin: 0 0 0.5rem;
}

.no-theory-state p, .no-content-state p {
  color: var(--color-text-secondary);
  margin: 0 0 1.5rem;
  max-width: 400px;
}

/* Generation Options */
.generation-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--color-surface-secondary);
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
  color: var(--color-text-secondary);
  min-width: 60px;
}

.option-select {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.875rem;
  cursor: pointer;
}

.option-select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.option-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.option-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.option-checkbox span {
  user-select: none;
}

.generate-chapter-btn, .generate-lesson-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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

.generate-chapter-btn:hover, .generate-lesson-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Chapter Theory Content */
.chapter-theory-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.theory-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.25rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 1rem;
}

.section-content {
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.learning-goals {
  margin: 0;
  padding-left: 1.5rem;
  color: var(--color-text-secondary);
}

.learning-goals li {
  margin-bottom: 0.5rem;
}

.concepts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.concept-card {
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
  padding: 1rem;
}

.concept-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem;
}

.concept-description {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
}

.concept-formula {
  margin-top: 0.75rem;
  padding: 0.5rem;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 0.25rem;
}

.concept-formula code {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.85rem;
  color: var(--color-primary);
}

.terms-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.term-item {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.term-item:last-child {
  border-bottom: none;
}

.term-item strong {
  color: var(--color-text-primary);
}

.exam-relevance {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.1));
  border-color: rgba(251, 191, 36, 0.3);
}

.chapter-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  padding-top: 1rem;
}

/* ============================================ */
/* LESSON SECTION */
/* ============================================ */
.lesson-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.lesson-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.lesson-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.lesson-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.lesson-subtitle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  margin: 0.25rem 0 0;
}

/* Legacy Tutor Section - keep for compatibility */
.tutor-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* View Toggle - removed, not needed anymore */
.view-toggle {
  display: flex;
  gap: 0.5rem;
  padding: 0.25rem;
  background: var(--color-surface-secondary);
  border-radius: 0.75rem;
  width: fit-content;
}

.toggle-btn {
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 0.5rem;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn:hover {
  color: var(--color-text-primary);
}

.toggle-btn.active {
  background: var(--color-surface);
  color: var(--color-primary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* ============================================ */
/* THEORY VIEW STYLES */
/* ============================================ */
.theory-view {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.theory-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.theory-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.lm-badge {
  padding: 0.25rem 0.75rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 1rem;
}

.theory-content {
  display: grid;
  gap: 1rem;
}

/* Schema Box */
.theory-schema-box {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1rem;
}

.schema-title, .note-title, .example-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 0.75rem;
}

.schema-table {
  width: 100%;
  border-collapse: collapse;
}

.schema-table tr {
  border-bottom: 1px solid var(--color-border);
}

.schema-table tr:last-child {
  border-bottom: none;
}

.schema-table td {
  padding: 0.5rem;
  font-size: 0.875rem;
}

.schema-table .schema-name {
  color: var(--color-text-primary);
}

.schema-table .schema-op {
  width: 30px;
  text-align: center;
  color: var(--color-text-tertiary);
  font-weight: 600;
}

.schema-table tr.schema-highlight {
  background: var(--color-primary-subtle);
}

.schema-table tr.schema-highlight td {
  color: var(--color-primary);
  font-weight: 600;
}

/* Note Box */
.theory-note-box {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.1));
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 0.75rem;
  padding: 1rem;
}

.note-text {
  color: var(--color-text-primary);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

/* Example Box */
.theory-example-box {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1rem;
}

.example-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.example-given, .example-calc, .example-result {
  color: var(--color-text-secondary);
}

.example-content code {
  font-family: 'Monaco', 'Menlo', monospace;
  background: var(--color-surface-secondary);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  color: var(--color-primary);
}

.example-result .result-value {
  font-weight: 700;
  color: #10b981;
  font-size: 1rem;
}

/* Generate Theory Button */
.generate-theory {
  display: flex;
  justify-content: center;
  padding: 1rem;
}

.generate-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Theory CTA */
.theory-cta {
  display: flex;
  gap: 1rem;
  justify-content: center;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.cta-btn {
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

.cta-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.cta-btn-secondary {
  padding: 1rem 2rem;
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.cta-btn-secondary:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

/* ============================================ */
/* EXPLANATION VIEW */
/* ============================================ */
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
  background: var(--color-surface);
  border: 1px solid var(--color-border);
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
}

.avatar-emoji {
  font-size: 1.5rem;
}

.tutor-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.tutor-name {
  font-weight: 600;
  color: var(--color-text-primary);
}

.tutor-status {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
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
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.75rem;
  cursor: pointer;
}

.tts-select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.voice-select {
  min-width: 110px;
}

.model-select {
  min-width: 180px;
}

.tts-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background: transparent;
  font-size: 1.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.tts-btn:hover {
  background: var(--color-surface-secondary);
}

.tts-btn.active {
  background: rgba(16, 185, 129, 0.15);
  border-color: #10b981;
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
  background: var(--color-surface-secondary);
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
  color: var(--color-text-tertiary);
  white-space: nowrap;
}

/* Step Card */
.step-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.step-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
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
  color: var(--color-text-primary);
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
  color: var(--color-text-primary);
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
  font-size: 1.25rem;
}

.calc-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
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
  color: var(--color-text-tertiary);
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
  border-bottom: 1px solid var(--color-border);
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
  color: var(--color-text-secondary);
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
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
}

.nav-prev:hover:not(:disabled) {
  background: var(--color-surface-secondary);
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

.nav-finish:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
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
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--color-surface-secondary);
  color: var(--color-text-primary);
}

.action-btn.primary {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.action-btn.primary:hover {
  filter: brightness(1.1);
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
  margin-bottom: 1rem;
}

.tts-error-banner .error-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.tts-error-banner .error-text {
  flex: 1;
  color: #ef4444;
  font-size: 0.875rem;
  line-height: 1.4;
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
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tts-error-banner .error-close:hover {
  background: rgba(239, 68, 68, 0.15);
}

/* ============================================ */
/* TUTOR MAIN AREA - Whiteboard + Step Card */
/* ============================================ */
.tutor-main-area {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* When whiteboard is present, show side by side on larger screens */
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

/* Whiteboard Loading/Animating State */
.whiteboard-container.animating {
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow: 0 4px 20px rgba(139, 92, 246, 0.2);
}

/* Whiteboard title bar */
.whiteboard-container::before {
  content: '📋 Whiteboard';
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* Start Explanation Button */
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
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.start-explanation-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

/* Animation indicator */
.animating-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.3);
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
</style>
