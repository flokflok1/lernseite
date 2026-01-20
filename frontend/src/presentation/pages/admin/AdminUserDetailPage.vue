<template>
  <div class="admin-user-detail-page">
    <!-- Page Header -->
    <div class="mb-6 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <button
          @click="router.back()"
          class="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
          :title="$t('admin.userDetail.back')"
        >
          ← {{ $t('admin.userDetail.back') }}
        </button>
        <div>
          <h1 class="text-2xl font-bold text-[var(--color-text-primary)]">
            {{ user?.first_name }} {{ user?.last_name }}
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
          {{ $t('admin.userDetail.banUser') }}
        </button>
        <button
          v-else
          @click="openUnbanModal"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          {{ $t('admin.userDetail.unbanUser') }}
        </button>
        <button
          @click="openGrantTokensModal"
          class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          {{ $t('admin.userDetail.grantTokens') }}
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
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $t('admin.userDetail.basicInfo') }}</h3>
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.userDetail.userId') }}</dt>
              <dd class="text-sm text-gray-900">{{ user.user_id }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.userDetail.role') }}</dt>
              <dd class="text-sm">
                <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getRoleBadgeClass(user.role)">
                  {{ user.role }}
                </span>
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.userDetail.status') }}</dt>
              <dd class="text-sm">
                <span :class="user.is_active ? 'text-green-600' : 'text-red-600'">
                  {{ user.is_active ? '✓ ' + $t('admin.userDetail.active') : '✗ ' + $t('admin.userDetail.inactive') }}
                </span>
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.userDetail.createdAt') }}</dt>
              <dd class="text-sm text-gray-900">{{ formatDate(user.created_at) }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.userDetail.lastLogin') }}</dt>
              <dd class="text-sm text-gray-900">{{ user.last_login ? formatDate(user.last_login) : $t('admin.userDetail.never') }}</dd>
            </div>
          </dl>
        </div>

        <!-- Token Info -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $t('admin.userDetail.tokenBalance') }}</h3>
          <div class="text-center py-4">
            <div class="text-4xl font-bold text-purple-600">
              {{ user.token_balance || 0 }}
            </div>
            <div class="text-sm text-gray-500 mt-1">{{ $t('admin.userDetail.availableTokens') }}</div>
          </div>
          <button
            @click="openGrantTokensModal"
            class="w-full mt-4 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200"
          >
            {{ $t('admin.userDetail.addTokens') }}
          </button>
        </div>

        <!-- Organisation Info -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $t('admin.userDetail.organisation') }}</h3>
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.userDetail.name') }}</dt>
              <dd class="text-sm text-gray-900">{{ user.organisation_name || $t('admin.userDetail.noOrganisation') }}</dd>
            </div>
            <div v-if="user.organisation_id">
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.userDetail.organisationId') }}</dt>
              <dd class="text-sm text-gray-900">{{ user.organisation_id }}</dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- Statistics Row -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="text-sm font-medium text-gray-500">{{ $t('admin.userDetail.coursesCreated') }}</div>
          <div class="text-2xl font-bold text-gray-900 mt-1">0</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="text-sm font-medium text-gray-500">{{ $t('admin.userDetail.coursesEnrolled') }}</div>
          <div class="text-2xl font-bold text-gray-900 mt-1">0</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="text-sm font-medium text-gray-500">{{ $t('admin.userDetail.tokensUsed') }}</div>
          <div class="text-2xl font-bold text-gray-900 mt-1">0</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="text-sm font-medium text-gray-500">{{ $t('admin.userDetail.logins30d') }}</div>
          <div class="text-2xl font-bold text-gray-900 mt-1">0</div>
        </div>
      </div>

      <!-- Action History -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">{{ $t('admin.userDetail.actionHistory') }}</h3>
        </div>
        <div class="p-6">
          <p class="text-sm text-gray-500 text-center py-8">
            {{ $t('admin.userDetail.noActions') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Ban User Modal -->
    <div v-if="showBanModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">{{ $t('admin.userDetail.banModal.title') }}</h3>
          <p class="text-sm text-gray-600 mt-1">{{ user?.first_name }} {{ user?.last_name }}</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('admin.userDetail.banModal.reasonLabel') }}</label>
            <textarea
              v-model="banForm.reason"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              :placeholder="$t('admin.userDetail.banModal.reasonPlaceholder')"
            ></textarea>
          </div>
          <div class="mb-4">
            <label class="flex items-center">
              <input
                v-model="banForm.permanent"
                type="checkbox"
                class="rounded border-gray-300 text-red-600 focus:ring-red-500"
              />
              <span class="ml-2 text-sm text-gray-700">{{ $t('admin.userDetail.banModal.permanent') }}</span>
            </label>
          </div>
          <div v-if="!banForm.permanent" class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('admin.userDetail.banModal.durationLabel') }}</label>
            <input
              v-model.number="banForm.duration_days"
              type="number"
              min="1"
              max="365"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              :placeholder="$t('admin.userDetail.banModal.durationPlaceholder')"
            />
          </div>
          <div class="mb-4">
            <label class="flex items-center">
              <input
                v-model="banForm.notify_user"
                type="checkbox"
                class="rounded border-gray-300 text-red-600 focus:ring-red-500"
              />
              <span class="ml-2 text-sm text-gray-700">{{ $t('admin.userDetail.banModal.notifyUser') }}</span>
            </label>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            @click="closeBanModal"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            {{ $t('admin.userDetail.banModal.cancel') }}
          </button>
          <button
            @click="confirmBan"
            :disabled="!canSubmitBan"
            class="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {{ $t('admin.userDetail.banModal.confirm') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Unban User Modal -->
    <div v-if="showUnbanModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">{{ $t('admin.userDetail.unbanModal.title') }}</h3>
          <p class="text-sm text-gray-600 mt-1">{{ user?.first_name }} {{ user?.last_name }}</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('admin.userDetail.unbanModal.reasonLabel') }}</label>
            <textarea
              v-model="unbanForm.reason"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              :placeholder="$t('admin.userDetail.unbanModal.reasonPlaceholder')"
            ></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            @click="closeUnbanModal"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            {{ $t('admin.userDetail.unbanModal.cancel') }}
          </button>
          <button
            @click="confirmUnban"
            :disabled="!canSubmitUnban"
            class="px-4 py-2 text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {{ $t('admin.userDetail.unbanModal.confirm') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Grant Tokens Modal -->
    <div v-if="showGrantTokensModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">{{ $t('admin.userDetail.grantTokensModal.title') }}</h3>
          <p class="text-sm text-gray-600 mt-1">{{ user?.first_name }} {{ user?.last_name }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ $t('admin.userDetail.grantTokensModal.currentBalance', { balance: user?.token_balance || 0 }) }}</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('admin.userDetail.grantTokensModal.amountLabel') }}</label>
            <input
              v-model.number="grantTokensForm.amount"
              type="number"
              min="1"
              max="1000000"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              :placeholder="$t('admin.userDetail.grantTokensModal.amountPlaceholder')"
            />
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('admin.userDetail.grantTokensModal.reasonLabel') }}</label>
            <textarea
              v-model="grantTokensForm.reason"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              :placeholder="$t('admin.userDetail.grantTokensModal.reasonPlaceholder')"
            ></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            @click="closeGrantTokensModal"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            {{ $t('admin.userDetail.grantTokensModal.cancel') }}
          </button>
          <button
            @click="confirmGrantTokens"
            :disabled="!canSubmitGrantTokens"
            class="px-4 py-2 text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            {{ $t('admin.userDetail.grantTokensModal.confirm') }}
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
import { useAdminStore } from '@/application/stores/admin.store'
import type { AdminUser, BanUserRequest } from '@/infrastructure/api/admin.api'
import { adminGetUserDetail } from '@/infrastructure/api/admin.api'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const adminStore = useAdminStore()

const user = ref<AdminUser | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

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
    error.value = err.response?.data?.message || t('admin.userDetail.loadError')
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
    await adminStore.banUser(user.value.user_id, banForm.value)
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
    await adminStore.unbanUser(user.value.user_id, unbanForm.value.reason)
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
    const newBalance = await adminStore.grantTokens(
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
    user: 'bg-gray-100 text-gray-800',
    premium: 'bg-yellow-100 text-yellow-800',
    creator: 'bg-blue-100 text-blue-800',
    teacher: 'bg-green-100 text-green-800',
    admin: 'bg-red-100 text-red-800'
  }
  return classes[role] || 'bg-gray-100 text-gray-800'
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
