<!--
  Admin Course Editor Window Content

  Window content for editing course details, chapters, and settings.
  Features:
  - Course metadata editing (title, description, category, level, etc.)
  - Chapter management overview
  - Quick actions (publish, archive, delete)
  Phase: B24-06 - Admin Desktop OS
  Refactored: modules → chapters (2025-11-27)
-->

<template>
  <div class="admin-course-editor-window h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[var(--color-primary)] mx-auto mb-3"></div>
        <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('windows.courseEditor.loadingCourse') }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 p-6">
      <div class="rounded-lg p-4 border" style="background-color: var(--color-error-bg, #fef2f2); border-color: var(--color-error-border, #fecaca);">
        <p style="color: var(--color-error-text, #b91c1c);">{{ error }}</p>
        <button
          @click="loadCourse"
          class="mt-3 px-3 py-1.5 bg-red-600 text-white text-sm rounded hover:bg-red-700"
        >
          {{ $t('windows.courseEditor.retry') }}
        </button>
      </div>
    </div>

    <!-- Course Editor Content -->
    <div v-else-if="course" class="flex-1 flex flex-col overflow-hidden">
      <!-- Tabs -->
      <div class="border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <div class="flex px-4">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-4 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
            ]"
          >
            <span class="mr-2">{{ tab.icon }}</span>
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="flex-1 overflow-y-auto">
        <!-- Metadata Tab -->
        <div v-if="activeTab === 'metadata'" class="p-6">
          <form @submit.prevent="saveCourse" class="space-y-6">
            <!-- Title -->
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                {{ $t('windows.courseEditor.metadata.title') }}
              </label>
              <input
                v-model="form.title"
                type="text"
                required
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                :placeholder="$t('windows.courseEditor.metadata.titlePlaceholder')"
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                {{ $t('windows.courseEditor.metadata.description') }}
              </label>
              <textarea
                v-model="form.description"
                rows="4"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                :placeholder="$t('windows.courseEditor.metadata.descriptionPlaceholder')"
              ></textarea>
            </div>

            <!-- Category & Level -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                  {{ $t('windows.courseEditor.metadata.category') }}
                </label>
                <select
                  v-model="form.category_id"
                  class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                >
                  <option :value="null">{{ $t('windows.courseEditor.metadata.noCategory') }}</option>
                  <option
                    v-for="cat in flatCategories"
                    :key="cat.category_id"
                    :value="cat.category_id"
                  >
                    {{ cat.indent }}{{ cat.name }}
                  </option>
                </select>
                <p v-if="loadingCategories" class="mt-1 text-xs text-[var(--color-text-secondary)]">{{ $t('windows.courseEditor.metadata.loadingCategories') }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                  {{ $t('windows.courseEditor.metadata.level') }}
                </label>
                <select
                  v-model="form.level"
                  class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                >
                  <option value="beginner">{{ $t('windows.courseEditor.metadata.levelBeginner') }}</option>
                  <option value="intermediate">{{ $t('windows.courseEditor.metadata.levelIntermediate') }}</option>
                  <option value="advanced">{{ $t('windows.courseEditor.metadata.levelAdvanced') }}</option>
                  <option value="expert">{{ $t('windows.courseEditor.metadata.levelExpert') }}</option>
                </select>
              </div>
            </div>

            <!-- Language & Price -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                  {{ $t('windows.courseEditor.metadata.language') }}
                </label>
                <select
                  v-model="form.language"
                  class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                >
                  <option value="de">Deutsch</option>
                  <option value="en">English</option>
                  <option value="fr">Français</option>
                  <option value="es">Español</option>
                  <option value="it">Italiano</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                  {{ $t('windows.courseEditor.metadata.price') }}
                </label>
                <input
                  v-model.number="form.price"
                  type="number"
                  min="0"
                  step="0.01"
                  class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  placeholder="0.00"
                />
              </div>
            </div>

            <!-- Tags -->
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                {{ $t('windows.courseEditor.metadata.tags') }}
              </label>
              <input
                v-model="tagsInput"
                type="text"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                :placeholder="$t('windows.courseEditor.metadata.tagsPlaceholder')"
              />
              <div v-if="form.tags && form.tags.length > 0" class="flex flex-wrap gap-2 mt-2">
                <span
                  v-for="tag in form.tags"
                  :key="tag"
                  class="px-2 py-1 bg-[var(--color-primary)]/10 text-[var(--color-primary)] rounded text-xs"
                >
                  {{ tag }}
                </span>
              </div>
            </div>

            <!-- Visibility -->
            <div class="flex items-center gap-3">
              <input
                v-model="form.is_public"
                type="checkbox"
                id="is_public"
                class="w-4 h-4 text-[var(--color-primary)] border-[var(--color-border)] rounded focus:ring-[var(--color-primary)]"
              />
              <label for="is_public" class="text-sm font-medium text-[var(--color-text-primary)]">
                {{ $t('windows.courseEditor.metadata.isPublic') }}
              </label>
            </div>

            <!-- Save Button -->
            <div class="flex gap-3 pt-4">
              <button
                type="submit"
                :disabled="saving"
                class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {{ saving ? $t('windows.courseEditor.metadata.saving') : $t('windows.courseEditor.metadata.saveChanges') }}
              </button>
              <button
                type="button"
                @click="resetForm"
                class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                {{ $t('windows.courseEditor.metadata.reset') }}
              </button>
            </div>
          </form>
        </div>

        <!-- Chapters Tab -->
        <div v-else-if="activeTab === 'chapters'" class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
              {{ $t('windows.courseEditor.chapters.title', { count: chapters.length }) }}
            </h3>
            <button
              @click="openChapterEditor(null)"
              class="px-3 py-1.5 bg-[var(--color-primary)] text-white text-sm rounded-lg hover:bg-[var(--color-primary-hover)]"
            >
              {{ $t('windows.courseEditor.chapters.addNew') }}
            </button>
          </div>

          <!-- Chapters List -->
          <div v-if="loadingChapters" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)] mx-auto"></div>
          </div>

          <div v-else-if="chapters.length === 0" class="text-center py-8">
            <p class="text-[var(--color-text-secondary)]">{{ $t('windows.courseEditor.chapters.noChapters') }}</p>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="chapter in chapters"
              :key="chapter.chapter_id"
              class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 hover:border-[var(--color-primary)] transition-colors"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h4 class="font-semibold text-[var(--color-text-primary)] mb-1">
                    {{ chapter.order_index }}. {{ chapter.title }}
                  </h4>
                  <p v-if="chapter.description" class="text-sm text-[var(--color-text-secondary)] mb-2">
                    {{ chapter.description }}
                  </p>
                  <div class="flex gap-4 text-xs text-[var(--color-text-secondary)]">
                    <span>📚 {{ $t('windows.courseEditor.chapters.lessons', { count: chapter.lesson_count || 0 }) }}</span>
                    <span>⏱️ {{ $t('windows.courseEditor.chapters.duration', { minutes: chapter.duration_minutes }) }}</span>
                  </div>
                </div>
                <div class="flex gap-2">
                  <button
                    @click="openChapterEditor(chapter)"
                    class="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    {{ $t('windows.courseEditor.chapters.edit') }}
                  </button>
                  <button
                    @click="deleteChapter(chapter.chapter_id)"
                    class="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    {{ $t('windows.courseEditor.chapters.delete') }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions Tab -->
        <div v-else-if="activeTab === 'actions'" class="p-6">
          <div class="space-y-6">
            <!-- Status Actions -->
            <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
              <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">{{ $t('windows.courseEditor.actions.title') }}</h3>
              <div class="space-y-3">
                <div v-if="course.status === 'draft'" class="flex items-center justify-between">
                  <div>
                    <p class="font-medium text-[var(--color-text-primary)]">{{ $t('windows.courseEditor.actions.publishCourse') }}</p>
                    <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('windows.courseEditor.actions.publishHint') }}</p>
                  </div>
                  <button
                    @click="publishCourse"
                    class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    {{ $t('windows.courseEditor.actions.publishButton') }}
                  </button>
                </div>

                <div v-if="course.status === 'published'" class="flex items-center justify-between">
                  <div>
                    <p class="font-medium text-[var(--color-text-primary)]">{{ $t('windows.courseEditor.actions.unpublishCourse') }}</p>
                    <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('windows.courseEditor.actions.unpublishHint') }}</p>
                  </div>
                  <button
                    @click="unpublishCourse"
                    class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
                  >
                    {{ $t('windows.courseEditor.actions.unpublishButton') }}
                  </button>
                </div>

                <div class="flex items-center justify-between">
                  <div>
                    <p class="font-medium text-[var(--color-text-primary)]">{{ $t('windows.courseEditor.actions.archiveCourse') }}</p>
                    <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('windows.courseEditor.actions.archiveHint') }}</p>
                  </div>
                  <button
                    @click="archiveCourse"
                    class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    {{ $t('windows.courseEditor.actions.archiveButton') }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Danger Zone -->
            <div class="rounded-lg p-4 border" style="background-color: var(--color-error-bg, #fef2f2); border-color: var(--color-error-border, #fecaca);">
              <h3 class="text-lg font-semibold mb-4" style="color: var(--color-error-text, #b91c1c);">{{ $t('windows.courseEditor.actions.dangerZone') }}</h3>
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium" style="color: var(--color-error-text, #b91c1c);">{{ $t('windows.courseEditor.actions.deleteCourse') }}</p>
                  <p class="text-sm" style="color: var(--color-error, #dc2626);">{{ $t('windows.courseEditor.actions.deleteHint') }}</p>
                </div>
                <button
                  @click="deleteCourse"
                  class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  {{ $t('windows.courseEditor.actions.deleteButton') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWindowStore } from '@/store/modules/desktop'
import type { LsxWindow } from '@/store/modules/desktop'
import {
  adminGetCourseDetail,
  adminUpdateCourse,
  adminGetCourseChapters,
  adminPublishCourse,
  adminUnpublishCourse,
  adminArchiveCourse,
  adminDeleteCourse,
  adminDeleteChapter,
  type AdminCourseDetail,
  type AdminChapter
} from '@/api/admin.api'
import { getCategoryTree, type Category, type CategoryTreeNode } from '@/api/categories.api'

interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const windowStore = useWindowStore()
const { t } = useI18n()

// State
const course = ref<AdminCourseDetail | null>(null)
const chapters = ref<AdminChapter[]>([])
const categories = ref<CategoryTreeNode[]>([])
const loading = ref(true)
const loadingChapters = ref(false)
const loadingCategories = ref(false)
const error = ref<string | null>(null)
const saving = ref(false)
const activeTab = ref<'metadata' | 'chapters' | 'actions'>('metadata')

// Form
const form = ref({
  title: '',
  description: '',
  category_id: null as number | null,
  level: 'beginner',
  language: 'de',
  price: 0,
  is_public: true,
  tags: [] as string[]
})

const tagsInput = ref('')

// Flatten categories with indentation for hierarchical display
const flatCategories = computed(() => {
  const result: Array<Category & { indent: string }> = []

  const flatten = (cats: CategoryTreeNode[], level: number) => {
    for (const cat of cats) {
      result.push({
        ...cat,
        indent: '\u2014'.repeat(level) + (level > 0 ? ' ' : '')
      })
      if (cat.children && cat.children.length > 0) {
        flatten(cat.children, level + 1)
      }
    }
  }

  flatten(categories.value, 0)
  return result
})

// Computed
const tabs = computed(() => [
  { id: 'metadata', label: t('windows.courseEditor.tabs.metadata'), icon: '📝' },
  { id: 'chapters', label: t('windows.courseEditor.tabs.chapters'), icon: '📚' },
  { id: 'actions', label: t('windows.courseEditor.tabs.actions'), icon: '⚡' }
])

const courseId = computed(() => props.window.payload?.courseId as string)

// Methods
const loadCategories = async () => {
  loadingCategories.value = true
  try {
    const tree = await getCategoryTree(false)
    categories.value = tree.categories || []
  } catch (err) {
    console.error('Failed to load categories:', err)
    categories.value = []
  } finally {
    loadingCategories.value = false
  }
}

const loadCourse = async () => {
  if (!courseId.value) {
    error.value = t('windows.courseEditor.errors.noCourseId')
    loading.value = false
    return
  }

  loading.value = true
  error.value = null

  try {
    // Load categories in parallel
    loadCategories()

    course.value = await adminGetCourseDetail(courseId.value)
    populateForm()
  } catch (err: any) {
    console.error('Error loading course:', err)
    error.value = err.response?.data?.message || t('windows.courseEditor.errors.loadError')
  } finally {
    loading.value = false
  }
}

const loadChapters = async () => {
  if (!courseId.value) return

  loadingChapters.value = true
  try {
    chapters.value = await adminGetCourseChapters(courseId.value)
  } catch (err: any) {
    console.error('Error loading chapters:', err)
  } finally {
    loadingChapters.value = false
  }
}

const populateForm = () => {
  if (!course.value) return

  form.value = {
    title: course.value.title,
    description: course.value.description || '',
    category_id: course.value.category_id || null,
    level: course.value.level || 'beginner',
    language: course.value.language || 'de',
    price: course.value.price || 0,
    is_public: course.value.is_public,
    tags: course.value.tags || []
  }

  tagsInput.value = (course.value.tags || []).join(', ')
}

const resetForm = () => {
  populateForm()
}

const saveCourse = async () => {
  if (!courseId.value || !form.value.title.trim()) return

  saving.value = true
  try {
    // Parse tags from input
    const tags = tagsInput.value
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0)

    const updateData = {
      title: form.value.title,
      description: form.value.description || undefined,
      category_id: form.value.category_id,
      level: form.value.level,
      language: form.value.language,
      price: form.value.price,
      is_public: form.value.is_public,
      tags: tags.length > 0 ? tags : undefined
    }

    course.value = await adminUpdateCourse(courseId.value, updateData)
    populateForm()

    // Update window title
    windowStore.updateWindowPayload(props.window.id, {
      course: course.value
    })

    alert(t('windows.courseEditor.alerts.changesSaved'))
  } catch (err: any) {
    console.error('Error saving course:', err)
    alert(t('windows.courseEditor.errors.saveError') + ': ' + (err.response?.data?.message || err.message))
  } finally {
    saving.value = false
  }
}

const publishCourse = async () => {
  if (!courseId.value || !confirm(t('windows.courseEditor.alerts.publishConfirm'))) return

  try {
    await adminPublishCourse(courseId.value)
    await loadCourse()
    alert(t('windows.courseEditor.alerts.coursePublished'))
  } catch (err: any) {
    console.error('Error publishing course:', err)
    alert(t('windows.courseEditor.errors.publishError') + ': ' + (err.response?.data?.message || err.message))
  }
}

const unpublishCourse = async () => {
  if (!courseId.value || !confirm(t('windows.courseEditor.alerts.unpublishConfirm'))) return

  try {
    await adminUnpublishCourse(courseId.value)
    await loadCourse()
    alert(t('windows.courseEditor.alerts.courseUnpublished'))
  } catch (err: any) {
    console.error('Error unpublishing course:', err)
    alert(t('windows.courseEditor.errors.unpublishError') + ': ' + (err.response?.data?.message || err.message))
  }
}

const archiveCourse = async () => {
  if (!courseId.value || !confirm(t('windows.courseEditor.alerts.archiveConfirm'))) return

  try {
    await adminArchiveCourse(courseId.value)
    await loadCourse()
    alert(t('windows.courseEditor.alerts.courseArchived'))
  } catch (err: any) {
    console.error('Error archiving course:', err)
    alert(t('windows.courseEditor.errors.archiveError') + ': ' + (err.response?.data?.message || err.message))
  }
}

const deleteCourse = async () => {
  if (!courseId.value) return

  const confirmed = confirm(t('windows.courseEditor.alerts.deleteConfirm'))

  if (!confirmed) return

  try {
    await adminDeleteCourse(courseId.value, t('windows.courseEditor.alerts.deleteReason'))
    alert(t('windows.courseEditor.alerts.courseDeleted'))
    emit('close')
  } catch (err: any) {
    console.error('Error deleting course:', err)
    alert(t('windows.courseEditor.errors.deleteError') + ': ' + (err.response?.data?.message || err.message))
  }
}

const openChapterEditor = (chapter: AdminChapter | null) => {
  windowStore.openWindow({
    type: 'admin-kapitel-editor',
    title: chapter ? t('windows.courseEditor.chapters.editTitle', { title: chapter.title }) : t('windows.courseEditor.chapters.newTitle'),
    icon: '📚',
    payload: {
      courseId: courseId.value,
      courseTitle: course.value?.title,
      chapterId: chapter?.chapter_id,
      chapter: chapter
    }
  })
}

const deleteChapter = async (chapterId: string) => {
  if (!confirm(t('windows.courseEditor.alerts.chapterDeleteConfirm'))) return

  try {
    await adminDeleteChapter(chapterId, t('windows.courseEditor.alerts.chapterDeleteReason'))
    await loadChapters()
    alert(t('windows.courseEditor.alerts.chapterDeleted'))
  } catch (err: any) {
    console.error('Error deleting chapter:', err)
    alert(t('windows.courseEditor.errors.chapterDeleteError') + ': ' + (err.response?.data?.message || err.message))
  }
}

// Watch for tab changes
watch(activeTab, (newTab) => {
  if (newTab === 'chapters' && chapters.value.length === 0) {
    loadChapters()
  }
})

// Lifecycle
onMounted(() => {
  loadCourse()
})
</script>
