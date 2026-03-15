<!--
  WorksheetPage — A4 paper-style container for lesson content.

  Renders content inside a realistic "paper" card with chapter header,
  lesson title, content area, and page-style footer.  Print-ready via
  @media print rules.
-->
<template>
  <article
    class="worksheet"
    :class="[`worksheet--${category}`, { 'worksheet--completed': isCompleted }]"
  >
    <!-- Paper -->
    <div class="paper">
      <!-- Page Header -->
      <header class="paper-header">
        <div class="header-accent" :style="{ background: accentColor }" />
        <div class="header-content">
          <span class="chapter-label">{{ chapterTitle }}</span>
          <div class="lesson-title-row">
            <span class="category-icon">{{ icon }}</span>
            <h1 class="lesson-title">{{ lessonTitle }}</h1>
          </div>
          <div class="header-meta">
            <span class="category-badge" :style="{ color: accentColor, borderColor: accentColor }">
              {{ categoryLabel }}
            </span>
            <span v-if="difficulty" class="difficulty-badge">
              {{ difficultyLabel }}
            </span>
          </div>
        </div>
      </header>

      <!-- Divider -->
      <div class="paper-divider" />

      <!-- Content Slot -->
      <div class="paper-body">
        <slot />
      </div>

      <!-- Footer -->
      <footer class="paper-footer">
        <div class="footer-left">
          <span class="page-category">{{ icon }} {{ categoryLabel }}</span>
          <span class="page-indicator">
            {{ $t('lessonTimeline.stepOf', pagePosition) }}
          </span>
        </div>
        <div class="footer-nav">
          <button
            v-if="hasPrevious"
            class="page-btn page-btn--prev"
            @click="$emit('previous')"
          >
            <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            {{ $t('lesson.previous_lesson') }}
          </button>
          <button
            v-if="hasNext"
            class="page-btn page-btn--next"
            @click="$emit('next')"
          >
            {{ $t('lesson.next_lesson') }}
            <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
          <button
            v-else
            class="page-btn page-btn--finish"
            @click="$emit('finish')"
          >
            {{ $t('lesson.finish_course') }}
          </button>
        </div>
      </footer>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { detectCategory, type PageCategory } from '@/application/composables/panel/user/learning/usePageCategory'

interface Props {
  chapterTitle: string
  lessonTitle: string
  lessonType: string
  pagePosition: { step: number; total: number }
  isCompleted: boolean
  hasPrevious: boolean
  hasNext: boolean
  difficulty?: string
}

const props = defineProps<Props>()

defineEmits<{
  previous: []
  next: []
  finish: []
}>()

const { t } = useI18n()

// Detect category from lesson title
const detected = computed(() => detectCategory(props.lessonTitle))
const category = computed<PageCategory>(() => detected.value?.category ?? 'theory')
const icon = computed(() => detected.value?.icon ?? '📄')

const ACCENT: Record<PageCategory, string> = {
  theory:     '#3b82f6',
  practice:   '#f59e0b',
  assessment: '#8b5cf6',
}

const accentColor = computed(() => ACCENT[category.value])

const categoryLabel = computed(() => {
  const keys: Record<PageCategory, string> = {
    theory:     'lessonTimeline.categoryTheory',
    practice:   'lessonTimeline.categoryPractice',
    assessment: 'lessonTimeline.categoryAssessment',
  }
  return t(keys[category.value])
})

const difficultyLabel = computed(() => {
  if (!props.difficulty) return ''
  const map: Record<string, string> = { easy: '●○○', medium: '●●○', hard: '●●●' }
  return map[props.difficulty] ?? ''
})
</script>

<style scoped>
/* ─── Worksheet Container ─── */
.worksheet {
  max-width: 52rem;
  width: 100%;
  margin: 0 auto;
  padding: 0 1rem;
}

/* ─── Paper Card ─── */
.paper {
  background: #ffffff;
  border-radius: 0.5rem;
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.06),
    0 4px 16px rgba(0, 0, 0, 0.04),
    0 12px 40px rgba(0, 0, 0, 0.03);
  overflow: hidden;
  min-height: 70vh;
  display: flex;
  flex-direction: column;
}

:root.dark .paper {
  background: #1e293b;
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.2),
    0 4px 16px rgba(0, 0, 0, 0.15);
}

/* ─── Header ─── */
.header-accent {
  height: 4px;
  width: 100%;
}

.header-content {
  padding: 1.5rem 2rem 1rem;
}

.chapter-label {
  display: block;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 0.5rem;
}

.lesson-title-row {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.category-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.lesson-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-text-primary, #111827);
  margin: 0;
  line-height: 1.25;
  letter-spacing: -0.01em;
}

:root.dark .lesson-title {
  color: #f1f5f9;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  font-size: 0.6875rem;
  font-weight: 600;
  border: 1px solid;
  border-radius: 9999px;
}

.difficulty-badge {
  font-size: 0.5rem;
  letter-spacing: 2px;
  color: var(--color-text-secondary, #9ca3af);
}

/* ─── Divider ─── */
.paper-divider {
  height: 1px;
  margin: 0 2rem;
  background: var(--color-border, #e5e7eb);
}

:root.dark .paper-divider {
  background: rgba(255, 255, 255, 0.08);
}

/* ─── Body ─── */
.paper-body {
  flex: 1;
  padding: 1.5rem 2rem 2rem;
  font-size: 0.9375rem;
  line-height: 1.75;
  color: var(--color-text-primary, #374151);
}

:root.dark .paper-body {
  color: #cbd5e1;
}

/* Hide redundant headers from task panels rendered inside */
.paper-body :deep(.back-btn) { display: none; }
.paper-body :deep(.task-header) { display: none; }
.paper-body :deep(.task-content-panel) {
  padding: 0;
  max-width: none;
}

/* ─── Footer ─── */
.paper-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 2rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
  background: var(--color-surface-secondary, #fafafa);
}

:root.dark .paper-footer {
  background: rgba(255, 255, 255, 0.02);
  border-top-color: rgba(255, 255, 255, 0.06);
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-category {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
}

.page-indicator {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #9ca3af);
  font-variant-numeric: tabular-nums;
}

.footer-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.875rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: 0.375rem;
  cursor: pointer;
  border: none;
  transition: all 0.15s;
}

.page-btn--prev {
  background: transparent;
  color: var(--color-text-secondary, #6b7280);
  border: 1px solid var(--color-border, #d1d5db);
}

.page-btn--prev:hover {
  background: var(--color-surface-secondary, #f3f4f6);
  color: var(--color-text-primary, #374151);
}

.page-btn--next,
.page-btn--finish {
  background: var(--color-primary, #3b82f6);
  color: #fff;
  box-shadow: 0 1px 4px rgba(59, 130, 246, 0.25);
}

.page-btn--next:hover,
.page-btn--finish:hover {
  filter: brightness(1.08);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn-icon {
  width: 0.875rem;
  height: 0.875rem;
}

/* Completed state */
.worksheet--completed .paper {
  border: 2px solid rgba(16, 185, 129, 0.3);
}

/* ─── Print Styles ─── */
@media print {
  .worksheet {
    max-width: 100%;
    padding: 0;
  }

  .paper {
    box-shadow: none;
    border-radius: 0;
    min-height: auto;
    border: 1px solid #d1d5db;
  }

  .header-accent { height: 2px; print-color-adjust: exact; }
  .paper-footer { break-inside: avoid; }
  .footer-nav { display: none; }
  .page-btn { display: none; }

  .paper-body {
    font-size: 11pt;
    line-height: 1.6;
  }
}
</style>
