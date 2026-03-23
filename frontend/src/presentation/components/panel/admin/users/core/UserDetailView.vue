<template>
  <div class="panel-user-detail-page">
    <!-- Page Header -->
    <div class="mb-6 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <button
          @click="router.back()"
          class="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
          :title="$t('panel.userDetail.back')"
        >
          ← {{ $t('panel.userDetail.back') }}
        </button>
        <div>
          <h1 class="text-2xl font-bold text-[var(--color-text-primary)]">
            {{ user?.full_name }}
          </h1>
          <p class="text-sm text-[var(--color-text-secondary)]">{{ user?.email }}</p>
        </div>
      </div>
      <div class="flex gap-2">
        <button
          v-if="user?.is_active"
          @click="openBanModal"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          {{ $t('panel.userDetail.banUser') }}
        </button>
        <button
          v-else
          @click="openUnbanModal"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          {{ $t('panel.userDetail.unbanUser') }}
        </button>
        <button
          @click="openGrantTokensModal"
          class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          {{ $t('panel.userDetail.grantTokens') }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center p-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
      {{ error }}
    </div>

    <!-- User Detail Content -->
    <div v-else-if="user" class="space-y-6">
      <!-- User Info Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Basic Info -->
        <div class="bg-[var(--color-surface)] rounded-lg shadow-sm border border-[var(--color-border)] p-6">
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">{{ $t('panel.userDetail.basicInfo') }}</h3>
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-[var(--color-text-secondary)]">{{ $t('panel.userDetail.userId') }}</dt>
              <dd class="text-sm text-[var(--color-text-primary)] font-mono">{{ user.user_id }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-[var(--color-text-secondary)]">{{ $t('panel.userDetail.name') }}</dt>
              <dd class="text-sm text-[var(--color-text-primary)]">
                <div v-if="!editingName" class="flex items-center gap-2">
                  <span>{{ user.full_name }}</span>
                  <button @click="startEditName" class="text-primary-500 hover:text-primary-600 text-xs">✎</button>
                </div>
                <div v-else class="flex items-center gap-2">
                  <input v-model="editForm.full_name" class="px-2 py-1 text-sm border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] rounded w-full" />
                  <button @click="saveField('full_name')" class="text-green-500 hover:text-green-600 text-sm">✓</button>
                  <button @click="editingName = false" class="text-red-500 hover:text-red-600 text-sm">✗</button>
                </div>
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-[var(--color-text-secondary)]">{{ $t('panel.users.username') }}</dt>
              <dd class="text-sm text-[var(--color-text-primary)]">
                <div v-if="!editingUsername" class="flex items-center gap-2">
                  <span class="font-mono">{{ user.username || '-' }}</span>
                  <button @click="startEditUsername" class="text-primary-500 hover:text-primary-600 text-xs">✎</button>
                </div>
                <div v-else class="flex items-center gap-2">
                  <input v-model="editForm.username" class="px-2 py-1 text-sm border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] rounded w-full font-mono" :placeholder="$t('panel.users.usernamePlaceholder')" />
                  <button @click="saveField('username')" class="text-green-500 hover:text-green-600 text-sm">✓</button>
                  <button @click="editingUsername = false" class="text-red-500 hover:text-red-600 text-sm">✗</button>
                </div>
                <p v-if="editingUsername" class="text-xs text-[var(--color-text-secondary)] mt-1">{{ $t('panel.users.usernameHint') }}</p>
                <p v-if="editError" class="text-xs text-red-500 mt-1">{{ editError }}</p>
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-[var(--color-text-secondary)]">{{ $t('panel.userDetail.role') }}</dt>
              <dd class="text-sm">
                <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getRoleBadgeClass(user.role)">
                  {{ user.role }}
                </span>
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-[var(--color-text-secondary)]">{{ $t('panel.userDetail.status') }}</dt>
              <dd class="text-sm">
                <span :class="user.is_active ? 'text-green-600' : 'text-red-600'">
                  {{ user.is_active ? '✓ ' + $t('panel.userDetail.active') : '✗ ' + $t('panel.userDetail.inactive') }}
                </span>
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-[var(--color-text-secondary)]">{{ $t('panel.userDetail.createdAt') }}</dt>
              <dd class="text-sm text-[var(--color-text-primary)]">{{ formatDate(user.created_at) }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-[var(--color-text-secondary)]">{{ $t('panel.userDetail.lastLogin') }}</dt>
              <dd class="text-sm text-[var(--color-text-primary)]">{{ user.last_login_at ? formatDate(user.last_login_at) : $t('panel.userDetail.never') }}</dd>
            </div>
          </dl>

          <!-- Password Change -->
          <div class="mt-4 pt-4 border-t border-[var(--color-border)]">
            <button v-if="!showPasswordForm" @click="showPasswordForm = true" class="text-sm text-primary-500 hover:text-primary-600">
              {{ $t('panel.userDetail.changePassword') || 'Passwort ändern' }}
            </button>
            <div v-else class="space-y-3">
              <h4 class="text-sm font-medium text-[var(--color-text-primary)]">{{ $t('panel.userDetail.changePassword') || 'Passwort ändern' }}</h4>
              <input v-model="passwordForm.newPassword" type="password" class="w-full px-3 py-2 text-sm border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] rounded-lg" :placeholder="$t('panel.users.passwordPlaceholder')" />
              <input v-model="passwordForm.confirmPassword" type="password" class="w-full px-3 py-2 text-sm border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] rounded-lg" :placeholder="$t('auth.confirm_password')" />
              <p v-if="passwordError" class="text-xs text-red-500">{{ passwordError }}</p>
              <p v-if="passwordSuccess" class="text-xs text-green-500">{{ passwordSuccess }}</p>
              <div class="flex gap-2">
                <button @click="savePassword" :disabled="!canSavePassword" class="px-3 py-1 text-sm text-white bg-primary-600 rounded hover:bg-primary-700 disabled:opacity-50">{{ $t('common.save') }}</button>
                <button @click="showPasswordForm = false; passwordError = ''; passwordSuccess = ''" class="px-3 py-1 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">{{ $t('common.cancel') }}</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Token Info -->
        <div class="bg-[var(--color-surface)] rounded-lg shadow-sm border border-[var(--color-border)] p-6">
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">{{ $t('panel.userDetail.tokenBalance') }}</h3>
          <div class="text-center py-4">
            <div class="text-4xl font-bold text-purple-600">
              {{ user.token_balance || 0 }}
            </div>
            <div class="text-sm text-[var(--color-text-secondary)] mt-1">{{ $t('panel.userDetail.availableTokens') }}</div>
          </div>
          <button
            @click="openGrantTokensModal"
            class="w-full mt-4 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200"
          >
            {{ $t('panel.userDetail.addTokens') }}
          </button>
        </div>

        <!-- Organisation Info -->
        <div class="bg-[var(--color-surface)] rounded-lg shadow-sm border border-[var(--color-border)] p-6">
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">{{ $t('panel.userDetail.organisation') }}</h3>
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-[var(--color-text-secondary)]">{{ $t('panel.userDetail.name') }}</dt>
              <dd class="text-sm text-[var(--color-text-primary)]">{{ user.organisation_name || $t('panel.userDetail.noOrganisation') }}</dd>
            </div>
            <div v-if="user.organisation_id">
              <dt class="text-sm font-medium text-[var(--color-text-secondary)]">{{ $t('panel.userDetail.organisationId') }}</dt>
              <dd class="text-sm text-[var(--color-text-primary)]">{{ user.organisation_id }}</dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- Statistics Row -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div class="bg-[var(--color-surface)] rounded-lg shadow-sm border border-[var(--color-border)] p-6">
          <div class="text-sm font-medium text-[var(--color-text-secondary)]">{{ $t('panel.userDetail.coursesCreated') }}</div>
          <div class="text-2xl font-bold text-[var(--color-text-primary)] mt-1">0</div>
        </div>
        <div class="bg-[var(--color-surface)] rounded-lg shadow-sm border border-[var(--color-border)] p-6">
          <div class="text-sm font-medium text-[var(--color-text-secondary)]">{{ $t('panel.userDetail.coursesEnrolled') }}</div>
          <div class="text-2xl font-bold text-[var(--color-text-primary)] mt-1">0</div>
        </div>
        <div class="bg-[var(--color-surface)] rounded-lg shadow-sm border border-[var(--color-border)] p-6">
          <div class="text-sm font-medium text-[var(--color-text-secondary)]">{{ $t('panel.userDetail.tokensUsed') }}</div>
          <div class="text-2xl font-bold text-[var(--color-text-primary)] mt-1">0</div>
        </div>
        <div class="bg-[var(--color-surface)] rounded-lg shadow-sm border border-[var(--color-border)] p-6">
          <div class="text-sm font-medium text-[var(--color-text-secondary)]">{{ $t('panel.userDetail.logins30d') }}</div>
          <div class="text-2xl font-bold text-[var(--color-text-primary)] mt-1">0</div>
        </div>
      </div>

      <!-- Action History -->
      <div class="bg-[var(--color-surface)] rounded-lg shadow-sm border border-[var(--color-border)]">
        <div class="px-6 py-4 border-b border-[var(--color-border)]">
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">{{ $t('panel.userDetail.actionHistory') }}</h3>
        </div>
        <div class="p-6">
          <p class="text-sm text-[var(--color-text-secondary)] text-center py-8">
            {{ $t('panel.userDetail.noActions') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Ban User Modal -->
    <div v-if="showBanModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-[var(--color-surface)] rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-[var(--color-border)]">
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">{{ $t('panel.userDetail.banModal.title') }}</h3>
          <p class="text-sm text-[var(--color-text-secondary)] mt-1">{{ user?.full_name }}</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">{{ $t('panel.userDetail.banModal.reasonLabel') }}</label>
            <textarea
              v-model="banForm.reason"
              rows="3"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              :placeholder="$t('panel.userDetail.banModal.reasonPlaceholder')"
            ></textarea>
          </div>
          <div class="mb-4">
            <label class="flex items-center">
              <input
                v-model="banForm.permanent"
                type="checkbox"
                class="rounded border-[var(--color-border)] text-red-600 focus:ring-red-500"
              />
              <span class="ml-2 text-sm text-[var(--color-text-primary)]">{{ $t('panel.userDetail.banModal.permanent') }}</span>
            </label>
          </div>
          <div v-if="!banForm.permanent" class="mb-4">
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">{{ $t('panel.userDetail.banModal.durationLabel') }}</label>
            <input
              v-model.number="banForm.duration_days"
              type="number"
              min="1"
              max="365"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              :placeholder="$t('panel.userDetail.banModal.durationPlaceholder')"
            />
          </div>
          <div class="mb-4">
            <label class="flex items-center">
              <input
                v-model="banForm.notify_user"
                type="checkbox"
                class="rounded border-[var(--color-border)] text-red-600 focus:ring-red-500"
              />
              <span class="ml-2 text-sm text-[var(--color-text-primary)]">{{ $t('panel.userDetail.banModal.notifyUser') }}</span>
            </label>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-[var(--color-border)] flex justify-end gap-3">
          <button
            @click="closeBanModal"
            class="px-4 py-2 text-[var(--color-text-primary)] bg-[var(--color-surface-secondary)] rounded-lg hover:bg-[var(--color-surface-secondary)]"
          >
            {{ $t('panel.userDetail.banModal.cancel') }}
          </button>
          <button
            @click="confirmBan"
            :disabled="!canSubmitBan"
            class="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {{ $t('panel.userDetail.banModal.confirm') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Unban User Modal -->
    <div v-if="showUnbanModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-[var(--color-surface)] rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-[var(--color-border)]">
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">{{ $t('panel.userDetail.unbanModal.title') }}</h3>
          <p class="text-sm text-[var(--color-text-secondary)] mt-1">{{ user?.full_name }}</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">{{ $t('panel.userDetail.unbanModal.reasonLabel') }}</label>
            <textarea
              v-model="unbanForm.reason"
              rows="3"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              :placeholder="$t('panel.userDetail.unbanModal.reasonPlaceholder')"
            ></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-[var(--color-border)] flex justify-end gap-3">
          <button
            @click="closeUnbanModal"
            class="px-4 py-2 text-[var(--color-text-primary)] bg-[var(--color-surface-secondary)] rounded-lg hover:bg-[var(--color-surface-secondary)]"
          >
            {{ $t('panel.userDetail.unbanModal.cancel') }}
          </button>
          <button
            @click="confirmUnban"
            :disabled="!canSubmitUnban"
            class="px-4 py-2 text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {{ $t('panel.userDetail.unbanModal.confirm') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Grant Tokens Modal -->
    <div v-if="showGrantTokensModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-[var(--color-surface)] rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-[var(--color-border)]">
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">{{ $t('panel.userDetail.grantTokensModal.title') }}</h3>
          <p class="text-sm text-[var(--color-text-secondary)] mt-1">{{ user?.full_name }}</p>
          <p class="text-xs text-[var(--color-text-secondary)] mt-1">{{ $t('panel.userDetail.grantTokensModal.currentBalance', { balance: user?.token_balance || 0 }) }}</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">{{ $t('panel.userDetail.grantTokensModal.amountLabel') }}</label>
            <input
              v-model.number="grantTokensForm.amount"
              type="number"
              min="1"
              max="1000000"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              :placeholder="$t('panel.userDetail.grantTokensModal.amountPlaceholder')"
            />
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">{{ $t('panel.userDetail.grantTokensModal.reasonLabel') }}</label>
            <textarea
              v-model="grantTokensForm.reason"
              rows="3"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              :placeholder="$t('panel.userDetail.grantTokensModal.reasonPlaceholder')"
            ></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-[var(--color-border)] flex justify-end gap-3">
          <button
            @click="closeGrantTokensModal"
            class="px-4 py-2 text-[var(--color-text-primary)] bg-[var(--color-surface-secondary)] rounded-lg hover:bg-[var(--color-surface-secondary)]"
          >
            {{ $t('panel.userDetail.grantTokensModal.cancel') }}
          </button>
          <button
            @click="confirmGrantTokens"
            :disabled="!canSubmitGrantTokens"
            class="px-4 py-2 text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            {{ $t('panel.userDetail.grantTokensModal.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/application/stores/modules/admin/panel.store'
import type { AdminUser, BanUserRequest } from '@/infrastructure/api/clients/panel/admin'
import { adminGetUserDetail } from '@/infrastructure/api/clients/panel/admin'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const panelStore = usePanelStore()

const user = ref<AdminUser | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

// Password change
const showPasswordForm = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')
const passwordForm = ref({ newPassword: '', confirmPassword: '' })

const canSavePassword = computed(() =>
  passwordForm.value.newPassword.length >= 12 &&
  passwordForm.value.newPassword === passwordForm.value.confirmPassword
)

const savePassword = async () => {
  try {
    passwordError.value = ''
    passwordSuccess.value = ''
    if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
      passwordError.value = t('auth.password_mismatch') || 'Passwörter stimmen nicht überein'
      return
    }
    const userId = route.params.userId as string
    const http = (await import('@/infrastructure/api/http')).default
    await http.post(`/users/${userId}/change-password`, {
      new_password: passwordForm.value.newPassword
    })
    passwordSuccess.value = t('panel.userDetail.passwordChanged') || 'Passwort erfolgreich geändert'
    passwordForm.value = { newPassword: '', confirmPassword: '' }
    setTimeout(() => { showPasswordForm.value = false; passwordSuccess.value = '' }, 2000)
  } catch (err: any) {
    passwordError.value = err.response?.data?.details || err.response?.data?.error || 'Fehler'
  }
}

// Inline editing
const editingName = ref(false)
const editingUsername = ref(false)
const editError = ref<string | null>(null)
const editForm = ref({ full_name: '', username: '' })

const startEditName = () => {
  editForm.value.full_name = user.value?.full_name || ''
  editingName.value = true
  editError.value = null
}

const startEditUsername = () => {
  editForm.value.username = user.value?.username || ''
  editingUsername.value = true
  editError.value = null
}

const saveField = async (field: string) => {
  try {
    editError.value = null
    const userId = route.params.userId as string
    const data: Record<string, string> = {}
    data[field] = editForm.value[field as keyof typeof editForm.value]

    const http = (await import('@/infrastructure/api/http')).default
    await http.put(`/users/${userId}`, data)

    // Update local state
    if (user.value) {
      (user.value as any)[field] = data[field]
    }
    editingName.value = false
    editingUsername.value = false
  } catch (err: any) {
    editError.value = err.response?.data?.details || err.response?.data?.error || t('panel.users.createUserError')
  }
}

// Modal States
const showBanModal = ref(false)
const showUnbanModal = ref(false)
const showGrantTokensModal = ref(false)

// Form Data
const banForm = ref<BanUserRequest>({
  reason: '',
  duration_days: 30,
  permanent: false,
  notify_user: true
})

const unbanForm = ref({
  reason: ''
})

const grantTokensForm = ref({
  amount: 0,
  reason: ''
})

// Computed Validations
const canSubmitBan = computed(() => banForm.value.reason.length >= 10)
const canSubmitUnban = computed(() => unbanForm.value.reason.length >= 10)
const canSubmitGrantTokens = computed(
  () => grantTokensForm.value.amount > 0 && grantTokensForm.value.reason.length >= 10
)

// Load User Detail
const loadUserDetail = async () => {
  loading.value = true
  error.value = null

  try {
    const userId = route.params.userId as string
    user.value = await adminGetUserDetail(userId)
  } catch (err: any) {
    error.value = err.response?.data?.message || t('panel.userDetail.loadError')
    console.error('Failed to load user detail:', err)
  } finally {
    loading.value = false
  }
}

// Ban User
const openBanModal = () => {
  banForm.value = {
    reason: '',
    duration_days: 30,
    permanent: false,
    notify_user: true
  }
  showBanModal.value = true
}

const closeBanModal = () => {
  showBanModal.value = false
}

const confirmBan = async () => {
  if (!user.value || !canSubmitBan.value) return

  try {
    await panelStore.banUser(user.value.user_id, banForm.value)
    closeBanModal()
    await loadUserDetail()
  } catch (err) {
    console.error('Failed to ban user:', err)
  }
}

// Unban User
const openUnbanModal = () => {
  unbanForm.value = { reason: '' }
  showUnbanModal.value = true
}

const closeUnbanModal = () => {
  showUnbanModal.value = false
}

const confirmUnban = async () => {
  if (!user.value || !canSubmitUnban.value) return

  try {
    await panelStore.unbanUser(user.value.user_id, unbanForm.value.reason)
    closeUnbanModal()
    await loadUserDetail()
  } catch (err) {
    console.error('Failed to unban user:', err)
  }
}

// Grant Tokens
const openGrantTokensModal = () => {
  grantTokensForm.value = { amount: 0, reason: '' }
  showGrantTokensModal.value = true
}

const closeGrantTokensModal = () => {
  showGrantTokensModal.value = false
}

const confirmGrantTokens = async () => {
  if (!user.value || !canSubmitGrantTokens.value) return

  try {
    const newBalance = await panelStore.grantTokens(
      user.value.user_id,
      grantTokensForm.value.amount,
      grantTokensForm.value.reason
    )
    user.value.token_balance = newBalance
    closeGrantTokensModal()
  } catch (err) {
    console.error('Failed to grant tokens:', err)
  }
}

// Utility
const getRoleBadgeClass = (role: string): string => {
  const classes: Record<string, string> = {
    user: 'bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)]',
    premium: 'bg-yellow-100 text-yellow-800',
    creator: 'bg-blue-100 text-blue-800',
    teacher: 'bg-green-100 text-green-800',
    admin: 'bg-red-100 text-red-800'
  }
  return classes[role] || 'bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)]'
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString(locale.value, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadUserDetail()
})
</script>
