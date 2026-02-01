<!--
  Admin Course Files Panel

  Manages course files (upload, list, delete) in a desktop panel.
  Can be opened multiple times for different courses.

  Phase: B24-06 - Admin Desktop OS
-->

<template>
  <div class="admin-course-files-panel h-full flex flex-col bg-white dark:bg-gray-900">
    <!-- Header -->
    <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between animated-header-gradient">
      <div>
        <h2 class="text-sm font-bold text-gray-900 dark:text-white">Kursdateien</h2>
        <p class="text-xs text-gray-500 dark:text-gray-400">{{ courseTitle }}</p>
      </div>
      <div class="flex items-center gap-2">
        <input
          ref="fileUploadInput"
          type="file"
          class="hidden"
          accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.png,.jpg,.jpeg,.gif,.mp4,.mp3,.zip"
          multiple
          @change="handleFileSelect"
        />
        <button
          @click="triggerFileUpload"
          :disabled="isUploading"
          class="px-3 py-1.5 bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 hover:from-pink-600 hover:via-purple-600 hover:to-indigo-600 text-white text-xs rounded-md font-medium transition-all shadow-sm hover:shadow-md flex items-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg v-if="!isUploading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
          </svg>
          <div v-else class="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
          <span>{{ isUploading ? 'Lädt...' : 'Hochladen' }}</span>
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-auto p-4">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center h-full">
        <div class="text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-2 border-purple-600 border-t-transparent mx-auto mb-3"></div>
          <p class="text-sm text-gray-600 dark:text-gray-400">Lade Dateien...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="p-4">
        <div class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p class="text-sm text-red-700 dark:text-red-300">{{ error }}</p>
          <button @click="loadFiles" class="mt-2 text-sm text-red-600 dark:text-red-400 hover:underline font-medium">
            Erneut versuchen
          </button>
        </div>
      </div>

      <!-- Files List -->
      <div v-else-if="files.length > 0" class="space-y-2">
        <div
          v-for="(file, idx) in files"
          :key="file.course_file_id"
          class="group p-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-purple-400 dark:hover:border-purple-500 rounded-lg transition-all hover:shadow-sm"
        >
          <div class="flex items-center gap-3">
            <!-- Number Badge -->
            <div class="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-pink-500 via-purple-500 to-indigo-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">
              {{ idx + 1 }}
            </div>

            <!-- File Icon based on type -->
            <div class="flex-shrink-0 w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <span class="text-xl">{{ getFileIcon(file.file_type) }}</span>
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors truncate">
                {{ file.display_name || file.file_name }}
              </h3>
              <div class="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                <span class="flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                  </svg>
                  {{ getCategoryLabel(file.file_category) }}
                </span>
                <span class="flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"/>
                  </svg>
                  {{ formatFileSize(file.file_size_bytes) }}
                </span>
                <span v-if="file.created_at" class="flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                  </svg>
                  {{ formatDate(file.created_at) }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex-shrink-0 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                @click="downloadFile(file)"
                class="p-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-all"
                :title="$t('admin.actions.download')"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                </svg>
              </button>
              <button
                @click="deleteFile(file)"
                class="p-2 text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all"
                :title="t('admin.actions.delete')"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="flex items-center justify-center h-full">
        <div class="text-center">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-pink-100 via-purple-100 to-indigo-100 dark:from-pink-900/30 dark:via-purple-900/30 dark:to-indigo-900/30 rounded-xl mb-4">
            <svg class="w-8 h-8 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
            </svg>
          </div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">Noch keine Dateien</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4 max-w-xs mx-auto">
            Lade Kursmaterialien, Skripte oder andere Dateien hoch.
          </p>
          <button
            @click="triggerFileUpload"
            class="px-4 py-2 bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 hover:from-pink-600 hover:via-purple-600 hover:to-indigo-600 text-white text-sm rounded-lg font-medium transition-all shadow-sm hover:shadow-md"
          >
            Erste Datei hochladen
          </button>
        </div>
      </div>
    </div>

    <!-- Footer with stats -->
    <div v-if="files.length > 0" class="px-4 py-2 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
      <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <span>{{ files.length }} Datei{{ files.length !== 1 ? 'en' : '' }}</span>
        <span>{{ formatFileSize(totalSize) }} gesamt</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxPanel } from '@/application/stores/modules/desktop'
import {
  adminListCourseFiles,
  adminUploadCourseFile,
  adminDeleteCourseFile,
  type CourseFile,
  type CourseFileCategory
} from '@/application/services/api/admin'

const { t } = useI18n()

// ============================================================================
// Props
// ============================================================================

interface Props {
  panel: LsxPanel
}

const props = defineProps<Props>()

// ============================================================================
// State
// ============================================================================

const courseId = computed(() => props.panel.payload?.courseId as string)
const courseTitle = computed(() => props.panel.payload?.courseTitle as string || 'Kurs')

const files = ref<CourseFile[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const fileUploadInput = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)

// ============================================================================
// Computed
// ============================================================================

const totalSize = computed(() => {
  return files.value.reduce((sum, file) => sum + (file.file_size_bytes || 0), 0)
})

// ============================================================================
// Methods
// ============================================================================

const loadFiles = async () => {
  if (!courseId.value) return

  loading.value = true
  error.value = null

  try {
    const response = await adminListCourseFiles(courseId.value)
    files.value = response.files
  } catch (err: any) {
    console.error('Error loading files:', err)
    error.value = err.response?.data?.message || err.message || 'Fehler beim Laden der Dateien'
  } finally {
    loading.value = false
  }
}

const triggerFileUpload = () => {
  fileUploadInput.value?.click()
}

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const selectedFiles = target.files

  if (!selectedFiles || selectedFiles.length === 0 || !courseId.value) return

  isUploading.value = true

  try {
    // Upload each file
    for (const file of Array.from(selectedFiles)) {
      const response = await adminUploadCourseFile(courseId.value, file, {
        file_category: 'material'
      })

    }

    await loadFiles()
  } catch (err: any) {
    console.error('Error uploading file:', err)
    error.value = err.response?.data?.error || t('common.errors.uploadFailed')
  } finally {
    isUploading.value = false
    if (target) target.value = ''
  }
}

const downloadFile = (file: CourseFile) => {
  if (file.storage_url) {
    window.open(file.storage_url, '_blank')
  }
}

const deleteFile = async (file: CourseFile) => {
  if (!courseId.value) return

  const confirmed = confirm(t('admin.files.confirmDelete', { name: file.display_name || file.file_name }))
  if (!confirmed) return

  try {
    await adminDeleteCourseFile(courseId.value, file.course_file_id)
    await loadFiles()
  } catch (err: any) {
    console.error('Error deleting file:', err)
    error.value = err.response?.data?.error || t('common.errors.deleteFailed')
  }
}

const formatFileSize = (bytes: number | null): string => {
  if (!bytes) return '–'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit'
  })
}

const getCategoryLabel = (category: CourseFileCategory): string => {
  const labels: Record<CourseFileCategory, string> = {
    script: 'Skript',
    material: 'Material',
    exercise: 'Übung',
    solution: 'Lösung',
    reference: 'Referenz',
    template: 'Vorlage',
    other: 'Sonstiges'
  }
  return labels[category] || category
}

const getFileIcon = (fileType: string): string => {
  const icons: Record<string, string> = {
    pdf: '📄',
    docx: '📝',
    doc: '📝',
    pptx: '📊',
    ppt: '📊',
    xlsx: '📈',
    xls: '📈',
    txt: '📃',
    png: '🖼️',
    jpg: '🖼️',
    jpeg: '🖼️',
    gif: '🖼️',
    mp4: '🎬',
    mp3: '🎵',
    zip: '📦'
  }
  return icons[fileType?.toLowerCase()] || '📎'
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  loadFiles()
})

// Reload when courseId changes
watch(courseId, () => {
  loadFiles()
})
</script>

<style scoped>
/* Animated header gradient */
.animated-header-gradient {
  background: linear-gradient(
    90deg,
    rgba(236, 72, 153, 0.15) 0%,
    rgba(139, 92, 246, 0.15) 25%,
    rgba(99, 102, 241, 0.15) 50%,
    rgba(6, 182, 212, 0.12) 75%,
    rgba(236, 72, 153, 0.15) 100%
  );
  background-size: 400% 400%;
  animation: gradient-shift 12s ease infinite;
}

@keyframes gradient-shift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.dark .animated-header-gradient {
  background: linear-gradient(
    90deg,
    rgba(124, 58, 237, 0.4) 0%,
    rgba(236, 72, 153, 0.4) 25%,
    rgba(139, 92, 246, 0.4) 50%,
    rgba(6, 182, 212, 0.3) 75%,
    rgba(124, 58, 237, 0.4) 100%
  );
  background-size: 400% 400%;
  animation: gradient-shift 12s ease infinite;
}
</style>
