<template>
  <div class="role-management-page p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="header mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {{ $t('admin.groups.title') }}
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            {{ $t('admin.groups.subtitle') }}
          </p>
          <div class="mt-2 flex items-center space-x-2 text-sm text-purple-600 dark:text-purple-400">
            <span class="inline-block px-2 py-1 bg-purple-100 dark:bg-purple-900 rounded">
              👑 {{ $t('admin.groups.ownerOnly') }}
            </span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3">
          <button
            @click="showTemplateSelector = true"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium flex items-center space-x-2"
          >
            <span>📋</span>
            <span>{{ $t('admin.groups.templates.title') }}</span>
          </button>

          <button
            @click="openCreateModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center space-x-2"
          >
            <span>➕</span>
            <span>{{ $t('admin.groups.createCustom') }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Error Alert -->
    <div
      v-if="rolesStore.error"
      class="mb-6 p-4 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 rounded-lg flex items-center justify-between"
    >
      <div class="flex items-center space-x-2 text-red-800 dark:text-red-200">
        <span>⚠️</span>
        <span>{{ rolesStore.error }}</span>
      </div>
      <button
        @click="rolesStore.clearError()"
        class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
      >
        ✕
      </button>
    </div>

    <!-- Roles List -->
    <GroupList
      :roles="rolesStore.roles"
      :loading="rolesStore.loading"
      @view-details="handleViewDetails"
      @edit="handleEdit"
      @delete="handleDelete"
      @assign-features="handleAssignFeatures"
      @assign-permissions="handleAssignPermissions"
    />

    <!-- Create/Edit Modal -->
    <div
      v-if="showFormModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto"
      @click.self="closeFormModal"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full my-8">
        <div class="p-6">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            {{ currentRole ? $t('admin.groups.edit') : $t('admin.groups.create') }}
          </h2>

          <GroupForm
            :role="currentRole"
            :available-features="systemFeatures"
            :available-permissions="availablePermissions"
            @submit="handleFormSubmit"
            @cancel="closeFormModal"
          />
        </div>
      </div>
    </div>

    <!-- Permission Matrix Modal -->
    <div
      v-if="showPermissionMatrix"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto"
      @click.self="showPermissionMatrix = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-6xl w-full my-8">
        <div class="p-6">
          <PermissionMatrix
            v-if="currentRole"
            :role="currentRole"
            :available-features="systemFeatures"
            :available-permissions="availablePermissions"
            @submit="handlePermissionSubmit"
            @cancel="showPermissionMatrix = false"
          />
        </div>
      </div>
    </div>

    <!-- Template Selector Modal -->
    <div
      v-if="showTemplateSelector"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto"
      @click.self="showTemplateSelector = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-6xl w-full my-8">
        <div class="p-6">
          <GroupTemplateSelector
            :templates="rolesStore.templates"
            :available-features="systemFeatures"
            :loading="rolesStore.loading"
            @create="handleTemplateCreate"
          />
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteConfirm"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showDeleteConfirm = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">
          {{ $t('admin.groups.delete') }}
        </h3>

        <p class="text-gray-600 dark:text-gray-400 mb-4">
          {{ $t('admin.groups.deleteWarning') }}
        </p>

        <div v-if="roleToDelete && roleToDelete.user_count && roleToDelete.user_count > 0" class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('admin.groups.reassignTo') }} *
          </label>
          <select
            v-model="reassignToRoleId"
            required
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          >
            <option value="">{{ $t('admin.groups.selectTargetRole') }}</option>
            <option
              v-for="role in rolesStore.roles.filter((r) => r.role_id !== roleToDelete?.role_id)"
              :key="role.role_id"
              :value="role.role_id"
            >
              {{ role.display_name }} ({{ role.user_count || 0 }} {{ $t('admin.groups.userCount') }})
            </option>
          </select>
        </div>

        <div class="flex justify-end gap-3">
          <button
            @click="showDeleteConfirm = false"
            class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>

          <button
            @click="confirmDelete"
            :disabled="roleToDelete && roleToDelete.user_count && roleToDelete.user_count > 0 && !reassignToRoleId"
            class="px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ $t('admin.groups.delete') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Admin Roles Management Page (RBAC 2.0)
 * =======================================
 * Owner-Admin can create custom roles, assign features/permissions,
 * and manage role templates.
 *
 * Features:
 * - Create/Edit/Delete custom roles
 * - Assign system features (25 features) to roles
 * - Assign permissions to roles
 * - Create roles from templates (Parent, Enterprise Admin, etc.)
 * - Role statistics (user count, feature count, permission count)
 *
 * Components:
 * - RoleList: Displays all roles with filters
 * - RoleForm: Create/edit form with validation
 * - PermissionMatrix: Feature/permission assignment UI
 * - RoleTemplateSelector: Template-based role creation
 */
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useGroupsStore } from '@/application/stores/modules/admin/groups.store'
import { getSystemFeatures, getPermissions } from '@/application/services/api/admin'
import type { RoleWithStats, SystemFeature, Permission, CreateRoleRequest, CreateFromTemplateRequest } from '@/application/services/api/admin'
import { GroupList, GroupForm, PermissionMatrix, GroupTemplateSelector } from '@/presentation/components/base/admin-ui/user-management/groups'

const { t } = useI18n()
const rolesStore = useGroupsStore()

// Local state
const showFormModal = ref(false)
const showPermissionMatrix = ref(false)
const showTemplateSelector = ref(false)
const showDeleteConfirm = ref(false)
const currentRole = ref<RoleWithStats | null>(null)
const roleToDelete = ref<RoleWithStats | null>(null)
const reassignToRoleId = ref<number | null>(null)
const systemFeatures = ref<SystemFeature[]>([])
const availablePermissions = ref<Permission[]>([])

// Initialize
onMounted(async () => {
  await Promise.all([
    rolesStore.fetchRoles({ include_features: true, include_permissions: true }),
    rolesStore.fetchTemplates(),
    loadSystemFeatures(),
    loadPermissions()
  ])
})

async function loadSystemFeatures() {
  try {
    systemFeatures.value = await getSystemFeatures()
  } catch (error) {
    console.error('Failed to load system features:', error)
  }
}

async function loadPermissions() {
  try {
    const result = await getPermissions()
    availablePermissions.value = Array.isArray(result) ? result : []
  } catch (error) {
    console.error('Failed to load permissions:', error)
  }
}

function openCreateModal() {
  currentRole.value = null
  showFormModal.value = true
}

function closeFormModal() {
  showFormModal.value = false
  currentRole.value = null
}

function handleViewDetails(role: RoleWithStats) {
  rolesStore.fetchRole(role.role_id)
  // TODO: Show details modal or navigate to details page
  console.log('View details:', role)
}

function handleEdit(role: RoleWithStats) {
  currentRole.value = role
  showFormModal.value = true
}

function handleDelete(role: RoleWithStats) {
  roleToDelete.value = role
  reassignToRoleId.value = null
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  if (!roleToDelete.value) return

  try {
    await rolesStore.deleteRole(roleToDelete.value.role_id, reassignToRoleId.value || undefined)
    showDeleteConfirm.value = false
    roleToDelete.value = null
    reassignToRoleId.value = null
  } catch (error) {
    console.error('Delete failed:', error)
  }
}

function handleAssignFeatures(role: RoleWithStats) {
  currentRole.value = role
  showPermissionMatrix.value = true
}

function handleAssignPermissions(role: RoleWithStats) {
  currentRole.value = role
  showPermissionMatrix.value = true
}

async function handleFormSubmit(data: CreateRoleRequest) {
  try {
    if (currentRole.value) {
      await rolesStore.updateRole(currentRole.value.role_id, data)
    } else {
      await rolesStore.createRole(data)
    }
    closeFormModal()
    await rolesStore.fetchRoles()
  } catch (error) {
    console.error('Form submit failed:', error)
  }
}

async function handlePermissionSubmit(data: { type: 'features' | 'permissions'; ids: number[]; replace: boolean }) {
  if (!currentRole.value) return

  try {
    if (data.type === 'features') {
      await rolesStore.assignFeatures(currentRole.value.role_id, {
        feature_ids: data.ids,
        replace: data.replace
      })
    } else {
      await rolesStore.assignPermissions(currentRole.value.role_id, {
        permission_ids: data.ids,
        replace: data.replace
      })
    }
    showPermissionMatrix.value = false
    await rolesStore.fetchRoles()
  } catch (error) {
    console.error('Permission assignment failed:', error)
  }
}

async function handleTemplateCreate(data: CreateFromTemplateRequest) {
  try {
    await rolesStore.createFromTemplate(data)
    showTemplateSelector.value = false
    await rolesStore.fetchRoles()
  } catch (error) {
    console.error('Template create failed:', error)
  }
}
</script>

<style scoped>
.role-management-page {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
