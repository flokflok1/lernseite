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
        <h2 class="text-xl font-bold text-[var(--color-text-primary)]">{{ $t('windows.aiEditorPrompts.title') }}</h2>
        <p class="text-sm text-[var(--color-text-secondary)] mt-1">
          {{ $t('windows.aiEditorPrompts.subtitle') }}
        </p>
      </div>
      <div class="flex gap-2">
        <button
          @click="showImportModal = true"
          class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-surface-secondary)] transition-colors flex items-center gap-2"
        >
          <span>📥</span> {{ $t('windows.aiEditorPrompts.import') }}
        </button>
        <button
          @click="exportPrompts"
          class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-surface-secondary)] transition-colors flex items-center gap-2"
        >
          <span>📤</span> {{ $t('windows.aiEditorPrompts.export') }}
        </button>
        <button
          @click="createNewPrompt"
          class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors flex items-center gap-2"
        >
          <span>+</span> {{ $t('windows.aiEditorPrompts.newPrompt') }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-3 gap-6">
      <!-- Left: Prompt Categories -->
      <div class="col-span-1 space-y-4">
        <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide">
          {{ $t('windows.aiEditorPrompts.categories') }}
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
                  <div class="text-xs text-[var(--color-text-tertiary)]">{{ $t('windows.aiEditorPrompts.promptsCount', { count: category.count }) }}</div>
                </div>
              </div>
              <span class="text-[var(--color-text-tertiary)]">›</span>
            </div>
          </button>
        </div>

        <!-- Learning Methods Quick Access -->
        <div class="mt-6">
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide mb-3">
            {{ $t('windows.aiEditorPrompts.learningMethods') }}
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
            {{ $t('windows.aiEditorPrompts.prompts') }}
          </h3>
          <input
            v-model="promptSearch"
            type="text"
            :placeholder="$t('windows.aiEditorPrompts.search')"
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
                {{ prompt.isActive ? $t('windows.aiEditorPrompts.active') : $t('windows.aiEditorPrompts.inactive') }}
              </span>
            </div>
            <p class="text-sm text-[var(--color-text-secondary)] line-clamp-2 mb-2">
              {{ prompt.description }}
            </p>
            <div class="flex items-center gap-2 text-xs text-[var(--color-text-tertiary)]">
              <span>{{ prompt.variables.length }} {{ $t('windows.aiEditorPrompts.variables') }}</span>
              <span>•</span>
              <span>{{ prompt.tokens }} {{ $t('windows.aiEditorPrompts.tokens') }}</span>
              <span>•</span>
              <span>{{ prompt.lastUpdated }}</span>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="filteredPrompts.length === 0" class="text-center py-8">
            <span class="text-4xl mb-2 block">📝</span>
            <p class="text-[var(--color-text-secondary)]">{{ $t('windows.aiEditorPrompts.noPromptsFound') }}</p>
          </div>
        </div>
      </div>

      <!-- Right: Prompt Editor -->
      <div class="col-span-1">
        <PromptEditor
          :prompt="selectedPrompt"
          :learning-methods="learningMethods"
          @test="testPrompt"
          @duplicate="duplicatePrompt"
          @save="savePrompt"
          @delete="deletePrompt"
          @add-variable="addVariable"
          @insert-variable="insertVariable"
          @toggle-l-m="toggleLM"
          @update:field="updatePromptField"
        />
      </div>
    </div>

    <!-- Test Modal -->
    <TestPromptModal
      :show="showTestModal"
      :variables="selectedPrompt?.variables || []"
      :test-variables="testVariables"
      :rendered-prompt="renderedPrompt"
      :test-result="testResult"
      :is-running="isTestRunning"
      @close="showTestModal = false"
      @run="runTest"
      @update:variable="updateTestVariable"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { TestPromptModal, PromptEditor } from '@/presentation/components/studio/assessment/admin/settings/exams'

const { t } = useI18n()

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

// Categories (computed for i18n)
const promptCategories = computed(() => [
  { id: 'content', name: t('windows.aiEditorPrompts.categories.content'), emoji: '📝', count: 8 },
  { id: 'video', name: t('windows.aiEditorPrompts.categories.video'), emoji: '🎬', count: 4 },
  { id: 'quiz', name: t('windows.aiEditorPrompts.categories.quiz'), emoji: '❓', count: 6 },
  { id: 'feedback', name: t('windows.aiEditorPrompts.categories.feedback'), emoji: '💬', count: 3 },
  { id: 'translation', name: t('windows.aiEditorPrompts.categories.translation'), emoji: '🌍', count: 2 },
  { id: 'summary', name: t('windows.aiEditorPrompts.categories.summary'), emoji: '📋', count: 3 }
])

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

function updatePromptField(field: keyof Prompt, value: unknown) {
  if (selectedPrompt.value) {
    (selectedPrompt.value as Record<string, unknown>)[field] = value
  }
}

function createNewPrompt() {
  selectedPrompt.value = {
    id: Date.now().toString(),
    name: t('windows.aiEditorPrompts.newPrompt'),
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
  if (!selectedPrompt.value || !confirm(t('windows.aiEditorPrompts.confirmDelete'))) return

  prompts.value = prompts.value.filter(p => p.id !== selectedPrompt.value!.id)
  selectedPrompt.value = null
}

function duplicatePrompt() {
  if (!selectedPrompt.value) return

  const newPrompt = {
    ...selectedPrompt.value,
    id: Date.now().toString(),
    name: `${selectedPrompt.value.name} ${t('windows.aiEditorPrompts.copy')}`
  }
  prompts.value.push(newPrompt)
  selectedPrompt.value = newPrompt
}

function addVariable() {
  const name = prompt(t('windows.aiEditorPrompts.variableNamePrompt'))
  if (name && selectedPrompt.value && !selectedPrompt.value.variables.includes(name)) {
    selectedPrompt.value.variables.push(name)
  }
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

function updateTestVariable(variable: string, value: string) {
  testVariables.value[variable] = value
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
