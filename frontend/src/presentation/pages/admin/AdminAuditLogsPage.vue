<template>
  <div class="admin-audit-logs-page">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-[var(--color-text-primary)]">{{ $t('admin.auditLogs.title') }}</h1>
      <p class="text-[var(--color-text-secondary)] mt-1">{{ $t('admin.auditLogs.subtitle') }}</p>
    </div>
    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('admin.auditLogs.userId') }}</label>
          <input
            v-model.number="filters.user_id"
            type="number"
            :placeholder="$t('admin.auditLogs.userIdPlaceholder')"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('admin.auditLogs.action') }}</label>
          <select
            v-model="filters.action"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">{{ $t('admin.auditLogs.allActions') }}</option>
            <option value="ban_user">{{ $t('admin.auditLogs.actions.ban_user') }}</option>
            <option value="unban_user">{{ $t('admin.auditLogs.actions.unban_user') }}</option>
            <option value="grant_tokens">{{ $t('admin.auditLogs.actions.grant_tokens') }}</option>
            <option value="verify_creator">{{ $t('admin.auditLogs.actions.verify_creator') }}</option>
            <option value="update_role">{{ $t('admin.auditLogs.actions.update_role') }}</option>
            <option value="delete_user">{{ $t('admin.auditLogs.actions.delete_user') }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('admin.auditLogs.category') }}</label>
          <select
            v-model="filters.event_category"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">{{ $t('admin.auditLogs.allCategories') }}</option>
            <option value="user_management">{{ $t('admin.auditLogs.categories.user_management') }}</option>
            <option value="token_management">{{ $t('admin.auditLogs.categories.token_management') }}</option>
            <option value="auth">{{ $t('admin.auditLogs.categories.auth') }}</option>
            <option value="system">{{ $t('admin.auditLogs.categories.system') }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('admin.auditLogs.status') }}</label>
          <select
            v-model="filters.success"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">{{ $t('admin.auditLogs.allStatus') }}</option>
            <option :value="true">{{ $t('admin.auditLogs.successful') }}</option>
            <option :value="false">{{ $t('admin.auditLogs.failed') }}</option>
          </select>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('admin.auditLogs.dateFrom') }}</label>
          <input
            v-model="filters.from"
            type="date"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('admin.auditLogs.dateTo') }}</label>
          <input
            v-model="filters.to"
            type="date"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div class="flex items-end gap-2">
          <button
            @click="loadLogs"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            {{ $t('admin.auditLogs.applyFilter') }}
          </button>
          <button
            @click="resetFilters"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            {{ $t('admin.auditLogs.resetFilters') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Audit Logs Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200">
      <div v-if="adminStore.loading" class="p-8 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      </div>

      <div v-else-if="adminStore.auditLogs.length === 0" class="p-8 text-center text-gray-500">
        {{ $t('admin.auditLogs.noLogs') }}
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('admin.auditLogs.timestamp') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('admin.auditLogs.user') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('admin.auditLogs.action') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('admin.auditLogs.category') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('admin.auditLogs.description') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('admin.auditLogs.status') }}</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">{{ $t('admin.auditLogs.details') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="log in adminStore.auditLogs" :key="log.log_id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatDateTime(log.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ log.user_email || $t('admin.auditLogs.system') }}</div>
                <div class="text-xs text-gray-500">{{ log.user_role || '-' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                  {{ log.action }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {{ log.event_category || '-' }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-600 max-w-md truncate">
                {{ log.description || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span v-if="log.success" class="text-green-600 text-sm">✓ {{ $t('admin.auditLogs.success') }}</span>
                <span v-else class="text-red-600 text-sm">✗ {{ $t('admin.auditLogs.error') }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                <button
                  @click="viewLogDetail(log)"
                  class="text-blue-600 hover:text-blue-900"
                >
                  {{ $t('admin.auditLogs.view') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div
        v-if="adminStore.auditLogsTotalPages > 1"
        class="px-6 py-4 border-t border-gray-200 flex justify-between items-center"
      >
        <p class="text-sm text-gray-600">
          {{ $t('admin.auditLogs.pagination', { page: adminStore.auditLogsPage, total: adminStore.auditLogsTotalPages, count: adminStore.auditLogsTotal }) }}
        </p>
        <div class="flex gap-2">
          <button
            @click="changePage(adminStore.auditLogsPage - 1)"
            :disabled="adminStore.auditLogsPage === 1"
            class="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
          >
            {{ $t('admin.auditLogs.prev') }}
          </button>
          <button
            @click="changePage(adminStore.auditLogsPage + 1)"
            :disabled="adminStore.auditLogsPage >= adminStore.auditLogsTotalPages"
            class="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
          >
            {{ $t('admin.auditLogs.next') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Log Detail Modal -->
    <div v-if="selectedLog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-auto">
        <div class="px-6 py-4 border-b border-gray-200 sticky top-0 bg-white">
          <h3 class="text-lg font-semibold text-gray-900">{{ $t('admin.auditLogs.logDetails') }}</h3>
        </div>
        <div class="px-6 py-4">
          <dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.logId') }}</dt>
              <dd class="text-sm text-gray-900 mt-1">{{ selectedLog.log_id }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.timestamp') }}</dt>
              <dd class="text-sm text-gray-900 mt-1">{{ formatDateTime(selectedLog.created_at) }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.userEmail') }}</dt>
              <dd class="text-sm text-gray-900 mt-1">{{ selectedLog.user_email || $t('admin.auditLogs.system') }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.userRole') }}</dt>
              <dd class="text-sm text-gray-900 mt-1">{{ selectedLog.user_role || '-' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.action') }}</dt>
              <dd class="text-sm text-gray-900 mt-1">{{ selectedLog.action }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.category') }}</dt>
              <dd class="text-sm text-gray-900 mt-1">{{ selectedLog.event_category || '-' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.resourceType') }}</dt>
              <dd class="text-sm text-gray-900 mt-1">{{ selectedLog.resource_type || '-' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.resourceId') }}</dt>
              <dd class="text-sm text-gray-900 mt-1">{{ selectedLog.resource_id || '-' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.ipAddress') }}</dt>
              <dd class="text-sm text-gray-900 mt-1">{{ selectedLog.ip_address || '-' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.sessionId') }}</dt>
              <dd class="text-sm text-gray-900 mt-1 truncate">{{ selectedLog.session_id || '-' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.status') }}</dt>
              <dd class="text-sm mt-1">
                <span v-if="selectedLog.success" class="text-green-600">✓ {{ $t('admin.auditLogs.successful') }}</span>
                <span v-else class="text-red-600">✗ {{ $t('admin.auditLogs.failed') }}</span>
              </dd>
            </div>
            <div v-if="!selectedLog.success && selectedLog.error_message" class="col-span-2">
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.errorMessage') }}</dt>
              <dd class="text-sm text-red-600 mt-1">{{ selectedLog.error_message }}</dd>
            </div>
            <div class="col-span-2">
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.description') }}</dt>
              <dd class="text-sm text-gray-900 mt-1">{{ selectedLog.description || '-' }}</dd>
            </div>
            <div class="col-span-2">
              <dt class="text-sm font-medium text-gray-500">{{ $t('admin.auditLogs.userAgent') }}</dt>
              <dd class="text-sm text-gray-900 mt-1 break-all">{{ selectedLog.user_agent || '-' }}</dd>
            </div>
            <div v-if="selectedLog.meta" class="col-span-2">
              <dt class="text-sm font-medium text-gray-500 mb-2">{{ $t('admin.auditLogs.metadata') }}</dt>
              <dd class="text-xs text-gray-900 bg-gray-50 p-3 rounded border border-gray-200 overflow-auto">
                <pre>{{ JSON.stringify(selectedLog.meta, null, 2) }}</pre>
              </dd>
            </div>
          </dl>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end sticky bottom-0 bg-white">
          <button
            @click="closeLogDetail"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            {{ $t('admin.auditLogs.close') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAdminStore } from '@/application/stores/admin.store'
import type { AuditLog, AuditLogsFilterParams } from '@/infrastructure/api/admin.api'

const { locale } = useI18n()
const adminStore = useAdminStore()

const filters = reactive<AuditLogsFilterParams>({
  user_id: undefined,
  action: '',
  event_category: '',
  from: '',
  to: '',
  success: undefined,
  page: 1,
  limit: 20
})

const selectedLog = ref<AuditLog | null>(null)

const loadLogs = async () => {
  const params: AuditLogsFilterParams = {
    page: filters.page,
    limit: filters.limit
  }

  if (filters.user_id) params.user_id = filters.user_id
  if (filters.action) params.action = filters.action
  if (filters.event_category) params.event_category = filters.event_category
  if (filters.from) params.from = filters.from
  if (filters.to) params.to = filters.to
  if (filters.success !== undefined && filters.success !== '') params.success = filters.success

  await adminStore.loadAuditLogs(params)
}

const resetFilters = () => {
  filters.user_id = undefined
  filters.action = ''
  filters.event_category = ''
  filters.from = ''
  filters.to = ''
  filters.success = undefined
  filters.page = 1
  loadLogs()
}

const changePage = (page: number) => {
  filters.page = page
  loadLogs()
}

const viewLogDetail = (log: AuditLog) => {
  selectedLog.value = log
}

const closeLogDetail = () => {
  selectedLog.value = null
}

const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  const localeMap: Record<string, string> = {
    de: 'de-DE',
    en: 'en-US',
    pl: 'pl-PL'
  }
  return date.toLocaleString(localeMap[locale.value] || 'de-DE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  loadLogs()
})
</script>
