<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAISettings, type AIProfile } from './composables/useAISettings'

interface Props {
  profile?: AIProfile | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  submit: []
  cancel: []
}>()

const { t } = useI18n()
const { settings, isLoading, createProfile, updateProfile, getModelsByProvider, getModelCategories } = useAISettings()

const form = ref({
  name: '',
  useCase: '',
  description: '',
  provider: 'claude' as 'claude' | 'openai',
  modelId: '',
  isActive: true
})

const categoryFilter = ref<string | 'all'>('all')
const error = ref<string | null>(null)

onMounted(() => {
  if (props.profile) {
    form.value = {
      name: props.profile.name,
      useCase: props.profile.useCase,
      description: props.profile.description || '',
      provider: props.profile.provider as 'claude' | 'openai',
      modelId: props.profile.modelId,
      isActive: props.profile.isActive
    }
  }
})

const availableModels = computed(() => {
  const models = getModelsByProvider(form.value.provider)

  if (categoryFilter.value === 'all') {
    return models
  }

  return models.filter(m => m.category === categoryFilter.value)
})

const availableCategories = computed(() => {
  const _allCategories = getModelCategories()
  const providerModels = getModelsByProvider(form.value.provider)
  const providerCategories = new Set<string>()

  providerModels.forEach(m => {
    if (m.category) providerCategories.add(m.category)
  })

  return Array.from(providerCategories).sort()
})

const handleSubmit = async () => {
  // Validation
  if (!form.value.name.trim()) {
    error.value = 'Profile name is required'
    return
  }

  if (!form.value.useCase.trim()) {
    error.value = 'Use case is required'
    return
  }

  if (!form.value.modelId) {
    error.value = 'Model selection is required'
    return
  }

  error.value = null

  try {
    if (props.profile) {
      // Update existing profile
      await updateProfile(props.profile.id, {
        name: form.value.name,
        useCase: form.value.useCase,
        description: form.value.description,
        provider: form.value.provider,
        modelId: form.value.modelId,
        isActive: form.value.isActive
      })
    } else {
      // Create new profile
      await createProfile({
        name: form.value.name,
        useCase: form.value.useCase,
        description: form.value.description,
        provider: form.value.provider,
        modelId: form.value.modelId,
        isActive: form.value.isActive
      })
    }

    emit('submit')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to save profile'
  }
}

const getModelInfo = (modelId: string) => {
  return settings.value.models.find(m => m.id === modelId)
}
</script>

<template>
  <div class="ai-profile-form p-6">
    <!-- Header -->
    <h3 class="text-xl font-semibold text-[var(--color-text-primary)] mb-4">
      {{ profile ? 'Edit AI Profile' : 'Create New AI Profile' }}
    </h3>

    <!-- Error Message -->
    <div v-if="error" class="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300">
      {{ error }}
    </div>

    <!-- Form -->
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Profile Name -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
          Profile Name *
        </label>
        <input
          v-model="form.name"
          type="text"
          placeholder="e.g., TTS Generator, Content Creator"
          class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-secondary)]/50 focus:outline-none focus:border-blue-500"
        />
      </div>

      <!-- Use Case -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
          Use Case *
        </label>
        <input
          v-model="form.useCase"
          type="text"
          placeholder="e.g., Text-to-Speech, Content Generation, Tutoring"
          class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-secondary)]/50 focus:outline-none focus:border-blue-500"
        />
      </div>

      <!-- Description -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
          Description
        </label>
        <textarea
          v-model="form.description"
          placeholder="Optional description..."
          rows="2"
          class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-secondary)]/50 focus:outline-none focus:border-blue-500 resize-none"
        ></textarea>
      </div>

      <!-- Provider Selection -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
          Provider *
        </label>
        <div class="flex gap-4">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="form.provider"
              type="radio"
              value="claude"
              class="w-4 h-4"
            />
            <span class="text-[var(--color-text-primary)]">Claude (Anthropic)</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="form.provider"
              type="radio"
              value="openai"
              class="w-4 h-4"
            />
            <span class="text-[var(--color-text-primary)]">OpenAI (GPT)</span>
          </label>
        </div>
      </div>

      <!-- Category Filter -->
      <div v-if="availableCategories.length > 0">
        <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
          Model Category
        </label>
        <select
          v-model="categoryFilter"
          class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:border-blue-500"
        >
          <option value="all">All Categories</option>
          <option v-for="category in availableCategories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>

      <!-- Model Selection -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
          Model *
        </label>
        <select
          v-model="form.modelId"
          class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:border-blue-500"
        >
          <option value="">Select a model...</option>
          <option v-for="model in availableModels" :key="model.id" :value="model.id">
            {{ model.name }}
            <span v-if="model.category">({{ model.category }})</span>
          </option>
        </select>

        <!-- Model Info -->
        <div v-if="form.modelId" class="mt-2 p-3 bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]">
          <div class="text-sm text-[var(--color-text-secondary)]">
            <p v-if="getModelInfo(form.modelId)?.description" class="mb-2">
              {{ getModelInfo(form.modelId)?.description }}
            </p>
            <div v-if="getModelInfo(form.modelId)?.inputTokens || getModelInfo(form.modelId)?.outputTokens" class="text-xs">
              <span v-if="getModelInfo(form.modelId)?.inputTokens">
                Input: {{ getModelInfo(form.modelId)?.inputTokens?.toLocaleString() }}
              </span>
              <span v-if="getModelInfo(form.modelId)?.outputTokens" class="ml-3">
                Output: {{ getModelInfo(form.modelId)?.outputTokens }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Status -->
      <div>
        <label class="flex items-center gap-3 cursor-pointer">
          <input
            v-model="form.isActive"
            type="checkbox"
            class="w-4 h-4"
          />
          <span class="text-[var(--color-text-primary)]">Active Profile</span>
        </label>
      </div>

      <!-- Actions -->
      <div class="flex gap-3 pt-4">
        <button
          type="submit"
          :disabled="isLoading"
          class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
        >
          {{ isLoading ? 'Saving...' : (profile ? 'Update Profile' : 'Create Profile') }}
        </button>
        <button
          type="button"
          @click="() => emit('cancel')"
          class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.ai-profile-form {
  /* Inherits colors from theme variables */
}
</style>
