<template>
  <div class="ai-lesson">
    <div class="lesson-intro">
      <div class="intro-header">
        <div class="intro-icon">📚</div>
        <div>
          <h3 class="intro-title">{{ $t('lesson.ai.title') }}</h3>
          <p class="intro-subtitle">{{ $t('lesson.ai.subtitle') }}</p>
        </div>
      </div>

      <!-- Topic (for interactive lessons) -->
      <div v-if="content.topic" class="topic-card">
        <h4 class="topic-label">{{ $t('lesson.ai.topic') }}</h4>
        <p class="topic-text">{{ content.topic }}</p>
      </div>

      <!-- Lesson Content (for AI lessons) -->
      <div v-if="content.text || content.description" class="content-text">
        <p>{{ content.text || content.description }}</p>
      </div>

      <!-- Interactive Lesson Info -->
      <div v-if="hasInteractiveContent" class="info-grid">
        <div v-if="content.dauer_min" class="info-card info-card--default">
          <p class="info-value">{{ content.dauer_min }}</p>
          <p class="info-label">{{ $t('lesson.ai.minutes') }}</p>
        </div>
        <div v-if="content.zeitlimit" class="info-card info-card--warning">
          <p class="info-value">{{ content.zeitlimit }}</p>
          <p class="info-label">{{ $t('lesson.ai.timeLimit') }}</p>
        </div>
        <div v-if="content.punkte_ziel || content.punkte" class="info-card info-card--success">
          <p class="info-value">{{ content.punkte_ziel || content.punkte }}</p>
          <p class="info-label">{{ $t('lesson.ai.points') }}</p>
        </div>
        <div v-if="content.pruefungs_relevanz" class="info-card info-card--primary">
          <p class="info-value info-value--small">{{ content.pruefungs_relevanz }}</p>
          <p class="info-label">{{ $t('lesson.ai.relevance') }}</p>
        </div>
      </div>

      <!-- Hint -->
      <div v-if="content.hinweis" class="hint-card">
        <h4 class="hint-label">{{ $t('lesson.ai.hint') }}</h4>
        <p class="hint-text">{{ content.hinweis }}</p>
      </div>

      <!-- Instructions -->
      <div class="instructions-card">
        <h4 class="instructions-title">{{ $t('lesson.ai.instructionsTitle') }}</h4>
        <p class="instructions-text">
          {{ $t('lesson.ai.instructionsText') }}
        </p>

        <ul class="instructions-list">
          <li>
            <span class="list-arrow">→</span>
            <span>{{ $t('lesson.ai.instruction1') }}</span>
          </li>
          <li>
            <span class="list-arrow">→</span>
            <span>{{ $t('lesson.ai.instruction2') }}</span>
          </li>
          <li>
            <span class="list-arrow">→</span>
            <span>{{ $t('lesson.ai.instruction3') }}</span>
          </li>
        </ul>

        <div class="token-hint">
          <p>
            <strong>{{ $t('lesson.ai.hint') }}:</strong> {{ $t('lesson.ai.tokenHint') }}
          </p>
        </div>
      </div>

      <!-- Learning Context -->
      <div v-if="content.learning_context" class="context-card">
        <h4 class="context-label">{{ $t('lesson.ai.learningContext') }}</h4>
        <p class="context-text">{{ content.learning_context }}</p>
      </div>

      <!-- Example Prompts -->
      <div v-if="content.example_prompts && content.example_prompts.length > 0" class="prompts-section">
        <h4 class="prompts-title">{{ $t('lesson.ai.examplePrompts') }}</h4>
        <div class="prompts-list">
          <div
            v-for="(prompt, index) in content.example_prompts"
            :key="index"
            class="prompt-item"
          >
            "{{ prompt }}"
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import type { Lesson } from '@/infrastructure/api/player.api'

// ============================================================================
// Props
// ============================================================================

interface Props {
  lesson: Lesson
}

const props = defineProps<Props>()

// ============================================================================
// Computed
// ============================================================================

const content = computed(() => {
  return props.lesson.content || {}
})

const hasInteractiveContent = computed(() => {
  return content.value.dauer_min || content.value.zeitlimit ||
         content.value.punkte_ziel || content.value.punkte ||
         content.value.pruefungs_relevanz
})
</script>

<style scoped>
.ai-lesson {
  background-color: var(--color-surface, #ffffff);
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.lesson-intro {
  margin-bottom: 1.5rem;
}

.intro-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.intro-icon {
  font-size: 2.5rem;
}

.intro-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
  margin: 0;
}

.intro-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

/* Topic Card */
.topic-card {
  background-color: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.topic-label {
  font-weight: 600;
  color: var(--color-primary, #3b82f6);
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
}

.topic-text {
  color: var(--color-text-primary, #111827);
  margin: 0;
}

/* Content Text */
.content-text {
  margin-bottom: 1.5rem;
}

.content-text p {
  color: var(--color-text-primary, #111827);
  line-height: 1.75;
  white-space: pre-wrap;
  margin: 0;
}

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 768px) {
  .info-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.info-card {
  border-radius: 0.5rem;
  padding: 1rem;
  text-align: center;
}

.info-card--default {
  background-color: var(--color-surface-secondary, #f9fafb);
}

.info-card--warning {
  background-color: rgba(245, 158, 11, 0.1);
}

.info-card--success {
  background-color: rgba(16, 185, 129, 0.1);
}

.info-card--primary {
  background-color: rgba(139, 92, 246, 0.1);
}

.info-value {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}

.info-card--default .info-value {
  color: var(--color-text-primary, #111827);
}

.info-card--warning .info-value {
  color: #f59e0b;
}

.info-card--success .info-value {
  color: #10b981;
}

.info-card--primary .info-value {
  color: #8b5cf6;
}

.info-value--small {
  font-size: 1rem;
}

.info-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

/* Hint Card */
.hint-card {
  background-color: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.hint-label {
  font-weight: 600;
  color: #f59e0b;
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
}

.hint-text {
  color: var(--color-text-primary, #111827);
  margin: 0;
}

/* Instructions Card */
.instructions-card {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.instructions-title {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0 0 0.75rem;
}

.instructions-text {
  color: var(--color-text-secondary, #6b7280);
  margin: 0 0 1rem;
}

.instructions-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;
}

.instructions-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  color: var(--color-text-primary, #111827);
}

.list-arrow {
  color: var(--color-primary, #3b82f6);
}

.token-hint {
  background-color: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 0.375rem;
  padding: 0.75rem;
}

.token-hint p {
  font-size: 0.875rem;
  color: var(--color-text-primary, #111827);
  margin: 0;
}

/* Context Card */
.context-card {
  margin-top: 1.5rem;
  background-color: var(--color-surface-secondary, #f9fafb);
  border-radius: 0.5rem;
  padding: 1rem;
}

.context-label {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0 0 0.5rem;
}

.context-text {
  color: var(--color-text-secondary, #6b7280);
  white-space: pre-wrap;
  margin: 0;
}

/* Prompts Section */
.prompts-section {
  margin-top: 1.5rem;
}

.prompts-title {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0 0 0.75rem;
}

.prompts-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.prompt-item {
  padding: 0.75rem;
  background-color: var(--color-surface-secondary, #f9fafb);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
}
</style>
