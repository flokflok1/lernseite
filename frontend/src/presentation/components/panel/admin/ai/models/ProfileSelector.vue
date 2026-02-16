<!--
  ProfileSelector - Profile Selection Card
  Sub-component of SettingsTab
-->

<template>
  <div class="settings-card">
    <div class="card-header">
      <span class="card-icon">🎯</span>
      <span class="card-title">{{ $t('aiEditorSettings.applyProfile') }}</span>
    </div>
    <div class="profile-grid">
      <button
        v-for="profile in profiles"
        :key="profile.key"
        @click="$emit('apply', profile.key)"
        class="profile-item"
        :class="{ active: activeProfileKey === profile.key, default: profile.is_default }"
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
        {{ $t('aiEditorSettings.profileHint') }}
      </span>
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
  activeProfileKey?: string
}>()

defineEmits<{
  (e: 'apply', profileKey: string): void
}>()
</script>

<style scoped>
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

.card-icon { font-size: 1.25rem; }

.card-title {
  font-weight: 600;
  color: var(--color-text-primary);
  flex: 1;
}

.card-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

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

.profile-item:hover { border-color: var(--color-primary); }

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
</style>
