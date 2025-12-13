<template>
  <div class="text-lesson">
    <!-- Lesson Content -->
    <div class="prose">
      <div v-if="content.html" v-html="sanitizedHtml"></div>
      <div v-else-if="content.markdown" class="whitespace-pre-wrap">
        {{ content.markdown }}
      </div>
      <div v-else-if="content.text" class="whitespace-pre-wrap">
        {{ content.text }}
      </div>
      <div v-else class="empty-content">
        Kein Inhalt verfügbar
      </div>
    </div>

    <!-- Images / Media -->
    <div v-if="content.images && content.images.length > 0" class="images-section">
      <div v-for="(image, index) in content.images" :key="index" class="image-wrapper">
        <img
          :src="image.url"
          :alt="image.caption || 'Bild'"
          class="lesson-image"
        />
        <p v-if="image.caption" class="image-caption">
          {{ image.caption }}
        </p>
      </div>
    </div>

    <!-- Additional Resources -->
    <div v-if="content.resources && content.resources.length > 0" class="resources-section">
      <h3 class="resources-title">Zusätzliche Ressourcen</h3>
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
import type { Lesson } from '@/api/player.api'
import DOMPurify from 'dompurify'

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

const sanitizedHtml = computed(() => {
  if (!content.value.html) return ''
  return DOMPurify.sanitize(content.value.html)
})
</script>

<style scoped>
.text-lesson {
  background-color: var(--color-surface, #ffffff);
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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
</style>
