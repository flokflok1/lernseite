<!--
  NewCourseModal - Modal for creating new courses with AI analysis
-->

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <!-- Header -->
      <h3 class="modal-title">{{ $t('panel.aiStudio.newCourse') }}</h3>

      <div class="modal-body">
        <!-- Step 1: File Upload -->
        <CourseFileUpload
          ref="fileUploadRef"
          :is-analyzing="isAnalyzing"
          :ai-analyzed="aiAnalyzed"
          @analyze="handleAnalyze"
        />

        <!-- Step 2: Course Details -->
        <CourseDetailsForm
          v-model="courseData"
          :available-categories="availableCategories"
          :available-profiles="availableProfiles"
          :ai-analyzed="aiAnalyzed"
          :is-faded="hasUploadedFiles && !aiAnalyzed && !courseData.title"
        />
      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <p class="footer-hint">
          {{ $t('panel.aiStudio.afterCreationHint') }}
        </p>
        <div class="footer-actions">
          <button @click="$emit('close')" class="btn-cancel">
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="handleCreate"
            :disabled="!canCreate || isCreating"
            class="btn-create"
          >
            <span v-if="isCreating" class="animate-spin">&#x23F3;</span>
            {{ $t('panel.aiStudio.createCourse') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * NewCourseModal - Multi-step course creation with AI analysis.
 * Delegates file upload to CourseFileUpload and form fields to CourseDetailsForm.
 */
import { ref, computed } from 'vue'
import type { Category, Profile, NewCourseData } from '../composables/useCourseManagement'
import CourseFileUpload from './CourseFileUpload.vue'
import CourseDetailsForm from './CourseDetailsForm.vue'

// =============================================================================
// Props
// =============================================================================

interface Props {
  availableCategories: Category[]
  availableProfiles: Profile[]
}

defineProps<Props>()

// =============================================================================
// Emits
// =============================================================================

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'create', data: NewCourseData): void
  (e: 'analyze', files: File[]): void
}>()

// =============================================================================
// State
// =============================================================================

const fileUploadRef = ref<InstanceType<typeof CourseFileUpload> | null>(null)
const isAnalyzing = ref(false)
const isCreating = ref(false)
const aiAnalyzed = ref(false)

const courseData = ref({
  title: '',
  description: '',
  language: 'de',
  level: 'beginner' as 'beginner' | 'intermediate' | 'advanced',
  categoryId: null as number | null,
  profileKey: 'standard'
})

// =============================================================================
// Computed
// =============================================================================

const canCreate = computed((): boolean => {
  return courseData.value.title.trim().length > 0
})

const hasUploadedFiles = computed((): boolean => {
  return fileUploadRef.value?.hasFiles() ?? false
})

// =============================================================================
// Methods
// =============================================================================

async function handleAnalyze(files: File[]): Promise<void> {
  if (files.length === 0) return

  isAnalyzing.value = true

  try {
    emit('analyze', files)
    aiAnalyzed.value = true
  } catch (error) {
    console.error('AI analysis failed:', error)
  } finally {
    isAnalyzing.value = false
  }
}

function updateFromAIAnalysis(data: {
  title: string
  description: string
  categoryId: number | null
  profileKey: string
}): void {
  courseData.value.title = data.title
  courseData.value.description = data.description
  courseData.value.categoryId = data.categoryId
  courseData.value.profileKey = data.profileKey
  aiAnalyzed.value = true
}

async function handleCreate(): Promise<void> {
  if (!canCreate.value) return

  isCreating.value = true

  try {
    const files = fileUploadRef.value?.getFiles() ?? []

    const data: NewCourseData = {
      title: courseData.value.title.trim(),
      description: courseData.value.description?.trim(),
      language: courseData.value.language,
      level: courseData.value.level,
      categoryId: courseData.value.categoryId,
      profileKey: courseData.value.profileKey,
      files
    }

    emit('create', data)
  } catch (error) {
    console.error('Course creation failed:', error)
  } finally {
    isCreating.value = false
  }
}

// =============================================================================
// Expose
// =============================================================================

defineExpose({
  updateFromAIAnalysis
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-content {
  background: var(--color-surface);
  border-radius: 0.75rem;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 42rem;
  padding: 1.5rem;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 1rem;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Footer */
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.footer-hint {
  flex: 1;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  margin: 0;
}

.footer-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-cancel,
.btn-create {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-cancel {
  background: none;
  border: none;
  color: var(--color-text-secondary);
}

.btn-cancel:hover {
  color: var(--color-text-primary);
}

.btn-create {
  background: var(--color-primary);
  color: white;
  border: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-create:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.btn-create:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
