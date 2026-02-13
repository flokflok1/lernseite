<!--
  Admin AI Kapitel Generator Window

  Window for generating course chapters using AI.
  Supports PDF upload and chapter structure generation.

  Phase: B24-06 - Admin Desktop OS
  Created: 2025-11-27 (modules → chapters refactoring)
-->

<template>
  <div class="admin-ai-kapitel-generator h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header -->
    <div class="p-4 border-b border-[var(--color-border)]">
      <h2 class="text-lg font-semibold text-[var(--color-text-primary)]">
        {{ $t('aiKapitelGenerator.title') }}
      </h2>
      <p class="text-sm text-[var(--color-text-secondary)] mt-1">
        {{ $t('aiKapitelGenerator.subtitle') }}
      </p>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-4 space-y-6">
      <!-- Course Selection -->
      <div v-if="!selectedCourseId" class="space-y-4">
        <label class="block text-sm font-medium text-[var(--color-text-primary)]">
          {{ $t('aiKapitelGenerator.selectCourse') }}
        </label>
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ $t('aiKapitelGenerator.noCourseHint') }}
        </p>
      </div>

      <!-- Generation Mode Selection -->
      <div v-else class="space-y-6">
        <!-- Mode Selection -->
        <div class="space-y-3">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            {{ $t('aiKapitelGenerator.generationMethod') }}
          </label>
          <div class="flex gap-3">
            <button
              @click="generationMode = 'pdf'"
              :class="[
                'flex-1 py-3 px-4 rounded-lg border-2 text-sm font-medium transition-colors',
                generationMode === 'pdf'
                  ? 'border-[var(--color-primary)] bg-[var(--color-primary-subtle)] text-[var(--color-primary)]'
                  : 'border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-[var(--color-border-hover)]'
              ]"
            >
              {{ $t('aiKapitelGenerator.pdfUpload') }}
            </button>
            <button
              @click="generationMode = 'prompt'"
              :class="[
                'flex-1 py-3 px-4 rounded-lg border-2 text-sm font-medium transition-colors',
                generationMode === 'prompt'
                  ? 'border-[var(--color-primary)] bg-[var(--color-primary-subtle)] text-[var(--color-primary)]'
                  : 'border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-[var(--color-border-hover)]'
              ]"
            >
              {{ $t('aiKapitelGenerator.textPrompt') }}
            </button>
          </div>
        </div>

        <!-- PDF Upload Mode -->
        <div v-if="generationMode === 'pdf'" class="space-y-4">
          <div
            class="border-2 border-dashed border-[var(--color-border)] rounded-lg p-8 text-center hover:border-[var(--color-primary)] transition-colors cursor-pointer"
            @click="triggerFileInput"
            @dragover.prevent
            @drop.prevent="handleFileDrop"
          >
            <input
              ref="fileInput"
              type="file"
              accept=".pdf"
              class="hidden"
              @change="handleFileSelect"
            />
            <div v-if="!selectedFile" class="space-y-2">
              <div class="text-4xl">📄</div>
              <p class="text-[var(--color-text-secondary)]">
                {{ $t('aiKapitelGenerator.dropPdfHint') }}
              </p>
              <p class="text-xs text-[var(--color-text-tertiary)]">
                {{ $t('aiKapitelGenerator.maxSize') }}
              </p>
            </div>
            <div v-else class="space-y-2">
              <div class="text-4xl">✅</div>
              <p class="text-[var(--color-text-primary)] font-medium">
                {{ selectedFile.name }}
              </p>
              <p class="text-xs text-[var(--color-text-secondary)]">
                {{ formatFileSize(selectedFile.size) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Prompt Mode -->
        <div v-if="generationMode === 'prompt'" class="space-y-4">
          <div class="space-y-2">
            <label class="block text-sm font-medium text-[var(--color-text-primary)]">
              {{ $t('aiKapitelGenerator.describeContent') }}
            </label>
            <textarea
              v-model="promptText"
              class="w-full h-32 px-3 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-sm text-[var(--color-text-primary)] placeholder-[var(--color-text-tertiary)] resize-none focus:outline-none focus:border-[var(--color-primary)]"
              :placeholder="$t('aiKapitelGenerator.contentPlaceholder')"
            ></textarea>
          </div>

          <!-- Chapter Count -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-[var(--color-text-primary)]">
              {{ $t('aiKapitelGenerator.chapterCount') }}
            </label>
            <input
              v-model.number="chapterCount"
              type="number"
              min="1"
              max="20"
              class="w-32 px-3 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-primary)]"
            />
          </div>
        </div>

        <!-- Generation Status -->
        <div v-if="isGenerating" class="space-y-4">
          <div class="flex items-center gap-3">
            <div class="animate-spin w-5 h-5 border-2 border-[var(--color-primary)] border-t-transparent rounded-full"></div>
            <span class="text-[var(--color-text-primary)]">{{ $t('aiKapitelGenerator.generatingChapters') }}</span>
          </div>
          <div class="w-full h-2 bg-[var(--color-surface)] rounded-full overflow-hidden">
            <div
              class="h-full bg-[var(--color-primary)] transition-all duration-300"
              :style="{ width: `${progress}%` }"
            ></div>
          </div>
          <p class="text-sm text-[var(--color-text-secondary)]">
            {{ statusMessage }}
          </p>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ errorMessage }}</p>
        </div>

        <!-- Generated Preview -->
        <div v-if="generatedChapters.length > 0" class="space-y-4">
          <h3 class="text-sm font-medium text-[var(--color-text-primary)]">
            {{ $t('aiKapitelGenerator.generatedChaptersTitle', { count: generatedChapters.length }) }}
          </h3>
          <div class="space-y-2 max-h-48 overflow-y-auto">
            <div
              v-for="(chapter, index) in generatedChapters"
              :key="index"
              class="p-3 bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]"
            >
              <p class="text-sm font-medium text-[var(--color-text-primary)]">
                {{ index + 1 }}. {{ chapter.title }}
              </p>
              <p v-if="chapter.description" class="text-xs text-[var(--color-text-secondary)] mt-1">
                {{ chapter.description }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="p-4 border-t border-[var(--color-border)] flex justify-end gap-3">
      <button
        @click="$emit('close')"
        class="px-4 py-2 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
      >
        {{ $t('aiKapitelGenerator.cancel') }}
      </button>
      <button
        v-if="generatedChapters.length > 0"
        @click="applyChapters"
        :disabled="isApplying"
        class="px-4 py-2 bg-[var(--color-primary)] text-white text-sm font-medium rounded-lg hover:bg-[var(--color-primary-hover)] disabled:opacity-50 transition-colors"
      >
        {{ isApplying ? $t('aiKapitelGenerator.applying') : $t('aiKapitelGenerator.applyChapters') }}
      </button>
      <button
        v-else
        @click="startGeneration"
        :disabled="!canGenerate || isGenerating"
        class="px-4 py-2 bg-[var(--color-primary)] text-white text-sm font-medium rounded-lg hover:bg-[var(--color-primary-hover)] disabled:opacity-50 transition-colors"
      >
        {{ $t('aiKapitelGenerator.generate') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxWindow } from '@/application/stores/window.store'

const { t } = useI18n()

interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
}

interface GeneratedChapter {
  title: string
  description?: string
  order_index: number
}

const props = defineProps<Props>()
defineEmits<Emits>()

// State
const generationMode = ref<'pdf' | 'prompt'>('prompt')
const selectedFile = ref<File | null>(null)
const promptText = ref('')
const chapterCount = ref(5)
const isGenerating = ref(false)
const isApplying = ref(false)
const progress = ref(0)
const statusMessage = ref('')
const errorMessage = ref('')
const generatedChapters = ref<GeneratedChapter[]>([])
const fileInput = ref<HTMLInputElement | null>(null)

// Computed
const selectedCourseId = computed(() => props.window.payload?.courseId as string | undefined)

const canGenerate = computed(() => {
  if (generationMode.value === 'pdf') {
    return !!selectedFile.value
  }
  return promptText.value.trim().length >= 10
})

// Methods
function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    selectedFile.value = input.files[0]
  }
}

function handleFileDrop(event: DragEvent) {
  const file = event.dataTransfer?.files[0]
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

async function startGeneration() {
  if (!canGenerate.value) return

  isGenerating.value = true
  progress.value = 0
  statusMessage.value = t('aiKapitelGenerator.initializing')
  errorMessage.value = ''
  generatedChapters.value = []

  try {
    // Simulate progress for now (real implementation would call API)
    for (let i = 0; i <= 100; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 300))
      progress.value = i
      statusMessage.value = i < 50 ? t('aiKapitelGenerator.analyzingContent') : t('aiKapitelGenerator.generatingStructure')
    }

    // Mock generated chapters (real implementation would use API response)
    generatedChapters.value = Array.from({ length: chapterCount.value }, (_, i) => ({
      title: `Kapitel ${i + 1}: ${['Einführung', 'Grundlagen', 'Vertiefung', 'Praxis', 'Zusammenfassung'][i % 5]}`,
      description: `Automatisch generiertes Kapitel ${i + 1}`,
      order_index: i + 1
    }))

    statusMessage.value = t('aiKapitelGenerator.done')
  } catch (error: any) {
    errorMessage.value = error.message || t('aiKapitelGenerator.generationError')
  } finally {
    isGenerating.value = false
  }
}

async function applyChapters() {
  if (!selectedCourseId.value || generatedChapters.value.length === 0) return

  isApplying.value = true
  try {
    // Real implementation would call API to create chapters
    console.log('Applying chapters to course:', selectedCourseId.value, generatedChapters.value)
    // Success - close window or show success message
  } catch (error: any) {
    errorMessage.value = error.message || t('aiKapitelGenerator.applyError')
  } finally {
    isApplying.value = false
  }
}
</script>

<style scoped>
.admin-ai-kapitel-generator {
  min-height: 400px;
}
</style>
