<template>
  <div>
    <h1 class="text-3xl font-bold text-[var(--color-text-primary)] mb-6">Mein Profil</h1>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <div v-else class="space-y-6">
      <!-- Sektion: Meine Daten -->
      <Card title="Meine Daten">
        <div v-if="!editing" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-[var(--color-text-secondary)]">Vorname</p>
              <p class="font-medium text-[var(--color-text-primary)]">{{ authStore.profile?.first_name }}</p>
            </div>
            <div>
              <p class="text-sm text-[var(--color-text-secondary)]">Nachname</p>
              <p class="font-medium text-[var(--color-text-primary)]">{{ authStore.profile?.last_name }}</p>
            </div>
          </div>

          <div>
            <p class="text-sm text-[var(--color-text-secondary)]">E-Mail</p>
            <p class="font-medium text-[var(--color-text-primary)]">{{ authStore.profile?.email }}</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-[var(--color-text-secondary)]">Rolle</p>
              <span class="px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded">
                {{ roleLabel }}
              </span>
            </div>
            <div v-if="authStore.profile?.organisation_name">
              <p class="text-sm text-[var(--color-text-secondary)]">Organisation</p>
              <p class="font-medium text-[var(--color-text-primary)]">{{ authStore.profile.organisation_name }}</p>
            </div>
          </div>

          <div v-if="updateSuccess" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            Profil erfolgreich aktualisiert!
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
              label="Vorname"
              required
            />
            <Input
              v-model="editForm.last_name"
              label="Nachname"
              required
            />
          </div>

          <Input
            v-model="editForm.email"
            type="email"
            label="E-Mail"
            required
          />

          <div v-if="updateError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {{ updateError }}
          </div>

          <div class="flex gap-3">
            <Button type="submit" variant="primary" :loading="updating">
              Speichern
            </Button>
            <Button type="button" variant="outline" @click="cancelEdit">
              Abbrechen
            </Button>
          </div>
        </form>

        <template #footer v-if="!editing">
          <Button variant="primary" @click="startEdit">
            Bearbeiten
          </Button>
        </template>
      </Card>

      <!-- Sektion: Sicherheit -->
      <Card title="Sicherheit">
        <div v-if="!changingPassword" class="text-sm text-[var(--color-text-secondary)]">
          <p>Ändere dein Passwort, um dein Konto zu schützen.</p>
        </div>

        <!-- Password Change Form -->
        <form v-else @submit.prevent="submitPasswordChange" class="space-y-4">
          <Input
            v-model="passwordForm.current_password"
            type="password"
            label="Aktuelles Passwort"
            required
          />

          <Input
            v-model="passwordForm.new_password"
            type="password"
            label="Neues Passwort"
            required
            hint="Min. 8 Zeichen, 1 Großbuchstabe, 1 Zahl"
          />

          <Input
            v-model="passwordForm.confirm_password"
            type="password"
            label="Neues Passwort wiederholen"
            required
          />

          <div v-if="passwordSuccess" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            Passwort erfolgreich geändert!
          </div>

          <div v-if="passwordError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {{ passwordError }}
          </div>

          <div class="flex gap-3">
            <Button type="submit" variant="primary" :loading="changingPasswordLoading">
              Passwort ändern
            </Button>
            <Button type="button" variant="outline" @click="cancelPasswordChange">
              Abbrechen
            </Button>
          </div>
        </form>

        <template #footer v-if="!changingPassword">
          <Button variant="outline" @click="startPasswordChange">
            Passwort ändern
          </Button>
        </template>
      </Card>

      <!-- Sektion: Plan & Tokens (read-only) -->
      <Card title="Plan & Tokens">
        <div class="space-y-4">
          <!-- Subscription Info -->
          <div class="border-b border-[var(--color-border)] pb-4">
            <h3 class="text-sm font-medium text-[var(--color-text-primary)] mb-3">Abo-Informationen</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-[var(--color-text-secondary)]">Plan</p>
                <p class="font-bold text-lg capitalize">{{ subscription?.plan || 'Free' }}</p>
                <span
                  class="px-2 py-1 text-xs font-medium rounded mt-1 inline-block"
                  :class="subscriptionStatusClass"
                >
                  {{ subscriptionStatusLabel }}
                </span>
              </div>
              <div v-if="subscription?.status !== 'none'">
                <p class="text-sm text-[var(--color-text-secondary)]">Quelle</p>
                <p class="font-medium text-[var(--color-text-primary)]">{{ subscriptionSourceLabel }}</p>
              </div>
            </div>

            <div v-if="subscription?.expires_at" class="mt-3">
              <p class="text-sm text-[var(--color-text-secondary)]">Läuft ab am</p>
              <p class="font-medium text-[var(--color-text-primary)]">{{ formatDate(subscription.expires_at) }}</p>
            </div>

            <div v-if="subscription?.auto_renew" class="mt-3 bg-blue-50 border border-blue-200 p-3 rounded">
              <p class="text-sm text-blue-800">
                Automatische Verlängerung ist aktiv
              </p>
            </div>
          </div>

          <!-- Token Balance -->
          <div>
            <h3 class="text-sm font-medium text-[var(--color-text-primary)] mb-3">Token-Guthaben</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p class="text-sm text-[var(--color-text-secondary)]">Verfügbar</p>
                <p class="text-2xl font-bold" :class="tokenBalanceClass">
                  {{ tokenBalance?.available?.toLocaleString() || 0 }}
                </p>
              </div>
              <div>
                <p class="text-sm text-[var(--color-text-secondary)]">Gesamt erhalten</p>
                <p class="font-medium text-[var(--color-text-primary)]">
                  {{ (tokenBalance?.total_purchased || 0) + (tokenBalance?.total_granted || 0) | 0 }}
                </p>
              </div>
              <div>
                <p class="text-sm text-[var(--color-text-secondary)]">Verbraucht</p>
                <p class="font-medium text-[var(--color-text-primary)]">{{ tokenBalance?.total_consumed?.toLocaleString() || 0 }}</p>
              </div>
            </div>

            <div v-if="tokenBalance?.monthly_grant" class="mt-3 bg-green-50 border border-green-200 p-3 rounded">
              <p class="text-sm text-green-800">
                Du erhältst {{ tokenBalance.monthly_grant.toLocaleString() }} Tokens pro Monat
              </p>
            </div>
          </div>
        </div>

        <template #footer>
          <router-link to="/dashboard" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
            Zum Dashboard →
          </router-link>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth.store'
import * as profileApi from '@/api/profile.api'
import * as tokensApi from '@/api/tokens.api'
import * as subscriptionsApi from '@/api/subscriptions.api'
import type { UpdateProfileRequest, ChangePasswordRequest } from '@/api/profile.api'
import type { TokenBalanceResponse } from '@/api/tokens.api'
import type { SubscriptionResponse } from '@/api/subscriptions.api'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'

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
  const roleMap: Record<string, string> = {
    user: 'User',
    premium: 'Premium',
    creator: 'Creator',
    teacher: 'Lehrer',
    school_admin: 'Schule',
    company_admin: 'Unternehmen',
    admin: 'Admin'
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
  if (!subscription.value) return 'Kein Abo'

  const statusMap: Record<string, string> = {
    active: 'Aktiv',
    trial: 'Testversion',
    cancelled: 'Gekündigt',
    expired: 'Abgelaufen',
    none: 'Kein Abo'
  }
  return statusMap[subscription.value.status] || subscription.value.status
})

const subscriptionSourceLabel = computed(() => {
  if (!subscription.value) return '-'

  const sourceMap: Record<string, string> = {
    user: 'Persönliches Abo',
    organisation: 'Organisations-Abo',
    default: 'Standard (Free)'
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
    updateError.value = err.response?.data?.message || 'Profil-Aktualisierung fehlgeschlagen'
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
    passwordError.value = 'Passwörter stimmen nicht überein'
    return
  }

  if (passwordForm.new_password.length < 8) {
    passwordError.value = 'Passwort muss mindestens 8 Zeichen lang sein'
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
    passwordError.value = err.response?.data?.message || 'Passwort-Änderung fehlgeschlagen'
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
