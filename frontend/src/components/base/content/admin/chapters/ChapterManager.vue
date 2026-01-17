<!--
  Admin Kapitel Manager Panel

  Übersicht aller Kapitel eines Kurses mit:
  - Liste aller Kapitel
  - Manuell erstellen
  - Bearbeiten
  - Löschen
  - Zurück zur Startseite

  Für KI-gestützte Kapitel-Erstellung: KI-Authoring-Studio verwenden

  Phase: Desktop OS - Kapitel-Manager
-->

<template>
  <div class="admin-kapitel-manager h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header mit Zurück-Button -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-surface)]">
      <div class="flex items-center gap-3">
        <button
          v-if="currentView !== 'list'"
          @click="goBack"
          class="p-1.5 rounded-lg hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div>
          <h2 class="text-sm font-semibold text-[var(--color-text-primary)]">
            {{ currentView === 'list' ? $t('features.chapterManager.title') : viewTitle }}
          </h2>
          <p class="text-xs text-[var(--color-text-secondary)]">
            {{ courseTitle }}
          </p>
        </div>
      </div>

      <!-- Action Buttons (nur in Liste) -->
      <div v-if="currentView === 'list'" class="flex items-center gap-2">
        <button
          @click="createManual"
          class="px-3 py-1.5 text-sm font-medium rounded-lg bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)] transition-colors flex items-center gap-1.5"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          {{ $t('features.chapterManager.newChapter') }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto">
      <!-- List View -->
      <div v-if="currentView === 'list'" class="p-4">
        <!-- Loading -->
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]"></div>
        </div>

        <!-- Empty State -->
        <div v-else-if="chapters.length === 0" class="text-center py-12">
          <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-[var(--color-surface-secondary)] flex items-center justify-center">
            <svg class="w-8 h-8 text-[var(--color-text-tertiary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
            {{ $t('features.chapterManager.noChaptersTitle') }}
          </h3>
          <p class="text-sm text-[var(--color-text-secondary)] mb-6 max-w-sm mx-auto">
            {{ $t('features.chapterManager.noChaptersDesc') }}
          </p>
          <button
            @click="createManual"
            class="px-4 py-2 text-sm font-medium rounded-lg bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)] transition-colors"
          >
            {{ $t('features.chapterManager.createFirst') }}
          </button>
        </div>

        <!-- Chapters List -->
        <div v-else class="space-y-2">
          <div
            v-for="chapter in sortedChapters"
            :key="chapter.chapter_id"
            class="group p-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-primary)] transition-all"
          >
            <div class="flex items-start gap-4">
              <!-- Order Number -->
              <div class="w-8 h-8 rounded-lg bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center text-sm font-bold flex-shrink-0">
                {{ chapter.order_index + 1 }}
              </div>

              <!-- Content -->
              <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-[var(--color-text-primary)] truncate">
                  {{ chapter.title }}
                </h3>
                <p v-if="chapter.description" class="text-sm text-[var(--color-text-secondary)] line-clamp-2 mt-1">
                  {{ chapter.description }}
                </p>
                <div class="flex items-center gap-4 mt-2 text-xs text-[var(--color-text-tertiary)]">
                  <span v-if="chapter.lesson_count !== undefined">
                    {{ $t('features.chapterManager.lessonsCount', { count: chapter.lesson_count }) }}
                  </span>
                  <span v-if="chapter.updated_at">
                    {{ formatDate(chapter.updated_at) }}
                  </span>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  @click="editChapter(chapter)"
                  class="p-2 rounded-lg hover:bg-blue-100 text-[var(--color-text-secondary)] hover:text-blue-600 transition-colors"
                  :title="$t('features.chapterManager.edit')"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  @click="deleteChapter(chapter)"
                  class="p-2 rounded-lg hover:bg-red-100 text-[var(--color-text-secondary)] hover:text-red-600 transition-colors"
                  :title="$t('features.chapterManager.delete')"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Create Manual View -->
      <div v-else-if="currentView === 'create-manual'" class="p-6">
        <div class="max-w-xl mx-auto space-y-6">
          <!-- Title -->
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ $t('features.chapterManager.chapterTitle') }}
            </label>
            <input
              v-model="newChapter.title"
              type="text"
              class="w-full px-4 py-2.5 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
              :placeholder="$t('features.chapterManager.titlePlaceholder')"
              @keydown.enter="saveNewChapter"
            />
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ $t('features.chapterManager.description') }}
            </label>
            <textarea
              v-model="newChapter.description"
              rows="4"
              class="w-full px-4 py-2.5 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent resize-none"
              :placeholder="$t('features.chapterManager.descriptionPlaceholder')"
            ></textarea>
          </div>

          <!-- Actions -->
          <div class="flex items-center justify-end gap-3 pt-4">
            <button
              @click="goBack"
              class="px-4 py-2 text-sm font-medium rounded-lg border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] transition-colors"
            >
              {{ $t('features.chapterManager.cancel') }}
            </button>
            <button
              @click="saveNewChapter"
              :disabled="!newChapter.title.trim() || saving"
              class="px-4 py-2 text-sm font-medium rounded-lg bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <svg v-if="saving" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ saving ? $t('features.chapterManager.creating') : $t('features.chapterManager.createChapter') }}
            </button>
          </div>

          <!-- Tipp -->
          <div class="p-4 rounded-lg bg-[var(--color-info-bg)] border border-[var(--color-info-border)]">
            <p class="text-sm text-[var(--color-info-text)]">
              {{ $t('features.chapterManager.tipAfterCreate') }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/store/modules/desktop'
import type { LsxPanel } from '@/store/modules/desktop'
import {
  adminGetCourseChapters,
  adminCreateChapter,
  adminDeleteChapter,
  type AdminChapter
} from '@/api/admin.api'

const { t, locale } = useI18n()

interface Props {
  panel: LsxPanel
}

const props = defineProps<Props>()
const emit = defineEmits<{ (e: 'close'): void }>()

const panelStore = usePanelStore()

// State
const currentView = ref<'list' | 'create-manual'>('list')
const viewTitle = ref('')
const loading = ref(true)
const saving = ref(false)
const chapters = ref<AdminChapter[]>([])
const newChapter = ref({
  title: '',
  description: ''
})

// Computed
const courseId = computed(() => props.panel.payload?.courseId as string)
const courseTitle = computed(() => props.panel.payload?.courseTitle as string || 'Kurs')

const sortedChapters = computed(() => {
  return [...chapters.value].sort((a, b) => (a.order_index || 0) - (b.order_index || 0))
})

// Methods
async function loadChapters() {
  if (!courseId.value) return

  loading.value = true
  try {
    const response = await adminGetCourseChapters(courseId.value)
    chapters.value = response.chapters || response || []
  } catch (error) {
    console.error('Failed to load chapters:', error)
    chapters.value = []
  } finally {
    loading.value = false
  }
}

function goBack() {
  currentView.value = 'list'
  viewTitle.value = ''
  newChapter.value = { title: '', description: '' }
}

function createManual() {
  currentView.value = 'create-manual'
  viewTitle.value = t('features.chapterManager.newChapterTitle')
  newChapter.value = { title: '', description: '' }
}

async function saveNewChapter() {
  if (!newChapter.value.title.trim() || !courseId.value) return

  saving.value = true
  try {
    const created = await adminCreateChapter(courseId.value, {
      title: newChapter.value.title.trim(),
      description: newChapter.value.description.trim() || undefined
    })

    // Refresh list
    await loadChapters()

    // Go back to list
    goBack()

    // Optionally open editor for the new chapter
    editChapter(created)

  } catch (error: any) {
    console.error('Failed to create chapter:', error)
    alert(t('features.chapterManager.createError') + ': ' + (error.response?.data?.message || error.message))
  } finally {
    saving.value = false
  }
}

function editChapter(chapter: AdminChapter) {
  panelStore.openPanel({
    type: 'admin-kapitel-editor',
    title: t('features.chapterManager.windowChapter', { title: chapter.title }),
    icon: '📖',
    payload: {
      courseId: courseId.value,
      courseTitle: courseTitle.value,
      chapterId: chapter.chapter_id,
      chapter: chapter
    }
  })
}

async function deleteChapter(chapter: AdminChapter) {
  if (!confirm(t('features.chapterManager.deleteConfirm', { title: chapter.title }))) {
    return
  }

  try {
    await adminDeleteChapter(chapter.chapter_id)
    await loadChapters()
  } catch (error: any) {
    console.error('Failed to delete chapter:', error)
    alert(t('features.chapterManager.deleteError') + ': ' + (error.response?.data?.message || error.message))
  }
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString(locale.value, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

// Lifecycle
onMounted(() => {
  loadChapters()

  // Listen for chapter updates
  window.addEventListener('chapter-updated', loadChapters)
})

import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('chapter-updated', loadChapters)
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
