<!--
  Admin Prompts Page - Prompt-Verwaltung mit Editor

  Features:
  - Liste aller Prompt-Templates aus der Datenbank
  - CRUD-Operationen (Erstellen, Bearbeiten, Duplizieren, Loeschen)
  - Live-Vorschau mit Variablen-Substitution
  - Filter nach Kategorie und Stil
  - Nutzungsstatistiken
  - TTS-Voice Auswahl fuer Audio-Generierung
-->

<template>
  <div class="admin-prompts-page p-6">
    <!-- Page Header -->
    <div class="flex justify-between items-start mb-6">
      <div>
        <h1 class="text-3xl font-bold text-[var(--color-text-primary)] mb-2">KI-Prompt-Verwaltung</h1>
        <p class="text-[var(--color-text-secondary)]">
          Verwalten Sie KI-Prompt-Templates fuer Theorieblatt-Generierung und Lernmethoden
        </p>
      </div>
      <button
        @click="openCreateModal"
        class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors flex items-center gap-2"
      >
        <span>+</span>
        <span>Neues Template</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-1">Gesamt Templates</p>
            <p class="text-2xl font-bold text-[var(--color-text-primary)]">{{ stats.total }}</p>
          </div>
          <div class="text-3xl opacity-60">T</div>
        </div>
      </div>

      <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-1">Kategorien</p>
            <p class="text-2xl font-bold text-[var(--color-text-primary)]">{{ categories.length }}</p>
          </div>
          <div class="text-3xl opacity-60">C</div>
        </div>
      </div>

      <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-1">Aufrufe (30d)</p>
            <p class="text-2xl font-bold text-[var(--color-text-primary)]">{{ stats.usageCount }}</p>
          </div>
          <div class="text-3xl opacity-60">U</div>
        </div>
      </div>

      <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-1">Tokens verbraucht</p>
            <p class="text-2xl font-bold text-[var(--color-text-primary)]">{{ formatNumber(stats.tokensUsed) }}</p>
          </div>
          <div class="text-3xl opacity-60">$</div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex gap-4 mb-6">
      <select
        v-model="selectedCategory"
        class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
      >
        <option value="">Alle Kategorien</option>
        <option v-for="cat in categories" :key="cat" :value="cat">{{ categoryLabels[cat] || cat }}</option>
      </select>

      <select
        v-model="selectedStyle"
        class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
      >
        <option value="">Alle Stile</option>
        <option v-for="style in availableStyles" :key="style" :value="style">{{ styleLabels[style] || style }}</option>
      </select>

      <input
        v-model="searchQuery"
        type="text"
        placeholder="Suchen..."
        class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] flex-1"
      />
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]"></div>
      <span class="ml-3 text-[var(--color-text-secondary)]">Lade Templates...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <p class="text-red-700">{{ error }}</p>
      <button @click="loadTemplates" class="mt-2 text-sm text-red-600 underline">Erneut versuchen</button>
    </div>

    <!-- Templates List -->
    <div v-else class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]">
      <div class="px-6 py-4 border-b border-[var(--color-border)] flex justify-between items-center">
        <h2 class="text-xl font-bold text-[var(--color-text-primary)]">
          Prompt Templates ({{ filteredTemplates.length }})
        </h2>
      </div>

      <div v-if="filteredTemplates.length === 0" class="p-8 text-center text-[var(--color-text-secondary)]">
        Keine Templates gefunden. Erstellen Sie ein neues Template.
      </div>

      <div v-else class="divide-y divide-[var(--color-border)]">
        <div
          v-for="template in filteredTemplates"
          :key="template.template_id"
          class="p-4 hover:bg-[var(--color-bg)] transition-colors"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
                  {{ template.name }}
                </h3>
                <span
                  v-if="template.is_default"
                  class="px-2 py-0.5 text-xs rounded bg-green-100 text-green-700"
                >
                  Standard
                </span>
                <span class="px-2 py-0.5 text-xs rounded bg-blue-100 text-blue-700">
                  {{ categoryLabels[template.category] || template.category }}
                </span>
                <span class="px-2 py-0.5 text-xs rounded bg-purple-100 text-purple-700">
                  {{ styleLabels[template.style] || template.style }}
                </span>
              </div>

              <p class="text-sm text-[var(--color-text-secondary)] mb-2">
                {{ template.description || 'Keine Beschreibung' }}
              </p>

              <div class="flex items-center gap-4 text-xs text-[var(--color-text-secondary)]">
                <span>Code: <code class="bg-[var(--color-bg)] px-1 rounded">{{ template.code }}</code></span>
                <span>Model: {{ template.model || 'gpt-4o-mini' }}</span>
                <span>Max Tokens: {{ template.max_tokens || 4000 }}</span>
                <span v-if="template.usage_count">{{ template.usage_count }}x verwendet</span>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <button
                @click="previewTemplate(template)"
                class="px-3 py-1.5 text-sm rounded-lg border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-bg)] transition-colors"
                title="Vorschau"
              >
                Vorschau
              </button>
              <button
                @click="editTemplate(template)"
                class="px-3 py-1.5 text-sm rounded-lg border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-bg)] transition-colors"
                title="Bearbeiten"
              >
                Bearbeiten
              </button>
              <button
                @click="duplicateTemplate(template)"
                class="px-3 py-1.5 text-sm rounded-lg border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-bg)] transition-colors"
                title="Duplizieren"
              >
                Duplizieren
              </button>
              <button
                v-if="!template.is_default"
                @click="confirmDelete(template)"
                class="px-3 py-1.5 text-sm rounded-lg border border-red-300 text-red-600 hover:bg-red-50 transition-colors"
                title="Loeschen"
              >
                X
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit/Create Modal -->
    <div
      v-if="showEditModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      @click.self="closeModal"
    >
      <div class="bg-[var(--color-surface)] rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Modal Header -->
        <div class="px-6 py-4 border-b border-[var(--color-border)] flex justify-between items-center">
          <h2 class="text-xl font-bold text-[var(--color-text-primary)]">
            {{ editingTemplate?.template_id ? 'Template bearbeiten' : 'Neues Template erstellen' }}
          </h2>
          <button @click="closeModal" class="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">
            X
          </button>
        </div>

        <!-- Modal Body -->
        <div class="flex-1 overflow-y-auto p-6">
          <div class="grid grid-cols-2 gap-6">
            <!-- Left Column: Basic Info -->
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Name *</label>
                <input
                  v-model="editingTemplate.name"
                  type="text"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                  placeholder="z.B. Theorieblatt ADHS-freundlich"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Code *</label>
                <input
                  v-model="editingTemplate.code"
                  type="text"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] font-mono"
                  placeholder="z.B. theory_adhs"
                />
                <p class="text-xs text-[var(--color-text-secondary)] mt-1">Eindeutiger Identifier (keine Leerzeichen)</p>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Kategorie *</label>
                  <select
                    v-model="editingTemplate.category"
                    class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                  >
                    <option value="theory">Theorieblatt</option>
                    <option value="lesson">Lektionsschritte</option>
                    <option value="quiz">Quiz</option>
                    <option value="flashcard">Karteikarten</option>
                    <option value="summary">Zusammenfassung</option>
                    <option value="explanation">Erklaerung</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Stil *</label>
                  <select
                    v-model="editingTemplate.style"
                    class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                  >
                    <option value="standard">Standard</option>
                    <option value="adhs">ADHS-freundlich</option>
                    <option value="detailed">Ausfuehrlich</option>
                    <option value="short">Kurz & Kompakt</option>
                    <option value="exam_focus">Pruefungsfokus</option>
                  </select>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Beschreibung</label>
                <textarea
                  v-model="editingTemplate.description"
                  rows="2"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                  placeholder="Kurze Beschreibung des Templates..."
                ></textarea>
              </div>

              <div class="grid grid-cols-3 gap-4">
                <div>
                  <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Model</label>
                  <select
                    v-model="editingTemplate.model"
                    class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                  >
                    <option value="gpt-4o-mini">GPT-4o Mini</option>
                    <option value="gpt-4o">GPT-4o</option>
                    <option value="gpt-4-turbo">GPT-4 Turbo</option>
                    <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                    <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Temperatur</label>
                  <input
                    v-model.number="editingTemplate.temperature"
                    type="number"
                    min="0"
                    max="2"
                    step="0.1"
                    class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Max Tokens</label>
                  <input
                    v-model.number="editingTemplate.max_tokens"
                    type="number"
                    min="100"
                    max="16000"
                    step="100"
                    class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                  />
                </div>
              </div>

              <!-- TTS Settings -->
              <div class="border-t border-[var(--color-border)] pt-4 mt-4">
                <h3 class="font-medium text-[var(--color-text-primary)] mb-3">TTS-Einstellungen (Audio)</h3>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Standard-Stimme</label>
                    <select
                      v-model="editingTemplate.tts_voice"
                      class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                    >
                      <option value="nova">Nova (weiblich, freundlich)</option>
                      <option value="alloy">Alloy (neutral)</option>
                      <option value="echo">Echo (maennlich, warm)</option>
                      <option value="fable">Fable (neutral, expressiv)</option>
                      <option value="onyx">Onyx (maennlich, tief)</option>
                      <option value="shimmer">Shimmer (weiblich, sanft)</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">TTS Model</label>
                    <select
                      v-model="editingTemplate.tts_model"
                      class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                    >
                      <option value="tts-1">TTS-1 (schnell)</option>
                      <option value="tts-1-hd">TTS-1-HD (hohe Qualitaet)</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right Column: Prompt Content -->
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">System Prompt *</label>
                <textarea
                  v-model="editingTemplate.system_prompt"
                  rows="8"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] font-mono text-sm"
                  placeholder="Du bist ein erfahrener IT-Ausbilder..."
                ></textarea>
              </div>

              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">User Prompt Template *</label>
                <textarea
                  v-model="editingTemplate.user_prompt"
                  rows="10"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] font-mono text-sm"
                  placeholder="Erstelle ein Theorieblatt fuer {{chapter_title}}..."
                ></textarea>
                <p class="text-xs text-[var(--color-text-secondary)] mt-1">
                  Variablen: <code>{{chapter_title}}</code>, <code>{{course_title}}</code>, <code>{{chapter_description}}</code>, <code>{{lesson_titles}}</code>, <code>{{target_audience}}</code>
                </p>
              </div>

              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
                  Erwartete JSON-Struktur (optional)
                </label>
                <textarea
                  v-model="editingTemplate.expected_json"
                  rows="4"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] font-mono text-sm"
                  placeholder='{"overview": "...", "learningGoals": [...], ...}'
                ></textarea>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="px-6 py-4 border-t border-[var(--color-border)] flex justify-between items-center">
          <div>
            <label class="flex items-center gap-2 text-sm text-[var(--color-text-primary)]">
              <input
                v-model="editingTemplate.is_default"
                type="checkbox"
                class="rounded border-[var(--color-border)]"
              />
              Als Standard fuer diese Kategorie/Stil setzen
            </label>
          </div>
          <div class="flex gap-3">
            <button
              @click="closeModal"
              class="px-4 py-2 border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] hover:bg-[var(--color-bg)] transition-colors"
            >
              Abbrechen
            </button>
            <button
              @click="saveTemplate"
              :disabled="saving"
              class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors disabled:opacity-50"
            >
              {{ saving ? 'Speichern...' : 'Speichern' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Preview Modal -->
    <div
      v-if="showPreviewModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      @click.self="closePreview"
    >
      <div class="bg-[var(--color-surface)] rounded-xl shadow-xl max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col">
        <div class="px-6 py-4 border-b border-[var(--color-border)] flex justify-between items-center">
          <h2 class="text-xl font-bold text-[var(--color-text-primary)]">Prompt-Vorschau</h2>
          <button @click="closePreview" class="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">
            X
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-4">
          <div>
            <h3 class="text-sm font-medium text-[var(--color-text-secondary)] mb-2">System Prompt</h3>
            <pre class="bg-[var(--color-bg)] p-4 rounded-lg text-sm whitespace-pre-wrap font-mono">{{ previewData?.system_prompt }}</pre>
          </div>
          <div>
            <h3 class="text-sm font-medium text-[var(--color-text-secondary)] mb-2">User Prompt (mit Beispieldaten)</h3>
            <pre class="bg-[var(--color-bg)] p-4 rounded-lg text-sm whitespace-pre-wrap font-mono">{{ previewData?.rendered_prompt }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      @click.self="showDeleteModal = false"
    >
      <div class="bg-[var(--color-surface)] rounded-xl shadow-xl max-w-md w-full p-6">
        <h2 class="text-xl font-bold text-[var(--color-text-primary)] mb-4">Template loeschen?</h2>
        <p class="text-[var(--color-text-secondary)] mb-6">
          Sind Sie sicher, dass Sie das Template "<strong>{{ deleteTarget?.name }}</strong>" loeschen moechten?
          Diese Aktion kann nicht rueckgaengig gemacht werden.
        </p>
        <div class="flex justify-end gap-3">
          <button
            @click="showDeleteModal = false"
            class="px-4 py-2 border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] hover:bg-[var(--color-bg)]"
          >
            Abbrechen
          </button>
          <button
            @click="deleteTemplate"
            :disabled="deleting"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {{ deleting ? 'Loeschen...' : 'Loeschen' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { http } from '@/api/http'

interface PromptTemplate {
  template_id?: string
  code: string
  name: string
  title?: string  // Backend may use 'title' instead of 'name'
  description?: string
  category: string
  style: string
  system_prompt: string
  user_prompt: string
  user_prompt_template?: string  // Backend may use 'user_prompt_template'
  expected_json?: string
  model?: string
  temperature?: number
  max_tokens?: number
  tts_voice?: string
  tts_model?: string
  is_default?: boolean
  is_active?: boolean
  usage_count?: number
  created_at?: string
  updated_at?: string
}

// State
const templates = ref<PromptTemplate[]>([])
const categories = ref<string[]>([])
const availableStyles = ref<string[]>(['standard', 'adhs', 'detailed', 'short', 'exam_focus'])
const loading = ref(true)
const error = ref('')
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedStyle = ref('')

// Modal State
const showEditModal = ref(false)
const showPreviewModal = ref(false)
const showDeleteModal = ref(false)
const editingTemplate = ref<PromptTemplate>(createEmptyTemplate())
const previewData = ref<any>(null)
const deleteTarget = ref<PromptTemplate | null>(null)
const saving = ref(false)
const deleting = ref(false)

// Stats
const stats = ref({
  total: 0,
  usageCount: 0,
  tokensUsed: 0
})

// Labels
const categoryLabels: Record<string, string> = {
  theory: 'Theorieblatt',
  lesson: 'Lektionsschritte',
  quiz: 'Quiz',
  flashcard: 'Karteikarten',
  summary: 'Zusammenfassung',
  explanation: 'Erklaerung'
}

const styleLabels: Record<string, string> = {
  standard: 'Standard',
  adhs: 'ADHS-freundlich',
  detailed: 'Ausfuehrlich',
  short: 'Kurz & Kompakt',
  exam_focus: 'Pruefungsfokus'
}

// Computed
const filteredTemplates = computed(() => {
  let result = templates.value

  if (selectedCategory.value) {
    result = result.filter(t => t.category === selectedCategory.value)
  }

  if (selectedStyle.value) {
    result = result.filter(t => t.style === selectedStyle.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(t =>
      t.name.toLowerCase().includes(query) ||
      t.code.toLowerCase().includes(query) ||
      (t.description?.toLowerCase().includes(query))
    )
  }

  return result
})

// Functions
function createEmptyTemplate(): PromptTemplate {
  return {
    code: '',
    name: '',
    description: '',
    category: 'theory',
    style: 'standard',
    system_prompt: '',
    user_prompt: '',
    expected_json: '',
    model: 'gpt-4o-mini',
    temperature: 0.7,
    max_tokens: 4000,
    tts_voice: 'nova',
    tts_model: 'tts-1',
    is_default: false,
    is_active: true
  }
}

function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

async function loadTemplates() {
  loading.value = true
  error.value = ''

  try {
    const response = await http.get('/admin/prompts')
    if (response.data.success) {
      // Backend returns 'templates' not 'data'
      templates.value = response.data.templates || response.data.data || []
      stats.value.total = templates.value.length

      // Extract unique categories
      categories.value = [...new Set(templates.value.map(t => t.category))]
    }
  } catch (e: any) {
    error.value = e.response?.data?.error || 'Fehler beim Laden der Templates'
    console.error('Error loading templates:', e)
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const response = await http.get('/admin/prompts/usage-stats')
    if (response.data.success) {
      const data = response.data.data
      stats.value.usageCount = data.total_usage || 0
      stats.value.tokensUsed = data.total_tokens || 0
    }
  } catch (e) {
    console.error('Error loading stats:', e)
  }
}

function openCreateModal() {
  editingTemplate.value = createEmptyTemplate()
  showEditModal.value = true
}

function editTemplate(template: PromptTemplate) {
  // Map backend fields to frontend fields
  editingTemplate.value = {
    ...template,
    name: template.name || template.title || '',  // Backend may use 'title'
    user_prompt: template.user_prompt || template.user_prompt_template || ''  // Backend may use 'user_prompt_template'
  }
  showEditModal.value = true
}

async function duplicateTemplate(template: PromptTemplate) {
  try {
    const response = await http.post(`/admin/prompts/${template.template_id}/duplicate`)
    if (response.data.success) {
      await loadTemplates()
    }
  } catch (e: any) {
    console.error('Error duplicating template:', e)
    alert('Fehler beim Duplizieren: ' + (e.response?.data?.error || e.message))
  }
}

async function previewTemplate(template: PromptTemplate) {
  try {
    const response = await http.post('/admin/prompts/preview', {
      template_id: template.template_id,
      variables: {
        chapter_title: 'IT1: Beschaffung & Kalkulation',
        course_title: 'AP1 Pruefungsvorbereitung',
        chapter_description: 'Grundlagen der Warenbeschaffung und Kalkulationsverfahren',
        lesson_titles: 'Bezugskalkulation, Verkaufskalkulation, Handelskalkulation',
        target_audience: 'Fachinformatiker Systemintegration (FISI)'
      }
    })

    if (response.data.success) {
      previewData.value = response.data.data
      showPreviewModal.value = true
    }
  } catch (e: any) {
    // Fallback: show raw template
    previewData.value = {
      system_prompt: template.system_prompt,
      rendered_prompt: template.user_prompt
    }
    showPreviewModal.value = true
  }
}

function closePreview() {
  showPreviewModal.value = false
  previewData.value = null
}

function confirmDelete(template: PromptTemplate) {
  deleteTarget.value = template
  showDeleteModal.value = true
}

async function deleteTemplate() {
  if (!deleteTarget.value?.template_id) return

  deleting.value = true
  try {
    await http.delete(`/admin/prompts/${deleteTarget.value.template_id}`)
    await loadTemplates()
    showDeleteModal.value = false
    deleteTarget.value = null
  } catch (e: any) {
    console.error('Error deleting template:', e)
    alert('Fehler beim Loeschen: ' + (e.response?.data?.error || e.message))
  } finally {
    deleting.value = false
  }
}

async function saveTemplate() {
  if (!editingTemplate.value.name || !editingTemplate.value.code) {
    alert('Name und Code sind erforderlich')
    return
  }

  saving.value = true
  try {
    // Map frontend fields to backend field names
    const payload = {
      ...editingTemplate.value,
      title: editingTemplate.value.name,  // Backend expects 'title'
      user_prompt_template: editingTemplate.value.user_prompt  // Backend expects 'user_prompt_template'
    }

    if (editingTemplate.value.template_id) {
      // Update
      await http.patch(`/admin/prompts/${editingTemplate.value.template_id}`, payload)
    } else {
      // Create
      await http.post('/admin/prompts', payload)
    }

    await loadTemplates()
    closeModal()
  } catch (e: any) {
    console.error('Error saving template:', e)
    alert('Fehler beim Speichern: ' + (e.response?.data?.error || e.message))
  } finally {
    saving.value = false
  }
}

function closeModal() {
  showEditModal.value = false
  editingTemplate.value = createEmptyTemplate()
}

// Lifecycle
onMounted(() => {
  loadTemplates()
  loadStats()
})
</script>
