/**
 * useAIProfileManager Composable
 *
 * Manages AI profile CRUD operations:
 * - Load, create, update, delete profiles
 * - Query models by category and provider
 *
 * Extracted from useAISettings to keep files under 500 LOC.
 */

import type { Ref } from 'vue'

import type { AIProfile, AISettings } from './useAISettings'

export interface ProfileManagerDeps {
  settings: Ref<AISettings>
  isLoading: Ref<boolean>
  error: Ref<string | null>
  profilesLoading: Ref<boolean>
}

export function useAIProfileManager(deps: ProfileManagerDeps) {
  const { settings, isLoading, error, profilesLoading } = deps

  /**
   * Load all AI profiles from API
   */
  async function loadProfiles(): Promise<void> {
    profilesLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await aiSettingsService.getProfiles()
      // settings.value.profiles = response.data

      console.log('Loading AI profiles...')
      settings.value.profiles = []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load profiles'
      console.error('Error loading profiles:', err)
    } finally {
      profilesLoading.value = false
    }
  }

  /**
   * Create new AI profile
   */
  async function createProfile(
    profile: Omit<AIProfile, 'id' | 'createdAt' | 'updatedAt'>
  ): Promise<AIProfile | null> {
    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await aiSettingsService.createProfile(profile)
      // settings.value.profiles.push(response.data)

      const newProfile: AIProfile = {
        id: `profile_${Date.now()}`,
        ...profile,
        createdAt: new Date(),
        updatedAt: new Date()
      }

      settings.value.profiles.push(newProfile)
      console.log('Profile created:', newProfile)
      return newProfile
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create profile'
      console.error('Error creating profile:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update existing AI profile
   */
  async function updateProfile(
    id: string,
    updates: Partial<AIProfile>
  ): Promise<AIProfile | null> {
    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      const index = settings.value.profiles.findIndex(p => p.id === id)
      if (index >= 0) {
        settings.value.profiles[index] = {
          ...settings.value.profiles[index],
          ...updates,
          updatedAt: new Date()
        }
        console.log('Profile updated:', settings.value.profiles[index])
        return settings.value.profiles[index]
      }

      throw new Error('Profile not found')
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update profile'
      console.error('Error updating profile:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete AI profile
   */
  async function deleteProfile(id: string): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      const index = settings.value.profiles.findIndex(p => p.id === id)
      if (index >= 0) {
        settings.value.profiles.splice(index, 1)
        console.log('Profile deleted:', id)
        return true
      }

      throw new Error('Profile not found')
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete profile'
      console.error('Error deleting profile:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Get models for specific category
   */
  function getModelsByCategory(category: string) {
    return settings.value.models.filter(m => m.category === category && m.isAvailable)
  }

  /**
   * Get all unique model categories
   */
  function getModelCategories(): string[] {
    const categories = new Set<string>()
    settings.value.models.forEach(m => {
      if (m.category) categories.add(m.category)
    })
    return Array.from(categories).sort()
  }

  /**
   * Get models for specific provider
   */
  function getModelsByProvider(provider: string) {
    return settings.value.models.filter(m => m.provider === provider && m.isAvailable)
  }

  return {
    loadProfiles,
    createProfile,
    updateProfile,
    deleteProfile,
    getModelsByCategory,
    getModelCategories,
    getModelsByProvider
  }
}
