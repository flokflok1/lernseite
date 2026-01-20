<!--
  Admin Lesson Preview Panel

  Loads and displays REAL lesson data from the database.
  Shows theory content and actual learning method exercises.

  Phase: D4 - KI-Authoring-Studio
-->

<template>
  <div class="lesson-preview-panel">
    <!-- Header -->
    <div class="preview-header">
      <div class="lesson-badge">{{ $t('features.lessonPreview.lessonN', { n: lessonPosition }) }}</div>
      <h1 class="lesson-title">{{ lessonData?.title || $t('features.lessonPreview.loading') }}</h1>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ $t('features.lessonPreview.loadingData') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <span class="error-icon">⚠️</span>
      <p>{{ error }}</p>
      <button @click="loadLessonData" class="retry-btn">{{ $t('features.lessonPreview.retry') }}</button>
    </div>

    <!-- Content -->
    <template v-else>
      <!-- Tabs -->
      <div class="preview-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          {{ tab.label }}
          <span v-if="tab.count !== undefined" class="tab-count">{{ tab.count }}</span>
        </button>
      </div>

      <!-- Tab Content -->
      <div class="preview-content">
        <!-- Theorie Tab -->
        <div v-if="activeTab === 'theory'" class="tab-content">
          <div v-if="lessonData?.content?.theory" class="theory-content">
            <div class="content-block" v-html="formatContent(lessonData.content.theory)"></div>
          </div>
          <div v-else-if="lessonData?.description" class="theory-content">
            <div class="content-block">
              <p>{{ lessonData.description }}</p>
            </div>
          </div>
          <div v-else class="empty-state">
            <span class="empty-icon">📝</span>
            <p>{{ $t('features.lessonPreview.noTheory') }}</p>
            <p class="empty-hint">{{ $t('features.lessonPreview.theoryHint') }}</p>
          </div>
        </div>

        <!-- Aufgaben Tab -->
        <div v-if="activeTab === 'exercises'" class="tab-content">
          <div v-if="methods.length > 0" class="exercises-list">
            <div
              v-for="(method, index) in methods"
              :key="method.method_id"
              class="exercise-card"
              :class="{ expanded: expandedMethod === method.method_id }"
            >
              <div class="exercise-header" @click="toggleMethod(method.method_id)">
                <span class="exercise-number">{{ index + 1 }}</span>
                <span class="exercise-icon">{{ getMethodIcon(method.method_type) }}</span>
                <div class="exercise-info">
                  <span class="exercise-type">{{ getMethodName(method.method_type) }}</span>
                  <span class="exercise-title">{{ cleanMethodTitle(method.method_name, method.method_type) }}</span>
                </div>
                <span class="method-badge">LM{{ String(method.method_type).padStart(2, '0') }}</span>
                <span class="expand-icon">{{ expandedMethod === method.method_id ? '▼' : '▶' }}</span>
              </div>

              <!-- Expanded Content -->
              <div v-if="expandedMethod === method.method_id" class="exercise-content">
                <!-- Render based on method type (description is AI-prompt, skip it) -->
                <component
                  :is="getMethodRenderer(method.method_type)"
                  :config="method.config"
                  :method="method"
                />
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <span class="empty-icon">📭</span>
            <p>{{ $t('features.lessonPreview.noMethods') }}</p>
            <p class="empty-hint">{{ $t('features.lessonPreview.methodsCreatedInStudio') }}</p>
          </div>
        </div>

        <!-- Info Tab -->
        <div v-if="activeTab === 'info'" class="tab-content">
          <div class="info-grid">
            <div class="info-card">
              <span class="info-label">{{ $t('features.lessonPreview.lesson') }}</span>
              <span class="info-value">{{ lessonData?.title }}</span>
            </div>
            <div class="info-card">
              <span class="info-label">{{ $t('features.lessonPreview.type') }}</span>
              <span class="info-value">{{ lessonData?.lesson_type || 'text' }}</span>
            </div>
            <div class="info-card">
              <span class="info-label">{{ $t('features.lessonPreview.duration') }}</span>
              <span class="info-value">{{ lessonData?.duration_minutes || 0 }} {{ $t('features.lessonPreview.min') }}</span>
            </div>
            <div class="info-card">
              <span class="info-label">{{ $t('features.lessonPreview.learningMethods') }}</span>
              <span class="info-value">{{ methods.length }}</span>
            </div>
            <div v-if="lessonData?.chapter_id" class="info-card full-width">
              <span class="info-label">{{ $t('features.lessonPreview.chapter') }}</span>
              <span class="info-value">{{ chapterTitle }}</span>
            </div>
            <div v-if="lessonData?.created_at" class="info-card">
              <span class="info-label">{{ $t('features.lessonPreview.created') }}</span>
              <span class="info-value">{{ formatDate(lessonData.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Footer -->
    <div class="preview-footer">
      <div class="footer-info">
        <span v-if="chapterTitle">📖 {{ chapterTitle }}</span>
      </div>
      <div class="footer-actions">
        <button class="action-btn secondary" @click="$emit('close')">{{ $t('features.lessonPreview.close') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineAsyncComponent, h } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxPanel } from '@/application/stores/modules/desktop'
import http from '@/infrastructure/api/http'

const { t, locale } = useI18n()

interface Props {
  panel: LsxPanel
}

const props = defineProps<Props>()
defineEmits<{ (e: 'close'): void }>()

// State
const loading = ref(true)
const error = ref<string | null>(null)
const lessonData = ref<any>(null)
const methods = ref<any[]>([])
const activeTab = ref('exercises')
const expandedMethod = ref<string | null>(null)

// Get lesson ID from payload
const lessonId = computed(() => {
  const payload = props.panel.payload
  return payload?.lesson?.lesson_id || payload?.lesson?.id || payload?.lessonId
})

const lessonPosition = computed(() => props.panel.payload?.position || '1')
const chapterTitle = computed(() => props.panel.payload?.chapter?.title || lessonData.value?.chapter_title || '')

// Tabs
const tabs = computed(() => [
  { id: 'exercises', label: t('features.lessonPreview.exercises'), icon: '📝', count: methods.value.length },
  { id: 'theory', label: t('features.lessonPreview.theory'), icon: '📖' },
  { id: 'info', label: t('features.lessonPreview.info'), icon: 'ℹ️' }
])

// Load data on mount
onMounted(() => {
  loadLessonData()
})

async function loadLessonData() {
  loading.value = true
  error.value = null

  try {
    // If we have a real lesson ID, load from API
    if (lessonId.value && !lessonId.value.startsWith('draft-')) {
      // Load lesson details
      const lessonResponse = await http.get(`/lessons/${lessonId.value}`)
      if (lessonResponse.data.success) {
        lessonData.value = lessonResponse.data.lesson
      }

      // Load learning methods
      const methodsResponse = await http.get(`/lessons/${lessonId.value}/methods`)
      if (methodsResponse.data.success) {
        methods.value = methodsResponse.data.methods || []
      }
    } else {
      // Use data from payload (draft mode)
      const payload = props.panel.payload?.lesson
      if (payload) {
        lessonData.value = {
          title: payload.title,
          description: payload.description,
          content: payload.content,
          duration_minutes: payload.duration_minutes,
          lesson_type: payload.lesson_type || 'text'
        }
        methods.value = payload.methods?.map((m: any) => ({
          method_id: m.id || `draft-${Math.random()}`,
          method_type: m.type,
          method_name: m.title,
          description: m.description,
          config: m.config || m.data || {}
        })) || []
      }
    }
  } catch (err: any) {
    console.error('Failed to load lesson:', err)
    error.value = err.response?.data?.error || t('features.lessonPreview.loadError')
  } finally {
    loading.value = false
  }
}

function toggleMethod(methodId: string) {
  expandedMethod.value = expandedMethod.value === methodId ? null : methodId
}

// Method Icons & Names
const methodIcons: Record<number, string> = {
  0: '📖', 1: '📝', 2: '🔄', 3: '📊', 4: '💭', 6: '🎯',
  8: '✏️', 9: '💻', 10: '🌐', 11: '🔧', 12: '🔢', 13: '🃏',
  14: '🎯', 15: '📝', 16: '🔍', 17: '🛠️', 18: '✍️', 19: '📋',
  20: '📑', 21: '⏱️', 22: '❓', 23: '✅', 24: '🎤', 25: '🏆',
  26: '👥', 27: '🤝', 28: '📊', 29: '📓', 30: '📁', 31: '🎓', 32: '🔄'
}

// Method names are loaded from i18n: features.lessonPreview.methodNames.lmN

function getMethodIcon(type: number | string | undefined): string {
  if (type === undefined || type === null) return '📚'
  const numType = typeof type === 'string' ? parseInt(type, 10) : type
  return isNaN(numType) ? '📚' : (methodIcons[numType] || '📚')
}

function getMethodName(type: number | string | undefined): string {
  if (type === undefined || type === null) return t('features.lessonPreview.methodDefault')
  const numType = typeof type === 'string' ? parseInt(type, 10) : type
  if (isNaN(numType)) return t('features.lessonPreview.methodDefault')
  const key = `features.lessonPreview.methodNames.lm${numType}`
  const name = t(key)
  // If key not found (returns the key itself), use fallback with ID
  return name === key ? t('features.lessonPreview.methodWithId', { id: numType }) : name
}

function cleanMethodTitle(title: string | undefined, methodType: number | string | undefined): string {
  if (!title) return t('features.lessonPreview.task')
  // Remove "LM12:", "LM22:", etc. prefix from title
  const numType = typeof methodType === 'string' ? parseInt(methodType, 10) : methodType
  if (numType !== undefined && !isNaN(numType)) {
    const prefix = `LM${String(numType).padStart(2, '0')}:`
    if (title.startsWith(prefix)) {
      return title.substring(prefix.length).trim()
    }
  }
  return title
}

function formatContent(content: string): string {
  if (!content) return ''
  // Basic markdown-like formatting
  return content
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

function formatDate(dateStr: string): string {
  const localeMap: Record<string, string> = { de: 'de-DE', en: 'en-US', pl: 'pl-PL' }
  return new Date(dateStr).toLocaleDateString(localeMap[locale.value] || 'de-DE', {
    day: '2-digit', month: '2-digit', year: 'numeric'
  })
}

// Dynamic method renderer component
function getMethodRenderer(methodType: number | string) {
  const type = typeof methodType === 'string' ? parseInt(methodType, 10) : methodType

  // Return a simple renderer based on method type
  return {
    props: ['config', 'method'],
    setup(props: any) {
      let config = props.config || {}

      // Handle raw_content (sometimes data is nested as string)
      if (config.raw_content && typeof config.raw_content === 'string') {
        try {
          config = { ...config, ...JSON.parse(config.raw_content) }
        } catch (e) { /* ignore parse errors */ }
      }

      // LM12 - Mathe-Interaktiv (uses "steps" in DB, not "exercises")
      if (type === 12) {
        const items = config.steps || config.exercises || []
        return () => h('div', { class: 'method-preview' }, [
          items.length > 0 ? [
            h('h4', t('features.lessonPreview.stepCount', { count: items.length })),
            h('div', { class: 'exercises-preview' },
              items.slice(0, 3).map((step: any, i: number) =>
                h('div', { class: 'exercise-item' }, [
                  h('span', { class: 'exercise-label' }, t('features.lessonPreview.stepLabel', { n: step.id || i + 1 })),
                  h('span', { class: 'exercise-text' },
                    step.prompt?.substring(0, 150) + (step.prompt?.length > 150 ? '...' : '') ||
                    step.question || step.text || t('features.lessonPreview.task')
                  )
                ])
              )
            ),
            items.length > 3 ?
              h('p', { class: 'more-hint' }, t('features.lessonPreview.moreSteps', { count: items.length - 3 })) : null
          ] : h('p', { class: 'no-content' }, t('features.lessonPreview.noStepsConfigured'))
        ])
      }

      // LM22 - Quiz (data can be array directly or {questions: [...]})
      if (type === 22) {
        const questions = Array.isArray(config) ? config : (config.questions || [])
        return () => h('div', { class: 'method-preview' }, [
          questions.length > 0 ? [
            h('h4', t('features.lessonPreview.questionCount', { count: questions.length })),
            h('div', { class: 'questions-preview' },
              questions.slice(0, 3).map((q: any, i: number) =>
                h('div', { class: 'question-item' }, [
                  h('span', { class: 'question-label' }, t('features.lessonPreview.questionLabel', { n: i + 1 })),
                  h('span', { class: 'question-text' }, q.question || q.text),
                  q.options ? h('div', { class: 'answers' },
                    q.options.map((opt: string, idx: number) => h('div', {
                      class: ['answer', q.correct_index === idx ? 'correct' : '']
                    }, opt))
                  ) : q.answers ? h('div', { class: 'answers' },
                    q.answers.map((a: any) => h('div', {
                      class: ['answer', a.correct ? 'correct' : '']
                    }, a.text || a))
                  ) : null
                ])
              )
            ),
            questions.length > 3 ?
              h('p', { class: 'more-hint' }, t('features.lessonPreview.moreQuestions', { count: questions.length - 3 })) : null
          ] : h('p', { class: 'no-content' }, t('features.lessonPreview.noQuestionsConfigured'))
        ])
      }

      // LM13 - Flashcards (data can be array directly or {cards: [...]})
      if (type === 13) {
        const cards = Array.isArray(config) ? config : (config.cards || [])
        return () => h('div', { class: 'method-preview' }, [
          cards.length > 0 ? [
            h('h4', t('features.lessonPreview.cardCount', { count: cards.length })),
            h('div', { class: 'cards-preview' },
              cards.slice(0, 3).map((card: any, i: number) =>
                h('div', { class: 'card-item' }, [
                  h('div', { class: 'card-front' }, [t('features.lessonPreview.cardFront') + ' ', (card.front || card.question || t('features.lessonPreview.cardN', { n: i + 1 }))?.substring(0, 80)]),
                  h('div', { class: 'card-back' }, [t('features.lessonPreview.cardBack') + ' ', (card.back || card.answer || '')?.substring(0, 100) + '...'])
                ])
              )
            ),
            cards.length > 3 ?
              h('p', { class: 'more-hint' }, t('features.lessonPreview.moreCards', { count: cards.length - 3 })) : null
          ] : h('p', { class: 'no-content' }, t('features.lessonPreview.noCardsConfigured'))
        ])
      }

      // Default renderer - show data summary
      const dataKeys = Array.isArray(config) ? ['items'] : Object.keys(config)
      const itemCount = Array.isArray(config) ? config.length :
        (config.steps?.length || config.questions?.length || config.cards?.length || config.items?.length || 0)

      return () => h('div', { class: 'method-preview' }, [
        itemCount > 0 ? [
          h('h4', t('features.lessonPreview.elementCount', { count: itemCount })),
          h('p', { class: 'data-hint' }, t('features.lessonPreview.dataFields', { fields: dataKeys.join(', ') })),
          h('details', { class: 'config-details' }, [
            h('summary', t('features.lessonPreview.showJsonData')),
            h('pre', { class: 'config-json' }, JSON.stringify(config, null, 2).substring(0, 1000))
          ])
        ] : dataKeys.length > 0 && !Array.isArray(config) ? [
          h('h4', t('features.lessonPreview.configuration')),
          h('p', { class: 'data-hint' }, t('features.lessonPreview.fields', { fields: dataKeys.join(', ') })),
          h('details', { class: 'config-details' }, [
            h('summary', t('features.lessonPreview.showJsonData')),
            h('pre', { class: 'config-json' }, JSON.stringify(config, null, 2).substring(0, 1000))
          ])
        ] : h('p', { class: 'no-content' }, t('features.lessonPreview.noConfiguration'))
      ])
    }
  }
}
</script>

<style scoped>
.lesson-preview-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

/* Header */
.preview-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
  color: white;
}

.lesson-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.lesson-title {
  flex: 1;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  width: 2rem;
  height: 2rem;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 0.5rem;
  font-size: 1.25rem;
  cursor: pointer;
}

/* Loading & Error */
.loading-state, .error-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: var(--color-text-secondary);
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon { font-size: 2rem; }
.retry-btn {
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
}

/* Tabs */
.preview-tabs {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.15s;
}

.tab-btn:hover {
  color: var(--color-text-primary);
  background: var(--color-surface-secondary);
}

.tab-btn.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-count {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  padding: 0.125rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.6875rem;
  font-weight: 600;
}

/* Content */
.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.tab-content {
  height: 100%;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  color: var(--color-text-secondary);
}

.empty-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.empty-hint { font-size: 0.75rem; color: var(--color-text-tertiary); }

/* Theory Content */
.theory-content {
  padding: 1rem;
  background: var(--color-surface);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
}

.content-block {
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--color-text-primary);
}

.content-block p { margin: 0 0 1rem 0; }
.content-block p:last-child { margin-bottom: 0; }

/* Exercises List */
.exercises-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.exercise-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
  transition: all 0.15s;
}

.exercise-card.expanded {
  border-color: var(--color-primary);
}

.exercise-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  cursor: pointer;
  transition: background 0.15s;
}

.exercise-header:hover {
  background: var(--color-surface-secondary);
}

.exercise-number {
  width: 1.75rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
}

.exercise-icon {
  font-size: 1.25rem;
}

.exercise-info {
  flex: 1;
  min-width: 0;
}

.exercise-type {
  display: block;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.exercise-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.method-badge {
  padding: 0.25rem 0.5rem;
  background: var(--color-primary);
  color: white;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 600;
}

.expand-icon {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
}

/* Exercise Content */
.exercise-content {
  padding: 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.content-section {
  margin-bottom: 1rem;
}

.content-section h4 {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
}

.content-section p {
  font-size: 0.8125rem;
  margin: 0;
  color: var(--color-text-primary);
}

/* Method Preview Styles */
:deep(.method-preview) {
  font-size: 0.8125rem;
}

:deep(.method-preview h4) {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
}

:deep(.exercises-preview),
:deep(.questions-preview),
:deep(.cards-preview) {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

:deep(.exercise-item),
:deep(.question-item),
:deep(.card-item) {
  padding: 0.75rem;
  background: var(--color-surface);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

:deep(.exercise-label),
:deep(.question-label) {
  display: block;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin-bottom: 0.25rem;
}

:deep(.exercise-text),
:deep(.question-text) {
  display: block;
  color: var(--color-text-primary);
}

:deep(.answers) {
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

:deep(.answer) {
  padding: 0.375rem 0.5rem;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

:deep(.answer.correct) {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

:deep(.card-front),
:deep(.card-back) {
  padding: 0.25rem 0;
  font-size: 0.75rem;
}

:deep(.card-front) {
  color: var(--color-text-primary);
  font-weight: 500;
}

:deep(.card-back) {
  color: var(--color-text-secondary);
}

:deep(.more-hint) {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  text-align: center;
  margin-top: 0.5rem;
}

:deep(.no-content) {
  color: var(--color-text-tertiary);
  font-style: italic;
}

:deep(.config-json) {
  padding: 0.75rem;
  background: var(--color-surface);
  border-radius: 0.5rem;
  font-size: 0.6875rem;
  font-family: monospace;
  overflow-x: auto;
  max-height: 200px;
  color: var(--color-text-secondary);
}

:deep(.data-hint) {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin: 0.25rem 0;
}

:deep(.config-details) {
  margin-top: 0.5rem;
}

:deep(.config-details summary) {
  font-size: 0.75rem;
  color: var(--color-primary);
  cursor: pointer;
  user-select: none;
}

:deep(.config-details summary:hover) {
  text-decoration: underline;
}

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.info-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  padding: 0.75rem;
}

.info-card.full-width {
  grid-column: span 2;
}

.info-label {
  display: block;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin-bottom: 0.25rem;
  text-transform: uppercase;
}

.info-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

/* Footer */
.preview-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
}

.footer-info {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.footer-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn.secondary {
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.action-btn.secondary:hover {
  background: var(--color-surface);
}
</style>
