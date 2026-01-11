<template>
  <div class="chapter-theory-panel p-6">
    <div class="max-w-4xl mx-auto">
      <!-- Loading State -->
      <div v-if="theoryLoading" class="flex flex-col items-center justify-center py-16">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400 mb-4"></div>
        <p class="text-gray-600 dark:text-gray-400">{{ $t('chapterTheory.loading.generating') }}</p>
        <p class="text-sm text-gray-500 dark:text-gray-500 mt-2">{{ $t('chapterTheory.loading.hint') }}</p>
      </div>

      <!-- No Theory State -->
      <div v-else-if="!theoryData" class="text-center py-16">
        <div class="max-w-md mx-auto">
          <!-- Empty State Icon -->
          <div class="mb-4">
            <svg class="w-20 h-20 mx-auto text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            {{ $t('chapterTheory.noTheory.title') }}
          </h3>
          <p class="text-gray-600 dark:text-gray-400 mb-6">
            {{ $t('chapterTheory.noTheory.description') }}
          </p>
          <button
            @click="$emit('generate-theory')"
            class="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <!-- AI Icon -->
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            {{ $t('chapterTheory.generateBtn') }}
          </button>
          <p class="text-xs text-gray-500 dark:text-gray-500 mt-4">
            {{ $t('chapterTheory.noTheory.info') }}
          </p>
        </div>
      </div>

      <!-- Theory Content -->
      <div v-else class="theory-content">
        <!-- Theory Header -->
        <div class="mb-6 pb-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1">
              <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {{ theoryData.title || $t('chapterTheory.theorySheet') }}
              </h2>
              <p v-if="theoryData.created_at" class="text-sm text-gray-500 dark:text-gray-500">
                {{ $t('common.createdAt') }}: {{ formatDate(theoryData.created_at) }}
              </p>
            </div>
            <!-- Regenerate Button -->
            <button
              @click="$emit('generate-theory')"
              class="px-4 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
            >
              {{ $t('chapterTheory.newTheory') }}
            </button>
          </div>
        </div>

        <!-- Theory Blocks -->
        <div class="space-y-6">
          <!-- Overview Block -->
          <div v-if="theoryData.overview" class="theory-block">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ $t('chapterTheory.blocks.overview') }}
            </h3>
            <div class="prose dark:prose-invert max-w-none" v-html="formatContent(theoryData.overview)"></div>
          </div>

          <!-- Learning Goals Block -->
          <div v-if="theoryData.learning_goals" class="theory-block">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ $t('chapterTheory.blocks.learningGoals') }}
            </h3>
            <div class="prose dark:prose-invert max-w-none" v-html="formatContent(theoryData.learning_goals)"></div>
          </div>

          <!-- Core Concepts Block -->
          <div v-if="theoryData.core_concepts" class="theory-block">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              {{ $t('chapterTheory.blocks.coreConcepts') }}
            </h3>
            <div class="prose dark:prose-invert max-w-none" v-html="formatContent(theoryData.core_concepts)"></div>
          </div>

          <!-- Important Terms Block -->
          <div v-if="theoryData.important_terms" class="theory-block">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
              {{ $t('chapterTheory.blocks.importantTerms') }}
            </h3>
            <div class="prose dark:prose-invert max-w-none" v-html="formatContent(theoryData.important_terms)"></div>
          </div>

          <!-- Exam Tips Block -->
          <div v-if="theoryData.exam_tips" class="theory-block bg-yellow-50 dark:bg-yellow-900/10 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              {{ $t('chapterTheory.blocks.examTips') }}
            </h3>
            <div class="prose dark:prose-invert max-w-none" v-html="formatContent(theoryData.exam_tips)"></div>
          </div>

          <!-- Summary Block -->
          <div v-if="theoryData.summary" class="theory-block bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              {{ $t('chapterTheory.blocks.summary') }}
            </h3>
            <div class="prose dark:prose-invert max-w-none" v-html="formatContent(theoryData.summary)"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ChapterTheoryPanel Component
 * ============================
 * Displays chapter theory content
 */
import { computed } from 'vue'

interface Props {
  theoryData: any | null
  theoryLoading: boolean
}

defineProps<Props>()

defineEmits<{
  'generate-theory': []
}>()

/**
 * Format date for display
 */
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('de-DE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}

/**
 * Format content (convert markdown/line breaks to HTML)
 */
function formatContent(content: string): string {
  if (!content) return ''

  // Simple markdown-like formatting
  return content
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
}
</script>

<style scoped>
.theory-block {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Prose styling for theory content */
.prose {
  line-height: 1.75;
}

.prose p {
  margin-bottom: 1rem;
}

.prose ul,
.prose ol {
  margin-top: 0.5rem;
  margin-bottom: 1rem;
  padding-left: 1.5rem;
}

.prose li {
  margin-bottom: 0.5rem;
}

.prose strong {
  font-weight: 600;
  color: inherit;
}

.prose em {
  font-style: italic;
}
</style>
