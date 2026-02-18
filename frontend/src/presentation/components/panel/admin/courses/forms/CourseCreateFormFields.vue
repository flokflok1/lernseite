<!--
  CourseCreateFormFields
  ======================
  Shared form fields for course creation (used by panel, window, and base variants).
  Renders: file upload, title, description, category, level, language, AI model selector.

  The parent passes the reactive form object -- this component binds v-model directly
  to its properties, which is the standard Vue 3 pattern for reactive object props.
-->

<template>
  <div class="space-y-5 max-w-2xl">

    <!-- File Upload -->
    <div class="p-4 bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]">
      <div class="flex items-center justify-between mb-2">
        <label class="text-sm font-medium text-[var(--color-text-primary)]">
          {{ $t('courseCreate.file.title') }}
        </label>
        <span class="text-xs text-[var(--color-text-secondary)]">{{ $t('courseCreate.file.optional') }}</span>
      </div>

      <!-- No file selected -->
      <div v-if="!selectedFile" class="flex items-center gap-3">
        <button
          type="button"
          @click="$emit('triggerFileInput')"
          :disabled="isProcessing"
          class="px-4 py-2 text-sm border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] hover:border-[var(--color-primary)] transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          <span>{{ getFileIcon('default.pdf') }}</span>
          <span>{{ $t('courseCreate.file.selectFile') }}</span>
        </button>
        <span class="text-xs text-[var(--color-text-secondary)]">
          {{ $t('courseCreate.file.hint') }}
        </span>
      </div>

      <!-- File selected -->
      <div v-else>
        <div class="flex items-center gap-3 p-3 bg-[var(--color-bg)] border border-[var(--color-success,#22c55e)]/30 rounded-lg">
          <span class="text-2xl">{{ getFileIcon(selectedFile.name) }}</span>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-[var(--color-text-primary)] truncate">{{ selectedFile.name }}</p>
            <p class="text-xs text-[var(--color-text-secondary)]">{{ formatFileSize(selectedFile.size) }}</p>
          </div>
          <button
            type="button"
            @click="$emit('clearFile')"
            :disabled="isProcessing"
            class="p-1.5 text-[var(--color-text-secondary)] hover:text-[var(--color-error,#dc2626)] rounded transition-colors"
            :title="$t('courseCreate.file.removeFile')"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- AI fill button -->
        <button
          v-if="aiStatus === 'idle'"
          type="button"
          @click="$emit('fillWithAI')"
          :disabled="isProcessing"
          class="mt-3 w-full px-4 py-2 text-sm bg-gradient-to-r from-[var(--color-magic-start,#8B5CF6)] to-[var(--color-magic-end,#EC4899)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
        >
          <span>{{ '\u2728' }}</span>
          <span>{{ $t('courseCreate.file.fillWithAI') }}</span>
        </button>

        <!-- AI processing -->
        <div v-else-if="aiStatus === 'processing'" class="mt-3 flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
          <span class="animate-pulse">{{ '\u2728' }}</span>
          <span>{{ $t('courseCreate.file.aiProcessing') }}</span>
        </div>

        <!-- AI completed -->
        <div v-else-if="aiStatus === 'completed'" class="mt-3 flex items-center gap-2 text-sm text-[var(--color-success,#22c55e)]">
          <span>{{ '\u2705' }}</span>
          <span>{{ $t('courseCreate.file.aiCompleted') }}</span>
        </div>
      </div>

      <p v-if="fileError" class="mt-2 text-sm text-[var(--color-error,#dc2626)]">{{ fileError }}</p>
    </div>

    <!-- Course Title -->
    <div>
      <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
        {{ $t('courseCreate.form.courseTitle') }}
      </label>
      <input
        v-model="form.title"
        type="text"
        required
        :disabled="isProcessing"
        class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent disabled:opacity-50"
        :placeholder="$t('courseCreate.form.courseTitlePlaceholder')"
      />
    </div>

    <!-- Description -->
    <div>
      <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
        {{ $t('courseCreate.form.description') }}
      </label>
      <textarea
        v-model="form.description"
        rows="3"
        :disabled="isProcessing"
        class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent disabled:opacity-50 resize-none"
        :placeholder="$t('courseCreate.form.descriptionPlaceholder')"
      ></textarea>
    </div>

    <!-- Category & Level -->
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
          {{ $t('courseCreate.form.category') }}
        </label>
        <select
          v-model="form.category_id"
          :disabled="isProcessing"
          class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent disabled:opacity-50"
        >
          <option value="">{{ $t('courseCreate.form.noCategory') }}</option>
          <option v-for="cat in categories" :key="cat.category_id" :value="cat.category_id">
            {{ cat.name }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
          {{ $t('courseCreate.form.difficulty') }}
        </label>
        <select
          v-model="form.level"
          :disabled="isProcessing"
          class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent disabled:opacity-50"
        >
          <option value="beginner">{{ $t('courseCreate.form.levelBeginner') }}</option>
          <option value="intermediate">{{ $t('courseCreate.form.levelIntermediate') }}</option>
          <option value="advanced">{{ $t('courseCreate.form.levelAdvanced') }}</option>
        </select>
      </div>
    </div>

    <!-- Language -->
    <div>
      <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
        {{ $t('courseCreate.form.language') }}
      </label>
      <select
        v-model="form.language"
        :disabled="isProcessing"
        class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent disabled:opacity-50"
      >
        <option value="de">Deutsch</option>
        <option value="en">English</option>
        <option value="fr">Fran&ccedil;ais</option>
        <option value="es">Espa&ntilde;ol</option>
      </select>
    </div>

    <!-- AI Model Override -->
    <div class="p-4 bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]">
      <div class="flex items-center justify-between mb-2">
        <label class="text-sm font-medium text-[var(--color-text-primary)]">
          {{ $t('courseCreate.form.aiModel') }}
        </label>
        <span class="text-xs text-[var(--color-text-secondary)]">{{ $t('courseCreate.file.optional') }}</span>
      </div>
      <div class="flex items-center gap-3">
        <button
          type="button"
          @click="$emit('openModelSelector')"
          :disabled="isProcessing"
          class="px-4 py-2 text-sm border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] hover:border-[var(--color-primary)] transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          <span>{{ '\uD83E\uDD16' }}</span>
          <span>{{ form.ai_model_override || $t('courseCreate.form.selectModel') }}</span>
        </button>
        <button
          v-if="form.ai_model_override"
          type="button"
          @click="$emit('clearModelOverride')"
          :disabled="isProcessing"
          class="p-2 text-[var(--color-text-secondary)] hover:text-[var(--color-error,#dc2626)] transition-colors"
          :title="$t('courseCreate.form.removeModelOverride')"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <p class="mt-2 text-xs text-[var(--color-text-secondary)]">
        {{ form.ai_model_override
          ? $t('courseCreate.form.courseUsesModel', { model: form.ai_model_override })
          : $t('courseCreate.form.usesDefaultModel')
        }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CourseCreateForm, AiStatus, CategoryOption } from '../composables/useCourseCreate'

interface Props {
  form: CourseCreateForm
  categories: CategoryOption[]
  selectedFile: File | null
  fileError: string | null
  aiStatus: AiStatus
  isProcessing: boolean
  formatFileSize: (bytes: number) => string
  getFileIcon: (filename: string) => string
}

interface Emits {
  (e: 'triggerFileInput'): void
  (e: 'clearFile'): void
  (e: 'fillWithAI'): void
  (e: 'openModelSelector'): void
  (e: 'clearModelOverride'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<style scoped>
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
