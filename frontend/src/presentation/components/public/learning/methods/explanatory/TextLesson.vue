<template>
  <div class="text-lesson">
    <!-- Detailed Steps (if available) -->
    <div v-if="hasDetailedSteps" class="detailed-section">
      <DetailedSteps
        :steps="detailedContent.steps"
        @completed="$emit('completed')"
      />

      <!-- Additional detailed info -->
      <div v-if="detailedContent.overview" class="detail-info overview">
        <strong>{{ $t('lesson.text.overview') }}</strong> {{ detailedContent.overview }}
      </div>
      <div v-if="detailedContent.summary" class="detail-info summary">
        <strong>{{ $t('lesson.text.summary') }}</strong> {{ detailedContent.summary }}
      </div>
      <div v-if="detailedContent.practiceTask" class="detail-info practice">
        <strong>{{ $t('lesson.text.practiceTask') }}</strong>
        <p>{{ detailedContent.practiceTask.description }}</p>
      </div>
    </div>

    <!-- Standard Lesson Content -->
    <div class="prose">
      <div v-if="content.html" v-html="sanitizedHtml"></div>
      <div v-else-if="renderedMarkdown" v-html="renderedMarkdown"></div>
      <div v-else-if="content.text" class="whitespace-pre-wrap">
        {{ content.text }}
      </div>
      <div v-else-if="!hasDetailedSteps" class="empty-content">
        {{ $t('lesson.text.noContent') }}
      </div>
    </div>

    <!-- Images / Media -->
    <div v-if="content.images && content.images.length > 0" class="images-section">
      <div v-for="(image, index) in content.images" :key="index" class="image-wrapper">
        <img
          :src="image.url"
          :alt="image.caption || $t('lesson.text.image')"
          class="lesson-image"
        />
        <p v-if="image.caption" class="image-caption">
          {{ image.caption }}
        </p>
      </div>
    </div>

    <!-- Additional Resources -->
    <div v-if="content.resources && content.resources.length > 0" class="resources-section">
      <h3 class="resources-title">{{ $t('lesson.text.additionalResources') }}</h3>
      <ul class="resources-list">
        <li v-for="(resource, index) in content.resources" :key="index">
          <a
            :href="resource.url"
            target="_blank"
            rel="noopener noreferrer"
            class="resource-link"
          >
            {{ resource.title }}
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Lesson } from '@/infrastructure/api/clients/public/learning/types/types'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import DetailedSteps from './DetailedSteps.vue'

const { t } = useI18n()

// ============================================================================
// Props
// ============================================================================

interface Props {
  lesson: Lesson
}

const props = defineProps<Props>()

defineEmits<{
  (e: 'completed'): void
}>()

// ============================================================================
// Computed
// ============================================================================

const content = computed(() => {
  let raw = props.lesson.content
  if (!raw) return {}

  // DB stores content as jsonb — it may arrive as string (double-encoded) or object
  if (typeof raw === 'string') {
    // Strip <p>...</p> wrapper if present (legacy data issue)
    const stripped = raw.replace(/^<p>(.*)<\/p>$/s, '$1').trim()
    try { return JSON.parse(stripped) } catch { return { raw_text: raw } }
  }

  // If it's an object but has only one key that's a JSON string, try to unwrap
  if (typeof raw === 'object' && raw !== null) {
    return raw
  }

  return { raw_text: String(raw) }
})

const sanitizedHtml = computed(() => {
  if (!content.value.html) return ''
  return DOMPurify.sanitize(content.value.html)
})

/**
 * Render markdown from raw_text (AI-generated) or markdown field.
 * AI plan execution stores content as { raw_text: "# Markdown..." }.
 */
const renderedMarkdown = computed(() => {
  let md = content.value.raw_text || content.value.markdown
  if (!md) return ''
  // Strip the first top-level heading (# ...) — the lesson title is already
  // shown in the top bar (LessonPlayerTopBar), so rendering it again in the
  // content area creates a duplicate title.
  md = md.replace(/^#\s+[^\n]+\n*/, '')
  const html = marked.parse(md, { async: false }) as string
  return DOMPurify.sanitize(html)
})

// Check if detailed content is available
const detailedContent = computed(() => {
  return content.value.detailed || null
})

const hasDetailedSteps = computed(() => {
  return detailedContent.value?.steps && detailedContent.value.steps.length > 0
})
</script>

<style scoped>
.text-lesson {
  padding: 0;
}

.prose {
  color: var(--color-text-primary, #374151);
}

.prose :deep(h1),
.prose :deep(h2),
.prose :deep(h3) {
  color: var(--color-text-primary, #111827);
  font-weight: 700;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

.prose :deep(h1) {
  font-size: 2rem;
}

.prose :deep(h2) {
  font-size: 1.5rem;
}

.prose :deep(h3) {
  font-size: 1.25rem;
}

.prose :deep(p) {
  margin-bottom: 1rem;
  line-height: 1.75;
}

.prose :deep(ul),
.prose :deep(ol) {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.prose :deep(li) {
  margin-bottom: 0.5rem;
}

.prose :deep(a) {
  color: var(--color-primary, #3b82f6);
  text-decoration: underline;
}

.prose :deep(code) {
  background-color: var(--color-surface-secondary, #f9fafb);
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-family: 'Courier New', monospace;
  color: var(--color-text-primary, #111827);
}

.prose :deep(pre) {
  background-color: #1f2937;
  color: #f3f4f6;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin-bottom: 1rem;
}

.empty-content {
  color: var(--color-text-secondary, #6b7280);
  font-style: italic;
}

.whitespace-pre-wrap {
  white-space: pre-wrap;
}

/* Images Section */
.images-section {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.image-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.lesson-image {
  width: 100%;
  border-radius: 0.5rem;
}

.image-caption {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  text-align: center;
  margin-top: 0.5rem;
}

/* Resources Section */
.resources-section {
  margin-top: 2rem;
  padding: 1rem;
  background-color: rgba(59, 130, 246, 0.1);
  border-radius: 0.5rem;
}

.resources-title {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0 0 0.75rem;
}

.resources-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.resource-link {
  color: var(--color-primary, #3b82f6);
  text-decoration: underline;
}

.resource-link:hover {
  color: #2563eb;
}

/* Detailed Section */
.detailed-section {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.detail-info {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
  line-height: 1.6;
}

.detail-info strong {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--color-text-primary, #111827);
}

.detail-info.overview {
  background: rgba(99, 102, 241, 0.05);
  border: 1px solid rgba(99, 102, 241, 0.15);
}

.detail-info.summary {
  background: rgba(16, 185, 129, 0.05);
  border: 1px solid rgba(16, 185, 129, 0.15);
}

.detail-info.practice {
  background: rgba(245, 158, 11, 0.05);
  border: 1px solid rgba(245, 158, 11, 0.15);
}

.detail-info p {
  margin: 0;
}
</style>
