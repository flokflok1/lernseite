<template>
  <div>
    <h1 class="text-3xl font-bold text-[var(--color-text-primary)] mb-6">{{ t('profile.title') }}</h1>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <div v-else class="space-y-6">
      <!-- Sektion: Meine Daten -->
      <Card :title="t('profile.my_data')">
        <div v-if="!editing" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-[var(--color-text-secondary)]">{{ t('auth.first_name') }}</p>
              <p class="font-medium text-[var(--color-text-primary)]">{{ authStore.profile?.first_name }}</p>
            </div>
            <div>
              <p class="text-sm text-[var(--color-text-secondary)]">{{ t('auth.last_name') }}</p>
              <p class="font-medium text-[var(--color-text-primary)]">{{ authStore.profile?.last_name }}</p>
            </div>
          </div>

          <div>
            <p class="text-sm text-[var(--color-text-secondary)]">{{ t('auth.email') }}</p>
            <p class="font-medium text-[var(--color-text-primary)]">{{ authStore.profile?.email }}</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-[var(--color-text-secondary)]">{{ t('profile.role') }}</p>
              <span class="px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded">
                {{ roleLabel }}
              </span>
            </div>
            <div v-if="authStore.profile?.organisation_name">
              <p class="text-sm text-[var(--color-text-secondary)]">{{ t('profile.organisation') }}</p>
              <p class="font-medium text-[var(--color-text-primary)]">{{ authStore.profile.organisation_name }}</p>
            </div>
          </div>

          <div v-if="updateSuccess" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {{ t('profile.update_success') }}
          </div>

          <div v-if="updateError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {{ updateError }}
          </div>
        </div>

        <!-- Edit Form -->
        <form v-else @submit.prevent="saveProfile" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              v-model="editForm.first_name"
              :label="t('auth.first_name')"
              required
            />
            <Input
              v-model="editForm.last_name"
              :label="t('auth.last_name')"
              required
            />
          </div>

          <Input
            v-model="editForm.email"
            type="email"
            :label="t('auth.email')"
            required
          />

          <div v-if="updateError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {{ updateError }}
          </div>

          <div class="flex gap-3">
            <Button type="submit" variant="primary" :loading="updating">
              {{ t('common.save') }}
            </Button>
            <Button type="button" variant="outline" @click="cancelEdit">
              {{ t('common.cancel') }}
            </Button>
          </div>
        </form>

        <template #footer v-if="!editing">
          <Button variant="primary" @click="startEdit">
            {{ t('profile.edit') }}
          </Button>
        </template>
      </Card>

      <!-- Sektion: Sicherheit -->
      <Card :title="t('profile.security')">
        <div v-if="!changingPassword" class="text-sm text-[var(--color-text-secondary)]">
          <p>{{ t('profile.security_hint') }}</p>
        </div>

        <!-- Password Change Form -->
        <form v-else @submit.prevent="submitPasswordChange" class="space-y-4">
          <Input
            v-model="passwordForm.current_password"
            type="password"
            :label="t('profile.current_password')"
            required
          />

          <Input
            v-model="passwordForm.new_password"
            type="password"
            :label="t('profile.new_password')"
            required
            :hint="t('auth.password_hint')"
          />

          <Input
            v-model="passwordForm.confirm_password"
            type="password"
            :label="t('profile.confirm_new_password')"
            required
          />

          <div v-if="passwordSuccess" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {{ t('profile.password_success') }}
          </div>

          <div v-if="passwordError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {{ passwordError }}
          </div>

          <div class="flex gap-3">
            <Button type="submit" variant="primary" :loading="changingPasswordLoading">
              {{ t('profile.change_password') }}
            </Button>
            <Button type="button" variant="outline" @click="cancelPasswordChange">
              {{ t('common.cancel') }}
            </Button>
          </div>
        </form>

        <template #footer v-if="!changingPassword">
          <Button variant="outline" @click="startPasswordChange">
            {{ t('profile.change_password') }}
          </Button>
        </template>
      </Card>

      <!-- Sektion: Plan & Tokens (read-only) -->
      <Card :title="t('profile.plan_tokens')">
        <div class="space-y-4">
          <!-- Subscription Info -->
          <div class="border-b border-[var(--color-border)] pb-4">
            <h3 class="text-sm font-medium text-[var(--color-text-primary)] mb-3">{{ t('profile.subscription_info') }}</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-[var(--color-text-secondary)]">{{ t('profile.plan') }}</p>
                <p class="font-bold text-lg capitalize">{{ subscription?.plan || 'Free' }}</p>
                <span
                  class="px-2 py-1 text-xs font-medium rounded mt-1 inline-block"
                  :class="subscriptionStatusClass"
                >
                  {{ subscriptionStatusLabel }}
                </span>
              </div>
              <div v-if="subscription?.status !== 'none'">
                <p class="text-sm text-[var(--color-text-secondary)]">{{ t('profile.source') }}</p>
                <p class="font-medium text-[var(--color-text-primary)]">{{ subscriptionSourceLabel }}</p>
              </div>
            </div>

            <div v-if="subscription?.expires_at" class="mt-3">
              <p class="text-sm text-[var(--color-text-secondary)]">{{ t('profile.expires_at') }}</p>
              <p class="font-medium text-[var(--color-text-primary)]">{{ formatDate(subscription.expires_at) }}</p>
            </div>

            <div v-if="subscription?.auto_renew" class="mt-3 bg-blue-50 border border-blue-200 p-3 rounded">
              <p class="text-sm text-blue-800">
                {{ t('profile.auto_renew_active') }}
              </p>
            </div>
          </div>

          <!-- Token Balance -->
          <div>
            <h3 class="text-sm font-medium text-[var(--color-text-primary)] mb-3">{{ t('profile.token_balance') }}</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p class="text-sm text-[var(--color-text-secondary)]">{{ t('profile.available') }}</p>
                <p class="text-2xl font-bold" :class="tokenBalanceClass">
                  {{ tokenBalance?.available?.toLocaleString() || 0 }}
                </p>
              </div>
              <div>
                <p class="text-sm text-[var(--color-text-secondary)]">{{ t('profile.total_received') }}</p>
                <p class="font-medium text-[var(--color-text-primary)]">
                  {{ (tokenBalance?.total_purchased || 0) + (tokenBalance?.total_granted || 0) | 0 }}
                </p>
              </div>
              <div>
                <p class="text-sm text-[var(--color-text-secondary)]">{{ t('profile.consumed') }}</p>
                <p class="font-medium text-[var(--color-text-primary)]">{{ tokenBalance?.total_consumed?.toLocaleString() || 0 }}</p>
              </div>
            </div>

            <div v-if="tokenBalance?.monthly_grant" class="mt-3 bg-green-50 border border-green-200 p-3 rounded">
              <p class="text-sm text-green-800">
                {{ t('profile.monthly_grant', { amount: tokenBalance.monthly_grant.toLocaleString() }) }}
              </p>
            </div>
          </div>
        </div>

        <template #footer>
          <router-link to="/dashboard" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
            {{ t('profile.to_dashboard') }} →
          </router-link>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/application/stores/auth.store'
import * as profileApi from '@/infrastructure/api/profile.api'
import * as tokensApi from '@/infrastructure/api/tokens.api'
import * as subscriptionsApi from '@/infrastructure/api/subscriptions.api'
import type { UpdateProfileRequest, ChangePasswordRequest } from '@/infrastructure/api/profile.api'
import type { TokenBalanceResponse } from '@/infrastructure/api/tokens.api'
import type { SubscriptionResponse } from '@/infrastructure/api/subscriptions.api'
import Card from '@/presentation/components/base/Card.vue'
import Button from '@/presentation/components/base/Button.vue'
import Input from '@/presentation/components/base/Input.vue'

const { t, locale } = useI18n()
const authStore = useAuthStore()

const loading = ref(true)
const editing = ref(false)
const updating = ref(false)
const updateSuccess = ref(false)
const updateError = ref('')

const changingPassword = ref(false)
const changingPasswordLoading = ref(false)
const passwordSuccess = ref(false)
const passwordError = ref('')

const tokenBalance = ref<TokenBalanceResponse | null>(null)
const subscription = ref<SubscriptionResponse | null>(null)

const editForm = reactive<UpdateProfileRequest>({
  first_name: '',
  last_name: '',
  email: ''
})

const passwordForm = reactive<ChangePasswordRequest>({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const roleLabel = computed(() => {
  void locale.value // Trigger reactivity on language change
  const roleMap: Record<string, string> = {
    user: t('profile.role_user'),
    premium: t('profile.role_premium'),
    creator: t('profile.role_creator'),
    teacher: t('profile.role_teacher'),
    school_admin: t('profile.role_school'),
    company_admin: t('profile.role_company'),
    admin: t('profile.role_admin')
  }
  return roleMap[authStore.userRole] || authStore.userRole
})

const subscriptionStatusClass = computed(() => {
  if (!subscription.value) return 'bg-gray-100 text-gray-800'

  switch (subscription.value.status) {
    case 'active':
      return 'bg-green-100 text-green-800'
    case 'trial':
      return 'bg-blue-100 text-blue-800'
    case 'cancelled':
      return 'bg-yellow-100 text-yellow-800'
    case 'expired':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
})

const subscriptionStatusLabel = computed(() => {
  void locale.value // Trigger reactivity on language change
  if (!subscription.value) return t('profile.status_none')

  const statusMap: Record<string, string> = {
    active: t('profile.status_active'),
    trial: t('profile.status_trial'),
    cancelled: t('profile.status_cancelled'),
    expired: t('profile.status_expired'),
    none: t('profile.status_none')
  }
  return statusMap[subscription.value.status] || subscription.value.status
})

const subscriptionSourceLabel = computed(() => {
  void locale.value // Trigger reactivity on language change
  if (!subscription.value) return '-'

  const sourceMap: Record<string, string> = {
    user: t('profile.source_user'),
    organisation: t('profile.source_organisation'),
    default: t('profile.source_default')
  }
  return sourceMap[subscription.value.source] || subscription.value.source
})

const tokenBalanceClass = computed(() => {
  if (!tokenBalance.value) return 'text-gray-900'

  const available = tokenBalance.value.available
  if (available < 1000) return 'text-red-600'
  if (available < 5000) return 'text-yellow-600'
  return 'text-green-600'
})

const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('de-DE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const startEdit = () => {
  if (authStore.profile) {
    editForm.first_name = authStore.profile.first_name
    editForm.last_name = authStore.profile.last_name
    editForm.email = authStore.profile.email
  }
  editing.value = true
  updateSuccess.value = false
  updateError.value = ''
}

const cancelEdit = () => {
  editing.value = false
  updateError.value = ''
}

const saveProfile = async () => {
  updating.value = true
  updateError.value = ''
  updateSuccess.value = false

  try {
    await profileApi.updateProfile(editForm)
    await authStore.loadProfile()

    updateSuccess.value = true
    editing.value = false

    // Clear success message after 3 seconds
    setTimeout(() => {
      updateSuccess.value = false
    }, 3000)

  } catch (err: any) {
    updateError.value = err.response?.data?.message || t('profile.update_failed')
  } finally {
    updating.value = false
  }
}

const startPasswordChange = () => {
  changingPassword.value = true
  passwordSuccess.value = false
  passwordError.value = ''
  passwordForm.current_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
}

const cancelPasswordChange = () => {
  changingPassword.value = false
  passwordError.value = ''
}

const submitPasswordChange = async () => {
  passwordError.value = ''
  passwordSuccess.value = false

  // Client-side validation
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordError.value = t('errors.password_mismatch')
    return
  }

  if (passwordForm.new_password.length < 8) {
    passwordError.value = t('errors.password_min_length')
    return
  }

  changingPasswordLoading.value = true

  try {
    await profileApi.changePassword(passwordForm)

    passwordSuccess.value = true
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''

    // Clear form and close after 2 seconds
    setTimeout(() => {
      changingPassword.value = false
      passwordSuccess.value = false
    }, 2000)

  } catch (err: any) {
    passwordError.value = err.response?.data?.message || t('profile.password_failed')
  } finally {
    changingPasswordLoading.value = false
  }
}

const loadProfileData = async () => {
  loading.value = true

  try {
    // Load profile if not cached
    if (!authStore.profile) {
      await authStore.loadProfile()
    }

    // Load tokens and subscription in parallel
    const [tokensResponse, subscriptionResponse] = await Promise.allSettled([
      tokensApi.getMyTokens(),
      subscriptionsApi.getMySubscription()
    ])

    if (tokensResponse.status === 'fulfilled') {
      tokenBalance.value = tokensResponse.value
    }

    if (subscriptionResponse.status === 'fulfilled') {
      subscription.value = subscriptionResponse.value
    }

  } catch (err: any) {
    console.error('Failed to load profile data:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadProfileData()
})
</script>
