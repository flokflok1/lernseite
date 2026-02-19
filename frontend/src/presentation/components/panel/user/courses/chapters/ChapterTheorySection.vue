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
    <div v-else-if="!explanation.hasTheory.value && theoryList.length === 0" class="no-theory-state">
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
    <div v-else-if="explanation.hasTheory.value" class="theory-content">
      <div class="theory-layout">
        <!-- Left: Whiteboard -->
        <TheoryWhiteboardPanel
          ref="whiteboardPanelRef"
          :is-animating="explanation.isAnimating.value"
          :is-playing="explanation.isPlaying.value"
          :selected-voice="explanation.selectedVoice.value"
          @start="handleStartExplanation"
          @stop="explanation.stopExplanation"
          @action-complete="explanation.onActionComplete"
          @update:selected-voice="explanation.selectedVoice.value = $event"
        />

        <!-- Right: Theory Text -->
        <TheoryTextContent :content="explanation.theoryContent.value" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, toRef } from 'vue'
import http from '@/infrastructure/api/http'
import TheoryWhiteboardPanel from './TheoryWhiteboardPanel.vue'
import TheoryTextContent from './TheoryTextContent.vue'
import { useTheoryExplanation } from './composables/useTheoryExplanation'

// ============================================================================
// Props & Emits
// ============================================================================

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

const theoryList = ref<TheoryListItem[]>([])
const selectedTheoryId = ref<string | null>(null)
const whiteboardPanelRef = ref<InstanceType<typeof TheoryWhiteboardPanel> | null>(null)

// ============================================================================
// Composable
// ============================================================================

const explanation = useTheoryExplanation({
  theory: toRef(props, 'theory'),
  chapterId: toRef(props, 'chapterId')
})

// ============================================================================
// Theory List Functions
// ============================================================================

async function loadTheoryList(): Promise<void> {
  if (!props.chapterId) return

  try {
    const response = await http.get(`/chapters/${props.chapterId}/theories`)
    if (response.data.success) {
      theoryList.value = response.data.data.theories || []

      if (theoryList.value.length > 0 && !selectedTheoryId.value) {
        selectedTheoryId.value = theoryList.value[0].theoryId
      }
    }
  } catch (error) {
    console.error('Failed to load theory list:', error)
    theoryList.value = []
  }
}

function onTheorySelect(): void {
  if (selectedTheoryId.value) {
    emit('select-theory', selectedTheoryId.value)
  }
}

function getStyleEmoji(style: string): string {
  const emojis: Record<string, string> = {
    'adhs': '\uD83C\uDFAF',
    'detailed': '\uD83D\uDCDA',
    'short': '\u26A1',
    'exam_focus': '\uD83D\uDCDD',
    'standard': '\uD83D\uDCC4'
  }
  return emojis[style] || '\uD83D\uDCC4'
}

async function handleStartExplanation(): Promise<void> {
  // Wire the whiteboard ref from the child panel to the composable
  if (whiteboardPanelRef.value?.whiteboardRef) {
    explanation.whiteboardRef.value = whiteboardPanelRef.value.whiteboardRef
  }
  await explanation.startExplanation()
}

// ============================================================================
// Lifecycle & Watchers
// ============================================================================

onMounted(() => {
  loadTheoryList()
})

watch(() => props.chapterId, () => {
  theoryList.value = []
  selectedTheoryId.value = null
  loadTheoryList()
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
</style>
