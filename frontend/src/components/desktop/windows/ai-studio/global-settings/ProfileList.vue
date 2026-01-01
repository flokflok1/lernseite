<!--
  ProfileList - List of AI model profiles

  Displays all profiles with selection and default indicator.
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
      <span v-if="profile.is_default" class="default-badge">Default</span>
    </div>

    <div v-if="!profiles.length" class="empty-list">
      Keine Profile vorhanden
    </div>
  </div>
</template>

<script setup lang="ts">
// Types
interface Profile {
  key: string
  name: string
  description?: string
  is_default: boolean
  [key: string]: any
}

// Props
defineProps<{
  profiles: Profile[]
  selectedKey?: string | null
}>()

// Emits
defineEmits<{
  (e: 'select', profile: Profile): void
}>()
</script>

<style scoped>
.profile-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 200px;
  max-height: 400px;
  overflow-y: auto;
  padding: 0.5rem;
  background: var(--color-surface);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

.profile-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s;
}

.profile-item:hover {
  background: var(--color-surface-secondary);
}

.profile-item.active {
  background: var(--color-primary-subtle);
  border: 1px solid var(--color-primary);
}

.profile-indicator {
  width: 4px;
  height: 24px;
  border-radius: 2px;
  background: var(--color-border);
}

.profile-indicator.default {
  background: var(--color-primary);
}

.profile-content {
  flex: 1;
  min-width: 0;
}

.profile-name {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.profile-key {
  display: block;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  font-family: monospace;
}

.default-badge {
  padding: 0.125rem 0.375rem;
  background: var(--color-primary);
  color: white;
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 500;
}

.empty-list {
  padding: 1.5rem;
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 0.8125rem;
}
</style>
