<!--
  ProfileList - Profile List Sidebar
  Sub-component of GlobalSettingsTab
-->

<template>
  <div class="profile-list">
    <div
      v-for="profile in profiles"
      :key="profile.key"
      class="profile-item"
      :class="{ active: selectedKey === profile.key }"
      @click="$emit('select', profile)"
    >
      <div class="profile-indicator" :class="{ default: profile.is_default }"></div>
      <div class="profile-content">
        <span class="profile-name">{{ profile.name }}</span>
        <span class="profile-key">{{ profile.key }}</span>
      </div>
      <span v-if="profile.is_default" class="default-badge">{{ $t('windows.aiEditorGlobalSettings.default') }}</span>
    </div>
    <div v-if="!profiles.length" class="empty-list">
      {{ $t('windows.aiEditorGlobalSettings.noProfiles') }}
    </div>
  </div>
</template>

<script setup lang="ts">
interface Profile {
  key: string
  name: string
  description?: string
  is_default: boolean
}

defineProps<{
  profiles: Profile[]
  selectedKey: string | null
}>()

defineEmits<{
  (e: 'select', profile: Profile): void
}>()
</script>

<style scoped>
.profile-list { border-right: 1px solid var(--color-border); overflow-y: auto; max-height: 320px; }
.profile-item { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.75rem; cursor: pointer; border-bottom: 1px solid var(--color-border); transition: background 0.15s; }
.profile-item:hover { background: var(--color-surface-secondary); }
.profile-item.active { background: var(--color-primary-subtle); }
.profile-indicator { width: 0.5rem; height: 0.5rem; border-radius: 50%; background: var(--color-border); }
.profile-indicator.default { background: var(--color-primary); }
.profile-content { flex: 1; min-width: 0; }
.profile-name { display: block; font-weight: 500; color: var(--color-text-primary); font-size: 0.8125rem; }
.profile-key { display: block; font-size: 0.625rem; color: var(--color-text-tertiary); font-family: ui-monospace, monospace; }
.default-badge { padding: 0.125rem 0.375rem; background: rgba(34, 197, 94, 0.1); color: #22c55e; border-radius: 0.25rem; font-size: 0.625rem; font-weight: 600; }
.empty-list { padding: 2rem; text-align: center; color: var(--color-text-tertiary); font-size: 0.875rem; }
</style>
