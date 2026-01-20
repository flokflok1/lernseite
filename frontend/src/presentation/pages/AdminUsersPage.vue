<template>
  <div class="admin-users-page">
    <!-- Page Header with Create Button -->
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-[var(--color-text-primary)]">{{ $t('admin.users.title') }}</h1>
        <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('admin.users.subtitle') }}</p>
      </div>
      <button
        @click="openCreateUserModal"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        {{ $t('admin.users.createUser') }}
      </button>
    </div>

    <!-- Filters & Search -->
    <div class="bg-[var(--color-surface)] rounded-lg shadow-sm p-4 mb-6 border border-[var(--color-border)]">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('admin.users.search_placeholder')"
          class="px-4 py-2 border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          @input="debouncedSearch"
        />
        <select
          v-model="roleFilter"
          class="px-4 py-2 border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          @change="loadUsers"
        >
          <option value="">{{ $t('admin.users.allRoles') }}</option>
          <option value="user">User</option>
          <option value="premium">Premium</option>
          <option value="creator">Creator</option>
          <option value="teacher">Teacher</option>
          <option value="admin">Admin</option>
        </select>
        <select
          v-model="statusFilter"
          class="px-4 py-2 border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          @change="loadUsers"
        >
          <option value="">{{ $t('admin.users.allStatus') }}</option>
          <option value="active">{{ $t('common.active') }}</option>
          <option value="inactive">{{ $t('common.inactive') }}</option>
        </select>
        <button
          @click="resetFilters"
          class="px-4 py-2 border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)]"
        >
          {{ $t('admin.users.resetFilters') }}
        </button>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-[var(--color-surface)] rounded-lg shadow-sm border border-[var(--color-border)]">
      <div v-if="adminStore.loading" class="p-8 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      </div>

      <div v-else-if="adminStore.users.length === 0" class="p-8 text-center text-[var(--color-text-secondary)]">
        {{ $t('admin.users.noUsers') }}
      </div>

      <table v-else class="w-full">
        <thead class="bg-[var(--color-surface-secondary)] border-b border-[var(--color-border)]">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">{{ $t('admin.users.name') }}</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">{{ $t('auth.email') }}</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">{{ $t('admin.users.role') }}</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">{{ $t('common.status') }}</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">Tokens</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">{{ $t('profile.organisation') }}</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-[var(--color-text-secondary)] uppercase">{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--color-border)]">
          <tr v-for="user in adminStore.users" :key="user.user_id" class="hover:bg-[var(--color-surface-secondary)]">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="font-medium text-[var(--color-text-primary)]">{{ user.first_name }} {{ user.last_name }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-text-secondary)]">
              {{ user.email }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getRoleBadgeClass(user.role)">
                {{ user.role }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="user.is_active ? 'text-green-600' : 'text-red-600'">
                {{ user.is_active ? '✓ ' + $t('common.active') : '✗ ' + $t('common.inactive') }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-text-secondary)]">
              {{ user.token_balance || 0 }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-text-secondary)]">
              {{ user.organisation_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <div class="flex justify-end gap-3">
                <button
                  @click="viewUserDetail(user.user_id)"
                  class="px-3 py-1 text-blue-600 hover:text-white hover:bg-blue-600 border border-blue-600 rounded transition-colors"
                  :title="$t('common.details')"
                >
                  {{ $t('common.details') }}
                </button>
                <button
                  v-if="user.is_active"
                  @click="openBanModal(user)"
                  class="px-3 py-1 text-red-600 hover:text-white hover:bg-red-600 border border-red-600 rounded transition-colors"
                  :title="$t('admin.users.banUser')"
                >
                  {{ $t('admin.users.ban') }}
                </button>
                <button
                  v-else
                  @click="openUnbanModal(user)"
                  class="px-3 py-1 text-green-600 hover:text-white hover:bg-green-600 border border-green-600 rounded transition-colors"
                  :title="$t('admin.users.unbanUser')"
                >
                  {{ $t('admin.users.unban') }}
                </button>
                <button
                  @click="openGrantTokensModal(user)"
                  class="px-3 py-1 text-purple-600 hover:text-white hover:bg-purple-600 border border-purple-600 rounded transition-colors"
                  :title="$t('admin.users.grantTokens')"
                >
                  Tokens
                </button>
                <button
                  v-if="user.role === 'creator'"
                  @click="openVerifyCreatorModal(user)"
                  class="px-3 py-1 text-yellow-600 hover:text-white hover:bg-yellow-600 border border-yellow-600 rounded transition-colors"
                  :title="$t('admin.users.verifyCreator')"
                >
                  {{ $t('admin.users.verify') }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="adminStore.usersTotalPages > 1" class="px-6 py-4 border-t border-[var(--color-border)] flex justify-between items-center">
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ $t('admin.users.pagination', { page: adminStore.usersPage, total: adminStore.usersTotalPages, count: adminStore.usersTotal }) }}
        </p>
        <div class="flex gap-2">
          <button
            @click="changePage(adminStore.usersPage - 1)"
            :disabled="adminStore.usersPage === 1"
            class="px-3 py-1 border border-[var(--color-border)] rounded hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] disabled:opacity-50"
          >
            {{ $t('common.back') }}
          </button>
          <button
            @click="changePage(adminStore.usersPage + 1)"
            :disabled="adminStore.usersPage >= adminStore.usersTotalPages"
            class="px-3 py-1 border border-[var(--color-border)] rounded hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] disabled:opacity-50"
          >
            {{ $t('common.next') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Ban User Modal -->
    <div v-if="showBanModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">{{ $t('admin.users.banUser') }}</h3>
          <p class="text-sm text-gray-600 mt-1">{{ selectedUser?.first_name }} {{ selectedUser?.last_name }}</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('admin.users.banReason') }} *</label>
            <textarea
              v-model="banForm.reason"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              :placeholder="$t('admin.users.minChars')"
            ></textarea>
          </div>
          <div class="mb-4">
            <label class="flex items-center">
              <input
                v-model="banForm.permanent"
                type="checkbox"
                class="rounded border-gray-300 text-red-600 focus:ring-red-500"
              />
              <span class="ml-2 text-sm text-gray-700">{{ $t('admin.users.permanentBan') }}</span>
            </label>
          </div>
          <div v-if="!banForm.permanent" class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('admin.users.durationDays') }}</label>
            <input
              v-model.number="banForm.duration_days"
              type="number"
              min="1"
              max="365"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="30"
            />
          </div>
          <div class="mb-4">
            <label class="flex items-center">
              <input
                v-model="banForm.notify_user"
                type="checkbox"
                class="rounded border-gray-300 text-red-600 focus:ring-red-500"
              />
              <span class="ml-2 text-sm text-gray-700">{{ $t('admin.users.notifyByEmail') }}</span>
            </label>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            @click="closeBanModal"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="confirmBan"
            :disabled="!canSubmitBan"
            class="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ $t('admin.users.banUser') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Unban User Modal -->
    <div v-if="showUnbanModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">{{ $t('admin.users.unbanUser') }}</h3>
          <p class="text-sm text-gray-600 mt-1">{{ selectedUser?.first_name }} {{ selectedUser?.last_name }}</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('admin.users.unbanReason') }} *</label>
            <textarea
              v-model="unbanForm.reason"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              :placeholder="$t('admin.users.minChars')"
            ></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            @click="closeUnbanModal"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="confirmUnban"
            :disabled="!canSubmitUnban"
            class="px-4 py-2 text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ $t('admin.users.unbanUser') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Grant Tokens Modal -->
    <div v-if="showGrantTokensModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">{{ $t('admin.users.grantTokens') }}</h3>
          <p class="text-sm text-gray-600 mt-1">{{ selectedUser?.first_name }} {{ selectedUser?.last_name }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ $t('admin.users.currentBalance') }}: {{ selectedUser?.token_balance || 0 }} Tokens</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('admin.users.tokenAmount') }} *</label>
            <input
              v-model.number="grantTokensForm.amount"
              type="number"
              min="1"
              max="1000000"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="5000"
            />
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('admin.users.reason') }} *</label>
            <textarea
              v-model="grantTokensForm.reason"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              :placeholder="$t('admin.users.minChars')"
            ></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            @click="closeGrantTokensModal"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="confirmGrantTokens"
            :disabled="!canSubmitGrantTokens"
            class="px-4 py-2 text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ $t('admin.users.grantTokens') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Verify Creator Modal -->
    <div v-if="showVerifyCreatorModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">{{ $t('admin.users.verifyCreator') }}</h3>
          <p class="text-sm text-gray-600 mt-1">{{ selectedUser?.first_name }} {{ selectedUser?.last_name }}</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('admin.users.action') }} *</label>
            <select
              v-model="verifyCreatorForm.verified"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
            >
              <option :value="true">{{ $t('admin.users.verify') }}</option>
              <option :value="false">{{ $t('admin.users.revokeVerification') }}</option>
            </select>
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('admin.users.reason') }} *</label>
            <textarea
              v-model="verifyCreatorForm.reason"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
              :placeholder="$t('admin.users.minChars')"
            ></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            @click="closeVerifyCreatorModal"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="confirmVerifyCreator"
            :disabled="!canSubmitVerifyCreator"
            class="px-4 py-2 text-white bg-yellow-600 rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ verifyCreatorForm.verified ? $t('admin.users.verify') : $t('admin.users.revoke') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Create User Modal -->
    <div v-if="showCreateUserModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ $t('admin.users.createUser') }}</h3>
        </div>
        <div class="px-6 py-4">
          <!-- Error Message -->
          <div v-if="createUserError" class="mb-4 p-4 bg-red-50 dark:bg-red-900 rounded-lg border border-red-200 dark:border-red-700">
            <p class="text-sm text-red-800 dark:text-red-100">{{ createUserError }}</p>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ $t('auth.email') }} *</label>
            <input
              v-model="createUserForm.email"
              type="email"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="user@example.com"
            />
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ $t('auth.password') }} *</label>
            <input
              v-model="createUserForm.password"
              type="password"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Min. 8 Zeichen"
            />
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ $t('profile.firstName') }} *</label>
            <input
              v-model="createUserForm.first_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Max"
            />
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ $t('profile.lastName') }} *</label>
            <input
              v-model="createUserForm.last_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Mustermann"
            />
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ $t('admin.users.role') }} *</label>
            <select
              v-model="createUserForm.role"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="free">Free</option>
              <option value="premium">Premium</option>
              <option value="creator">Creator</option>
              <option value="teacher">Teacher</option>
              <option value="admin">Admin</option>
            </select>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <button
            @click="closeCreateUserModal"
            class="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="confirmCreateUser"
            :disabled="!canSubmitCreateUser || isCreatingUser"
            class="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isCreatingUser ? '...' : $t('admin.users.createUser') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAdminStore } from '@/application/stores/modules/admin'

const { t } = useI18n()
import type { AdminUser, BanUserRequest } from '@/infrastructure/api/clients/admin'

const adminStore = useAdminStore()
const router = useRouter()

// Search & Filters
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')

let searchTimeout: ReturnType<typeof setTimeout> | null = null

const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadUsers()
  }, 500)
}

const loadUsers = async () => {
  await adminStore.loadUsers({
    search: searchQuery.value || undefined,
    role: roleFilter.value || undefined,
    status: statusFilter.value as any,
    page: adminStore.usersPage
  })
}

const resetFilters = () => {
  searchQuery.value = ''
  roleFilter.value = ''
  statusFilter.value = ''
  loadUsers()
}

const changePage = (page: number) => {
  adminStore.usersPage = page
  loadUsers()
}

// Modal States
const showBanModal = ref(false)
const showUnbanModal = ref(false)
const showGrantTokensModal = ref(false)
const showVerifyCreatorModal = ref(false)
const showCreateUserModal = ref(false)
const selectedUser = ref<AdminUser | null>(null)

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

const verifyCreatorForm = ref({
  verified: true,
  reason: ''
})

const createUserForm = ref({
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  role: 'free'
})

const isCreatingUser = ref(false)
const createUserError = ref<string | null>(null)

// Computed Validations
const canSubmitBan = computed(() => banForm.value.reason.length >= 10)
const canSubmitUnban = computed(() => unbanForm.value.reason.length >= 10)
const canSubmitGrantTokens = computed(
  () => grantTokensForm.value.amount > 0 && grantTokensForm.value.reason.length >= 10
)
const canSubmitVerifyCreator = computed(() => verifyCreatorForm.value.reason.length >= 10)
const canSubmitCreateUser = computed(() => {
  const form = createUserForm.value
  return form.email.length > 0 &&
    form.password.length >= 8 &&
    form.first_name.length > 0 &&
    form.last_name.length > 0 &&
    form.role.length > 0
})

// Navigation
const viewUserDetail = (userId: string) => {
  router.push({ name: 'AdminUserDetail', params: { userId } })
}

// Ban User
const openBanModal = (user: AdminUser) => {
  selectedUser.value = user
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
  selectedUser.value = null
}

const confirmBan = async () => {
  if (!selectedUser.value || !canSubmitBan.value) return

  try {
    await adminStore.banUser(selectedUser.value.user_id, banForm.value)
    closeBanModal()
    await loadUsers()
  } catch (err) {
    console.error('Failed to ban user:', err)
  }
}

// Unban User
const openUnbanModal = (user: AdminUser) => {
  selectedUser.value = user
  unbanForm.value = { reason: '' }
  showUnbanModal.value = true
}

const closeUnbanModal = () => {
  showUnbanModal.value = false
  selectedUser.value = null
}

const confirmUnban = async () => {
  if (!selectedUser.value || !canSubmitUnban.value) return

  try {
    await adminStore.unbanUser(selectedUser.value.user_id, unbanForm.value.reason)
    closeUnbanModal()
    await loadUsers()
  } catch (err) {
    console.error('Failed to unban user:', err)
  }
}

// Grant Tokens
const openGrantTokensModal = (user: AdminUser) => {
  selectedUser.value = user
  grantTokensForm.value = { amount: 0, reason: '' }
  showGrantTokensModal.value = true
}

const closeGrantTokensModal = () => {
  showGrantTokensModal.value = false
  selectedUser.value = null
}

const confirmGrantTokens = async () => {
  if (!selectedUser.value || !canSubmitGrantTokens.value) return

  try {
    await adminStore.grantTokens(
      selectedUser.value.user_id,
      grantTokensForm.value.amount,
      grantTokensForm.value.reason
    )
    closeGrantTokensModal()
    await loadUsers()
  } catch (err) {
    console.error('Failed to grant tokens:', err)
  }
}

// Verify Creator
const openVerifyCreatorModal = (user: AdminUser) => {
  selectedUser.value = user
  verifyCreatorForm.value = { verified: true, reason: '' }
  showVerifyCreatorModal.value = true
}

const closeVerifyCreatorModal = () => {
  showVerifyCreatorModal.value = false
  selectedUser.value = null
}

const confirmVerifyCreator = async () => {
  if (!selectedUser.value || !canSubmitVerifyCreator.value) return

  try {
    await adminStore.verifyCreator(
      selectedUser.value.user_id,
      verifyCreatorForm.value.verified,
      verifyCreatorForm.value.reason
    )
    closeVerifyCreatorModal()
    await loadUsers()
  } catch (err) {
    console.error('Failed to verify creator:', err)
  }
}

// Create User
const openCreateUserModal = () => {
  createUserForm.value = {
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'free'
  }
  createUserError.value = null
  showCreateUserModal.value = true
}

const closeCreateUserModal = () => {
  showCreateUserModal.value = false
  createUserForm.value = {
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'free'
  }
}

const confirmCreateUser = async () => {
  if (!canSubmitCreateUser.value || isCreatingUser.value) return

  try {
    isCreatingUser.value = true
    createUserError.value = null
    await adminStore.createUser(createUserForm.value)
    closeCreateUserModal()
    await loadUsers()
  } catch (err: any) {
    const message = err.response?.data?.message ||
                   err.response?.data?.error ||
                   err.message ||
                   t('admin.users.createUserError')
    createUserError.value = message
    console.error('Failed to create user:', err)
  } finally {
    isCreatingUser.value = false
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

onMounted(() => {
  loadUsers()
})
</script>
