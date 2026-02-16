<!--
  Admin Prompt Browser Window
  Phase C2.3: Prompt-System im Frontend

  Features:
  - Liste aller verfügbaren Prompts (System + Kurs-spezifisch)
  - Filter nach Scope/Kategorie
  - Vorschau der Prompt-Templates
  - Auswahl für AI-Flows
  - Kurs-spezifische Prompt-Override-Anzeige
-->

<template>
  <div class="admin-prompt-browser-window flex flex-col h-full">
    <!-- Header -->
    <div class="p-4 border-b border-[var(--color-border)]">
      <div class="flex items-center justify-between mb-3">
        <div>
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">KI-Prompt Browser</h3>
          <p class="text-sm text-[var(--color-text-secondary)]">
            {{ courseTitle ? `Prompts für: ${courseTitle}` : 'System-Prompts' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <span class="px-3 py-1 rounded-full text-xs font-medium bg-[var(--color-primary)]/10 text-[var(--color-primary)]">
            {{ filteredPrompts.length }} Prompts
          </span>
        </div>
      </div>

      <!-- Filter Tabs -->
      <div class="flex gap-2 flex-wrap">
        <button
          v-for="scope in availableScopes"
          :key="scope.value"
          @click="selectedScope = scope.value"
          :class="[
            'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
            selectedScope === scope.value
              ? 'bg-[var(--color-primary)] text-white'
              : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-background)] border border-[var(--color-border)]'
          ]"
        >
          {{ scope.icon }} {{ scope.label }}
        </button>
      </div>
    </div>

    <!-- Prompt List -->
    <div class="flex-1 overflow-y-auto p-4">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="animate-pulse text-4xl mb-3">🤖</div>
          <p class="text-[var(--color-text-secondary)]">Lade Prompts...</p>
        </div>
      </div>

      <div v-else-if="filteredPrompts.length === 0" class="text-center py-12">
        <div class="text-4xl mb-3 opacity-30">📝</div>
        <p class="text-[var(--color-text-secondary)]">Keine Prompts gefunden</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="prompt in filteredPrompts"
          :key="prompt.id"
          @click="selectPrompt(prompt)"
          :class="[
            'prompt-card p-4 rounded-lg border transition-all cursor-pointer',
            selectedPrompt?.id === prompt.id
              ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/5'
              : 'border-[var(--color-border)] hover:border-[var(--color-primary)]/50 hover:bg-[var(--color-surface)]'
          ]"
        >
          <!-- Prompt Header -->
          <div class="flex items-start justify-between mb-2">
            <div class="flex items-center gap-2">
              <span class="text-xl">{{ getScopeIcon(prompt.scope) }}</span>
              <h4 class="font-medium text-[var(--color-text-primary)]">{{ prompt.name }}</h4>
            </div>
            <div class="flex items-center gap-2">
              <span v-if="prompt.is_override" class="px-2 py-0.5 rounded text-xs bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]">
                Override
              </span>
              <span class="px-2 py-0.5 rounded text-xs bg-[var(--color-surface)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">
                v{{ prompt.version || 1 }}
              </span>
            </div>
          </div>

          <!-- Description -->
          <p class="text-sm text-[var(--color-text-secondary)] mb-3 line-clamp-2">
            {{ prompt.description }}
          </p>

          <!-- Tags -->
          <div class="flex flex-wrap gap-1">
            <span
              v-for="tag in (prompt.tags || []).slice(0, 4)"
              :key="tag"
              class="px-2 py-0.5 rounded text-xs bg-[var(--color-info-bg,#eff6ff)] text-[var(--color-info-text,#1e40af)]"
            >
              {{ tag }}
            </span>
            <span v-if="(prompt.tags || []).length > 4" class="text-xs text-[var(--color-text-secondary)]">
              +{{ prompt.tags.length - 4 }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Selected Prompt Preview -->
    <div v-if="selectedPrompt" class="border-t border-[var(--color-border)] p-4 bg-[var(--color-surface)]">
      <div class="flex items-center justify-between mb-3">
        <h4 class="font-semibold text-[var(--color-text-primary)]">Prompt-Vorschau</h4>
        <button
          @click="copyPrompt"
          class="px-3 py-1 text-sm bg-[var(--color-background)] border border-[var(--color-border)] rounded hover:bg-[var(--color-surface)] transition-colors"
        >
          {{ copied ? '✓ Kopiert' : '📋 Kopieren' }}
        </button>
      </div>

      <!-- Template Preview -->
      <div class="bg-[var(--color-background)] rounded-lg p-3 font-mono text-sm text-[var(--color-text-secondary)] max-h-32 overflow-y-auto border border-[var(--color-border)]">
        <pre class="whitespace-pre-wrap">{{ selectedPrompt.template || selectedPrompt.messages?.[0]?.content || 'Kein Template verfügbar' }}</pre>
      </div>

      <!-- Variables -->
      <div v-if="selectedPrompt.variables?.length" class="mt-3">
        <p class="text-xs font-medium text-[var(--color-text-secondary)] mb-1">Variablen:</p>
        <div class="flex flex-wrap gap-1">
          <span
            v-for="variable in selectedPrompt.variables"
            :key="variable.name"
            class="px-2 py-0.5 rounded text-xs font-mono"
            :class="variable.required
              ? 'bg-[var(--color-error,#dc2626)]/10 text-[var(--color-error,#dc2626)]'
              : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)]'"
          >
            {{ `{${'{'}${variable.name}${'}'}` + '}' }}
            <span v-if="variable.required" class="ml-1">*</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Footer Actions -->
    <div class="px-4 py-3 bg-[var(--color-background)] border-t border-[var(--color-border)] flex justify-between items-center">
      <button
        type="button"
        @click="$emit('close')"
        class="px-4 py-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
      >
        Schließen
      </button>

      <div class="flex gap-2">
        <button
          v-if="selectedPrompt && courseId"
          @click="overridePrompt"
          class="px-4 py-2 bg-[var(--color-surface)] text-[var(--color-text-primary)] rounded-lg border border-[var(--color-border)] hover:bg-[var(--color-background)] transition-colors"
        >
          Für Kurs anpassen
        </button>
        <button
          v-if="selectedPrompt && selectionMode"
          @click="confirmSelection"
          class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors"
        >
          Prompt auswählen
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'

// Types
interface PromptVariable {
  name: string
  required: boolean
  default?: string
  description?: string
}

interface PromptMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

interface Prompt {
  id: string
  name: string
  description: string
  scope: string
  template?: string
  messages?: PromptMessage[]
  variables?: PromptVariable[]
  tags?: string[]
  version?: number
  is_override?: boolean
}

interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
  (e: 'select', prompt: Prompt): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Extract payload data
const courseId = computed(() => props.window.payload?.courseId as string | undefined)
const courseTitle = computed(() => props.window.payload?.courseTitle as string | undefined)
const selectionMode = computed(() => props.window.payload?.mode === 'select')

// State
const loading = ref(true)
const prompts = ref<Prompt[]>([])
const selectedScope = ref('all')
const selectedPrompt = ref<Prompt | null>(null)
const copied = ref(false)

// Available scopes for filtering
const availableScopes = [
  { value: 'all', label: 'Alle', icon: '📋' },
  { value: 'course_generation', label: 'Kurs-Generierung', icon: '📚' },
  { value: 'module_generation', label: 'Modul-Generierung', icon: '📖' },
  { value: 'lesson_generation', label: 'Lektion-Generierung', icon: '📄' },
  { value: 'quiz_generation', label: 'Quiz-Generierung', icon: '❓' },
  { value: 'exam_generation', label: 'Prüfungs-Generierung', icon: '📝' }
]

// Computed
const filteredPrompts = computed(() => {
  if (selectedScope.value === 'all') {
    return prompts.value
  }
  return prompts.value.filter(p => p.scope === selectedScope.value)
})

// Methods
const getScopeIcon = (scope: string): string => {
  const found = availableScopes.find(s => s.value === scope)
  return found?.icon || '📋'
}

const selectPrompt = (prompt: Prompt): void => {
  selectedPrompt.value = prompt
}

const copyPrompt = async (): Promise<void> => {
  if (!selectedPrompt.value) return

  const content = selectedPrompt.value.template ||
    selectedPrompt.value.messages?.map(m => `[${m.role}]\n${m.content}`).join('\n\n') ||
    ''

  try {
    await navigator.clipboard.writeText(content)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const overridePrompt = (): void => {
  // TODO: Open prompt editor for course-specific override
  alert(
    `Prompt-Override für Kurs\n\n` +
    `Diese Funktion ermöglicht es, den Prompt "${selectedPrompt.value?.name}" ` +
    `speziell für diesen Kurs anzupassen.\n\n` +
    `Vollständige Implementierung folgt in der nächsten Iteration.`
  )
}

const confirmSelection = (): void => {
  if (selectedPrompt.value) {
    // Emit through Vue emit for direct listeners
    emit('select', selectedPrompt.value)

    // Also dispatch a global event for cross-window communication
    const callbackId = props.window.payload?.callbackId as string | undefined
    if (callbackId) {
      window.dispatchEvent(new CustomEvent('prompt-selected', {
        detail: {
          callbackId,
          prompt: selectedPrompt.value
        }
      }))
    }

    emit('close')
  }
}

const loadPrompts = async (): Promise<void> => {
  loading.value = true

  try {
    // System prompts (hardcoded for now, will be API in future)
    const systemPrompts: Prompt[] = [
      {
        id: 'explain_concept',
        name: 'Konzept Erklärung',
        description: 'Erklärt ein Konzept schrittweise mit verständlichen Beispielen. Passt sich an das Wissenslevel des Lernenden an.',
        scope: 'lesson_generation',
        template: 'Du bist ein erfahrener Lehrer. Erkläre das folgende Konzept: {{concept}}\n\nZielgruppe: {{target_audience}}\nSprache: {{language}}',
        variables: [
          { name: 'concept', required: true, description: 'Das zu erklärende Konzept' },
          { name: 'target_audience', required: false, default: 'Anfänger' },
          { name: 'language', required: false, default: 'Deutsch' }
        ],
        tags: ['learning', 'explanation', 'concept'],
        version: 1
      },
      {
        id: 'flashcards',
        name: 'Karteikarten Generator',
        description: 'Generiert Frage-Antwort-Paare (Flashcards) aus Lektionsinhalten.',
        scope: 'quiz_generation',
        template: 'Erstelle {{count}} Karteikarten basierend auf folgendem Inhalt:\n\n{{content}}\n\nFormat: JSON Array mit {question, answer}',
        variables: [
          { name: 'content', required: true },
          { name: 'count', required: false, default: '10' }
        ],
        tags: ['learning', 'flashcards', 'memorization'],
        version: 1
      },
      {
        id: 'quiz_generator',
        name: 'Quiz Generator',
        description: 'Erstellt Multiple-Choice-Quizfragen mit Distraktoren aus Lektionsinhalten.',
        scope: 'quiz_generation',
        template: 'Erstelle {{count}} Multiple-Choice-Fragen basierend auf:\n\n{{content}}\n\nJede Frage hat 4 Optionen, eine richtige Antwort.',
        variables: [
          { name: 'content', required: true },
          { name: 'count', required: false, default: '5' }
        ],
        tags: ['quiz', 'multiple-choice', 'assessment'],
        version: 1
      },
      {
        id: 'course_structure',
        name: 'Kursstruktur Generator',
        description: 'Generiert eine vollständige Kursstruktur aus PDF-Inhalten oder einem Thema.',
        scope: 'course_generation',
        template: 'Analysiere den folgenden Inhalt und erstelle eine Kursstruktur:\n\nTitel: {{title}}\nInhalt: {{content}}\n\nErstelle Module mit Lektionen.',
        variables: [
          { name: 'title', required: true },
          { name: 'content', required: true }
        ],
        tags: ['course', 'structure', 'generation'],
        version: 1
      },
      {
        id: 'exam_generator',
        name: 'Prüfungs-Generator',
        description: 'Erstellt eine vollständige Prüfung basierend auf Kursinhalten.',
        scope: 'exam_generation',
        template: 'Erstelle eine Prüfung für den Kurs "{{course_title}}".\n\nModule: {{modules}}\n\nAnzahl Fragen: {{question_count}}\nSchwierigkeit: {{difficulty}}',
        variables: [
          { name: 'course_title', required: true },
          { name: 'modules', required: true },
          { name: 'question_count', required: false, default: '20' },
          { name: 'difficulty', required: false, default: 'mixed' }
        ],
        tags: ['exam', 'assessment', 'generation'],
        version: 1
      },
      {
        id: 'socratic_tutor',
        name: 'Sokratischer Tutor',
        description: 'Führt sokratischen Dialog mit gezielten Gegenfragen.',
        scope: 'lesson_generation',
        template: 'Du bist ein sokratischer Tutor. Das Thema ist: {{topic}}\n\nFühre den Lernenden durch Fragen zur Erkenntnis.',
        variables: [
          { name: 'topic', required: true }
        ],
        tags: ['dialogue', 'socratic', 'premium'],
        version: 1
      }
    ]

    prompts.value = systemPrompts

    // TODO: Load course-specific prompts if courseId is set
    // const coursePrompts = await adminApi.getCoursePrompts(courseId.value)
    // prompts.value = [...systemPrompts, ...coursePrompts.map(p => ({ ...p, is_override: true }))]

  } catch (err) {
    console.error('Failed to load prompts:', err)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadPrompts()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.prompt-card:hover {
  transform: translateY(-1px);
}

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
