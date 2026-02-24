<!--
  Admin Lesson Preview

  Loads and displays REAL lesson data from the database.
  Shows theory content and actual learning method exercises.

  Phase: D4 - AI Editor
-->

<template>
  <div class="lesson-preview-window">
    <!-- Header -->
    <div class="preview-header">
      <div class="lesson-badge">{{ $t('panel.lessons.preview.lessonN', { n: lessonPosition }) }}</div>
      <h1 class="lesson-title">{{ lessonData?.title || $t('panel.lessons.preview.loading') }}</h1>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ $t('panel.lessons.preview.loadingData') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <span class="error-icon">⚠️</span>
      <p>{{ error }}</p>
      <button @click="loadLessonData" class="retry-btn">{{ $t('panel.lessons.preview.retry') }}</button>
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
            <div class="content-block" v-html="formatTheoryContent(lessonData.content.theory)"></div>
          </div>
          <div v-else-if="lessonData?.description" class="theory-content">
            <div class="content-block">
              <p>{{ lessonData.description }}</p>
            </div>
          </div>
          <div v-else class="empty-state">
            <span class="empty-icon">📝</span>
            <p>{{ $t('panel.lessons.preview.noTheory') }}</p>
            <p class="empty-hint">{{ $t('panel.lessons.preview.theoryHint') }}</p>
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
                  <span class="exercise-type">{{ getMethodName(method.method_type, t) }}</span>
                  <span class="exercise-title">{{ cleanMethodTitle(method.method_name, method.method_type) }}</span>
                </div>
                <span class="method-badge">{{ getMethodName(method.method_type, t) }}</span>
                <span class="expand-icon">{{ expandedMethod === method.method_id ? '▼' : '▶' }}</span>
              </div>

              <!-- Expanded Content -->
              <div v-if="expandedMethod === method.method_id" class="exercise-content">
                <LessonMethodRenderer
                  :method-type="method.method_type"
                  :config="method.config"
                />
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <span class="empty-icon">📭</span>
            <p>{{ $t('panel.lessons.preview.noMethods') }}</p>
            <p class="empty-hint">{{ $t('panel.lessons.preview.methodsCreatedInEditor') }}</p>
          </div>
        </div>

        <!-- Info Tab -->
        <div v-if="activeTab === 'info'" class="tab-content">
          <div class="info-grid">
            <div class="info-card">
              <span class="info-label">{{ $t('panel.lessons.preview.lesson') }}</span>
              <span class="info-value">{{ lessonData?.title }}</span>
            </div>
            <div class="info-card">
              <span class="info-label">{{ $t('panel.lessons.preview.type') }}</span>
              <span class="info-value">{{ lessonData?.lesson_type || 'text' }}</span>
            </div>
            <div class="info-card">
              <span class="info-label">{{ $t('panel.lessons.preview.duration') }}</span>
              <span class="info-value">{{ lessonData?.duration_minutes || 0 }} {{ $t('panel.lessons.preview.min') }}</span>
            </div>
            <div class="info-card">
              <span class="info-label">{{ $t('panel.lessons.preview.learningMethods') }}</span>
              <span class="info-value">{{ methods.length }}</span>
            </div>
            <div v-if="lessonData?.chapter_id" class="info-card full-width">
              <span class="info-label">{{ $t('panel.lessons.preview.chapter') }}</span>
              <span class="info-value">{{ chapterTitle }}</span>
            </div>
            <div v-if="lessonData?.created_at" class="info-card">
              <span class="info-label">{{ $t('panel.lessons.preview.created') }}</span>
              <span class="info-value">{{ formatDate(lessonData.created_at, dateLocale) }}</span>
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
        <button class="action-btn secondary" @click="$emit('close')">{{ $t('panel.lessons.preview.close') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import LessonMethodRenderer from './views/LessonMethodRenderer.vue'
import {
  useLessonPreview,
  getMethodIcon,
  getMethodName,
  cleanMethodTitle,
  formatTheoryContent,
  formatDate,
  buildPreviewTabs
} from './composables'

const { t, locale } = useI18n()

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()
defineEmits<{ (e: 'close'): void }>()

const payload = computed(() => props.window.payload)

const {
  loading, error, lessonData, methods,
  activeTab, expandedMethod, lessonPosition,
  chapterTitle, loadLessonData, toggleMethod
} = useLessonPreview(payload)

const tabs = computed(() => buildPreviewTabs(methods.value.length, t))

const LOCALE_MAP: Record<string, string> = { de: 'de-DE', en: 'en-US', pl: 'pl-PL' }
const dateLocale = computed(() => LOCALE_MAP[locale.value] || 'de-DE')

onMounted(() => { loadLessonData() })
</script>

<style scoped>
.lesson-preview-window {
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

@keyframes spin { to { transform: rotate(360deg); } }

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
.preview-content { flex: 1; overflow-y: auto; padding: 1rem; }
.tab-content { height: 100%; }

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

.content-block { font-size: 0.875rem; line-height: 1.6; color: var(--color-text-primary); }
.content-block p { margin: 0 0 1rem 0; }
.content-block p:last-child { margin-bottom: 0; }

/* Exercises List */
.exercises-list { display: flex; flex-direction: column; gap: 0.75rem; }

.exercise-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
  transition: all 0.15s;
}

.exercise-card.expanded { border-color: var(--color-primary); }

.exercise-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  cursor: pointer;
  transition: background 0.15s;
}

.exercise-header:hover { background: var(--color-surface-secondary); }

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

.exercise-icon { font-size: 1.25rem; }
.exercise-info { flex: 1; min-width: 0; }

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

.expand-icon { font-size: 0.625rem; color: var(--color-text-tertiary); }

/* Exercise Content */
.exercise-content {
  padding: 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
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

.info-card.full-width { grid-column: span 2; }

.info-label {
  display: block;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin-bottom: 0.25rem;
  text-transform: uppercase;
}

.info-value { font-size: 0.875rem; font-weight: 500; color: var(--color-text-primary); }

/* Footer */
.preview-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
}

.footer-info { font-size: 0.75rem; color: var(--color-text-secondary); }
.footer-actions { display: flex; gap: 0.5rem; }

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

.action-btn.secondary:hover { background: var(--color-surface); }
</style>
