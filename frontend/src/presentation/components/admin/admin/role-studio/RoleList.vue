<template>
  <div class="role-list">
    <!-- Search and Filter -->
    <div class="list-controls">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="$t('common.search')"
        class="search-input"
      />
      <select v-model="filterStudioMode" class="filter-select">
        <option value="">{{ $t('admin.roleStudio.allModes') }}</option>
        <option value="admin">Admin</option>
        <option value="moderator">Moderator</option>
        <option value="teacher">Teacher</option>
        <option value="user">User</option>
        <option value="guest">Guest</option>
      </select>
    </div>

    <!-- Roles Table -->
    <div class="table-container">
      <table class="roles-table">
        <thead>
          <tr>
            <th>{{ $t('admin.roleStudio.roleCode') }}</th>
            <th>{{ $t('admin.roleStudio.displayName') }}</th>
            <th>{{ $t('admin.roleStudio.studioMode') }}</th>
            <th>{{ $t('admin.roleStudio.permissions') }}</th>
            <th>{{ $t('admin.roleStudio.status') }}</th>
            <th>{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="role in filteredRoles" :key="role.role_code" class="role-row">
            <td class="role-code">{{ role.role_code }}</td>
            <td>{{ role.display_name }}</td>
            <td>
              <span class="studio-mode-badge">{{ role.studio_mode }}</span>
            </td>
            <td>
              <span class="permission-count">
                {{ Object.keys(role.permissions).length }}
                {{ $t('admin.roleStudio.permissions') }}
              </span>
            </td>
            <td>
              <span :class="['status-badge', role.is_active ? 'active' : 'inactive']">
                {{ role.is_active ? $t('common.active') : $t('common.inactive') }}
              </span>
            </td>
            <td class="actions">
              <button
                class="btn-small btn-view"
                @click="$emit('selectRole', role)"
                :title="$t('common.view')"
              >
                {{ $t('common.view') }}
              </button>
              <button
                v-if="role.is_active"
                class="btn-small btn-danger"
                @click="$emit('deactivateRole', role.role_code)"
                :title="$t('common.deactivate')"
              >
                {{ $t('common.deactivate') }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="filteredRoles.length === 0" class="empty-state">
        <p>{{ $t('admin.roleStudio.noRoles') }}</p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="pagination">
      <button
        class="btn-pagination"
        :disabled="page === 1"
        @click="$emit('pageChange', page - 1)"
      >
        {{ $t('common.previous') }}
      </button>

      <span class="page-info">
        {{ $t('common.page') }} {{ page }}
        {{ $t('common.of') }}
        {{ Math.ceil(total / pageSize) }}
      </span>

      <button
        class="btn-pagination"
        :disabled="page * pageSize >= total"
        @click="$emit('pageChange', page + 1)"
      >
        {{ $t('common.next') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { RoleStudioMode } from './types'

interface Props {
  roles: RoleStudioMode[]
  page: number
  pageSize: number
  total: number
}

interface Emits {
  selectRole: [role: RoleStudioMode]
  deactivateRole: [roleCode: string]
  pageChange: [page: number]
}

defineProps<Props>()
defineEmits<Emits>()

// Local state
const searchQuery = ref('')
const filterStudioMode = ref('')

// Computed
const filteredRoles = computed(() => {
  return defineProps().roles.filter(role => {
    const matchesSearch =
      role.role_code.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      role.display_name.toLowerCase().includes(searchQuery.value.toLowerCase())

    const matchesMode =
      !filterStudioMode.value || role.studio_mode === filterStudioMode.value

    return matchesSearch && matchesMode
  })
})
</script>

<style scoped>
.role-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.list-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-input,
.filter-select {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
}

.search-input {
  flex: 1;
  min-width: 250px;
}

.filter-select {
  min-width: 150px;
}

.table-container {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
}

.roles-table {
  width: 100%;
  border-collapse: collapse;
}

.roles-table thead {
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.roles-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
  text-transform: uppercase;
}

.roles-table td {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.role-row:hover {
  background-color: #f9fafb;
}

.role-code {
  font-family: 'Courier New', monospace;
  font-weight: 600;
}

.studio-mode-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background-color: #dbeafe;
  color: #1e40af;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.permission-count {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background-color: #f0fdf4;
  color: #166534;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-badge.active {
  background-color: #dcfce7;
  color: #166534;
}

.status-badge.inactive {
  background-color: #fee2e2;
  color: #991b1b;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-small {
  padding: 0.375rem 0.75rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-view {
  background-color: #dbeafe;
  color: #1e40af;
}

.btn-view:hover {
  background-color: #bfdbfe;
}

.btn-danger {
  background-color: #fee2e2;
  color: #991b1b;
}

.btn-danger:hover {
  background-color: #fecaca;
}

.empty-state {
  padding: 3rem 2rem;
  text-align: center;
  color: #6b7280;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
}

.btn-pagination {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background-color: white;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-pagination:hover:not(:disabled) {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.btn-pagination:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #6b7280;
  font-size: 0.875rem;
}
</style>
