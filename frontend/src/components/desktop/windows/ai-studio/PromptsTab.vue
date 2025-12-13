<!--
  Prompts Tab - System Prompts Management

  Features:
  - System-Prompts pro Lernmethode (LM00-LM32)
  - Prompt-Vorlagen erstellen und verwalten
  - Variablen-System für dynamische Prompts
  - Prompt-Testing mit Vorschau
  - Import/Export von Prompts
-->

<template>
  <div class="prompts-tab p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-[var(--color-text-primary)]">Prompt-Editor</h2>
        <p class="text-sm text-[var(--color-text-secondary)] mt-1">
          System-Prompts für KI-Generierung verwalten
        </p>
      </div>
      <div class="flex gap-2">
        <button
          @click="showImportModal = true"
          class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-surface-secondary)] transition-colors flex items-center gap-2"
        >
          <span>📥</span> Import
        </button>
        <button
          @click="exportPrompts"
          class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-surface-secondary)] transition-colors flex items-center gap-2"
        >
          <span>📤</span> Export
        </button>
        <button
          @click="createNewPrompt"
          class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors flex items-center gap-2"
        >
          <span>+</span> Neuer Prompt
        </button>
      </div>
    </div>

    <div class="grid grid-cols-3 gap-6">
      <!-- Left: Prompt Categories -->
      <div class="col-span-1 space-y-4">
        <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide">
          Kategorien
        </h3>

        <!-- Category List -->
        <div class="space-y-1">
          <button
            v-for="category in promptCategories"
            :key="category.id"
            @click="selectCategory(category.id)"
            class="w-full p-3 rounded-xl text-left transition-all"
            :class="selectedCategory === category.id
              ? 'bg-[var(--color-primary-subtle)] border-2 border-[var(--color-primary)]'
              : 'bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-primary)]'"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="text-xl">{{ category.emoji }}</span>
                <div>
                  <div class="text-sm font-medium text-[var(--color-text-primary)]">{{ category.name }}</div>
                  <div class="text-xs text-[var(--color-text-tertiary)]">{{ category.count }} Prompts</div>
                </div>
              </div>
              <span class="text-[var(--color-text-tertiary)]">›</span>
            </div>
          </button>
        </div>

        <!-- Learning Methods Quick Access -->
        <div class="mt-6">
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide mb-3">
            Lernmethoden
          </h3>
          <div class="space-y-1 max-h-64 overflow-y-auto">
            <button
              v-for="lm in learningMethods"
              :key="lm.id"
              @click="selectLearningMethod(lm.id)"
              class="w-full p-2 rounded-lg text-left text-sm transition-all"
              :class="selectedLM === lm.id
                ? 'bg-[var(--color-primary-subtle)] text-[var(--color-primary)]'
                : 'hover:bg-[var(--color-surface)] text-[var(--color-text-secondary)]'"
            >
              <span class="font-mono text-xs mr-2">{{ lm.code }}</span>
              {{ lm.name }}
            </button>
          </div>
        </div>
      </div>

      <!-- Middle: Prompt List -->
      <div class="col-span-1 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide">
            Prompts
          </h3>
          <input
            v-model="promptSearch"
            type="text"
            placeholder="Suchen..."
            class="px-3 py-1.5 text-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg"
          />
        </div>

        <!-- Prompt Cards -->
        <div class="space-y-2 max-h-[500px] overflow-y-auto">
          <div
            v-for="prompt in filteredPrompts"
            :key="prompt.id"
            @click="selectPrompt(prompt)"
            class="p-4 rounded-xl cursor-pointer transition-all"
            :class="selectedPrompt?.id === prompt.id
              ? 'bg-[var(--color-primary-subtle)] border-2 border-[var(--color-primary)]'
              : 'bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-primary)]'"
          >
            <div class="flex items-start justify-between mb-2">
              <h4 class="font-medium text-[var(--color-text-primary)]">{{ prompt.name }}</h4>
              <span
                class="px-2 py-0.5 text-xs rounded-full"
                :class="prompt.isActive
                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'"
              >
                {{ prompt.isActive ? 'Aktiv' : 'Inaktiv' }}
              </span>
            </div>
            <p class="text-sm text-[var(--color-text-secondary)] line-clamp-2 mb-2">
              {{ prompt.description }}
            </p>
            <div class="flex items-center gap-2 text-xs text-[var(--color-text-tertiary)]">
              <span>{{ prompt.variables.length }} Variablen</span>
              <span>•</span>
              <span>{{ prompt.tokens }} Tokens</span>
              <span>•</span>
              <span>{{ prompt.lastUpdated }}</span>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="filteredPrompts.length === 0" class="text-center py-8">
            <span class="text-4xl mb-2 block">📝</span>
            <p class="text-[var(--color-text-secondary)]">Keine Prompts gefunden</p>
          </div>
        </div>
      </div>

      <!-- Right: Prompt Editor -->
      <div class="col-span-1 space-y-4">
        <template v-if="selectedPrompt">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide">
              Editor
            </h3>
            <div class="flex gap-2">
              <button
                @click="testPrompt"
                class="px-3 py-1.5 text-sm bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400 rounded-lg hover:bg-violet-200 dark:hover:bg-violet-900/50 transition-colors"
              >
                🧪 Testen
              </button>
              <button
                @click="duplicatePrompt"
                class="px-3 py-1.5 text-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface-secondary)]"
              >
                📋
              </button>
            </div>
          </div>

          <!-- Prompt Name -->
          <div>
            <label class="text-xs text-[var(--color-text-tertiary)] mb-1 block">Name</label>
            <input
              v-model="selectedPrompt.name"
              type="text"
              class="w-full px-3 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
            />
          </div>

          <!-- Description -->
          <div>
            <label class="text-xs text-[var(--color-text-tertiary)] mb-1 block">Beschreibung</label>
            <input
              v-model="selectedPrompt.description"
              type="text"
              class="w-full px-3 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
            />
          </div>

          <!-- Prompt Content -->
          <div class="flex-1">
            <div class="flex items-center justify-between mb-1">
              <label class="text-xs text-[var(--color-text-tertiary)]">Prompt</label>
              <span class="text-xs text-[var(--color-text-tertiary)]">{{ selectedPrompt.content.length }} Zeichen</span>
            </div>
            <textarea
              v-model="selectedPrompt.content"
              class="w-full h-48 px-3 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] font-mono text-sm resize-none"
              placeholder="System Prompt eingeben..."
            ></textarea>
          </div>

          <!-- Variables -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="text-xs text-[var(--color-text-tertiary)]">Variablen</label>
              <button
                @click="addVariable"
                class="text-xs text-[var(--color-primary)] hover:underline"
              >
                + Variable
              </button>
            </div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="variable in selectedPrompt.variables"
                :key="variable"
                class="px-2 py-1 bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 rounded text-xs font-mono cursor-pointer hover:bg-blue-200"
                @click="insertVariable(variable)"
              >
                {{ formatVariable(variable) }}
              </span>
            </div>
            <p class="text-xs text-[var(--color-text-tertiary)] mt-1">
              Klicke auf eine Variable, um sie einzufügen
            </p>
          </div>

          <!-- Target LMs -->
          <div>
            <label class="text-xs text-[var(--color-text-tertiary)] mb-2 block">Gilt für Lernmethoden</label>
            <div class="flex flex-wrap gap-1">
              <button
                v-for="lm in learningMethods.slice(0, 10)"
                :key="lm.id"
                @click="toggleLM(lm.id)"
                class="px-2 py-1 text-xs rounded transition-colors"
                :class="selectedPrompt.targetLMs.includes(lm.id)
                  ? 'bg-[var(--color-primary)] text-white'
                  : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface)]'"
              >
                {{ lm.code }}
              </button>
              <button class="px-2 py-1 text-xs text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)]">
                +{{ learningMethods.length - 10 }} mehr
              </button>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 pt-4 border-t border-[var(--color-border)]">
            <button
              @click="savePrompt"
              class="flex-1 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors"
            >
              Speichern
            </button>
            <button
              @click="deletePrompt"
              class="px-4 py-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
            >
              🗑️
            </button>
          </div>
        </template>

        <!-- No Prompt Selected -->
        <div v-else class="flex flex-col items-center justify-center h-full text-center py-12">
          <span class="text-4xl mb-4">📝</span>
          <h3 class="text-lg font-medium text-[var(--color-text-primary)] mb-2">Prompt auswählen</h3>
          <p class="text-sm text-[var(--color-text-secondary)]">
            Wähle einen Prompt aus der Liste oder erstelle einen neuen.
          </p>
        </div>
      </div>
    </div>

    <!-- Test Modal -->
    <div
      v-if="showTestModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showTestModal = false"
    >
      <div class="bg-[var(--color-surface)] rounded-xl p-6 w-[700px] max-h-[80vh] overflow-y-auto">
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">Prompt testen</h3>

        <!-- Variable Inputs -->
        <div class="space-y-3 mb-4">
          <div v-for="variable in selectedPrompt?.variables" :key="variable">
            <label class="text-sm text-[var(--color-text-secondary)] mb-1 block">{{ variable }}</label>
            <input
              v-model="testVariables[variable]"
              type="text"
              class="w-full px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg"
              :placeholder="`Wert für ${variable}...`"
            />
          </div>
        </div>

        <!-- Rendered Prompt -->
        <div class="mb-4">
          <label class="text-sm text-[var(--color-text-secondary)] mb-1 block">Generierter Prompt</label>
          <div class="bg-gray-900 text-green-400 rounded-lg p-4 font-mono text-sm max-h-48 overflow-y-auto">
            {{ renderedPrompt }}
          </div>
        </div>

        <!-- Test Result -->
        <div v-if="testResult">
          <label class="text-sm text-[var(--color-text-secondary)] mb-1 block">KI-Antwort</label>
          <div class="bg-[var(--color-surface-secondary)] rounded-lg p-4 text-sm max-h-48 overflow-y-auto">
            {{ testResult }}
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-6">
          <button
            @click="showTestModal = false"
            class="px-4 py-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
          >
            Schließen
          </button>
          <button
            @click="runTest"
            :disabled="isTestRunning"
            class="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 disabled:opacity-50"
          >
            {{ isTestRunning ? 'Läuft...' : 'Test ausführen' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Prompt {
  id: string
  name: string
  description: string
  content: string
  category: string
  variables: string[]
  targetLMs: string[]
  tokens: number
  isActive: boolean
  lastUpdated: string
}

// State
const selectedCategory = ref('content')
const selectedLM = ref<string | null>(null)
const selectedPrompt = ref<Prompt | null>(null)
const promptSearch = ref('')
const showImportModal = ref(false)
const showTestModal = ref(false)
const testVariables = ref<Record<string, string>>({})
const testResult = ref<string | null>(null)
const isTestRunning = ref(false)

// Categories
const promptCategories = [
  { id: 'content', name: 'Content-Generierung', emoji: '📝', count: 8 },
  { id: 'video', name: 'Video-Skripte', emoji: '🎬', count: 4 },
  { id: 'quiz', name: 'Quiz & Fragen', emoji: '❓', count: 6 },
  { id: 'feedback', name: 'Feedback', emoji: '💬', count: 3 },
  { id: 'translation', name: 'Übersetzung', emoji: '🌍', count: 2 },
  { id: 'summary', name: 'Zusammenfassung', emoji: '📋', count: 3 }
]

// Learning Methods
const learningMethods = [
  { id: 'LM00', code: 'LM00', name: 'Deep Explanation' },
  { id: 'LM01', code: 'LM01', name: 'Step-by-Step' },
  { id: 'LM02', code: 'LM02', name: 'Interactive Theory' },
  { id: 'LM03', code: 'LM03', name: 'Visualisierung' },
  { id: 'LM04', code: 'LM04', name: 'Glossar' },
  { id: 'LM05', code: 'LM05', name: 'Mindmap' },
  { id: 'LM06', code: 'LM06', name: 'Szenarien' },
  { id: 'LM07', code: 'LM07', name: 'NPC Tutor' },
  { id: 'LM08', code: 'LM08', name: 'Whiteboard' },
  { id: 'LM09', code: 'LM09', name: 'Code Sandbox' },
  { id: 'LM10', code: 'LM10', name: 'Netzwerk Sim' },
  { id: 'LM11', code: 'LM11', name: 'IT Szenario' },
  { id: 'LM12', code: 'LM12', name: 'Math Interactive' }
]

// Sample Prompts
const prompts = ref<Prompt[]>([
  {
    id: '1',
    name: 'Content Generator - Standard',
    description: 'Standard-Prompt für Lektions-Inhalt Generierung',
    content: 'Du bist ein erfahrener Lehrer. Erstelle einen Lerninhalt für das Thema "{{topic}}" auf {{level}}-Niveau. Der Inhalt sollte {{length}} Wörter umfassen.',
    category: 'content',
    variables: ['topic', 'level', 'length'],
    targetLMs: ['LM00', 'LM01', 'LM02'],
    tokens: 1200,
    isActive: true,
    lastUpdated: '10.12.2025'
  },
  {
    id: '2',
    name: 'Video-Skript Bezugskalkulation',
    description: 'Skript für Erklärungs-Video zur Bezugskalkulation',
    content: 'Erstelle ein Skript für ein Erklärungs-Video. Thema: {{topic}}. Zielgruppe: {{audience}}. Stil: {{style}}.',
    category: 'video',
    variables: ['topic', 'audience', 'style'],
    targetLMs: ['LM00', 'LM07'],
    tokens: 800,
    isActive: true,
    lastUpdated: '09.12.2025'
  },
  {
    id: '3',
    name: 'Quiz Generator',
    description: 'Generiert Multiple-Choice Fragen',
    content: 'Erstelle {{count}} Multiple-Choice Fragen zum Thema "{{topic}}". Schwierigkeit: {{difficulty}}.',
    category: 'quiz',
    variables: ['count', 'topic', 'difficulty'],
    targetLMs: ['LM22'],
    tokens: 600,
    isActive: true,
    lastUpdated: '08.12.2025'
  }
])

// Computed
const filteredPrompts = computed(() => {
  let result = prompts.value

  // Filter by category
  if (selectedCategory.value) {
    result = result.filter(p => p.category === selectedCategory.value)
  }

  // Filter by LM
  if (selectedLM.value) {
    result = result.filter(p => p.targetLMs.includes(selectedLM.value!))
  }

  // Filter by search
  if (promptSearch.value) {
    const search = promptSearch.value.toLowerCase()
    result = result.filter(p =>
      p.name.toLowerCase().includes(search) ||
      p.description.toLowerCase().includes(search)
    )
  }

  return result
})

const renderedPrompt = computed(() => {
  if (!selectedPrompt.value) return ''

  let content = selectedPrompt.value.content
  for (const [key, value] of Object.entries(testVariables.value)) {
    content = content.replace(new RegExp(`{{${key}}}`, 'g'), value || `[${key}]`)
  }
  return content
})

// Methods
function selectCategory(categoryId: string) {
  selectedCategory.value = categoryId
  selectedLM.value = null
}

function selectLearningMethod(lmId: string) {
  selectedLM.value = lmId
  selectedCategory.value = ''
}

function selectPrompt(prompt: Prompt) {
  selectedPrompt.value = { ...prompt }
}

function createNewPrompt() {
  selectedPrompt.value = {
    id: Date.now().toString(),
    name: 'Neuer Prompt',
    description: '',
    content: '',
    category: selectedCategory.value || 'content',
    variables: [],
    targetLMs: [],
    tokens: 0,
    isActive: true,
    lastUpdated: new Date().toLocaleDateString('de-DE')
  }
}

function savePrompt() {
  if (!selectedPrompt.value) return

  const index = prompts.value.findIndex(p => p.id === selectedPrompt.value!.id)
  if (index >= 0) {
    prompts.value[index] = { ...selectedPrompt.value }
  } else {
    prompts.value.push({ ...selectedPrompt.value })
  }
}

function deletePrompt() {
  if (!selectedPrompt.value || !confirm('Prompt wirklich löschen?')) return

  prompts.value = prompts.value.filter(p => p.id !== selectedPrompt.value!.id)
  selectedPrompt.value = null
}

function duplicatePrompt() {
  if (!selectedPrompt.value) return

  const newPrompt = {
    ...selectedPrompt.value,
    id: Date.now().toString(),
    name: `${selectedPrompt.value.name} (Kopie)`
  }
  prompts.value.push(newPrompt)
  selectedPrompt.value = newPrompt
}

function addVariable() {
  const name = prompt('Variable Name:')
  if (name && selectedPrompt.value && !selectedPrompt.value.variables.includes(name)) {
    selectedPrompt.value.variables.push(name)
  }
}

function formatVariable(variable: string): string {
  return '{{' + variable + '}}'
}

function insertVariable(variable: string) {
  if (!selectedPrompt.value) return
  selectedPrompt.value.content += '{{' + variable + '}}'
}

function toggleLM(lmId: string) {
  if (!selectedPrompt.value) return

  const index = selectedPrompt.value.targetLMs.indexOf(lmId)
  if (index >= 0) {
    selectedPrompt.value.targetLMs.splice(index, 1)
  } else {
    selectedPrompt.value.targetLMs.push(lmId)
  }
}

function testPrompt() {
  if (!selectedPrompt.value) return

  // Initialize test variables
  testVariables.value = {}
  for (const variable of selectedPrompt.value.variables) {
    testVariables.value[variable] = ''
  }

  testResult.value = null
  showTestModal.value = true
}

async function runTest() {
  isTestRunning.value = true

  try {
    // TODO: Call AI API with rendered prompt
    await new Promise(resolve => setTimeout(resolve, 2000))
    testResult.value = 'Dies ist eine simulierte KI-Antwort auf den Test-Prompt. In der echten Implementation würde hier die Antwort vom AI-Modell erscheinen.'
  } catch (error) {
    console.error('Test failed:', error)
  } finally {
    isTestRunning.value = false
  }
}

function exportPrompts() {
  const data = JSON.stringify(prompts.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'prompts-export.json'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.prompts-tab {
  min-height: 400px;
}
</style>
