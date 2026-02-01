<!--
  ChapterTheoryView - Chapter Theory Management Component

  Displays and manages chapter theories (Theorieblätter).
  Uses useTheoryManagement composable for data loading.
-->

<template>
  <div class="chapter-theory-view">
    <!-- Header -->
    <div class="view-header">
      <div class="header-icon">📚</div>
      <div class="header-info">
        <h2>{{ $t('windows.chapterTheoryView.title') }}</h2>
        <p>{{ chapter?.title }} • {{ course?.title }}</p>
      </div>
      <div class="header-stats">
        <div class="stat">
          <span class="stat-value">{{ chapterTheories.length }}</span>
          <span class="stat-label">{{ $t('windows.chapterTheoryView.available') }}</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ selectedTheoryId ? 1 : 0 }}</span>
          <span class="stat-label">{{ $t('windows.chapterTheoryView.selected') }}</span>
        </div>
      </div>
    </div>

    <!-- Three-Column Layout -->
    <div class="main-layout">
      <!-- Left: Theory List -->
      <div class="list-panel">
        <div class="panel-header">
          <span class="panel-icon">📚</span>
          <span class="panel-title">{{ $t('windows.chapterTheoryView.theories') }}</span>
          <button @click="loadTheories" class="refresh-btn" :title="$t('windows.chapterTheoryView.refresh')">🔄</button>
        </div>

        <!-- Loading -->
        <div v-if="isLoading" class="list-loading">
          <div class="spinner"></div>
          <span>{{ $t('windows.chapterTheoryView.loading') }}</span>
        </div>

        <!-- Theory List -->
        <div v-else class="content-list">
          <div v-if="chapterTheories.length === 0" class="list-empty">
            <span class="empty-icon-small">📝</span>
            <p>{{ $t('windows.chapterTheoryView.noTheories') }}</p>
          </div>
          <div
            v-for="theory in chapterTheories"
            :key="theory.theoryId"
            class="list-item"
            :class="{ active: selectedTheoryId === theory.theoryId }"
            @click="onSelectTheory(theory.theoryId)"
          >
            <div class="item-icon">{{ getStyleEmoji(theory.style) }}</div>
            <div class="item-info">
              <span class="item-name">{{ theory.title }}</span>
              <span class="item-meta">{{ formatDate(theory.createdAt) }}</span>
            </div>
            <div class="item-actions">
              <button v-if="theory.audioUrl" @click.stop="playAudio(theory.audioUrl)" class="item-btn" :title="$t('windows.chapterTheoryView.playAudio')">
                🔊
              </button>
              <button @click.stop="onDeleteTheory(theory.theoryId)" class="item-btn danger" :title="$t('windows.chapterTheoryView.delete')">🗑️</button>
            </div>
          </div>
        </div>

        <!-- Create New Button -->
        <div class="list-actions">
          <button @click="showCreateForm = true" class="create-btn">
            {{ $t('windows.chapterTheoryView.createNew') }}
          </button>
        </div>
      </div>

      <!-- Middle: Detail/Generator Panel -->
      <div class="detail-panel">
        <div class="panel-header">
          <span class="panel-icon">{{ showCreateForm ? '✨' : '📄' }}</span>
          <span class="panel-title">{{ showCreateForm ? $t('windows.chapterTheoryView.newTheory') : $t('windows.chapterTheoryView.preview') }}</span>
        </div>

        <!-- Create Form -->
        <div v-if="showCreateForm" class="create-form">
          <div class="form-section">
            <label>{{ $t('windows.chapterTheoryView.titleLabel') }}</label>
            <input v-model="newTitle" type="text" class="form-input" :placeholder="$t('windows.chapterTheoryView.titlePlaceholder')" />
          </div>

          <div class="form-section">
            <label>{{ $t('windows.chapterTheoryView.styleLabel') }}</label>
            <select v-model="selectedStyle" class="form-select">
              <option value="standard">{{ $t('windows.chapterTheoryView.styles.standard') }}</option>
              <option value="compact">{{ $t('windows.chapterTheoryView.styles.compact') }}</option>
              <option value="detailed">{{ $t('windows.chapterTheoryView.styles.detailed') }}</option>
              <option value="visual">{{ $t('windows.chapterTheoryView.styles.visual') }}</option>
              <option value="exam">{{ $t('windows.chapterTheoryView.styles.exam') }}</option>
            </select>
          </div>

          <div class="form-section">
            <label class="checkbox-label">
              <input type="checkbox" v-model="generateWithAudio" />
              {{ $t('windows.chapterTheoryView.generateWithAudio') }}
            </label>
          </div>

          <button
            @click="generateNewTheory"
            class="generate-btn"
            :disabled="isGenerating"
          >
            <span v-if="isGenerating">{{ $t('windows.chapterTheoryView.generating') }}</span>
            <span v-else>{{ $t('windows.chapterTheoryView.generate') }}</span>
          </button>

          <button @click="showCreateForm = false" class="cancel-btn">
            {{ $t('windows.chapterTheoryView.cancel') }}
          </button>
        </div>

        <!-- Theory Detail View -->
        <div v-else-if="selectedTheory" class="theory-detail">
          <div class="theory-header">
            <h3>{{ currentTheoryTitle }}</h3>
            <span class="style-badge">{{ getStyleEmoji(currentTheoryStyle) }} {{ getStyleName(currentTheoryStyle) }}</span>
          </div>

          <div class="theory-content">
            <!-- Overview -->
            <div v-if="selectedTheory.overview" class="theory-section">
              <h4>{{ $t('windows.chapterTheoryView.sections.overview') }}</h4>
              <p>{{ selectedTheory.overview }}</p>
            </div>

            <!-- Learning Goals -->
            <div v-if="selectedTheory.learningGoals?.length" class="theory-section">
              <h4>{{ $t('windows.chapterTheoryView.sections.learningGoals') }}</h4>
              <ul>
                <li v-for="(goal, i) in selectedTheory.learningGoals" :key="i">{{ goal }}</li>
              </ul>
            </div>

            <!-- Concepts -->
            <div v-if="selectedTheory.concepts?.length" class="theory-section">
              <h4>{{ $t('windows.chapterTheoryView.sections.concepts') }}</h4>
              <div v-for="(concept, i) in selectedTheory.concepts" :key="i" class="concept-item">
                <strong>{{ concept.name }}</strong>
                <p>{{ concept.description }}</p>
              </div>
            </div>

            <!-- Terms -->
            <div v-if="selectedTheory.terms?.length" class="theory-section">
              <h4>{{ $t('windows.chapterTheoryView.sections.terms') }}</h4>
              <dl class="terms-list">
                <template v-for="(term, i) in selectedTheory.terms" :key="i">
                  <dt>{{ term.term }}</dt>
                  <dd>{{ term.definition }}</dd>
                </template>
              </dl>
            </div>

            <!-- Exam Relevance -->
            <div v-if="selectedTheory.examRelevance" class="theory-section exam-section">
              <h4>{{ $t('windows.chapterTheoryView.sections.examRelevance') }}</h4>
              <p>{{ selectedTheory.examRelevance }}</p>
            </div>

            <!-- Exam Tips -->
            <div v-if="selectedTheory.examTips?.length" class="theory-section">
              <h4>{{ $t('windows.chapterTheoryView.sections.examTips') }}</h4>
              <ul>
                <li v-for="(tip, i) in selectedTheory.examTips" :key="i">{{ tip }}</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- No Selection -->
        <div v-else class="no-selection">
          <span class="empty-icon">📄</span>
          <p>{{ $t('windows.chapterTheoryView.noSelection') }}</p>
        </div>
      </div>

      <!-- Right: Settings Panel -->
      <div class="settings-panel">
        <div class="panel-header">
          <span class="panel-icon">⚙️</span>
          <span class="panel-title">{{ $t('windows.chapterTheoryView.settings') }}</span>
        </div>

        <div class="settings-content">
          <!-- TTS Settings -->
          <div class="settings-section">
            <h4>{{ $t('windows.chapterTheoryView.tts.title') }}</h4>
            <div class="setting-row">
              <label>{{ $t('windows.chapterTheoryView.tts.enabled') }}</label>
              <button @click="tts.toggleTTS()" class="toggle-btn" :class="{ active: tts.ttsEnabled.value }">
                {{ tts.ttsEnabled.value ? $t('windows.chapterTheoryView.tts.on') : $t('windows.chapterTheoryView.tts.off') }}
              </button>
            </div>
            <div class="setting-row">
              <label>{{ $t('windows.chapterTheoryView.tts.voice') }}</label>
              <select v-model="tts.selectedVoice.value" class="setting-select">
                <option v-for="voice in tts.voices.value" :key="voice.id" :value="voice.id">
                  {{ voice.name }}
                </option>
              </select>
            </div>
            <div class="setting-row">
              <label>{{ $t('windows.chapterTheoryView.tts.model') }}</label>
              <select v-model="tts.selectedModel.value" class="setting-select">
                <option value="browser">{{ $t('windows.chapterTheoryView.tts.models.browser') }}</option>
                <option value="tts-1">{{ $t('windows.chapterTheoryView.tts.models.tts1') }}</option>
                <option value="tts-1-hd">{{ $t('windows.chapterTheoryView.tts.models.tts1hd') }}</option>
              </select>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="settings-section">
            <h4>{{ $t('windows.chapterTheoryView.quickActions.title') }}</h4>
            <button v-if="selectedTheory" @click="regenerateTheory" class="quick-action-btn">
              {{ $t('windows.chapterTheoryView.quickActions.regenerate') }}
            </button>
            <button v-if="selectedTheory" @click="copyToClipboard" class="quick-action-btn">
              {{ $t('windows.chapterTheoryView.quickActions.copy') }}
            </button>
            <button v-if="selectedTheory" @click="printTheory" class="quick-action-btn">
              {{ $t('windows.chapterTheoryView.quickActions.print') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="error-banner">
      <span>⚠️ {{ error }}</span>
      <button @click="clearError">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTheoryManagement } from '@/application/composables/useTheoryManagement'
import { useTTS } from '@/application/composables/useTTS'
import http from '@/application/services/api/system'

const { t } = useI18n()

// ============================================================================
// Props & Emits
// ============================================================================

interface Course {
  course_id: string
  title: string
}

interface Chapter {
  chapter_id: string
  title: string
}

const props = defineProps<{
  course: Course | null
  chapter: Chapter | null
}>()

const emit = defineEmits<{
  (e: 'generated', theoryId: string): void
  (e: 'deleted', theoryId: string): void
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
const newTitle = ref('')
const selectedStyle = ref('standard')
const generateWithAudio = ref(false)
const isGenerating = ref(false)
const localError = ref<string | null>(null)

// ============================================================================
// Computed (delegate to composable)
// ============================================================================

const chapterTheories = computed(() => theoryMgmt.chapterTheories.value)
const isLoading = computed(() => theoryMgmt.isLoading.value)
const selectedTheoryId = computed(() => theoryMgmt.selectedTheoryId.value)
const selectedTheory = computed(() => theoryMgmt.selectedTheory.value)
const currentTheoryTitle = computed(() => theoryMgmt.currentTheoryTitle.value)
const currentTheoryStyle = computed(() => theoryMgmt.currentTheoryStyle.value)
const error = computed(() => localError.value || theoryMgmt.error.value)

// ============================================================================
// Methods
// ============================================================================

async function loadTheories() {
  if (props.chapter?.chapter_id) {
    await theoryMgmt.loadChapterTheories(props.chapter.chapter_id)
  }
}

async function onSelectTheory(theoryId: string) {
  await theoryMgmt.selectTheory(theoryId)
  showCreateForm.value = false
}

async function onDeleteTheory(theoryId: string) {
  if (!confirm(t('windows.chapterTheoryView.confirmDelete'))) return

  const success = await theoryMgmt.deleteTheory(theoryId)
  if (success) {
    emit('deleted', theoryId)
  }
}

async function generateNewTheory() {
  if (!props.chapter?.chapter_id) return

  isGenerating.value = true
  localError.value = null

  try {
    const response = await http.post('/admin/ai/generate-chapter-theory', {
      chapter_id: props.chapter.chapter_id,
      style: selectedStyle.value,
      title: newTitle.value || undefined,
      generate_tts: generateWithAudio.value
    })

    if (response.data.success) {
      // Reload theories list
      await loadTheories()
      showCreateForm.value = false
      newTitle.value = ''

      // Select the new theory if we have an ID
      const newTheoryId = response.data.data?.theory_id
      if (newTheoryId) {
        await theoryMgmt.selectTheory(newTheoryId)
        emit('generated', newTheoryId)
      }
    } else {
      throw new Error(response.data.error?.message || t('windows.chapterTheoryView.generationFailed'))
    }
  } catch (err: any) {
    console.error('Theory generation failed:', err)
    localError.value = err.response?.data?.error?.message || err.message || t('windows.chapterTheoryView.generationError')
  } finally {
    isGenerating.value = false
  }
}

async function regenerateTheory() {
  if (selectedTheoryId.value) {
    selectedStyle.value = currentTheoryStyle.value || 'standard'
    showCreateForm.value = true
  }
}

function playAudio(url: string) {
  tts.playAudioUrl(url)
}

function copyToClipboard() {
  if (!selectedTheory.value) return

  const content = [
    `# ${currentTheoryTitle.value}`,
    '',
    selectedTheory.value.overview,
    '',
    t('windows.chapterTheoryView.clipboard.learningGoals'),
    ...(selectedTheory.value.learningGoals || []).map(g => `- ${g}`),
    '',
    t('windows.chapterTheoryView.clipboard.concepts'),
    ...(selectedTheory.value.concepts || []).map(c => `### ${c.name}\n${c.description}`),
    '',
    t('windows.chapterTheoryView.clipboard.terms'),
    ...(selectedTheory.value.terms || []).map(t => `**${t.term}**: ${t.definition}`)
  ].join('\n')

  navigator.clipboard.writeText(content)
}

function printTheory() {
  window.print()
}

function clearError() {
  localError.value = null
}

// Utility functions from composable
const { getStyleEmoji, getStyleName, formatDate } = theoryMgmt

// ============================================================================
// Watchers & Lifecycle
// ============================================================================

watch(() => props.chapter, async (newChapter) => {
  theoryMgmt.reset()
  showCreateForm.value = false

  if (newChapter?.chapter_id) {
    await loadTheories()
  }
}, { immediate: true })

onMounted(() => {
  tts.loadModels()
})
</script>

<style scoped>
.chapter-theory-view {
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
  color: var(--color-text-primary);
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
  grid-template-columns: 280px 1fr 280px;
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
  transition: opacity 0.2s;
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
  display: flex;
  gap: 0.25rem;
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
  transition: opacity 0.15s;
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
  transition: transform 0.15s, box-shadow 0.15s;
}

.create-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Create Form */
.create-form {
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

.form-input,
.form-select {
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: var(--color-surface);
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--color-primary);
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
  transition: transform 0.15s;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
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

/* Theory Detail */
.theory-detail {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.theory-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.theory-header h3 {
  margin: 0;
  font-size: 1.125rem;
}

.style-badge {
  padding: 0.25rem 0.75rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 1rem;
  font-size: 0.75rem;
}

.theory-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.theory-section h4 {
  margin: 0 0 0.5rem;
  font-size: 0.9375rem;
  color: var(--color-text-primary);
}

.theory-section p {
  margin: 0;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.theory-section ul {
  margin: 0;
  padding-left: 1.25rem;
}

.theory-section li {
  margin-bottom: 0.375rem;
  color: var(--color-text-secondary);
}

.concept-item {
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
}

.concept-item strong {
  color: var(--color-primary);
}

.concept-item p {
  margin-top: 0.25rem;
}

.terms-list {
  margin: 0;
}

.terms-list dt {
  font-weight: 600;
  color: var(--color-text-primary);
  margin-top: 0.5rem;
}

.terms-list dd {
  margin: 0.25rem 0 0 0;
  color: var(--color-text-secondary);
}

.exam-section {
  padding: 1rem;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 191, 36, 0.1) 100%);
  border-radius: 0.5rem;
  border-left: 3px solid #f59e0b;
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
  color: var(--color-text-primary);
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
  max-width: 140px;
}

.toggle-btn {
  padding: 0.375rem 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.15s;
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
  transition: background 0.15s;
}

.quick-action-btn:hover {
  background: var(--color-border);
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
