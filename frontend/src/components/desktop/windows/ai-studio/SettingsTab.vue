<!--
  SettingsTab.vue

  KI-Studio Pro Kurs-Einstellungen Tab
  Verwaltet kurs-spezifische KI-Modell-Konfiguration.

  Features:
  - Globale Profile anwenden (Standard, Qualität, Sparsam, Anthropic)
  - 6 Modell-Kategorien: Chat, Reasoning, Image, Audio, Realtime, Embedding
  - Effektive Einstellungen mit Fallback-Auflösung
  - Prompt-Templates Verwaltung

  Phase: KI-Studio Pro - Kurs-Einstellungen
-->

<template>
  <div class="settings-tab p-6">
    <!-- Kein Kurs gewählt -->
    <div v-if="!course" class="empty-state">
      <div class="icon">⚙️</div>
      <h3>Kein Kurs ausgewählt</h3>
      <p>Wähle einen Kurs aus, um die KI-Einstellungen zu bearbeiten.</p>
    </div>

    <!-- Settings Content -->
    <template v-else>
      <!-- Header -->
      <div class="mb-6">
        <h2 class="text-xl font-bold text-[var(--color-text-primary)]">
          ⚙️ Kurs-Einstellungen: {{ course.title }}
        </h2>
        <p class="text-sm text-[var(--color-text-secondary)] mt-1">
          KI-Modelle für diesen Kurs konfigurieren
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Lade Einstellungen...</p>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Profile Selection Card -->
        <div class="settings-card">
          <div class="card-header">
            <span class="card-icon">🎯</span>
            <span class="card-title">Profil anwenden</span>
          </div>
          <div class="profile-grid">
            <button
              v-for="profile in profiles"
              :key="profile.key"
              @click="applyProfile(profile.key)"
              class="profile-item"
              :class="{
                active: settings.effective?.profile_key === profile.key,
                default: profile.is_default
              }"
            >
              <div class="profile-header">
                <span class="profile-name">{{ profile.name }}</span>
                <span v-if="profile.is_default" class="default-badge">Default</span>
              </div>
              <span class="profile-desc">{{ profile.description }}</span>
            </button>
          </div>
          <div class="card-footer">
            <span class="text-xs text-[var(--color-text-tertiary)]">
              Profile definieren Modelle für alle 6 Kategorien.
              Globale Profile werden im Admin-Bereich verwaltet.
            </span>
          </div>
        </div>

        <!-- Current Settings Card - 6 Model Categories -->
        <div class="settings-card">
          <div class="card-header">
            <span class="card-icon">🤖</span>
            <span class="card-title">Modell-Konfiguration</span>
            <span v-if="settings.effective?.is_custom" class="custom-badge">Angepasst</span>
          </div>
          <div class="model-list">
            <!-- Chat Model -->
            <div class="model-item">
              <div class="model-label">
                <span class="model-icon">💬</span>
                <span>Chat / Text</span>
              </div>
              <select
                v-model="formData.chat_model_id"
                @change="saveSettings"
                class="model-select"
              >
                <option value="">Profil-Default</option>
                <option
                  v-for="model in modelsByCategory.chat"
                  :key="model.model_id"
                  :value="model.model_id"
                >
                  {{ model.display_name || model.model_id }}
                </option>
              </select>
            </div>

            <!-- Reasoning Model -->
            <div class="model-item">
              <div class="model-label">
                <span class="model-icon">🧠</span>
                <span>Reasoning / Prüfungen</span>
              </div>
              <select
                v-model="formData.reasoning_model_id"
                @change="saveSettings"
                class="model-select"
              >
                <option value="">Profil-Default</option>
                <option
                  v-for="model in modelsByCategory.reasoning"
                  :key="model.model_id"
                  :value="model.model_id"
                >
                  {{ model.display_name || model.model_id }}
                </option>
              </select>
            </div>

            <!-- Image Model -->
            <div class="model-item">
              <div class="model-label">
                <span class="model-icon">🖼️</span>
                <span>Bildgenerierung</span>
              </div>
              <select
                v-model="formData.image_model_id"
                @change="saveSettings"
                class="model-select"
              >
                <option value="">Profil-Default</option>
                <option
                  v-for="model in modelsByCategory.image"
                  :key="model.model_id"
                  :value="model.model_id"
                >
                  {{ model.display_name || model.model_id }}
                </option>
              </select>
            </div>

            <!-- Audio Model -->
            <div class="model-item">
              <div class="model-label">
                <span class="model-icon">🔊</span>
                <span>Audio / TTS</span>
              </div>
              <select
                v-model="formData.audio_model_id"
                @change="saveSettings"
                class="model-select"
              >
                <option value="">Profil-Default</option>
                <option
                  v-for="model in modelsByCategory.audio"
                  :key="model.model_id"
                  :value="model.model_id"
                >
                  {{ model.display_name || model.model_id }}
                </option>
              </select>
            </div>

            <!-- Realtime Model -->
            <div class="model-item">
              <div class="model-label">
                <span class="model-icon">⚡</span>
                <span>Realtime</span>
              </div>
              <select
                v-model="formData.realtime_model_id"
                @change="saveSettings"
                class="model-select"
              >
                <option value="">Profil-Default</option>
                <option
                  v-for="model in modelsByCategory.realtime"
                  :key="model.model_id"
                  :value="model.model_id"
                >
                  {{ model.display_name || model.model_id }}
                </option>
              </select>
            </div>

            <!-- Embedding Model -->
            <div class="model-item">
              <div class="model-label">
                <span class="model-icon">🔗</span>
                <span>Embedding</span>
              </div>
              <select
                v-model="formData.embedding_model_id"
                @change="saveSettings"
                class="model-select"
              >
                <option value="">Profil-Default</option>
                <option
                  v-for="model in modelsByCategory.embedding"
                  :key="model.model_id"
                  :value="model.model_id"
                >
                  {{ model.display_name || model.model_id }}
                </option>
              </select>
            </div>
          </div>
          <div class="card-footer">
            <button
              @click="resetToDefaults"
              class="reset-btn"
              :disabled="!settings.effective?.is_custom"
            >
              Auf Defaults zurücksetzen
            </button>
          </div>
        </div>

        <!-- Effective Settings Display - 6 Categories -->
        <div class="settings-card lg:col-span-2">
          <div class="card-header">
            <span class="card-icon">✅</span>
            <span class="card-title">Effektive Einstellungen</span>
            <span v-if="settings.effective?.profile_name" class="profile-badge">
              Profil: {{ settings.effective.profile_name }}
            </span>
          </div>
          <div class="effective-grid">
            <div class="effective-item">
              <span class="effective-label">💬 Chat</span>
              <span class="effective-value">{{ settings.effective?.chat_model_id || 'gpt-4o-mini' }}</span>
            </div>
            <div class="effective-item">
              <span class="effective-label">🧠 Reasoning</span>
              <span class="effective-value">{{ settings.effective?.reasoning_model_id || 'gpt-4o' }}</span>
            </div>
            <div class="effective-item">
              <span class="effective-label">🖼️ Image</span>
              <span class="effective-value">{{ settings.effective?.image_model_id || 'dall-e-3' }}</span>
            </div>
            <div class="effective-item">
              <span class="effective-label">🔊 Audio</span>
              <span class="effective-value">{{ settings.effective?.audio_model_id || 'tts-1' }}</span>
            </div>
            <div class="effective-item">
              <span class="effective-label">⚡ Realtime</span>
              <span class="effective-value">{{ settings.effective?.realtime_model_id || 'gpt-4o-realtime' }}</span>
            </div>
            <div class="effective-item">
              <span class="effective-label">🔗 Embedding</span>
              <span class="effective-value">{{ settings.effective?.embedding_model_id || 'text-embedding-3-small' }}</span>
            </div>
          </div>
          <div class="card-footer text-xs text-[var(--color-text-tertiary)]">
            Fallback-Kette: Kurs-Override → Profil → Default-Profil → System-Default
          </div>
        </div>

        <!-- Prompt Templates Section -->
        <div class="settings-card lg:col-span-2">
          <div class="card-header">
            <span class="card-icon">📝</span>
            <span class="card-title">Prompt-Templates</span>
            <button @click="showPromptEditor = true" class="add-btn">
              + Neues Template
            </button>
          </div>
          <div class="prompt-list">
            <div v-if="loadingPrompts" class="text-center py-4">
              <div class="spinner small"></div>
            </div>
            <div v-else-if="!prompts.length" class="text-center py-4 text-[var(--color-text-tertiary)]">
              Keine kurs-spezifischen Templates vorhanden
            </div>
            <div
              v-else
              v-for="prompt in prompts"
              :key="prompt.template_key"
              class="prompt-item"
            >
              <div class="prompt-info">
                <span class="prompt-key">{{ prompt.template_key }}</span>
                <span class="prompt-name">{{ prompt.template_name }}</span>
              </div>
              <div class="prompt-category">{{ prompt.category }}</div>
              <button @click="editPrompt(prompt)" class="edit-btn">Bearbeiten</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Save Status -->
      <div v-if="saveStatus" class="save-status" :class="saveStatus.type">
        {{ saveStatus.message }}
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import http from '@/api/http'

interface Course {
  course_id: string
  title: string
}

interface Settings {
  settings?: Record<string, any>
  effective?: {
    course_id: string
    profile_key?: string
    profile_name?: string
    chat_model_id: string
    reasoning_model_id: string
    image_model_id: string
    audio_model_id: string
    realtime_model_id: string
    embedding_model_id: string
    is_custom: boolean
  }
}

interface Profile {
  key: string
  name: string
  description?: string
  is_default: boolean
}

interface AIModel {
  model_id: string
  display_name?: string
  provider?: string
  category?: string
}

interface ModelsByCategory {
  chat: AIModel[]
  reasoning: AIModel[]
  image: AIModel[]
  audio: AIModel[]
  realtime: AIModel[]
  embedding: AIModel[]
}

interface PromptTemplate {
  template_key: string
  template_name: string
  category: string
  system_prompt: string
  user_prompt_template: string
}

const props = defineProps<{
  course?: Course | null
}>()

const loading = ref(false)
const loadingPrompts = ref(false)
const settings = ref<Settings>({})
const profiles = ref<Profile[]>([])
const modelsByCategory = ref<ModelsByCategory>({
  chat: [],
  reasoning: [],
  image: [],
  audio: [],
  realtime: [],
  embedding: []
})
const prompts = ref<PromptTemplate[]>([])
const showPromptEditor = ref(false)
const saveStatus = ref<{ type: string; message: string } | null>(null)

const formData = reactive({
  chat_model_id: '',
  reasoning_model_id: '',
  image_model_id: '',
  audio_model_id: '',
  realtime_model_id: '',
  embedding_model_id: ''
})

// Methods
async function loadSettings() {
  if (!props.course?.course_id) return

  loading.value = true
  try {
    const response = await http.get(`/admin/course-ai-settings/${props.course.course_id}`)
    settings.value = response.data.data || {}

    // Populate form with current settings
    const s = settings.value.settings || {}
    formData.chat_model_id = s.chat_model_id || ''
    formData.reasoning_model_id = s.reasoning_model_id || ''
    formData.image_model_id = s.image_model_id || ''
    formData.audio_model_id = s.audio_model_id || ''
    formData.realtime_model_id = s.realtime_model_id || ''
    formData.embedding_model_id = s.embedding_model_id || ''
  } catch (error) {
    console.error('Failed to load settings:', error)
  } finally {
    loading.value = false
  }
}

async function loadProfiles() {
  try {
    // Load from global profiles API
    const response = await http.get('/admin/ai-model-profiles?summary=true')
    profiles.value = response.data.data?.profiles || []
  } catch (error) {
    console.error('Failed to load profiles:', error)
  }
}

async function loadModelsByCategory() {
  try {
    const response = await http.get('/admin/ai-model-profiles/models-by-category')
    modelsByCategory.value = response.data.data?.categories || {
      chat: [],
      reasoning: [],
      image: [],
      audio: [],
      realtime: [],
      embedding: []
    }
  } catch (error) {
    console.error('Failed to load models by category:', error)
  }
}

async function loadPrompts() {
  if (!props.course?.course_id) return

  loadingPrompts.value = true
  try {
    const response = await http.get(`/admin/prompts?course_id=${props.course.course_id}`)
    prompts.value = response.data.data?.templates || []
  } catch (error) {
    console.error('Failed to load prompts:', error)
  } finally {
    loadingPrompts.value = false
  }
}

async function saveSettings() {
  if (!props.course?.course_id) return

  try {
    const response = await http.put(`/admin/course-ai-settings/${props.course.course_id}`, {
      chat_model_id: formData.chat_model_id || null,
      reasoning_model_id: formData.reasoning_model_id || null,
      image_model_id: formData.image_model_id || null,
      audio_model_id: formData.audio_model_id || null,
      realtime_model_id: formData.realtime_model_id || null,
      embedding_model_id: formData.embedding_model_id || null
    })

    settings.value = response.data.data || {}
    showSaveStatus('success', 'Einstellungen gespeichert')
  } catch (error) {
    console.error('Failed to save settings:', error)
    showSaveStatus('error', 'Fehler beim Speichern')
  }
}

async function applyProfile(profileKey: string) {
  if (!props.course?.course_id) return

  try {
    const response = await http.post(`/admin/course-ai-settings/${props.course.course_id}/apply-profile`, {
      profile_key: profileKey
    })

    const data = response.data
    settings.value = data.data || {}

    // Update form with applied profile values
    const s = settings.value.settings || {}
    formData.chat_model_id = s.chat_model_id || ''
    formData.reasoning_model_id = s.reasoning_model_id || ''
    formData.image_model_id = s.image_model_id || ''
    formData.audio_model_id = s.audio_model_id || ''
    formData.realtime_model_id = s.realtime_model_id || ''
    formData.embedding_model_id = s.embedding_model_id || ''

    showSaveStatus('success', `Profil "${data.data?.profile_applied}" angewendet`)
  } catch (error) {
    console.error('Failed to apply profile:', error)
    showSaveStatus('error', 'Fehler beim Anwenden des Profils')
  }
}

async function resetToDefaults() {
  if (!props.course?.course_id) return

  try {
    await http.delete(`/admin/course-ai-settings/${props.course.course_id}`)

    showSaveStatus('success', 'Auf Defaults zurückgesetzt')

    // Reset form
    formData.chat_model_id = ''
    formData.reasoning_model_id = ''
    formData.image_model_id = ''
    formData.audio_model_id = ''
    formData.realtime_model_id = ''
    formData.embedding_model_id = ''

    // Reload settings to get new effective values
    loadSettings()
  } catch (error) {
    console.error('Failed to reset settings:', error)
    showSaveStatus('error', 'Fehler beim Zurücksetzen')
  }
}

function editPrompt(prompt: PromptTemplate) {
  // TODO: Open prompt editor modal
  console.log('Edit prompt:', prompt)
}

function showSaveStatus(type: string, message: string) {
  saveStatus.value = { type, message }
  setTimeout(() => {
    saveStatus.value = null
  }, 3000)
}

// Watch for course changes
watch(() => props.course?.course_id, (newId) => {
  if (newId) {
    loadSettings()
    loadPrompts()
  } else {
    settings.value = {}
    prompts.value = []
  }
}, { immediate: true })

onMounted(() => {
  loadProfiles()
  loadModelsByCategory()
  if (props.course?.course_id) {
    loadSettings()
    loadPrompts()
  }
})
</script>

<style scoped>
.settings-tab {
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

.spinner.small {
  width: 1.5rem;
  height: 1.5rem;
  border-width: 2px;
  margin-bottom: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.settings-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.card-icon {
  font-size: 1.25rem;
}

.card-title {
  font-weight: 600;
  color: var(--color-text-primary);
  flex: 1;
}

.custom-badge,
.profile-badge {
  padding: 0.125rem 0.5rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 600;
}

.add-btn {
  padding: 0.25rem 0.75rem;
  background: var(--color-primary);
  color: white;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.add-btn:hover {
  opacity: 0.9;
}

.card-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

/* Profile Grid */
.profile-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  padding: 1rem;
}

.profile-item {
  display: flex;
  flex-direction: column;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border: 2px solid transparent;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.15s;
  text-align: left;
}

.profile-item:hover {
  border-color: var(--color-primary);
}

.profile-item.active {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.profile-name {
  font-weight: 600;
  color: var(--color-text-primary);
}

.default-badge {
  padding: 0.0625rem 0.375rem;
  background: var(--color-success-subtle, rgba(34, 197, 94, 0.1));
  color: var(--color-success, #22c55e);
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 600;
}

.profile-desc {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

/* Model List */
.model-list {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.model-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.model-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 160px;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.model-icon {
  font-size: 1rem;
}

.model-select {
  flex: 1;
  padding: 0.5rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  color: var(--color-text-primary);
  font-size: 0.8125rem;
}

.model-select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.reset-btn {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.15s;
}

.reset-btn:hover:not(:disabled) {
  border-color: var(--color-error);
  color: var(--color-error);
}

.reset-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Effective Grid - 6 items */
.effective-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.5rem;
  padding: 1rem;
}

@media (max-width: 1200px) {
  .effective-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .effective-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.effective-item {
  display: flex;
  flex-direction: column;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
  text-align: center;
}

.effective-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.25rem;
}

.effective-value {
  font-family: ui-monospace, monospace;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-primary);
  word-break: break-all;
}

/* Prompt List */
.prompt-list {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.prompt-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
}

.prompt-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.prompt-key {
  font-family: ui-monospace, monospace;
  font-size: 0.75rem;
  color: var(--color-primary);
}

.prompt-name {
  font-size: 0.8125rem;
  color: var(--color-text-primary);
}

.prompt-category {
  padding: 0.125rem 0.5rem;
  background: var(--color-surface);
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
}

.edit-btn {
  padding: 0.25rem 0.5rem;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.edit-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

/* Save Status */
.save-status {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  z-index: 100;
  animation: slideIn 0.2s ease;
}

.save-status.success {
  background: #22c55e;
  color: white;
}

.save-status.error {
  background: #ef4444;
  color: white;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(1rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
