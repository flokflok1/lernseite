<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/application/stores/modules/core/auth.store'

const { t } = useI18n()
const userStore = useUserStore()

const currentUser = computed(() => userStore.currentUser)

const activeTab = ref<'profile' | 'subscription' | 'notifications' | 'security'>('profile')

// Profile form
const profileForm = ref({
  name: currentUser.value?.name || '',
  email: currentUser.value?.email || '',
  bio: '',
  avatar: null as File | null
})

const profileErrors = ref<Record<string, string>>({})

// Subscription info
const subscription = ref({
  tier: 'free' as 'free' | 'creator' | 'pro',
  nextBillingDate: '2024-03-01',
  autoRenew: true
})

const subscriptionOptions = computed(() => [
  {
    id: 'free',
    name: t('subscription.free'),
    price: t('subscription.priceFree'),
    features: [
      t('subscription.feature1'),
      t('subscription.feature2'),
      t('subscription.feature3')
    ]
  },
  {
    id: 'creator',
    name: t('subscription.creator'),
    price: '$9.99/mo',
    features: [
      t('subscription.feature1'),
      t('subscription.feature2'),
      t('subscription.feature3'),
      t('subscription.feature4')
    ]
  },
  {
    id: 'pro',
    name: t('subscription.pro'),
    price: '$19.99/mo',
    features: [
      t('subscription.feature1'),
      t('subscription.feature2'),
      t('subscription.feature3'),
      t('subscription.feature4'),
      t('subscription.feature5')
    ]
  }
])

// Notification settings
const notifications = ref({
  emailCourseUpdate: true,
  emailWeeklySummary: true,
  emailPromotions: false,
  emailCommunity: true,
  pushNotifications: true
})

// Security settings
const securitySettings = ref({
  twoFactorEnabled: false,
  lastPasswordChange: '2024-01-10',
  activeDevices: 3
})

const handleProfileSubmit = async () => {
  profileErrors.value = {}

  if (!profileForm.value.name) {
    profileErrors.value.name = t('validation.nameRequired')
  }

  if (!profileForm.value.email) {
    profileErrors.value.email = t('validation.emailRequired')
  }

  if (Object.keys(profileErrors.value).length === 0) {
    // Call API to update profile
    console.log('Updating profile:', profileForm.value)
    // alert(t('common.saved'))
  }
}

const handleSubscriptionChange = (tier: string) => {
  subscription.value.tier = tier as 'free' | 'creator' | 'pro'
  console.log('Changing subscription to:', tier)
}

const handleLogout = () => {
  if (confirm(t('settings.confirmLogout'))) {
    userStore.logout()
    window.location.href = '/login'
  }
}

const handleDeleteAccount = () => {
  if (
    confirm(t('settings.confirmDeleteAccount')) &&
    confirm(t('settings.confirmDeleteAccountWarning'))
  ) {
    console.log('Deleting account...')
    // Call API to delete account
  }
}
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

    <!-- Profile Tab -->
    <div v-if="activeTab === 'profile'" class="settings__content">
      <h2>{{ $t('settings.profileSettings') }}</h2>

      <form class="form" @submit.prevent="handleProfileSubmit">
        <div class="form__group">
          <label for="name" class="form__label">{{ $t('form.name') }}</label>
          <input
            id="name"
            v-model="profileForm.name"
            type="text"
            class="form__input"
            :class="{ 'form__input--error': profileErrors.name }"
          />
          <span v-if="profileErrors.name" class="form__error">{{ profileErrors.name }}</span>
        </div>

        <div class="form__group">
          <label for="email" class="form__label">{{ $t('form.email') }}</label>
          <input
            id="email"
            v-model="profileForm.email"
            type="email"
            class="form__input"
            :class="{ 'form__input--error': profileErrors.email }"
          />
          <span v-if="profileErrors.email" class="form__error">{{ profileErrors.email }}</span>
        </div>

        <div class="form__group">
          <label for="bio" class="form__label">{{ $t('form.bio') }}</label>
          <textarea
            id="bio"
            v-model="profileForm.bio"
            rows="4"
            class="form__textarea"
            :placeholder="$t('form.bioPlaceholder')"
          ></textarea>
        </div>

        <div class="form__group">
          <label for="avatar" class="form__label">{{ $t('form.profilePicture') }}</label>
          <div class="file-upload">
            <input
              id="avatar"
              type="file"
              accept="image/*"
              class="file-upload__input"
              @change="profileForm.avatar = $event.target.files?.[0] || null"
            />
            <label for="avatar" class="file-upload__label">
              {{ profileForm.avatar ? profileForm.avatar.name : $t('form.chooseFile') }}
            </label>
          </div>
        </div>

        <div class="form__actions">
          <button type="submit" class="btn btn--primary">{{ $t('common.save') }}</button>
        </div>
      </form>
    </div>

    <!-- Subscription Tab -->
    <div v-if="activeTab === 'subscription'" class="settings__content">
      <h2>{{ $t('settings.subscriptionSettings') }}</h2>

      <div class="subscription-info">
        <p>
          {{ $t('settings.currentPlan') }}:
          <strong>{{ subscription.tier.toUpperCase() }}</strong>
        </p>
        <p>
          {{ $t('settings.nextBillingDate') }}:
          <strong>{{ new Date(subscription.nextBillingDate).toLocaleDateString() }}</strong>
        </p>
      </div>

      <div class="subscription-plans">
        <div
          v-for="plan in subscriptionOptions"
          :key="plan.id"
          :class="['plan-card', { 'plan-card--active': subscription.tier === plan.id }]"
        >
          <h3>{{ plan.name }}</h3>
          <p class="plan-card__price">{{ plan.price }}</p>

          <ul class="plan-card__features">
            <li v-for="(feature, idx) in plan.features" :key="idx">✓ {{ feature }}</li>
          </ul>

          <button
            :disabled="subscription.tier === plan.id"
            class="btn btn--primary"
            @click="handleSubscriptionChange(plan.id)"
          >
            {{
              subscription.tier === plan.id ? $t('subscription.current') : $t('subscription.upgrade')
            }}
          </button>
        </div>
      </div>

      <div class="form__group">
        <label>
          <input v-model="subscription.autoRenew" type="checkbox" />
          {{ $t('settings.autoRenew') }}
        </label>
      </div>
    </div>

    <!-- Notifications Tab -->
    <div v-if="activeTab === 'notifications'" class="settings__content">
      <h2>{{ $t('settings.notificationSettings') }}</h2>

      <div class="notifications-list">
        <div class="notification-item">
          <input
            id="email-course-update"
            v-model="notifications.emailCourseUpdate"
            type="checkbox"
          />
          <label for="email-course-update">
            <strong>{{ $t('notifications.courseUpdates') }}</strong>
            <p>{{ $t('notifications.courseUpdatesDesc') }}</p>
          </label>
        </div>

        <div class="notification-item">
          <input
            id="email-weekly-summary"
            v-model="notifications.emailWeeklySummary"
            type="checkbox"
          />
          <label for="email-weekly-summary">
            <strong>{{ $t('notifications.weeklySummary') }}</strong>
            <p>{{ $t('notifications.weeklySummaryDesc') }}</p>
          </label>
        </div>

        <div class="notification-item">
          <input
            id="email-promotions"
            v-model="notifications.emailPromotions"
            type="checkbox"
          />
          <label for="email-promotions">
            <strong>{{ $t('notifications.promotions') }}</strong>
            <p>{{ $t('notifications.promotionsDesc') }}</p>
          </label>
        </div>

        <div class="notification-item">
          <input
            id="email-community"
            v-model="notifications.emailCommunity"
            type="checkbox"
          />
          <label for="email-community">
            <strong>{{ $t('notifications.communityUpdates') }}</strong>
            <p>{{ $t('notifications.communityUpdatesDesc') }}</p>
          </label>
        </div>

        <div class="notification-item">
          <input
            id="push-notifications"
            v-model="notifications.pushNotifications"
            type="checkbox"
          />
          <label for="push-notifications">
            <strong>{{ $t('notifications.pushNotifications') }}</strong>
            <p>{{ $t('notifications.pushNotificationsDesc') }}</p>
          </label>
        </div>
      </div>
    </div>

    <!-- Security Tab -->
    <div v-if="activeTab === 'security'" class="settings__content">
      <h2>{{ $t('settings.securitySettings') }}</h2>

      <div class="security-info">
        <div class="security-item">
          <h3>{{ $t('settings.twoFactorAuth') }}</h3>
          <p v-if="securitySettings.twoFactorEnabled" class="status status--enabled">
            ✓ {{ $t('settings.enabled') }}
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

  &__content {
    h2 {
      font-size: 1.5rem;
      font-weight: 600;
      margin-bottom: 1.5rem;
      color: var(--color-text-primary);
    }
  }
}

.form {
  max-width: 600px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  &__group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  &__label {
    font-weight: 500;
    color: var(--color-text-primary);
    font-size: 0.95rem;
  }

  &__input,
  &__textarea {
    padding: 0.75rem 1rem;
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    font-size: 0.95rem;
    background: var(--color-background-primary);
    color: var(--color-text-primary);
    font-family: inherit;

    &:focus {
      outline: none;
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
    }

    &--error {
      border-color: var(--color-error);
    }
  }

  &__textarea {
    resize: vertical;
    min-height: 120px;
  }

  &__error {
    color: var(--color-error);
    font-size: 0.85rem;
  }

  &__actions {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
  }
}

.file-upload {
  position: relative;

  &__input {
    display: none;
  }

  &__label {
    display: block;
    padding: 1rem;
    border: 2px dashed var(--color-border);
    border-radius: 0.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    background: var(--color-background-secondary);

    &:hover {
      border-color: var(--color-primary);
      background: var(--color-background-primary);
    }
  }
}

.subscription-info {
  background: var(--color-background-secondary);
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 2rem;

  p {
    margin: 0.5rem 0;
    color: var(--color-text-primary);
  }

  strong {
    color: var(--color-primary);
  }
}

.subscription-plans {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.plan-card {
  padding: 1.5rem;
  border: 2px solid var(--color-border);
  border-radius: 0.5rem;
  transition: all 0.2s ease-in-out;

  &:hover {
    border-color: var(--color-primary);
  }

  &--active {
    border-color: var(--color-primary);
    background: rgba(var(--color-primary-rgb), 0.05);
  }

  h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 0.5rem 0;
  }

  &__price {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--color-primary);
    margin: 0 0 1rem 0;
  }

  &__features {
    list-style: none;
    padding: 0;
    margin: 0 0 1.5rem 0;

    li {
      padding: 0.5rem 0;
      color: var(--color-text-secondary);
      font-size: 0.9rem;
    }
  }
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.notification-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;

  input[type='checkbox'] {
    margin-top: 0.25rem;
    cursor: pointer;
  }

  label {
    cursor: pointer;
    flex: 1;

    strong {
      display: block;
      color: var(--color-text-primary);
      margin-bottom: 0.25rem;
    }

    p {
      margin: 0;
      color: var(--color-text-secondary);
      font-size: 0.85rem;
    }
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

  &--primary {
    background: var(--color-primary);
    color: white;

    &:hover:not(:disabled) {
      background: var(--color-primary-hover);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

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
