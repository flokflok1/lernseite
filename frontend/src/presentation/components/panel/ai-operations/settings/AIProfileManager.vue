<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAISettings, type AIProfile } from './composables/useAISettings'
import AIProfileForm from './AIProfileForm.vue'

const { t } = useI18n()
const { settings, profilesLoading, loadProfiles, deleteProfile, getModelsByProvider } = useAISettings()

const showForm = ref(false)
const editingProfile = ref<AIProfile | null>(null)
const filterProvider = ref<string | 'all'>('all')
const searchQuery = ref('')

onMounted(() => {
  loadProfiles()
})

const handleCreateClick = () => {
  editingProfile.value = null
  showForm.value = true
}

const handleEditClick = (profile: AIProfile) => {
  editingProfile.value = profile
  showForm.value = true
}

const handleFormSubmit = () => {
  showForm.value = false
  editingProfile.value = null
  loadProfiles()
}

const handleDeleteClick = async (profileId: string) => {
  if (confirm('Are you sure you want to delete this profile?')) {
    await deleteProfile(profileId)
  }
}

const filteredProfiles = () => {
  return settings.value.profiles.filter(p => {
    if (filterProvider.value !== 'all' && p.provider !== filterProvider.value) return false
    if (searchQuery.value && !p.name.toLowerCase().includes(searchQuery.value.toLowerCase())) return false
    return true
  })
}

const getModelName = (modelId: string) => {
  const model = settings.value.models.find(m => m.id === modelId)
  return model?.name || modelId
}
</script>

<template>
  <div class="ai-profile-manager">
    <!-- Header -->
    <div class="mb-6 flex items-center justify-between">
      <h4 class="text-lg font-semibold text-[var(--color-text-primary)]">AI Profiles</h4>
      <button
        @click="handleCreateClick"
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
      >
        + New Profile
      </button>
    </div>

    <!-- Filters -->
    <div class="mb-4 flex gap-3">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search profiles..."
        class="flex-1 px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-secondary)]/50 focus:outline-none focus:border-blue-500"
      />
      <select
        v-model="filterProvider"
        class="px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:border-blue-500"
      >
        <option value="all">All Providers</option>
        <option value="claude">Claude</option>
        <option value="openai">OpenAI</option>
      </select>
    </div>

    <!-- Loading State -->
    <div v-if="profilesLoading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-3"></div>
      <p class="text-[var(--color-text-secondary)]">Loading profiles...</p>
    </div>

    <!-- Profiles Table -->
    <div v-else-if="filteredProfiles().length > 0" class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-[var(--color-surface)] border-b border-[var(--color-border)]">
          <tr>
            <th class="px-4 py-3 text-left text-sm font-semibold text-[var(--color-text-primary)]">
              Name
            </th>
            <th class="px-4 py-3 text-left text-sm font-semibold text-[var(--color-text-primary)]">
              Use Case
            </th>
            <th class="px-4 py-3 text-left text-sm font-semibold text-[var(--color-text-primary)]">
              Provider
            </th>
            <th class="px-4 py-3 text-left text-sm font-semibold text-[var(--color-text-primary)]">
              Model
            </th>
            <th class="px-4 py-3 text-left text-sm font-semibold text-[var(--color-text-primary)]">
              Status
            </th>
            <th class="px-4 py-3 text-right text-sm font-semibold text-[var(--color-text-primary)]">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="profile in filteredProfiles()" :key="profile.id" class="border-b border-[var(--color-border)] hover:bg-[var(--color-surface)]">
            <td class="px-4 py-3 text-[var(--color-text-primary)]">
              <p class="font-medium">{{ profile.name }}</p>
              <p v-if="profile.description" class="text-xs text-[var(--color-text-secondary)]">
                {{ profile.description }}
              </p>
            </td>
            <td class="px-4 py-3 text-[var(--color-text-secondary)]">
              <span class="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs font-medium">
                {{ profile.useCase }}
              </span>
            </td>
            <td class="px-4 py-3 text-[var(--color-text-secondary)]">
              <span :class="['px-2 py-1 rounded text-xs font-medium', profile.provider === 'claude' ? 'bg-purple-500/20 text-purple-300' : 'bg-green-500/20 text-green-300']">
                {{ profile.provider }}
              </span>
            </td>
            <td class="px-4 py-3 text-[var(--color-text-secondary)]">
              {{ getModelName(profile.modelId) }}
            </td>
            <td class="px-4 py-3">
              <span :class="['px-2 py-1 rounded text-xs font-medium', profile.isActive ? 'bg-green-500/20 text-green-300' : 'bg-gray-500/20 text-gray-300']">
                {{ profile.isActive ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <div class="flex gap-2 justify-end">
                <button
                  @click="() => handleEditClick(profile)"
                  class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium transition-colors"
                >
                  Edit
                </button>
                <button
                  @click="() => handleDeleteClick(profile.id)"
                  class="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-medium transition-colors"
                >
                  Delete
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8 bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]">
      <p class="text-[var(--color-text-secondary)]">No profiles found</p>
      <button
        @click="handleCreateClick"
        class="mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
      >
        Create First Profile
      </button>
    </div>

    <!-- Profile Form Modal -->
    <div v-if="showForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-[var(--color-surface)] rounded-lg shadow-lg max-w-2xl w-full mx-4">
        <AIProfileForm
          :profile="editingProfile"
          @submit="handleFormSubmit"
          @cancel="showForm = false"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-profile-manager {
  /* Inherits colors from theme variables */
}
</style>
