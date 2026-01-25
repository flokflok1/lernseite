<!--
  SettingsTab.vue

  KI-Studio Pro Kurs-Einstellungen Tab
  Verwaltet kurs-spezifische KI-Modell-Konfiguration.
-->

<template>
  <div class="settings-tab p-6">
    <!-- Kein Kurs gewählt -->
    <div v-if="!course" class="empty-state">
      <div class="icon">⚙️</div>
      <h3>{{ $t('windows.aiStudioSettings.noCourse') }}</h3>
      <p>{{ $t('windows.aiStudioSettings.selectCourse') }}</p>
    </div>

    <!-- Settings Content -->
    <template v-else>
      <!-- Header -->
      <div class="mb-6">
        <h2 class="text-xl font-bold text-[var(--color-text-primary)]">
          ⚙️ {{ $t('windows.aiStudioSettings.title') }}: {{ course.title }}
        </h2>
        <p class="text-sm text-[var(--color-text-secondary)] mt-1">
          {{ $t('windows.aiStudioSettings.subtitle') }}
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>{{ $t('windows.aiStudioSettings.loading') }}</p>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Profile Selection Card -->
        <ProfileSelector
          :profiles="profiles"
          :active-profile-key="settings.effective?.profile_key"
          @apply="applyProfile"
        />

        <!-- Model Configuration Card -->
        <ModelConfigCard
          :form-data="formData"
          :models-by-category="modelsByCategory"
          :is-custom="settings.effective?.is_custom || false"
          @update="handleModelUpdate"
          @reset="resetToDefaults"
        />

        <!-- Effective Settings Display -->
        <EffectiveSettings
          :effective="settings.effective"
          :profile-name="settings.effective?.profile_name"
        />

        <!-- Prompt Templates Section -->
        <PromptTemplatesList
          :prompts="prompts"
          :loading="loadingPrompts"
          @add-new="showPromptEditor = true"
          @edit="editPrompt"
        />
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
import { useI18n } from 'vue-i18n'
import http from '@/application/services/api/system'
import { ProfileSelector, ModelConfigCard, EffectiveSettings, PromptTemplatesList } from '@/presentation/components/assessment/admin/settings/exams'

const { t } = useI18n()

interface Course {
  course_id: string
  title: string
}

interface Settings {
  settings?: Record<string, unknown>
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
}

const props = defineProps<{
  course?: Course | null
}>()

const loading = ref(false)
const loadingPrompts = ref(false)
const settings = ref<Settings>({})
const profiles = ref<Profile[]>([])
const modelsByCategory = ref<ModelsByCategory>({
  chat: [], reasoning: [], image: [], audio: [], realtime: [], embedding: []
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
    const s = settings.value.settings || {}
    formData.chat_model_id = String(s.chat_model_id || '')
    formData.reasoning_model_id = String(s.reasoning_model_id || '')
    formData.image_model_id = String(s.image_model_id || '')
    formData.audio_model_id = String(s.audio_model_id || '')
    formData.realtime_model_id = String(s.realtime_model_id || '')
    formData.embedding_model_id = String(s.embedding_model_id || '')
  } catch (error) {
    console.error('Failed to load settings:', error)
  } finally {
    loading.value = false
  }
}

async function loadProfiles() {
  try {
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
      chat: [], reasoning: [], image: [], audio: [], realtime: [], embedding: []
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

async function handleModelUpdate(key: string, value: string) {
  (formData as Record<string, string>)[key] = value
  await saveSettings()
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
    showSaveStatus('success', t('windows.aiStudioSettings.saved'))
  } catch (error) {
    console.error('Failed to save settings:', error)
    showSaveStatus('error', t('windows.aiStudioSettings.saveFailed'))
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
    const s = settings.value.settings || {}
    formData.chat_model_id = String(s.chat_model_id || '')
    formData.reasoning_model_id = String(s.reasoning_model_id || '')
    formData.image_model_id = String(s.image_model_id || '')
    formData.audio_model_id = String(s.audio_model_id || '')
    formData.realtime_model_id = String(s.realtime_model_id || '')
    formData.embedding_model_id = String(s.embedding_model_id || '')
    showSaveStatus('success', t('windows.aiStudioSettings.profileApplied', { profile: data.data?.profile_applied }))
  } catch (error) {
    console.error('Failed to apply profile:', error)
    showSaveStatus('error', t('windows.aiStudioSettings.profileFailed'))
  }
}

async function resetToDefaults() {
  if (!props.course?.course_id) return
  try {
    await http.delete(`/admin/course-ai-settings/${props.course.course_id}`)
    showSaveStatus('success', t('windows.aiStudioSettings.resetSuccess'))
    formData.chat_model_id = ''
    formData.reasoning_model_id = ''
    formData.image_model_id = ''
    formData.audio_model_id = ''
    formData.realtime_model_id = ''
    formData.embedding_model_id = ''
    loadSettings()
  } catch (error) {
    console.error('Failed to reset settings:', error)
    showSaveStatus('error', t('windows.aiStudioSettings.resetFailed'))
  }
}

function editPrompt(prompt: PromptTemplate) {
  console.log('Edit prompt:', prompt)
}

function showSaveStatus(type: string, message: string) {
  saveStatus.value = { type, message }
  setTimeout(() => { saveStatus.value = null }, 3000)
}

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

@keyframes spin {
  to { transform: rotate(360deg); }
}

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
  from { opacity: 0; transform: translateY(1rem); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
