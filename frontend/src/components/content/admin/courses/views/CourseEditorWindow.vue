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
        <p class="text-sm text-[var(--color-text-secondary)]">Lade Kursdaten...</p>
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
          Erneut versuchen
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
                Titel *
              </label>
              <input
                v-model="form.title"
                type="text"
                required
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                placeholder="Kurstititel eingeben..."
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                Beschreibung
              </label>
              <textarea
                v-model="form.description"
                rows="4"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                placeholder="Kursbeschreibung eingeben..."
              ></textarea>
            </div>

            <!-- Category & Level -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                  Kategorie
                </label>
                <select
                  v-model="form.category_id"
                  class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                >
                  <option :value="null">Keine Kategorie</option>
                  <option
                    v-for="cat in flatCategories"
                    :key="cat.category_id"
                    :value="cat.category_id"
                  >
                    {{ cat.indent }}{{ cat.name }}
                  </option>
                </select>
                <p v-if="loadingCategories" class="mt-1 text-xs text-[var(--color-text-secondary)]">Kategorien werden geladen...</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                  Level
                </label>
                <select
                  v-model="form.level"
                  class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                >
                  <option value="beginner">Anfänger</option>
                  <option value="intermediate">Fortgeschritten</option>
                  <option value="advanced">Experte</option>
                  <option value="expert">Meister</option>
                </select>
              </div>
            </div>

            <!-- Language & Price -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                  Sprache
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
                  Preis (€)
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
                Tags (kommagetrennt)
              </label>
              <input
                v-model="tagsInput"
                type="text"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                placeholder="python, programmieren, anfänger"
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
                Kurs öffentlich sichtbar
              </label>
            </div>

            <!-- Save Button -->
            <div class="flex gap-3 pt-4">
              <button
                type="submit"
                :disabled="saving"
                class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {{ saving ? 'Speichert...' : 'Änderungen speichern' }}
              </button>
              <button
                type="button"
                @click="resetForm"
                class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                Zurücksetzen
              </button>
            </div>
          </form>
        </div>

        <!-- Chapters Tab -->
        <div v-else-if="activeTab === 'chapters'" class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
              Kapitel ({{ chapters.length }})
            </h3>
            <button
              @click="openChapterEditor(null)"
              class="px-3 py-1.5 bg-[var(--color-primary)] text-white text-sm rounded-lg hover:bg-[var(--color-primary-hover)]"
            >
              + Neues Kapitel
            </button>
          </div>

          <!-- Chapters List -->
          <div v-if="loadingChapters" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)] mx-auto"></div>
          </div>

          <div v-else-if="chapters.length === 0" class="text-center py-8">
            <p class="text-[var(--color-text-secondary)]">Noch keine Kapitel vorhanden</p>
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
                    <span>📚 {{ chapter.lesson_count || 0 }} Lektionen</span>
                    <span>⏱️ {{ chapter.duration_minutes }} Min.</span>
                  </div>
                </div>
                <div class="flex gap-2">
                  <button
                    @click="openChapterEditor(chapter)"
                    class="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Bearbeiten
                  </button>
                  <button
                    @click="deleteChapter(chapter.chapter_id)"
                    class="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    Löschen
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
              <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">Status-Aktionen</h3>
              <div class="space-y-3">
                <div v-if="course.status === 'draft'" class="flex items-center justify-between">
                  <div>
                    <p class="font-medium text-[var(--color-text-primary)]">Kurs veröffentlichen</p>
                    <p class="text-sm text-[var(--color-text-secondary)]">Macht den Kurs für Lernende sichtbar</p>
                  </div>
                  <button
                    @click="publishCourse"
                    class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Veröffentlichen
                  </button>
                </div>

                <div v-if="course.status === 'published'" class="flex items-center justify-between">
                  <div>
                    <p class="font-medium text-[var(--color-text-primary)]">Veröffentlichung zurückziehen</p>
                    <p class="text-sm text-[var(--color-text-secondary)]">Setzt Kurs auf "Entwurf" zurück</p>
                  </div>
                  <button
                    @click="unpublishCourse"
                    class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
                  >
                    Zurückziehen
                  </button>
                </div>

                <div class="flex items-center justify-between">
                  <div>
                    <p class="font-medium text-[var(--color-text-primary)]">Kurs archivieren</p>
                    <p class="text-sm text-[var(--color-text-secondary)]">Archiviert den Kurs</p>
                  </div>
                  <button
                    @click="archiveCourse"
                    class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Archivieren
                  </button>
                </div>
              </div>
            </div>

            <!-- Danger Zone -->
            <div class="rounded-lg p-4 border" style="background-color: var(--color-error-bg, #fef2f2); border-color: var(--color-error-border, #fecaca);">
              <h3 class="text-lg font-semibold mb-4" style="color: var(--color-error-text, #b91c1c);">Danger Zone</h3>
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium" style="color: var(--color-error-text, #b91c1c);">Kurs löschen</p>
                  <p class="text-sm" style="color: var(--color-error, #dc2626);">Diese Aktion kann nicht rückgängig gemacht werden</p>
                </div>
                <button
                  @click="deleteCourse"
                  class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Kurs löschen
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
import { useWindowStore } from '@/store/window.store'
import type { LsxWindow } from '@/store/window.store'
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
  { id: 'metadata', label: 'Metadaten', icon: '📝' },
  { id: 'chapters', label: 'Kapitel', icon: '📚' },
  { id: 'actions', label: 'Aktionen', icon: '⚡' }
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
    error.value = 'Keine Kurs-ID angegeben'
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
    error.value = err.response?.data?.message || 'Fehler beim Laden der Kursdaten'
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

    alert('Änderungen gespeichert!')
  } catch (err: any) {
    console.error('Error saving course:', err)
    alert('Fehler beim Speichern: ' + (err.response?.data?.message || err.message))
  } finally {
    saving.value = false
  }
}

const publishCourse = async () => {
  if (!courseId.value || !confirm('Möchten Sie diesen Kurs wirklich veröffentlichen?')) return

  try {
    await adminPublishCourse(courseId.value)
    await loadCourse()
    alert('Kurs wurde veröffentlicht!')
  } catch (err: any) {
    console.error('Error publishing course:', err)
    alert('Fehler beim Veröffentlichen: ' + (err.response?.data?.message || err.message))
  }
}

const unpublishCourse = async () => {
  if (!courseId.value || !confirm('Möchten Sie die Veröffentlichung wirklich zurückziehen?')) return

  try {
    await adminUnpublishCourse(courseId.value)
    await loadCourse()
    alert('Veröffentlichung wurde zurückgezogen!')
  } catch (err: any) {
    console.error('Error unpublishing course:', err)
    alert('Fehler: ' + (err.response?.data?.message || err.message))
  }
}

const archiveCourse = async () => {
  if (!courseId.value || !confirm('Möchten Sie diesen Kurs wirklich archivieren?')) return

  try {
    await adminArchiveCourse(courseId.value)
    await loadCourse()
    alert('Kurs wurde archiviert!')
  } catch (err: any) {
    console.error('Error archiving course:', err)
    alert('Fehler: ' + (err.response?.data?.message || err.message))
  }
}

const deleteCourse = async () => {
  if (!courseId.value) return

  const confirmed = confirm(
    'WARNUNG: Möchten Sie diesen Kurs wirklich PERMANENT löschen?\n\nDiese Aktion kann nicht rückgängig gemacht werden!'
  )

  if (!confirmed) return

  try {
    await adminDeleteCourse(courseId.value, 'Manuell durch Admin gelöscht')
    alert('Kurs wurde gelöscht!')
    emit('close')
  } catch (err: any) {
    console.error('Error deleting course:', err)
    alert('Fehler beim Löschen: ' + (err.response?.data?.message || err.message))
  }
}

const openChapterEditor = (chapter: AdminChapter | null) => {
  windowStore.openWindow({
    type: 'admin-kapitel-editor',
    title: chapter ? `Kapitel bearbeiten: ${chapter.title}` : 'Neues Kapitel',
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
  if (!confirm('Möchten Sie dieses Kapitel wirklich löschen?')) return

  try {
    await adminDeleteChapter(chapterId, 'Gelöscht durch Admin')
    await loadChapters()
    alert('Kapitel wurde gelöscht!')
  } catch (err: any) {
    console.error('Error deleting chapter:', err)
    alert('Fehler: ' + (err.response?.data?.message || err.message))
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
