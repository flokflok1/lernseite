<!--
  Content Tab - Lesson Content Editor

  Features:
  - Lektions-Inhalt bearbeiten
  - Teaching Steps verwalten
  - KI-Generierung für Content
  - Vorschau des generierten Contents
-->

<template>
  <div class="content-tab p-6">
    <!-- No Lesson Selected -->
    <div v-if="!lesson" class="flex flex-col items-center justify-center h-full text-center py-12">
      <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mb-4">
        <span class="text-4xl">📝</span>
      </div>
      <h3 class="text-xl font-bold text-[var(--color-text-primary)] mb-2">Content-Editor</h3>
      <p class="text-[var(--color-text-secondary)] max-w-md mb-6">
        Wähle links eine Lektion aus, um den Inhalt zu bearbeiten oder mit KI zu generieren.
      </p>
    </div>

    <!-- Lesson Selected -->
    <div v-else class="space-y-6">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div>
          <h2 class="text-xl font-bold text-[var(--color-text-primary)]">{{ lesson.title }}</h2>
          <p class="text-sm text-[var(--color-text-secondary)] mt-1">
            {{ chapter?.title }} • {{ lesson.lm_type || 'LM00' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="generateContent"
            :disabled="isGenerating"
            class="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all disabled:opacity-50 flex items-center gap-2"
          >
            <span v-if="isGenerating" class="animate-spin">⏳</span>
            <span v-else>✨</span>
            {{ isGenerating ? 'Generiert...' : 'Mit KI generieren' }}
          </button>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-2 gap-6">
        <!-- Left: Content Editor -->
        <div class="space-y-4">
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide">
            Lektions-Inhalt
          </h3>

          <!-- Content Type Selection -->
          <div class="flex gap-2 mb-4">
            <button
              v-for="type in contentTypes"
              :key="type.id"
              @click="selectedContentType = type.id"
              class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all"
              :class="selectedContentType === type.id
                ? 'bg-[var(--color-primary)] text-white'
                : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)]'"
            >
              {{ type.emoji }} {{ type.name }}
            </button>
          </div>

          <!-- Rich Text Editor -->
          <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] overflow-hidden">
            <!-- Toolbar -->
            <div class="flex items-center gap-1 p-2 border-b border-[var(--color-border)] bg-[var(--color-surface-secondary)]">
              <button class="p-1.5 rounded hover:bg-[var(--color-surface)] text-[var(--color-text-secondary)]" title="Fett">
                <span class="font-bold">B</span>
              </button>
              <button class="p-1.5 rounded hover:bg-[var(--color-surface)] text-[var(--color-text-secondary)]" title="Kursiv">
                <span class="italic">I</span>
              </button>
              <button class="p-1.5 rounded hover:bg-[var(--color-surface)] text-[var(--color-text-secondary)]" title="Unterstrichen">
                <span class="underline">U</span>
              </button>
              <div class="w-px h-4 bg-[var(--color-border)] mx-1"></div>
              <button class="p-1.5 rounded hover:bg-[var(--color-surface)] text-[var(--color-text-secondary)]" title="Liste">
                📋
              </button>
              <button class="p-1.5 rounded hover:bg-[var(--color-surface)] text-[var(--color-text-secondary)]" title="Nummerierte Liste">
                🔢
              </button>
              <div class="w-px h-4 bg-[var(--color-border)] mx-1"></div>
              <button class="p-1.5 rounded hover:bg-[var(--color-surface)] text-[var(--color-text-secondary)]" title="Formel">
                ƒx
              </button>
              <button class="p-1.5 rounded hover:bg-[var(--color-surface)] text-[var(--color-text-secondary)]" title="Code">
                &lt;/&gt;
              </button>
              <button class="p-1.5 rounded hover:bg-[var(--color-surface)] text-[var(--color-text-secondary)]" title="Bild einfügen">
                🖼️
              </button>
            </div>

            <!-- Editor Area -->
            <textarea
              v-model="contentText"
              class="w-full h-64 p-4 bg-transparent text-[var(--color-text-primary)] resize-none focus:outline-none"
              placeholder="Lektions-Inhalt hier eingeben oder mit KI generieren..."
            ></textarea>
          </div>

          <!-- Word Count -->
          <div class="flex justify-between text-xs text-[var(--color-text-tertiary)]">
            <span>{{ wordCount }} Wörter</span>
            <span>{{ characterCount }} Zeichen</span>
          </div>
        </div>

        <!-- Right: Teaching Steps -->
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide">
              Teaching Steps
            </h3>
            <button
              @click="addTeachingStep"
              class="text-sm text-[var(--color-primary)] hover:underline"
            >
              + Schritt hinzufügen
            </button>
          </div>

          <!-- Teaching Steps List -->
          <div class="space-y-3 max-h-96 overflow-y-auto">
            <div
              v-for="(step, index) in teachingSteps"
              :key="index"
              class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4"
            >
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 rounded-full bg-[var(--color-primary-subtle)] text-[var(--color-primary)] flex items-center justify-center text-sm font-bold flex-shrink-0">
                  {{ index + 1 }}
                </div>
                <div class="flex-1 space-y-2">
                  <input
                    v-model="step.title"
                    type="text"
                    class="w-full bg-transparent text-[var(--color-text-primary)] font-medium focus:outline-none"
                    placeholder="Schritt-Titel..."
                  />
                  <textarea
                    v-model="step.speech"
                    class="w-full bg-[var(--color-surface-secondary)] rounded-lg p-2 text-sm text-[var(--color-text-secondary)] resize-none focus:outline-none"
                    rows="2"
                    placeholder="Was der Tutor sagt..."
                  ></textarea>
                  <div class="flex items-center gap-2 text-xs">
                    <select
                      v-model="step.animation"
                      class="bg-[var(--color-surface-secondary)] rounded px-2 py-1 text-[var(--color-text-secondary)]"
                    >
                      <option value="idle">Idle</option>
                      <option value="talking">Spricht</option>
                      <option value="pointing">Zeigt</option>
                      <option value="gesture">Geste</option>
                      <option value="thinking">Denkt</option>
                    </select>
                    <input
                      v-model="step.duration"
                      type="text"
                      class="w-20 bg-[var(--color-surface-secondary)] rounded px-2 py-1 text-[var(--color-text-secondary)]"
                      placeholder="Dauer"
                    />
                  </div>
                </div>
                <button
                  @click="removeTeachingStep(index)"
                  class="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                >
                  🗑️
                </button>
              </div>
            </div>

            <!-- Empty State -->
            <div v-if="teachingSteps.length === 0" class="text-center py-8 text-[var(--color-text-tertiary)]">
              <p>Keine Teaching Steps vorhanden.</p>
              <button
                @click="generateTeachingSteps"
                class="mt-2 text-[var(--color-primary)] hover:underline text-sm"
              >
                ✨ Steps mit KI generieren
              </button>
            </div>
          </div>

          <!-- Generate Steps Button -->
          <button
            v-if="teachingSteps.length > 0"
            @click="generateTeachingSteps"
            class="w-full p-3 bg-[var(--color-surface)] border border-dashed border-[var(--color-border)] rounded-xl text-sm text-[var(--color-text-secondary)] hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] transition-colors"
          >
            ✨ Teaching Steps mit KI neu generieren
          </button>
        </div>
      </div>

      <!-- Bottom Actions -->
      <div class="flex justify-between items-center pt-4 border-t border-[var(--color-border)]">
        <div class="text-sm text-[var(--color-text-tertiary)]">
          <span v-if="lastSaved">Zuletzt gespeichert: {{ lastSaved }}</span>
          <span v-else>Nicht gespeichert</span>
        </div>
        <div class="flex gap-2">
          <button
            @click="resetContent"
            class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-secondary)] rounded-lg hover:bg-[var(--color-surface-secondary)] transition-colors"
          >
            Zurücksetzen
          </button>
          <button
            @click="saveContent"
            :disabled="isSaving"
            class="px-6 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors disabled:opacity-50"
          >
            {{ isSaving ? 'Speichert...' : 'Speichern' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Lesson {
  lesson_id: string
  title: string
  lm_type?: string
  content?: Record<string, unknown>
}

interface Chapter {
  chapter_id: string
  title: string
}

interface Course {
  course_id: string
  title: string
}

interface TeachingStep {
  title: string
  speech: string
  animation: string
  duration: string
  whiteboard?: unknown[]
}

interface Props {
  lesson?: Lesson | null
  chapter?: Chapter | null
  course?: Course | null
}

const props = withDefaults(defineProps<Props>(), {
  lesson: null,
  chapter: null,
  course: null
})
const emit = defineEmits<{
  (e: 'save', data: { content: string; teachingSteps: TeachingStep[] }): void
}>()

// State
const contentText = ref('')
const selectedContentType = ref('theory')
const teachingSteps = ref<TeachingStep[]>([])
const isGenerating = ref(false)
const isSaving = ref(false)
const lastSaved = ref<string | null>(null)

// Content Types
const contentTypes = [
  { id: 'theory', name: 'Theorie', emoji: '📚' },
  { id: 'example', name: 'Beispiel', emoji: '💡' },
  { id: 'exercise', name: 'Übung', emoji: '✏️' },
  { id: 'summary', name: 'Zusammenfassung', emoji: '📋' }
]

// Computed
const wordCount = computed(() => {
  return contentText.value.trim().split(/\s+/).filter(w => w).length
})

const characterCount = computed(() => {
  return contentText.value.length
})

// Methods
function addTeachingStep() {
  teachingSteps.value.push({
    title: `Schritt ${teachingSteps.value.length + 1}`,
    speech: '',
    animation: 'talking',
    duration: '0:30'
  })
}

function removeTeachingStep(index: number) {
  teachingSteps.value.splice(index, 1)
}

async function generateContent() {
  if (!props.lesson) return

  isGenerating.value = true

  try {
    // TODO: API call to generate content
    await new Promise(resolve => setTimeout(resolve, 2000))

    contentText.value = `# ${props.lesson.title}\n\n## Einführung\n\nHier kommt der generierte Inhalt für die Lektion...\n\n## Hauptteil\n\n...\n\n## Zusammenfassung\n\n...`
  } catch (error) {
    console.error('Content generation failed:', error)
  } finally {
    isGenerating.value = false
  }
}

async function generateTeachingSteps() {
  isGenerating.value = true

  try {
    // TODO: API call to generate teaching steps
    await new Promise(resolve => setTimeout(resolve, 1500))

    teachingSteps.value = [
      { title: 'Einführung', speech: 'Willkommen zu dieser Lektion...', animation: 'talking', duration: '0:30' },
      { title: 'Hauptkonzept', speech: 'Das wichtigste Konzept ist...', animation: 'pointing', duration: '1:00' },
      { title: 'Beispiel', speech: 'Schauen wir uns ein Beispiel an...', animation: 'gesture', duration: '1:30' },
      { title: 'Zusammenfassung', speech: 'Fassen wir zusammen...', animation: 'talking', duration: '0:30' }
    ]
  } catch (error) {
    console.error('Teaching steps generation failed:', error)
  } finally {
    isGenerating.value = false
  }
}

async function saveContent() {
  isSaving.value = true

  try {
    // TODO: API call to save content
    await new Promise(resolve => setTimeout(resolve, 500))

    emit('save', {
      content: contentText.value,
      teachingSteps: teachingSteps.value
    })

    lastSaved.value = new Date().toLocaleTimeString('de-DE')
  } catch (error) {
    console.error('Save failed:', error)
  } finally {
    isSaving.value = false
  }
}

function resetContent() {
  if (confirm('Änderungen verwerfen?')) {
    contentText.value = ''
    teachingSteps.value = []
    lastSaved.value = null
  }
}

// Watch for lesson changes
watch(() => props.lesson, (newLesson) => {
  if (newLesson) {
    // Load lesson content
    contentText.value = ''
    teachingSteps.value = []
    lastSaved.value = null
  }
}, { immediate: true })
</script>

<style scoped>
.content-tab {
  min-height: 400px;
}
</style>
