<!--
  Admin AI Studio Pro - Vollständiges KI-Authoring-System

  Features:
  - 📚 Inhalt: Kapitel & Lektionen verwalten
  - 🎬 Videos: Erklärungs-Videos mit Sora 2 generieren
  - 🎨 Assets: Grafiken, Formeln, Diagramme
  - 📝 Prompts: System-Prompts pro LM bearbeiten
  - ⚙️ Modelle: KI-Modelle konfigurieren
  - 📊 Stats: Verbrauch und Statistiken
  - 💬 Chat: KI-Assistent (collapsible)

  Phase: KI-Studio Pro Rebuild
  Created: 2025-12-11
-->

<template>
  <div class="ai-studio-pro h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] bg-gradient-to-r from-violet-600 to-purple-600">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-bold text-white">KI-Authoring-Studio Pro</h2>
          <p class="text-xs text-white/70">{{ selectedCourse?.title || 'Kurs auswählen' }}</p>
        </div>
      </div>

      <!-- Course Selector -->
      <div class="flex items-center gap-3">
        <select
          v-model="selectedCourseId"
          @change="onCourseChange"
          class="px-3 py-2 text-sm bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-white/40"
        >
          <option value="" class="text-gray-900">Kurs auswählen...</option>
          <option v-for="course in courses" :key="course.course_id" :value="course.course_id" class="text-gray-900">
            {{ course.title }}
          </option>
        </select>

        <!-- Quick Stats -->
        <div class="flex items-center gap-2 px-3 py-1.5 bg-white/10 rounded-lg">
          <span class="text-xs text-white/70">Lektionen:</span>
          <span class="text-sm font-bold text-white">{{ stats.totalLessons }}</span>
        </div>
      </div>
    </div>

    <!-- Main Tabs -->
    <div class="flex border-b border-[var(--color-border)] bg-[var(--color-surface-secondary)]">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all relative"
        :class="activeTab === tab.id
          ? 'text-[var(--color-primary)] bg-[var(--color-bg)]'
          : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface)]'"
      >
        <span class="text-lg">{{ tab.icon }}</span>
        <span>{{ tab.label }}</span>
        <span
          v-if="tab.badge"
          class="px-1.5 py-0.5 text-[10px] font-bold rounded-full"
          :class="tab.badgeColor || 'bg-[var(--color-primary)] text-white'"
        >
          {{ tab.badge }}
        </span>
        <div
          v-if="activeTab === tab.id"
          class="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--color-primary)]"
        ></div>
      </button>

      <!-- Spacer -->
      <div class="flex-1"></div>

      <!-- Chat Toggle -->
      <button
        @click="chatExpanded = !chatExpanded"
        class="flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all"
        :class="chatExpanded ? 'text-[var(--color-primary)]' : 'text-[var(--color-text-secondary)]'"
      >
        <span class="text-lg">💬</span>
        <span>Chat</span>
        <svg
          class="w-4 h-4 transition-transform"
          :class="chatExpanded ? 'rotate-180' : ''"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Left Sidebar: Course Structure -->
      <div class="w-64 flex-shrink-0 border-r border-[var(--color-border)] bg-[var(--color-surface-secondary)] flex flex-col">
        <!-- Sidebar Header -->
        <div class="p-3 border-b border-[var(--color-border)]">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Suchen..."
              class="w-full pl-8 pr-3 py-2 text-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg"
            />
            <svg class="absolute left-2.5 top-2.5 w-4 h-4 text-[var(--color-text-tertiary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        <!-- Chapter Tree -->
        <div class="flex-1 overflow-y-auto p-2">
          <div v-if="!selectedCourseId" class="p-4 text-center text-sm text-[var(--color-text-tertiary)]">
            Wähle einen Kurs aus
          </div>
          <div v-else-if="loading" class="p-4 text-center">
            <div class="animate-spin w-6 h-6 border-2 border-[var(--color-primary)] border-t-transparent rounded-full mx-auto"></div>
          </div>
          <template v-else>
            <div v-for="chapter in filteredChapters" :key="chapter.chapter_id" class="mb-1">
              <!-- Chapter Header -->
              <button
                @click="toggleChapter(chapter)"
                class="w-full p-2 rounded-lg text-left flex items-center gap-2 transition-colors"
                :class="selectedChapterId === chapter.chapter_id
                  ? 'bg-[var(--color-primary-subtle)] text-[var(--color-primary)]'
                  : 'hover:bg-[var(--color-surface)]'"
              >
                <svg
                  class="w-4 h-4 transition-transform flex-shrink-0"
                  :class="expandedChapters.has(chapter.chapter_id) ? 'rotate-90' : ''"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
                <span class="text-xs font-mono text-[var(--color-text-tertiary)]">{{ chapter.order_index + 1 }}.</span>
                <span class="text-sm font-medium truncate flex-1">{{ chapter.title }}</span>
                <span class="text-xs text-[var(--color-text-tertiary)]">{{ chapter.lessons?.length || 0 }}</span>
              </button>

              <!-- Lessons -->
              <div v-if="expandedChapters.has(chapter.chapter_id)" class="ml-4 mt-1 space-y-0.5">
                <button
                  v-for="lesson in chapter.lessons"
                  :key="lesson.lesson_id"
                  @click="selectLesson(lesson, chapter)"
                  class="w-full p-2 rounded-lg text-left flex items-center gap-2 transition-colors text-sm"
                  :class="selectedLessonId === lesson.lesson_id
                    ? 'bg-[var(--color-primary)] text-white'
                    : 'hover:bg-[var(--color-surface)] text-[var(--color-text-secondary)]'"
                >
                  <span class="text-xs font-mono opacity-60">{{ lesson.order_index + 1 }}.</span>
                  <span class="truncate flex-1">{{ lesson.title }}</span>
                  <!-- LM Badge -->
                  <span
                    v-if="lesson.lm_type"
                    class="px-1.5 py-0.5 text-[10px] font-medium rounded"
                    :class="selectedLessonId === lesson.lesson_id ? 'bg-white/20' : 'bg-[var(--color-primary-subtle)] text-[var(--color-primary)]'"
                  >
                    {{ lesson.lm_type }}
                  </span>
                </button>
              </div>
            </div>
          </template>
        </div>

        <!-- Quick Actions -->
        <div class="p-3 border-t border-[var(--color-border)] space-y-2">
          <button
            @click="createNewChapter"
            class="w-full p-2 rounded-lg text-sm font-medium bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)] transition-colors flex items-center justify-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Neues Kapitel
          </button>
        </div>
      </div>

      <!-- Main Content -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Tab Content -->
        <div class="flex-1 overflow-y-auto">
          <!-- 📚 Inhalt Tab -->
          <ContentTab
            v-if="activeTab === 'content'"
            :lesson="selectedLesson"
            :chapter="selectedChapter"
            :course="selectedCourse"
            @save="onContentUpdate"
          />

          <!-- 👨‍🏫 Tutor Tab -->
          <TutorTab
            v-if="activeTab === 'tutor'"
            :lesson="selectedLesson"
            :chapter="selectedChapter"
            :course="selectedCourse"
          />

          <!-- 🎨 Assets Tab -->
          <AssetsTab
            v-if="activeTab === 'assets'"
            :courseId="selectedCourseId"
            :lessonId="selectedLessonId"
          />

          <!-- 📝 Prompts Tab -->
          <PromptsTab
            v-if="activeTab === 'prompts'"
            :lesson="selectedLesson"
          />

          <!-- ⚙️ Modelle Tab -->
          <ModelsTab
            v-if="activeTab === 'models'"
          />

          <!-- 📊 Stats Tab -->
          <StatsTab
            v-if="activeTab === 'stats'"
            :course="selectedCourse"
            :stats="stats"
          />
        </div>

        <!-- Chat Panel (collapsible) -->
        <div
          v-if="chatExpanded"
          class="h-64 border-t border-[var(--color-border)] flex flex-col bg-[var(--color-surface-secondary)]"
        >
          <ChatPanel
            :lessonTitle="selectedLesson?.title"
            :courseTitle="selectedCourse?.title"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { LsxWindow } from '@/store/window.store'

// Sub-components
import ContentTab from './ai-studio/ContentTab.vue'
import TutorTab from './ai-studio/TutorTab.vue'
import AssetsTab from './ai-studio/AssetsTab.vue'
import PromptsTab from './ai-studio/PromptsTab.vue'
import ModelsTab from './ai-studio/ModelsTab.vue'
import StatsTab from './ai-studio/StatsTab.vue'
import ChatPanel from './ai-studio/ChatPanel.vue'

// Types
interface Course {
  course_id: string
  title: string
  description?: string
}

interface Chapter {
  chapter_id: string
  title: string
  order_index: number
  lessons?: Lesson[]
}

interface Lesson {
  lesson_id: string
  title: string
  order_index: number
  lm_type?: string
  has_video?: boolean
  video_generating?: boolean
  content?: Record<string, unknown>
}

interface Stats {
  videosGenerated: number
  totalLessons: number
  tokensUsed: number
  costToday: number
}

// Props
interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

// State
const loading = ref(false)
const courses = ref<Course[]>([])
const selectedCourseId = ref('')
const selectedCourse = computed(() => courses.value.find(c => c.course_id === selectedCourseId.value))

const chapters = ref<Chapter[]>([])
const expandedChapters = ref<Set<string>>(new Set())
const selectedChapterId = ref<string | null>(null)
const selectedChapter = computed(() => chapters.value.find(c => c.chapter_id === selectedChapterId.value))

const selectedLessonId = ref<string | null>(null)
const selectedLesson = computed(() => {
  for (const chapter of chapters.value) {
    const lesson = chapter.lessons?.find(l => l.lesson_id === selectedLessonId.value)
    if (lesson) return lesson
  }
  return null
})

const searchQuery = ref('')
const activeTab = ref('tutor') // Default to tutor tab
const chatExpanded = ref(false)

const stats = ref<Stats>({
  videosGenerated: 0,
  totalLessons: 0,
  tokensUsed: 0,
  costToday: 0
})

// Tabs configuration
const tabs = computed(() => [
  { id: 'content', icon: '📚', label: 'Inhalt' },
  { id: 'tutor', icon: '👨‍🏫', label: 'Tutor', badge: stats.value.totalLessons > 0 ? `${stats.value.totalLessons}` : undefined, badgeColor: 'bg-violet-500 text-white' },
  { id: 'assets', icon: '🎨', label: 'Assets' },
  { id: 'prompts', icon: '📝', label: 'Prompts' },
  { id: 'models', icon: '⚙️', label: 'Modelle' },
  { id: 'stats', icon: '📊', label: 'Stats' }
])

// Filtered chapters based on search
const filteredChapters = computed(() => {
  if (!searchQuery.value) return chapters.value
  const query = searchQuery.value.toLowerCase()
  return chapters.value.filter(chapter => {
    if (chapter.title.toLowerCase().includes(query)) return true
    return chapter.lessons?.some(lesson => lesson.title.toLowerCase().includes(query))
  })
})

// Methods
async function loadCourses() {
  try {
    const response = await fetch('/api/v1/admin/courses', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    })
    if (response.ok) {
      const data = await response.json()
      courses.value = data.data?.courses || data.courses || []
    }
  } catch (error) {
    console.error('Failed to load courses:', error)
  }
}

async function loadChaptersWithLessons(courseId: string) {
  loading.value = true
  try {
    // Load chapters
    const chaptersRes = await fetch(`/api/v1/admin/courses/${courseId}/chapters`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    })
    if (chaptersRes.ok) {
      const data = await chaptersRes.json()
      const loadedChapters = data.data?.chapters || data.chapters || []

      // Load lessons for each chapter
      for (const chapter of loadedChapters) {
        const lessonsRes = await fetch(`/api/v1/admin/chapters/${chapter.chapter_id}/lessons`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        })
        if (lessonsRes.ok) {
          const lessonsData = await lessonsRes.json()
          chapter.lessons = (lessonsData.data?.lessons || lessonsData.lessons || []).map((l: any) => ({
            ...l,
            lm_type: l.content?.lm_primary,
            has_video: l.content?.has_video || false,
            video_generating: false
          }))
        }
      }

      chapters.value = loadedChapters
      updateStats()
    }
  } catch (error) {
    console.error('Failed to load chapters:', error)
  } finally {
    loading.value = false
  }
}

function updateStats() {
  let total = 0
  let withVideo = 0
  for (const chapter of chapters.value) {
    for (const lesson of chapter.lessons || []) {
      total++
      if (lesson.has_video) withVideo++
    }
  }
  stats.value.totalLessons = total
  stats.value.videosGenerated = withVideo
}

function onCourseChange(_event?: Event) {
  // Reset state
  chapters.value = []
  selectedChapterId.value = null
  selectedLessonId.value = null
  expandedChapters.value.clear()

  // Load chapters if course is selected
  if (selectedCourseId.value) {
    loadChaptersWithLessons(selectedCourseId.value)
  }
}

function toggleChapter(chapter: Chapter) {
  if (expandedChapters.value.has(chapter.chapter_id)) {
    expandedChapters.value.delete(chapter.chapter_id)
  } else {
    expandedChapters.value.add(chapter.chapter_id)
  }
  selectedChapterId.value = chapter.chapter_id
}

function selectLesson(lesson: Lesson, chapter: Chapter) {
  selectedLessonId.value = lesson.lesson_id
  selectedChapterId.value = chapter.chapter_id
  if (!expandedChapters.value.has(chapter.chapter_id)) {
    expandedChapters.value.add(chapter.chapter_id)
  }
}

function createNewChapter() {
  // Open chat with prompt
  chatExpanded.value = true
  // TODO: Send message to chat
}


function onContentUpdate() {
  // Reload lessons after content update
  if (selectedCourseId.value) {
    loadChaptersWithLessons(selectedCourseId.value)
  }
}


// Lifecycle
onMounted(() => {
  loadCourses()

  // Check if opened with courseId
  const courseId = props.window.payload?.courseId
  if (courseId && typeof courseId === 'string') {
    selectedCourseId.value = courseId
    onCourseChange()
  }
})

// Watch for payload changes
watch(() => props.window.payload?.courseId, (newCourseId) => {
  if (newCourseId && typeof newCourseId === 'string' && newCourseId !== selectedCourseId.value) {
    selectedCourseId.value = newCourseId
    onCourseChange()
  }
})
</script>

<style scoped>
.ai-studio-pro {
  min-height: 600px;
  min-width: 900px;
}
</style>
