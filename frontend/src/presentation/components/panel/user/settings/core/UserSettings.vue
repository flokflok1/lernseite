<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUserStore } from '@/application/stores/modules/core/auth.store'
import SettingsProfileTab from './SettingsProfileTab.vue'
import SettingsSubscriptionTab from './SettingsSubscriptionTab.vue'
import SettingsNotificationsTab from './SettingsNotificationsTab.vue'
import SettingsSecurityTab from './SettingsSecurityTab.vue'

const userStore = useUserStore()
const currentUser = computed(() => userStore.currentUser)

const activeTab = ref<'profile' | 'subscription' | 'notifications' | 'security'>('profile')
</script>

<template>
  <div class="settings">
    <!-- Settings Tabs -->
    <div class="settings__tabs">
      <button
        :class="['settings__tab', { 'settings__tab--active': activeTab === 'profile' }]"
        @click="activeTab = 'profile'"
      >
        {{ $t('settings.profile') }}
      </button>
      <button
        :class="['settings__tab', { 'settings__tab--active': activeTab === 'subscription' }]"
        @click="activeTab = 'subscription'"
      >
        {{ $t('settings.subscription') }}
      </button>
      <button
        :class="['settings__tab', { 'settings__tab--active': activeTab === 'notifications' }]"
        @click="activeTab = 'notifications'"
      >
        {{ $t('settings.notifications') }}
      </button>
      <button
        :class="['settings__tab', { 'settings__tab--active': activeTab === 'security' }]"
        @click="activeTab = 'security'"
      >
        {{ $t('settings.security') }}
      </button>
    </div>

    <!-- Tab Content -->
    <SettingsProfileTab
      v-if="activeTab === 'profile'"
      :initial-name="currentUser?.name || ''"
      :initial-email="currentUser?.email || ''"
    />

    <SettingsSubscriptionTab v-if="activeTab === 'subscription'" />

    <SettingsNotificationsTab v-if="activeTab === 'notifications'" />

    <SettingsSecurityTab v-if="activeTab === 'security'" />
  </div>
</template>

<style scoped lang="scss">
.settings {
  &__tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid var(--color-border);
    padding-bottom: 1rem;
    overflow-x: auto;
  }

  &__tab {
    padding: 0.75rem 1.5rem;
    background: none;
    border: none;
    color: var(--color-text-secondary);
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 500;
    transition: all 0.2s ease-in-out;
    white-space: nowrap;

    &:hover {
      color: var(--color-text-primary);
    }

    &--active {
      color: var(--color-primary);
      border-bottom: 2px solid var(--color-primary);
    }
  }
}
</style>
