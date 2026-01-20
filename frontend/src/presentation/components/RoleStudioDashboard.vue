<template>
  <div class="role-studio-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div>
        <h1 class="dashboard-title">{{ $t('admin.roleStudio.title') }}</h1>
        <p class="dashboard-subtitle">{{ $t('admin.roleStudio.subtitle') }}</p>
      </div>
      <button class="btn-primary" @click="handleCreateRole">
        {{ $t('admin.roleStudio.createRole') }}
      </button>
    </div>

    <!-- Tab Navigation -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <p class="error-message">{{ error }}</p>
      <button class="btn-secondary" @click="clearError">
        {{ $t('common.dismiss') }}
      </button>
    </div>

    <!-- Role List -->
    <div v-else-if="activeTab === 'all-roles'" class="tab-content">
      <RoleList
        :roles="sortedRoles"
        :page="currentPage"
        :page-size="pageSize"
        :total="totalRoles"
        @select-role="handleSelectRole"
        @deactivate-role="handleDeactivateRole"
        @page-change="setCurrentPage"
      />
    </div>

    <!-- Active Roles -->
    <div v-else-if="activeTab === 'active-roles'" class="tab-content">
      <RoleList
        :roles="activeRoles"
        :page="1"
        :page-size="pageSize"
        :total="activeRoles.length"
        @select-role="handleSelectRole"
      />
    </div>

    <!-- Organization Roles -->
    <div v-else-if="activeTab === 'org-roles'" class="tab-content">
      <RoleList
        :roles="organizationRoles"
        :page="1"
        :page-size="pageSize"
        :total="organizationRoles.length"
        @select-role="handleSelectRole"
      />
    </div>

    <!-- Role Editor Modal -->
    <div v-if="showEditor" class="modal-overlay" @click.self="closeEditor">
      <div class="modal-content">
        <RoleEditor
          :role="selectedRole"
          :is-new="isNewRole"
          @save="handleSaveRole"
          @cancel="closeEditor"
        />
      </div>
    </div>

    <!-- Role Details Modal -->
    <div v-if="showDetails && selectedRole" class="modal-overlay" @click.self="closeDetails">
      <div class="modal-content">
        <RoleDetails
          :role="selectedRole"
          :history="changeHistory"
          @edit="showEditor = true"
          @close="closeDetails"
          @fetch-history="fetchChangeHistory"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoleStudio } from './composables'
import type { RoleStudioMode } from './types'
import RoleList from './RoleList.vue'
import RoleEditor from './RoleEditor.vue'
import RoleDetails from './RoleDetails.vue'

const { t } = useI18n()

// Use composable
const {
  roles,
  selectedRole,
  loading,
  error,
  totalRoles,
  currentPage,
  pageSize,
  changeHistory,
  sortedRoles,
  activeRoles,
  organizationRoles,
  fetchRoles,
  createRole,
  updateRole,
  deactivateRole,
  fetchChangeHistory,
  selectRole,
  clearSelection,
  clearError,
  setCurrentPage
} = useRoleStudio()

// Local state
const activeTab = ref<'all-roles' | 'active-roles' | 'org-roles'>('all-roles')
const showEditor = ref(false)
const showDetails = ref(false)
const isNewRole = ref(false)

// Tabs configuration
const tabs = computed(() => [
  {
    id: 'all-roles' as const,
    label: t('admin.roleStudio.tabs.allRoles')
  },
  {
    id: 'active-roles' as const,
    label: t('admin.roleStudio.tabs.activeRoles')
  },
  {
    id: 'org-roles' as const,
    label: t('admin.roleStudio.tabs.organizationRoles')
  }
])

// Handlers
async function handleCreateRole() {
  selectedRole.value = null
  isNewRole.value = true
  showEditor.value = true
}

function handleSelectRole(role: RoleStudioMode) {
  selectRole(role)
  showDetails.value = true
}

function closeEditor() {
  showEditor.value = false
  clearSelection()
}

function closeDetails() {
  showDetails.value = false
  clearSelection()
}

async function handleSaveRole(roleData: any) {
  try {
    if (isNewRole.value) {
      await createRole(roleData)
    } else {
      const roleCode = selectedRole.value?.role_code
      if (roleCode) {
        await updateRole(roleCode, roleData)
      }
    }
    closeEditor()
    await fetchRoles()
  } catch (err) {
    console.error('[RoleStudioDashboard] Error saving role:', err)
  }
}

async function handleDeactivateRole(roleCode: string) {
  if (confirm(t('admin.roleStudio.confirmDeactivate'))) {
    try {
      await deactivateRole(roleCode)
      await fetchRoles()
    } catch (err) {
      console.error('[RoleStudioDashboard] Error deactivating role:', err)
    }
  }
}
</script>

<style scoped>
.role-studio-dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.dashboard-title {
  font-size: 2rem;
  font-weight: bold;
  margin: 0 0 0.5rem 0;
  color: #111827;
}

.dashboard-subtitle {
  color: #6b7280;
  margin: 0;
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

.btn-primary:hover {
  background-color: #2563eb;
}

.tabs {
  display: flex;
  gap: 1rem;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 2rem;
}

.tab {
  padding: 1rem 1.5rem;
  background: none;
  border: none;
  color: #6b7280;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab:hover {
  color: #111827;
}

.tab.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.tab-content {
  padding: 1rem 0;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-container {
  background-color: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.error-message {
  color: #991b1b;
  margin: 0;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background-color: #f3f4f6;
  color: #111827;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 0.75rem;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
</style>
