<template>
  <div class="panel-users-page">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-[var(--color-text-primary)]">{{ $t('panel.users.title') }}</h1>
      <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('panel.users.subtitle') }}</p>
    </div>

    <!-- Filters & Search -->
    <div class="bg-[var(--color-surface)] rounded-lg shadow-sm p-4 mb-6 border border-[var(--color-border)]">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('panel.users.search_placeholder')"
          class="px-4 py-2 border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          @input="debouncedSearch"
        />
        <select
          v-model="roleFilter"
          class="px-4 py-2 border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          @change="loadUsers"
        >
          <option value="">{{ $t('panel.users.allRoles') }}</option>
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
          <option value="">{{ $t('panel.users.allStatus') }}</option>
          <option value="active">{{ $t('common.active') }}</option>
          <option value="inactive">{{ $t('common.inactive') }}</option>
        </select>
        <button
          @click="resetFilters"
          class="px-4 py-2 border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)]"
        >
          {{ $t('panel.users.resetFilters') }}
        </button>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-[var(--color-surface)] rounded-lg shadow-sm border border-[var(--color-border)]">
      <div v-if="panelStore.loading" class="p-8 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      </div>

      <div v-else-if="panelStore.users.length === 0" class="p-8 text-center text-[var(--color-text-secondary)]">
        {{ $t('panel.users.noUsers') }}
      </div>

      <table v-else class="w-full">
        <thead class="bg-[var(--color-surface-secondary)] border-b border-[var(--color-border)]">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">{{ $t('panel.users.name') }}</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">{{ $t('auth.email') }}</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">{{ $t('panel.users.role') }}</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">{{ $t('common.status') }}</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">Tokens</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">{{ $t('profile.organisation') }}</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-[var(--color-text-secondary)] uppercase">{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--color-border)]">
          <tr v-for="user in panelStore.users" :key="user.user_id" class="hover:bg-[var(--color-surface-secondary)]">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="font-medium text-[var(--color-text-primary)]">{{ user.first_name }} {{ user.last_name }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-text-secondary)]">{{ user.email }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getRoleBadgeClass(user.role)">{{ user.role }}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="user.is_active ? 'text-green-600' : 'text-red-600'">
                {{ user.is_active ? '\u2713 ' + $t('common.active') : '\u2717 ' + $t('common.inactive') }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-text-secondary)]">{{ user.token_balance || 0 }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-text-secondary)]">{{ user.organisation_name || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <div class="flex justify-end gap-3">
                <button @click="viewUserDetail(user.user_id)" class="px-3 py-1 text-blue-600 hover:text-white hover:bg-blue-600 border border-blue-600 rounded transition-colors" :title="$t('common.details')">{{ $t('common.details') }}</button>
                <button v-if="user.is_active" @click="openBanModal(user)" class="px-3 py-1 text-red-600 hover:text-white hover:bg-red-600 border border-red-600 rounded transition-colors" :title="$t('panel.users.banUser')">{{ $t('panel.users.ban') }}</button>
                <button v-else @click="openUnbanModal(user)" class="px-3 py-1 text-green-600 hover:text-white hover:bg-green-600 border border-green-600 rounded transition-colors" :title="$t('panel.users.unbanUser')">{{ $t('panel.users.unban') }}</button>
                <button @click="openGrantTokensModal(user)" class="px-3 py-1 text-purple-600 hover:text-white hover:bg-purple-600 border border-purple-600 rounded transition-colors" :title="$t('panel.users.grantTokens')">Tokens</button>
                <button v-if="user.role === 'creator'" @click="openVerifyCreatorModal(user)" class="px-3 py-1 text-yellow-600 hover:text-white hover:bg-yellow-600 border border-yellow-600 rounded transition-colors" :title="$t('panel.users.verifyCreator')">{{ $t('panel.users.verify') }}</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="panelStore.usersTotalPages > 1" class="px-6 py-4 border-t border-[var(--color-border)] flex justify-between items-center">
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ $t('panel.users.pagination', { page: panelStore.usersPage, total: panelStore.usersTotalPages, count: panelStore.usersTotal }) }}
        </p>
        <div class="flex gap-2">
          <button @click="changePage(panelStore.usersPage - 1)" :disabled="panelStore.usersPage === 1" class="px-3 py-1 border border-[var(--color-border)] rounded hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] disabled:opacity-50">{{ $t('common.back') }}</button>
          <button @click="changePage(panelStore.usersPage + 1)" :disabled="panelStore.usersPage >= panelStore.usersTotalPages" class="px-3 py-1 border border-[var(--color-border)] rounded hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] disabled:opacity-50">{{ $t('common.next') }}</button>
        </div>
      </div>
    </div>

    <!-- Ban User Modal -->
    <div v-if="showBanModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">{{ $t('panel.users.banUser') }}</h3>
          <p class="text-sm text-gray-600 mt-1">{{ selectedUser?.first_name }} {{ selectedUser?.last_name }}</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.banReason') }} *</label>
            <textarea v-model="banForm.reason" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500" :placeholder="$t('panel.users.minChars')"></textarea>
          </div>
          <div class="mb-4">
            <label class="flex items-center">
              <input v-model="banForm.permanent" type="checkbox" class="rounded border-gray-300 text-red-600 focus:ring-red-500" />
              <span class="ml-2 text-sm text-gray-700">{{ $t('panel.users.permanentBan') }}</span>
            </label>
          </div>
          <div v-if="!banForm.permanent" class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.durationDays') }}</label>
            <input v-model.number="banForm.duration_days" type="number" min="1" max="365" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500" placeholder="30" />
          </div>
          <div class="mb-4">
            <label class="flex items-center">
              <input v-model="banForm.notify_user" type="checkbox" class="rounded border-gray-300 text-red-600 focus:ring-red-500" />
              <span class="ml-2 text-sm text-gray-700">{{ $t('panel.users.notifyByEmail') }}</span>
            </label>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button @click="closeBanModal" class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200">{{ $t('common.cancel') }}</button>
          <button @click="confirmBan" :disabled="!canSubmitBan" class="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed">{{ $t('panel.users.banUser') }}</button>
        </div>
      </div>
    </div>

    <!-- Unban User Modal -->
    <div v-if="showUnbanModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">{{ $t('panel.users.unbanUser') }}</h3>
          <p class="text-sm text-gray-600 mt-1">{{ selectedUser?.first_name }} {{ selectedUser?.last_name }}</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.unbanReason') }} *</label>
            <textarea v-model="unbanForm.reason" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500" :placeholder="$t('panel.users.minChars')"></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button @click="closeUnbanModal" class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200">{{ $t('common.cancel') }}</button>
          <button @click="confirmUnban" :disabled="!canSubmitUnban" class="px-4 py-2 text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed">{{ $t('panel.users.unbanUser') }}</button>
        </div>
      </div>
    </div>

    <!-- Grant Tokens Modal -->
    <div v-if="showGrantTokensModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">{{ $t('panel.users.grantTokens') }}</h3>
          <p class="text-sm text-gray-600 mt-1">{{ selectedUser?.first_name }} {{ selectedUser?.last_name }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ $t('panel.users.currentBalance') }}: {{ selectedUser?.token_balance || 0 }} Tokens</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.tokenAmount') }} *</label>
            <input v-model.number="grantTokensForm.amount" type="number" min="1" max="1000000" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500" placeholder="5000" />
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.reason') }} *</label>
            <textarea v-model="grantTokensForm.reason" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500" :placeholder="$t('panel.users.minChars')"></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button @click="closeGrantTokensModal" class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200">{{ $t('common.cancel') }}</button>
          <button @click="confirmGrantTokens" :disabled="!canSubmitGrantTokens" class="px-4 py-2 text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed">{{ $t('panel.users.grantTokens') }}</button>
        </div>
      </div>
    </div>

    <!-- Verify Creator Modal -->
    <div v-if="showVerifyCreatorModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">{{ $t('panel.users.verifyCreator') }}</h3>
          <p class="text-sm text-gray-600 mt-1">{{ selectedUser?.first_name }} {{ selectedUser?.last_name }}</p>
        </div>
        <div class="px-6 py-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.action') }} *</label>
            <select v-model="verifyCreatorForm.verified" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500">
              <option :value="true">{{ $t('panel.users.verify') }}</option>
              <option :value="false">{{ $t('panel.users.revokeVerification') }}</option>
            </select>
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.reason') }} *</label>
            <textarea v-model="verifyCreatorForm.reason" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500" :placeholder="$t('panel.users.minChars')"></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button @click="closeVerifyCreatorModal" class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200">{{ $t('common.cancel') }}</button>
          <button @click="confirmVerifyCreator" :disabled="!canSubmitVerifyCreator" class="px-4 py-2 text-white bg-yellow-600 rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed">
            {{ verifyCreatorForm.verified ? $t('panel.users.verify') : $t('panel.users.revoke') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { usePanelStore } from '@/application/stores/modules/admin/panel.store'
import { useUserManagement } from '@/presentation/components/panel/admin/users/composables/useUserManagement'

const panelStore = usePanelStore()

const {
  // Search & Filters
  searchQuery,
  roleFilter,
  statusFilter,
  debouncedSearch,
  loadUsers,
  resetFilters,
  changePage,

  // Navigation
  viewUserDetail,

  // Modal State
  showBanModal,
  showUnbanModal,
  showGrantTokensModal,
  showVerifyCreatorModal,
  selectedUser,

  // Form Data
  banForm,
  unbanForm,
  grantTokensForm,
  verifyCreatorForm,

  // Validations
  canSubmitBan,
  canSubmitUnban,
  canSubmitGrantTokens,
  canSubmitVerifyCreator,

  // Actions
  openBanModal,
  closeBanModal,
  confirmBan,
  openUnbanModal,
  closeUnbanModal,
  confirmUnban,
  openGrantTokensModal,
  closeGrantTokensModal,
  confirmGrantTokens,
  openVerifyCreatorModal,
  closeVerifyCreatorModal,
  confirmVerifyCreator,

  // Utility
  getRoleBadgeClass
} = useUserManagement()

onMounted(() => {
  loadUsers()
})
</script>
