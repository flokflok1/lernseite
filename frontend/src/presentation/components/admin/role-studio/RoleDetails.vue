<template>
  <div class="role-details">
    <!-- Header -->
    <div class="details-header">
      <h2>{{ $t('admin.roleStudio.roleDetails') }}</h2>
      <button class="btn-close" @click="$emit('close')" :title="$t('common.close')">×</button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <!-- Role Not Found -->
    <div v-else-if="!role" class="empty-state">
      <p>{{ $t('admin.roleStudio.roleNotFound') }}</p>
    </div>

    <!-- Role Details -->
    <div v-else class="details-container">
      <!-- Role Information Section -->
      <div class="details-section">
        <h3>{{ $t('admin.roleStudio.roleInformation') }}</h3>

        <div class="info-grid">
          <div class="info-item">
            <label>{{ $t('admin.roleStudio.roleCode') }}</label>
            <p class="info-value role-code">{{ role.role_code }}</p>
          </div>

          <div class="info-item">
            <label>{{ $t('admin.roleStudio.displayName') }}</label>
            <p class="info-value">{{ role.display_name }}</p>
          </div>

          <div class="info-item">
            <label>{{ $t('admin.roleStudio.studioMode') }}</label>
            <span class="studio-mode-badge">{{ role.studio_mode }}</span>
          </div>

          <div class="info-item">
            <label>{{ $t('common.status') }}</label>
            <span :class="['status-badge', role.is_active ? 'active' : 'inactive']">
              {{ role.is_active ? $t('common.active') : $t('common.inactive') }}
            </span>
          </div>

          <div class="info-item" v-if="role.description">
            <label>{{ $t('admin.roleStudio.description') }}</label>
            <p class="info-value">{{ role.description }}</p>
          </div>

          <div class="info-item">
            <label>{{ $t('admin.roleStudio.requiresOrganization') }}</label>
            <p class="info-value">
              {{ role.requires_organization ? $t('common.yes') : $t('common.no') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Permissions Section -->
      <div class="details-section">
        <h3>{{ $t('admin.roleStudio.permissions') }}</h3>
        <div class="permissions-display">
          <div v-if="Object.keys(role.permissions).length === 0" class="no-permissions">
            <p>{{ $t('admin.roleStudio.noPermissions') }}</p>
          </div>
          <div v-else class="permissions-list">
            <div
              v-for="(hasPermission, permissionName) in role.permissions"
              :key="permissionName"
              :class="['permission-row', { granted: hasPermission }]"
            >
              <span class="permission-name">{{ permissionName }}</span>
              <span :class="['permission-status', hasPermission ? 'granted' : 'denied']">
                {{ hasPermission ? $t('common.granted') : $t('common.denied') }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Metadata Section -->
      <div class="details-section">
        <h3>{{ $t('common.metadata') }}</h3>
        <div class="metadata-grid">
          <div class="metadata-item">
            <label>{{ $t('common.createdAt') }}</label>
            <p class="metadata-value">{{ formatDate(role.created_at) }}</p>
          </div>
          <div class="metadata-item" v-if="role.updated_at">
            <label>{{ $t('common.updatedAt') }}</label>
            <p class="metadata-value">{{ formatDate(role.updated_at) }}</p>
          </div>
        </div>
      </div>

      <!-- Change History Section -->
      <div class="details-section">
        <div class="history-header">
          <h3>{{ $t('admin.roleStudio.changeHistory') }}</h3>
          <button
            v-if="!historyLoading && !history.length"
            class="btn-small btn-load"
            @click="loadHistory"
            :title="$t('admin.roleStudio.loadHistory')"
          >
            {{ $t('admin.roleStudio.loadHistory') }}
          </button>
        </div>

        <div v-if="historyLoading" class="history-loading">
          <div class="spinner"></div>
          <p>{{ $t('common.loading') }}</p>
        </div>

        <div v-else-if="history.length === 0" class="empty-state">
          <p>{{ $t('admin.roleStudio.noChangeHistory') }}</p>
        </div>

        <div v-else class="history-list">
          <div v-for="(entry, index) in history" :key="index" class="history-entry">
            <!-- Change timestamp and user -->
            <div class="history-meta">
              <span class="history-date">{{ formatDate(entry.changed_at) }}</span>
              <span class="history-user" v-if="entry.changed_by">
                by {{ entry.changed_by }}
              </span>
            </div>

            <!-- Changed fields -->
            <div class="history-changes">
              <div v-if="entry.previous_display_name !== entry.new_display_name" class="change-item">
                <span class="field-name">{{ $t('admin.roleStudio.displayName') }}</span>
                <span class="change-value">
                  <span class="old-value">{{ entry.previous_display_name }}</span>
                  <span class="arrow">→</span>
                  <span class="new-value">{{ entry.new_display_name }}</span>
                </span>
              </div>

              <div v-if="entry.previous_studio_mode !== entry.new_studio_mode" class="change-item">
                <span class="field-name">{{ $t('admin.roleStudio.studioMode') }}</span>
                <span class="change-value">
                  <span class="old-value">{{ entry.previous_studio_mode }}</span>
                  <span class="arrow">→</span>
                  <span class="new-value">{{ entry.new_studio_mode }}</span>
                </span>
              </div>

              <div
                v-if="entry.previous_permissions !== entry.new_permissions"
                class="change-item"
              >
                <span class="field-name">{{ $t('admin.roleStudio.permissions') }}</span>
                <span class="change-value">
                  {{ $t('admin.roleStudio.permissionsChanged') }}
                </span>
              </div>
            </div>

            <!-- Change reason -->
            <div v-if="entry.change_reason" class="history-reason">
              <span class="reason-label">{{ $t('admin.roleStudio.changeReason') }}:</span>
              <span class="reason-value">{{ entry.change_reason }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="details-actions">
        <button class="btn-primary" @click="$emit('edit')" :disabled="!role.is_active">
          {{ $t('common.edit') }}
        </button>
        <button class="btn-secondary" @click="$emit('close')">
          {{ $t('common.close') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { RoleStudioMode, RoleChangeHistory } from './types'

interface Props {
  role: RoleStudioMode | null
  history: RoleChangeHistory[]
}

interface Emits {
  (e: 'edit'): void
  (e: 'close'): void
  (e: 'fetch-history', roleCode: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

const isLoading = ref(false)
const historyLoading = ref(false)
const history = ref<RoleChangeHistory[]>([])

// Watch for changes to role
watch(
  () => props.role,
  (newRole) => {
    if (newRole) {
      history.value = []
    }
  }
)

// Watch for history changes from parent
watch(
  () => props.history,
  (newHistory) => {
    history.value = newHistory || []
    historyLoading.value = false
  }
)

// Format date helper
const formatDate = (dateString: string | null | undefined): string => {
  if (!dateString) return '-'

  try {
    const date = new Date(dateString)
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return dateString
  }
}

// Load change history
const loadHistory = async () => {
  if (!props.role) return

  historyLoading.value = true
  emit('fetch-history', props.role.role_code)
}
</script>

<style scoped>
.role-details {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-height: 80vh;
  overflow-y: auto;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 1rem;
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
}

.details-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  color: #111827;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.details-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.details-section {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.details-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item label {
  font-weight: 500;
  color: #6b7280;
  font-size: 0.875rem;
  text-transform: uppercase;
}

.info-value {
  margin: 0;
  color: #111827;
  word-break: break-word;
}

.role-code {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  background-color: #f3f4f6;
  padding: 0.5rem;
  border-radius: 0.25rem;
}

.studio-mode-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background-color: #dbeafe;
  color: #1e40af;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  width: fit-content;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  width: fit-content;
}

.status-badge.active {
  background-color: #dcfce7;
  color: #166534;
}

.status-badge.inactive {
  background-color: #fee2e2;
  color: #991b1b;
}

.permissions-display {
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.no-permissions {
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
  text-align: center;
  color: #6b7280;
}

.permissions-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.permission-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  background-color: #f9fafb;
}

.permission-row.granted {
  background-color: #f0fdf4;
  border-color: #dcfce7;
}

.permission-name {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.permission-status {
  font-size: 0.875rem;
  font-weight: 500;
}

.permission-status.granted {
  color: #166534;
}

.permission-status.denied {
  color: #9ca3af;
}

.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.metadata-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metadata-item label {
  font-weight: 500;
  color: #6b7280;
  font-size: 0.875rem;
}

.metadata-value {
  margin: 0;
  color: #111827;
  font-size: 0.875rem;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.history-entry {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  background-color: #f9fafb;
}

.history-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.history-date {
  font-weight: 600;
  color: #111827;
}

.history-user {
  color: #6b7280;
}

.history-changes {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.change-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: white;
  border-radius: 0.375rem;
  border-left: 3px solid #3b82f6;
  padding-left: 0.75rem;
}

.field-name {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.change-value {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.old-value {
  background-color: #fee2e2;
  color: #991b1b;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.arrow {
  color: #9ca3af;
  font-weight: 600;
}

.new-value {
  background-color: #dcfce7;
  color: #166534;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.history-reason {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
  padding: 0.5rem;
  background: white;
  border-radius: 0.375rem;
  border-left: 3px solid #f59e0b;
  padding-left: 0.75rem;
}

.reason-label {
  font-weight: 500;
  color: #9ca3af;
}

.reason-value {
  color: #374151;
  flex: 1;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: #6b7280;
  background-color: #f9fafb;
  border-radius: 0.5rem;
}

.empty-state p {
  margin: 0;
}

.details-actions {
  display: flex;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background-color: #f3f4f6;
  color: #111827;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

.btn-small {
  padding: 0.375rem 0.75rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-load {
  background-color: #dbeafe;
  color: #1e40af;
}

.btn-load:hover {
  background-color: #bfdbfe;
}
</style>
