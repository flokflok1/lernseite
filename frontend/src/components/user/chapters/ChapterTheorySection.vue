<template>
  <div class="chapter-theory-section">
    <!-- Theory Selector (when multiple theories exist) -->
    <div v-if="theoryList.length > 0" class="theory-selector">
      <div class="selector-left">
        <label>{{ $t('chapterTheory.theorySheet') }}</label>
        <select v-model="selectedTheoryId" @change="onTheorySelect" class="theory-dropdown">
          <option v-for="t in theoryList" :key="t.theoryId" :value="t.theoryId">
            {{ getStyleEmoji(t.style) }} {{ t.title }}
          </option>
        </select>
        <span class="theory-count">{{ $t('chapterTheory.available', { count: theoryList.length }) }}</span>
      </div>
      <button class="new-theory-btn" @click="$emit('generate')" :title="$t('chapterTheory.newTheoryTitle')">
        {{ $t('chapterTheory.newTheory') }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>{{ $t('chapterTheory.loading.generating') }}</p>
      <p class="loading-hint">{{ $t('chapterTheory.loading.hint') }}</p>
    </div>

    <!-- No Theory State -->
    <div v-else-if="!hasTheory && theoryList.length === 0" class="no-theory-state">
      <div class="no-theory-icon">&#128218;</div>
      <h3>{{ $t('chapterTheory.noTheory.title') }}</h3>
      <p>{{ $t('chapterTheory.noTheory.description') }}</p>
      <p class="info-text">
        {{ $t('chapterTheory.noTheory.info') }}
      </p>
      <button class="generate-btn" @click="$emit('generate')">
        <span class="btn-icon">&#10024;</span>
        {{ $t('chapterTheory.generateBtn') }}
      </button>
    </div>

    <!-- Theory Content -->
    <div v-else-if="hasTheory" class="theory-content">
      <!-- Two Column Layout -->
      <div class="theory-layout">
        <!-- Left: Whiteboard -->
        <div class="whiteboard-section">
          <div class="whiteboard-header">
            <span class="whiteboard-icon">&#128203;</span>
            <span>{{ $t('chapterTheory.whiteboard.title') }}</span>
          </div>

          <div class="whiteboard-container" :class="{ animating: isAnimating }">
            <InteractiveWhiteboard
              ref="whiteboardRef"
              :width="480"
              :height="320"
              :show-controls="false"
              background-color="#1e293b"
              text-color="#f1f5f9"
              @action-complete="onActionComplete"
            />
          </div>

          <!-- TTS Controls -->
          <div class="tts-controls">
            <button
              v-if="!isPlaying"
              class="play-btn"
              :disabled="isAnimating"
              @click="startExplanation"
            >
              <span class="btn-icon">&#9654;</span>
              {{ $t('chapterTheory.controls.startExplanation') }}
            </button>
            <button
              v-else
              class="stop-btn"
              @click="stopExplanation"
            >
              <span class="btn-icon">&#9632;</span>
              {{ $t('chapterTheory.controls.stop') }}
            </button>

            <div class="voice-select">
              <label>{{ $t('chapterTheory.controls.voice') }}</label>
              <select v-model="selectedVoice">
                <option value="nova">{{ $t('chapterTheory.voices.nova') }}</option>
                <option value="alloy">{{ $t('chapterTheory.voices.alloy') }}</option>
                <option value="echo">{{ $t('chapterTheory.voices.echo') }}</option>
                <option value="onyx">{{ $t('chapterTheory.voices.onyx') }}</option>
                <option value="fable">{{ $t('chapterTheory.voices.fable') }}</option>
                <option value="shimmer">{{ $t('chapterTheory.voices.shimmer') }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Right: Theory Text -->
        <div class="text-section">
          <!-- Overview -->
          <div v-if="theoryContent.overview" class="theory-block overview">
            <h3><span class="block-icon">&#128161;</span> {{ $t('chapterTheory.blocks.overview') }}</h3>
            <p>{{ theoryContent.overview }}</p>
          </div>

          <!-- Learning Goals -->
          <div v-if="theoryContent.learningGoals?.length" class="theory-block goals">
            <h3><span class="block-icon">&#127919;</span> {{ $t('chapterTheory.blocks.learningGoals') }}</h3>
            <ul>
              <li v-for="(goal, i) in theoryContent.learningGoals" :key="i">
                {{ goal }}
              </li>
            </ul>
          </div>

          <!-- Concepts -->
          <div v-if="theoryContent.concepts?.length" class="theory-block concepts">
            <h3><span class="block-icon">&#128218;</span> {{ $t('chapterTheory.blocks.coreConcepts') }}</h3>
            <div class="concepts-grid">
              <div
                v-for="(concept, i) in theoryContent.concepts"
                :key="i"
                class="concept-card"
              >
                <div class="concept-header">
                  <span v-if="concept.emoji" class="concept-emoji">{{ concept.emoji }}</span>
                  <span class="concept-title">{{ concept.title }}</span>
                </div>
                <p class="concept-desc">
                  {{ concept.description || concept.oneLiner }}
                </p>
                <p v-if="concept.example" class="concept-example">
                  <strong>{{ $t('chapterTheory.blocks.example') }}</strong> {{ concept.example }}
                </p>
                <p v-if="concept.tip" class="concept-tip">
                  <span>&#128161;</span> {{ concept.tip }}
                </p>
              </div>
            </div>
          </div>

          <!-- Terms -->
          <div v-if="theoryContent.terms?.length" class="theory-block terms">
            <h3><span class="block-icon">&#128214;</span> {{ $t('chapterTheory.blocks.importantTerms') }}</h3>
            <div class="terms-list">
              <div v-for="(term, i) in theoryContent.terms" :key="i" class="term-item">
                <span class="term-name">{{ term.term }}</span>
                <span class="term-def">{{ term.definition || term.simple }}</span>
              </div>
            </div>
          </div>

          <!-- Exam Tips -->
          <div v-if="theoryContent.examTips?.length" class="theory-block exam-tips">
            <h3><span class="block-icon">&#128293;</span> {{ $t('chapterTheory.blocks.examTips') }}</h3>
            <ul class="tips-list">
              <li v-for="(tip, i) in theoryContent.examTips" :key="i">
                {{ tip }}
              </li>
            </ul>
          </div>

          <!-- Summary -->
          <div v-if="theoryContent.summary" class="theory-block summary">
            <h3><span class="block-icon">&#128221;</span> {{ $t('chapterTheory.blocks.summary') }}</h3>
            <p>{{ theoryContent.summary }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { InteractiveWhiteboard } from '@/components/system-features/tutor/user'
import http from '@/api/http'

const { t } = useI18n()

// ============================================================================
// Props & Emits
// ============================================================================

interface WhiteboardAction {
  type: 'write' | 'draw' | 'highlight' | 'arrow' | 'underline' | 'box' | 'clear' | 'schema'
  content?: string
  position?: { x: number, y: number }
  endPosition?: { x: number, y: number }
  duration?: number
  color?: string
  fontSize?: number
  schema?: Array<{ name: string, operator: string, value: string, highlight?: boolean }>
}

interface TheoryListItem {
  theoryId: string
  title: string
  style: string
  hasAudio: boolean
  createdAt: string
}

interface Props {
  chapterId: string
  chapterTitle: string
  courseTitle?: string
  theory: any
  loading?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'generate'): void
  (e: 'start-explanation'): void
  (e: 'select-theory', theoryId: string): void
}>()

// ============================================================================
// State
// ============================================================================

const whiteboardRef = ref<InstanceType<typeof InteractiveWhiteboard> | null>(null)
const isAnimating = ref(false)
const isPlaying = ref(false)
const currentActionIndex = ref(0)
const selectedVoice = ref('nova')

// Theory list management
const theoryList = ref<TheoryListItem[]>([])
const selectedTheoryId = ref<string | null>(null)

// Audio element for TTS
let audioElement: HTMLAudioElement | null = null

// ============================================================================
// Theory List Functions
// ============================================================================

async function loadTheoryList() {
  if (!props.chapterId) return

  try {
    const response = await http.get(`/chapters/${props.chapterId}/theories`)
    if (response.data.success) {
      theoryList.value = response.data.data.theories || []

      // Auto-select first if we have theories but none selected
      if (theoryList.value.length > 0 && !selectedTheoryId.value) {
        selectedTheoryId.value = theoryList.value[0].theoryId
      }
    }
  } catch (error) {
    console.error('Failed to load theory list:', error)
    theoryList.value = []
  }
}

function onTheorySelect() {
  if (selectedTheoryId.value) {
    emit('select-theory', selectedTheoryId.value)
  }
}

function getStyleEmoji(style: string): string {
  const emojis: Record<string, string> = {
    'adhs': '🎯',
    'detailed': '📚',
    'short': '⚡',
    'exam_focus': '📝',
    'standard': '📄'
  }
  return emojis[style] || '📄'
}

// Load theory list on mount and when chapterId changes
onMounted(() => {
  loadTheoryList()
})

watch(() => props.chapterId, () => {
  theoryList.value = []
  selectedTheoryId.value = null
  loadTheoryList()
})

// ============================================================================
// Computed
// ============================================================================

const hasTheory = computed(() => {
  return props.theory?.hasTheory && props.theory?.theory
})

const theoryContent = computed(() => {
  return props.theory?.theory || {}
})

const whiteboardActions = computed((): WhiteboardAction[] => {
  return theoryContent.value.whiteboardActions || []
})

const audioUrl = computed(() => {
  return props.theory?.audioUrl
})

// ============================================================================
// Methods
// ============================================================================

const onActionComplete = (action: WhiteboardAction) => {
  console.log('Action complete:', action.type)
}

const startExplanation = async () => {
  if (!whiteboardRef.value) return

  isPlaying.value = true
  isAnimating.value = true
  currentActionIndex.value = 0

  // Clear whiteboard first
  whiteboardRef.value.clearBoard()

  // Start TTS if audio URL available
  if (audioUrl.value) {
    playAudio(audioUrl.value)
  }

  // Execute whiteboard actions
  if (whiteboardActions.value.length > 0) {
    await whiteboardRef.value.executeActions(whiteboardActions.value)
  }

  isAnimating.value = false
}

const stopExplanation = () => {
  isPlaying.value = false
  isAnimating.value = false

  // Stop audio
  if (audioElement) {
    audioElement.pause()
    audioElement.currentTime = 0
  }
}

const playAudio = (url: string) => {
  // Clean up previous audio
  if (audioElement) {
    audioElement.pause()
    audioElement = null
  }

  audioElement = new Audio(url)
  audioElement.onended = () => {
    isPlaying.value = false
  }
  audioElement.onerror = (e) => {
    console.error('Audio playback error:', e)
    isPlaying.value = false
  }
  audioElement.play().catch(err => {
    console.error('Failed to play audio:', err)
  })
}

// Cleanup on unmount
watch(() => props.chapterId, () => {
  stopExplanation()
})
</script>

<style scoped>
.chapter-theory-section {
  min-height: 400px;
}

/* Theory Selector */
.theory-selector {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--color-surface, #1e293b);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  margin-bottom: 1rem;
}

.selector-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.selector-left label {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
}

.theory-dropdown {
  padding: 0.5rem 0.75rem;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 0.5rem;
  color: var(--color-text-primary, #f1f5f9);
  font-size: 0.875rem;
  min-width: 200px;
  cursor: pointer;
}

.theory-dropdown:hover {
  border-color: rgba(99, 102, 241, 0.5);
}

.theory-dropdown:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.theory-count {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #64748b);
  background: rgba(99, 102, 241, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
}

.new-theory-btn {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.new-theory-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(99, 102, 241, 0.2);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-hint {
  font-size: 0.875rem;
  color: var(--color-text-tertiary, #64748b);
  margin-top: 0.5rem;
}

/* No Theory State */
.no-theory-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: var(--color-surface, #1e293b);
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.no-theory-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.no-theory-state h3 {
  font-size: 1.5rem;
  margin: 0 0 0.5rem;
}

.no-theory-state p {
  color: var(--color-text-secondary, #94a3b8);
  margin: 0 0 0.5rem;
}

.info-text {
  font-size: 0.875rem;
  max-width: 400px;
  margin-bottom: 1.5rem !important;
}

.generate-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
}

.btn-icon {
  font-size: 1.2rem;
}

/* Theory Content */
.theory-content {
  background: var(--color-surface, #1e293b);
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.theory-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

@media (max-width: 1024px) {
  .theory-layout {
    grid-template-columns: 1fr;
  }
}

/* Whiteboard Section */
.whiteboard-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.whiteboard-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.whiteboard-icon {
  font-size: 1rem;
}

.whiteboard-container {
  background: #0f172a;
  border-radius: 0.75rem;
  padding: 0.5rem;
  border: 1px solid rgba(99, 102, 241, 0.2);
  transition: border-color 0.3s, box-shadow 0.3s;
}

.whiteboard-container.animating {
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
}

/* TTS Controls */
.tts-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.play-btn, .stop-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.play-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.play-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.play-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stop-btn {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.stop-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.voice-select {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
}

.voice-select select {
  padding: 0.5rem 0.75rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.375rem;
  color: var(--color-text-primary, #f1f5f9);
  font-size: 0.875rem;
}

/* Text Section */
.text-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.text-section::-webkit-scrollbar {
  width: 6px;
}

.text-section::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.text-section::-webkit-scrollbar-thumb {
  background: rgba(99, 102, 241, 0.3);
  border-radius: 3px;
}

/* Theory Blocks */
.theory-block {
  padding: 1rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.theory-block h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.75rem;
  color: var(--color-text-primary, #f1f5f9);
}

.block-icon {
  font-size: 1.1rem;
}

.theory-block p {
  margin: 0;
  color: var(--color-text-secondary, #94a3b8);
  line-height: 1.6;
}

.theory-block ul {
  margin: 0;
  padding-left: 1.5rem;
  color: var(--color-text-secondary, #94a3b8);
}

.theory-block li {
  margin-bottom: 0.25rem;
}

/* Concepts Grid */
.concepts-grid {
  display: grid;
  gap: 1rem;
}

.concept-card {
  padding: 1rem;
  background: rgba(99, 102, 241, 0.05);
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: 0.5rem;
}

.concept-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.concept-emoji {
  font-size: 1.25rem;
}

.concept-title {
  font-weight: 600;
  color: var(--color-text-primary, #f1f5f9);
}

.concept-desc {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
  margin: 0 0 0.5rem;
}

.concept-example {
  font-size: 0.8rem;
  color: var(--color-text-tertiary, #64748b);
  margin: 0 0 0.25rem;
}

.concept-tip {
  display: flex;
  align-items: flex-start;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #f59e0b;
  margin: 0;
  padding-top: 0.5rem;
  border-top: 1px dashed rgba(245, 158, 11, 0.3);
}

/* Terms List */
.terms-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.term-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.term-item:last-child {
  border-bottom: none;
}

.term-name {
  font-weight: 600;
  color: #818cf8;
  min-width: 120px;
}

.term-def {
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.875rem;
}

/* Tips List */
.tips-list li {
  position: relative;
  padding-left: 0.25rem;
}

.tips-list li::marker {
  color: #f59e0b;
}

/* Summary Block */
.summary {
  background: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.1);
}

.summary h3 {
  color: #10b981;
}
</style>
