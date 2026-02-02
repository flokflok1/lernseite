<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        {{ $t('panel.groups.title') }}
      </h1>
      <p class="text-gray-600 dark:text-gray-400 mt-1">
        {{ $t('panel.groups.subtitle') }}
      </p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-2 mb-6 border-b border-gray-200 dark:border-gray-700">
      <button
        @click="activeTab = 'roles'"
        :class="[
          'px-4 py-2 font-medium border-b-2 -mb-px transition-colors',
          activeTab === 'roles'
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        ]"
      >
        {{ $t('panel.groups.tabRoles') }}
      </button>
      <button
        @click="activeTab = 'permissions'"
        :class="[
          'px-4 py-2 font-medium border-b-2 -mb-px transition-colors',
          activeTab === 'permissions'
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        ]"
      >
        {{ $t('panel.groups.tabPermissions') }}
      </button>
    </div>

    <!-- Roles Tab -->
    <div v-if="activeTab === 'roles'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Roles List -->
      <div class="lg:col-span-1">
        <RolesListView
          :system-roles="systemRoles"
          :custom-roles="customRoles"
          :selected-role-id="selectedRole?.role_id"
          @select="selectRole"
          @create="openCreateModal"
          @delete="handleDeleteRole"
        />
      </div>

      <!-- Role Details -->
      <div class="lg:col-span-2">
        <RoleDetailsPanel
          :role="selectedRole"
          :users="roleUsers"
          :available-permissions="permissions"
          @edit="openEditModal"
          @save-permissions="handleSavePermissions"
        />
      </div>
    </div>

    <!-- Permissions Tab -->
    <PermissionsOverview
      v-if="activeTab === 'permissions'"
      :permissions="permissions"
    />

    <!-- Create/Edit Modal -->
    <RoleEditModal
      :show="showModal"
      :mode="modalMode"
      :role="selectedRole"
      @close="showModal = false"
      @save="handleSaveRole"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * Admin Roles & Permissions Page
 * ===============================
 * Orchestrator page for roles management.
 * Uses sub-components from components/panel/user-management/groups/
 */
import { ref, onMounted } from 'vue'
import {
  RolesListView,
  RoleDetailsPanel,
  RoleEditModal,
  PermissionsOverview,
  useRolesManagement,
  type RoleFormData
} from '@/presentation/components/users/panel/groups'
import type { Role } from '@/application/services/api/admin'

const {
  // State
  selectedRole,
  roleUsers,
  permissions,
  // Computed
  systemRoles,
  customRoles,
  // Methods
  selectRole,
  createRole,
  updateRole,
  deleteRole,
  setRolePermissions,
  initialize
} = useRolesManagement()

const activeTab = ref<'roles' | 'permissions'>('roles')

// Modal state
const showModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')

function openCreateModal() {
  modalMode.value = 'create'
  showModal.value = true
}

function openEditModal(role: Role) {
  if (role.is_system) return
  modalMode.value = 'edit'
  showModal.value = true
}

async function handleSaveRole(data: RoleFormData) {
  let success = false

  if (modalMode.value === 'create') {
    success = await createRole(data)
  } else if (selectedRole.value) {
    success = await updateRole(selectedRole.value.role_id, data)
  }

  if (success) {
    showModal.value = false
  }
}

async function handleDeleteRole(role: Role) {
  await deleteRole(role)
}

async function handleSavePermissions(permissionIds: number[]) {
  if (!selectedRole.value) return
  await setRolePermissions(selectedRole.value.role_id, permissionIds)
}

// Initialize on mount
onMounted(() => {
  initialize()
})
</script>
