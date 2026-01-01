<!--
  LernmethodenTab.vue

  KI-Studio Pro Lernmethoden Tab
  Verwaltet die 19 Content-Lernmethoden (LM00-LM25 mit Lücken) für den Kurs.

  Features:
  - Übersicht aller verfügbaren Lernmethoden
  - Gruppiert nach Kategorie (A-C)
  - Generierung von Lernmethoden-Inhalten
  - Methoden-Statistiken pro Kurs

  Content-Lernmethoden (19 aktiv):
  - A: Erklärend (LM00, LM01, LM02, LM03, LM06)
  - B: Praxis (LM08, LM12, LM13, LM14, LM15, LM17)
  - C: Prüfung (LM18, LM19, LM20, LM21, LM22, LM23, LM24, LM25)

  System-Features (separat, siehe 02a_System-Features.md):
  - TutorAgent, Mindmap, IT-Sandbox, Kollaboration, etc.

  Phase: KI-Studio Pro - Lernmethoden Tab
-->

<template>
  <div class="lernmethoden-tab p-6">
    <!-- Kein Kurs gewählt -->
    <div v-if="!course" class="empty-state">
      <div class="icon">🧩</div>
      <h3>Kein Kurs ausgewählt</h3>
      <p>Wähle einen Kurs aus, um Lernmethoden zu verwalten.</p>
    </div>

    <!-- Lernmethoden Content -->
    <template v-else>
      <!-- Header -->
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-[var(--color-text-primary)]">
            🧩 Lernmethoden: {{ course.title }}
          </h2>
          <p class="text-sm text-[var(--color-text-secondary)] mt-1">
            {{ methodStats.total }} Lernmethoden-Instanzen in {{ methodStats.lessons }} Lektionen
          </p>
        </div>

        <!-- View Toggle -->
        <div class="flex items-center gap-2">
          <button
            @click="viewMode = 'grid'"
            class="view-btn"
            :class="{ active: viewMode === 'grid' }"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </button>
          <button
            @click="viewMode = 'list'"
            class="view-btn"
            :class="{ active: viewMode === 'list' }"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Lade Lernmethoden...</p>
      </div>

      <!-- Method Groups -->
      <div v-else class="method-groups">
        <div v-for="group in methodGroups" :key="group.code" class="method-group">
          <!-- Group Header -->
          <div class="group-header" @click="toggleGroup(group.code)">
            <div class="group-info">
              <span class="group-icon">{{ group.icon }}</span>
              <span class="group-name">{{ group.name }}</span>
              <span class="group-code">Gruppe {{ group.code }}</span>
            </div>
            <div class="group-stats">
              <span class="group-count">{{ getGroupMethodCount(group.code) }} verwendet</span>
              <svg
                class="expand-icon"
                :class="{ expanded: expandedGroups.has(group.code) }"
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          <!-- Group Methods -->
          <div v-if="expandedGroups.has(group.code)" class="group-content">
            <div :class="viewMode === 'grid' ? 'method-grid' : 'method-list'">
              <div
                v-for="method in group.methods"
                :key="method.method_number"
                class="method-card"
                :class="{ 'has-instances': getMethodInstanceCount(method.method_number) > 0 }"
              >
                <div class="method-header">
                  <span class="method-badge">LM{{ String(method.method_number).padStart(2, '0') }}</span>
                  <span v-if="method.tier === 'premium'" class="premium-badge">Pro</span>
                </div>
                <h4 class="method-name">{{ method.name }}</h4>
                <p class="method-desc">{{ method.description }}</p>
                <div class="method-footer">
                  <span class="method-ki">
                    <span class="ki-dot" :class="method.ki_usage"></span>
                    {{ formatKiUsage(method.ki_usage) }}
                  </span>
                  <span class="method-count">
                    {{ getMethodInstanceCount(method.method_number) }} Instanzen
                  </span>
                </div>
                <button
                  @click="openMethodGenerator(method)"
                  class="generate-btn"
                  :disabled="!selectedLesson"
                >
                  + Generieren
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Selected Context Info -->
      <div v-if="selectedChapter || selectedLesson" class="context-info">
        <span class="context-label">Aktiver Kontext:</span>
        <span v-if="selectedLesson" class="context-value">
          {{ selectedChapter?.title }} → {{ selectedLesson.title }}
        </span>
        <span v-else-if="selectedChapter" class="context-value">
          {{ selectedChapter.title }}
        </span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import http from '@/api/http'

interface Course {
  course_id: string
  title: string
}

interface Chapter {
  chapter_id: string
  title: string
  lessons?: Lesson[]
}

interface Lesson {
  lesson_id: string
  title: string
}

interface LearningMethod {
  method_number: number
  name: string
  description: string
  tier: string
  active: boolean
  icon: string
  group_code: string
  ki_usage: string
}

interface MethodGroup {
  code: string
  name: string
  icon: string
  methods: LearningMethod[]
}

const props = defineProps<{
  course?: Course | null
  chapter?: Chapter | null
  lesson?: Lesson | null
  chapters?: Chapter[]
}>()

const loading = ref(false)
const viewMode = ref<'grid' | 'list'>('grid')
const methods = ref<LearningMethod[]>([])
const methodInstances = ref<Record<number, number>>({})
const expandedGroups = ref<Set<string>>(new Set(['A', 'B', 'C']))

// Group definitions
const groupDefinitions = [
  { code: 'A', name: 'Erklärend', icon: '📖' },
  { code: 'B', name: 'Praxis', icon: '🎯' },
  { code: 'C', name: 'Prüfung', icon: '📝' },
  { code: 'D', name: 'Pro', icon: '⭐' },
  { code: 'E', name: 'IT', icon: '💻' },
  { code: 'F', name: 'Kollaborativ', icon: '👥' }
]

// Computed
const selectedChapter = computed(() => props.chapter)
const selectedLesson = computed(() => props.lesson)

const methodStats = computed(() => {
  const total = Object.values(methodInstances.value).reduce((sum, count) => sum + count, 0)
  const lessons = new Set(
    Object.keys(methodInstances.value).filter(k => methodInstances.value[parseInt(k)] > 0)
  ).size
  return { total, lessons }
})

const methodGroups = computed<MethodGroup[]>(() => {
  return groupDefinitions.map(group => ({
    ...group,
    methods: methods.value.filter(m => m.group_code === group.code && m.active)
  })).filter(g => g.methods.length > 0)
})

// Methods
async function loadMethods() {
  loading.value = true
  try {
    const response = await http.get('/admin/learning-methods')
    methods.value = response.data.data?.methods || response.data.methods || []
  } catch (error) {
    console.error('Failed to load methods:', error)
  } finally {
    loading.value = false
  }
}

async function loadMethodInstances() {
  if (!props.course?.course_id) return

  try {
    const response = await http.get(`/admin/course-analytics/${props.course.course_id}/content`)
    const distribution = response.data.data?.method_distribution || []
    methodInstances.value = distribution.reduce((acc: Record<number, number>, item: any) => {
      acc[item.method_type] = item.count
      return acc
    }, {})
  } catch (error) {
    console.error('Failed to load method instances:', error)
  }
}

function getMethodInstanceCount(methodNumber: number): number {
  return methodInstances.value[methodNumber] || 0
}

function getGroupMethodCount(groupCode: string): number {
  const groupMethods = methods.value.filter(m => m.group_code === groupCode && m.active)
  return groupMethods.reduce((sum, m) => sum + getMethodInstanceCount(m.method_number), 0)
}

function toggleGroup(code: string) {
  if (expandedGroups.value.has(code)) {
    expandedGroups.value.delete(code)
  } else {
    expandedGroups.value.add(code)
  }
}

function formatKiUsage(usage: string): string {
  const labels: Record<string, string> = {
    'none': 'Keine KI',
    'optional': 'Optional',
    'low': 'Wenig',
    'medium': 'Mittel',
    'high': 'Intensiv',
    'intensive': 'Intensiv'
  }
  return labels[usage] || usage
}

function openMethodGenerator(method: LearningMethod) {
  // TODO: Open method generator modal/panel
  console.log('Generate method:', method, 'for lesson:', props.lesson)
}

// Watch for course changes
watch(() => props.course?.course_id, (newId) => {
  if (newId) {
    loadMethodInstances()
  } else {
    methodInstances.value = {}
  }
}, { immediate: true })

onMounted(() => {
  loadMethods()
  if (props.course?.course_id) {
    loadMethodInstances()
  }
})
</script>

<style scoped>
.lernmethoden-tab {
  max-width: 1400px;
  margin: 0 auto;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-state .icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: var(--color-text-secondary);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* View Toggle */
.view-btn {
  padding: 0.5rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.view-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.view-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

/* Method Groups */
.method-groups {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.method-group {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: var(--color-surface-secondary);
  cursor: pointer;
  transition: background 0.15s;
}

.group-header:hover {
  background: var(--color-surface);
}

.group-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.group-icon {
  font-size: 1.25rem;
}

.group-name {
  font-weight: 600;
  color: var(--color-text-primary);
}

.group-code {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  padding: 0.125rem 0.5rem;
  background: var(--color-surface);
  border-radius: 0.25rem;
}

.group-stats {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.group-count {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.expand-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-text-tertiary);
  transition: transform 0.2s;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.group-content {
  padding: 1rem;
  border-top: 1px solid var(--color-border);
}

/* Method Grid */
.method-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.method-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.method-list .method-card {
  flex-direction: row;
  align-items: center;
}

/* Method Card */
.method-card {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  background: var(--color-surface-secondary);
  border: 1px solid transparent;
  border-radius: 0.5rem;
  transition: all 0.15s;
}

.method-card:hover {
  border-color: var(--color-border);
}

.method-card.has-instances {
  border-left: 3px solid var(--color-primary);
}

.method-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.method-badge {
  padding: 0.125rem 0.375rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 600;
  font-family: ui-monospace, monospace;
}

.premium-badge {
  padding: 0.125rem 0.375rem;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 600;
}

.method-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.25rem;
}

.method-desc {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  line-height: 1.4;
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.method-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin-bottom: 0.75rem;
}

.method-ki {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.ki-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}

.ki-dot.none { background: #9ca3af; }
.ki-dot.optional { background: #60a5fa; }
.ki-dot.low { background: #34d399; }
.ki-dot.medium { background: #fbbf24; }
.ki-dot.high, .ki-dot.intensive { background: #f87171; }

.generate-btn {
  width: 100%;
  padding: 0.5rem;
  background: var(--color-primary);
  color: white;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s;
}

.generate-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Context Info */
.context-info {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  font-size: 0.8125rem;
}

.context-label {
  color: var(--color-text-secondary);
}

.context-value {
  font-weight: 500;
  color: var(--color-text-primary);
}
</style>
