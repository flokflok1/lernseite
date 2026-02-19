<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/application/stores/modules/core/auth.store'

const { t } = useI18n()
const userStore = useUserStore()

const securitySettings = ref({
  twoFactorEnabled: false,
  lastPasswordChange: '2024-01-10',
  activeDevices: 3
})

function handleLogout(): void {
  if (confirm(t('settings.confirmLogout'))) {
    userStore.logout()
    window.location.href = '/login'
  }
}

function handleDeleteAccount(): void {
  if (
    confirm(t('settings.confirmDeleteAccount')) &&
    confirm(t('settings.confirmDeleteAccountWarning'))
  ) {
    console.log('Deleting account...')
  }
}
</script>

<template>
  <div class="settings__content">
    <h2>{{ $t('settings.securitySettings') }}</h2>

    <div class="security-info">
      <div class="security-item">
        <h3>{{ $t('settings.twoFactorAuth') }}</h3>
        <p v-if="securitySettings.twoFactorEnabled" class="status status--enabled">
          &#x2713; {{ $t('settings.enabled') }}
        </p>
        <p v-else class="status status--disabled">{{ $t('settings.disabled') }}</p>
        <button class="btn btn--secondary">
          {{ securitySettings.twoFactorEnabled ? $t('settings.disable') : $t('settings.enable') }}
        </button>
      </div>

      <div class="security-item">
        <h3>{{ $t('settings.changePassword') }}</h3>
        <p class="meta">
          {{ $t('settings.lastChanged') }}:
          {{ new Date(securitySettings.lastPasswordChange).toLocaleDateString() }}
        </p>
        <button class="btn btn--secondary">{{ $t('settings.changePassword') }}</button>
      </div>

      <div class="security-item">
        <h3>{{ $t('settings.activeDevices') }}</h3>
        <p class="meta">{{ securitySettings.activeDevices }} {{ $t('settings.devicesActive') }}</p>
        <button class="btn btn--secondary">{{ $t('settings.manageDevices') }}</button>
      </div>
    </div>

    <hr class="divider" />

    <div class="danger-zone">
      <h3>{{ $t('settings.dangerZone') }}</h3>

      <button class="btn btn--danger" @click="handleLogout">
        {{ $t('settings.logout') }}
      </button>

      <button class="btn btn--danger" @click="handleDeleteAccount">
        {{ $t('settings.deleteAccount') }}
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.settings__content {
  h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--color-text-primary);
  }
}

.security-info {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.security-item {
  padding: 1.5rem;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;

  h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 0.75rem 0;
  }

  .meta {
    color: var(--color-text-secondary);
    font-size: 0.9rem;
    margin: 0 0 1rem 0;
  }
}

.status {
  margin: 0 0 1rem 0;
  font-weight: 500;

  &--enabled {
    color: var(--color-success);
  }

  &--disabled {
    color: var(--color-warning);
  }
}

.divider {
  margin: 2rem 0;
  border: none;
  border-top: 1px solid var(--color-border);
}

.danger-zone {
  padding: 1.5rem;
  background: rgba(var(--color-error-rgb), 0.05);
  border: 1px solid var(--color-error-light);
  border-radius: 0.5rem;

  h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-error);
    margin: 0 0 1rem 0;
  }

  .btn {
    display: block;
    width: 100%;
    margin-bottom: 0.75rem;

    &:last-child {
      margin-bottom: 0;
    }
  }
}

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;

  &--secondary {
    background: var(--color-secondary);
    color: white;

    &:hover {
      background: var(--color-secondary-hover);
    }
  }

  &--danger {
    background: var(--color-error);
    color: white;

    &:hover {
      background: var(--color-error-hover);
    }
  }
}
</style>
