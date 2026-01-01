<script setup lang="ts">
/**
 * Admin Roles & Permissions Page
 * ===============================
 * Manage roles, permissions, and user assignments.
 */
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import rolesApi, {
  type Role,
  type Permission,
  type RoleUser
} from '@/api/admin/roles.api'

const { t } = useI18n()

// State
const roles = ref<Role[]>([])
const permissions = ref<Record<string, Permission[]>>({})
const selectedRole = ref<Role | null>(null)
const roleUsers = ref<RoleUser[]>([])
const loading = ref(false)
const activeTab = ref<'roles' | 'permissions'>('roles')

// Create/Edit Modal
const showModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const modalForm = ref({
  role_name: '',
  display_name: '',
  description: '',
  hierarchy_level: 1,
  color: '#6b7280',
  icon: 'user'
})

// Permission editing
const editingPermissions = ref(false)
const selectedPermissionIds = ref<number[]>([])

// Icons for roles
const roleIcons = [
  'user', 'users', 'crown', 'shield', 'star', 'award', 'briefcase',
  'school', 'building', 'wrench', 'cog', 'eye', 'book', 'graduation-cap'
]

// Colors for roles
const roleColors = [
  '#6b7280', '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#6366f1'
]

// Computed
const systemRoles = computed(() => roles.value.filter(r => r.is_system))
const customRoles = computed(() => roles.value.filter(r => r.is_custom))

// Load data
async function loadRoles() {
  loading.value = true
  try {
    roles.value = await rolesApi.getRoles(true)
  } catch (e) {
    console.error('Failed to load roles:', e)
  } finally {
    loading.value = false
  }
}

async function loadPermissions() {
  try {
    permissions.value = await rolesApi.getPermissionsGrouped()
  } catch (e) {
    console.error('Failed to load permissions:', e)
  }
}

async function selectRole(role: Role) {
  selectedRole.value = role
  editingPermissions.value = false

  try {
    const [fullRole, users] = await Promise.all([
      rolesApi.getRole(role.role_id),
      rolesApi.getRoleUsers(role.role_id, 50)
    ])
    selectedRole.value = fullRole
    roleUsers.value = users
    selectedPermissionIds.value = fullRole.permissions?.map(p => p.permission_id) || []
  } catch (e) {
    console.error('Failed to load role details:', e)
  }
}

// CRUD operations
function openCreateModal() {
  modalMode.value = 'create'
  modalForm.value = {
    role_name: '',
    display_name: '',
    description: '',
    hierarchy_level: 1,
    color: '#6b7280',
    icon: 'user'
  }
  showModal.value = true
}

function openEditModal(role: Role) {
  if (role.is_system) return
  modalMode.value = 'edit'
  modalForm.value = {
    role_name: role.role_name,
    display_name: role.display_name,
    description: role.description || '',
    hierarchy_level: role.hierarchy_level,
    color: role.color,
    icon: role.icon
  }
  showModal.value = true
}

async function saveRole() {
  try {
    if (modalMode.value === 'create') {
      await rolesApi.createRole(modalForm.value)
    } else if (selectedRole.value) {
      await rolesApi.updateRole(selectedRole.value.role_id, modalForm.value)
    }
    showModal.value = false
    await loadRoles()
  } catch (e) {
    console.error('Failed to save role:', e)
  }
}

async function deleteRole(role: Role) {
  if (role.is_system) return
  if (!confirm(t('admin.roles.deleteConfirm', { name: role.display_name }))) return

  try {
    await rolesApi.deleteRole(role.role_id)
    if (selectedRole.value?.role_id === role.role_id) {
      selectedRole.value = null
    }
    await loadRoles()
  } catch (e) {
    console.error('Failed to delete role:', e)
  }
}

// Permission management
function startEditPermissions() {
  editingPermissions.value = true
  selectedPermissionIds.value = selectedRole.value?.permissions?.map(p => p.permission_id) || []
}

function togglePermission(permId: number) {
  const idx = selectedPermissionIds.value.indexOf(permId)
  if (idx >= 0) {
    selectedPermissionIds.value.splice(idx, 1)
  } else {
    selectedPermissionIds.value.push(permId)
  }
}

async function savePermissions() {
  if (!selectedRole.value) return

  try {
    await rolesApi.setRolePermissions(selectedRole.value.role_id, selectedPermissionIds.value)
    await selectRole(selectedRole.value)
    editingPermissions.value = false
  } catch (e) {
    console.error('Failed to save permissions:', e)
  }
}

function cancelEditPermissions() {
  editingPermissions.value = false
  selectedPermissionIds.value = selectedRole.value?.permissions?.map(p => p.permission_id) || []
}

// Init
onMounted(async () => {
  await Promise.all([loadRoles(), loadPermissions()])
})
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        {{ $t('admin.roles.title') }}
      </h1>
      <p class="text-gray-600 dark:text-gray-400 mt-1">
        {{ $t('admin.roles.subtitle') }}
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
        {{ $t('admin.roles.tabRoles') }}
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
        {{ $t('admin.roles.tabPermissions') }}
      </button>
    </div>

    <!-- Roles Tab -->
    <div v-if="activeTab === 'roles'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Roles List -->
      <div class="lg:col-span-1">
        <Card class="p-4">
          <div class="flex justify-between items-center mb-4">
            <h2 class="font-semibold text-gray-900 dark:text-white">{{ $t('admin.roles.roles') }}</h2>
            <Button size="sm" @click="openCreateModal">+ {{ $t('admin.roles.newRole') }}</Button>
          </div>

          <!-- System Roles -->
          <div class="mb-4">
            <h3 class="text-xs uppercase text-gray-500 font-medium mb-2">{{ $t('admin.roles.systemRoles') }}</h3>
            <div class="space-y-1">
              <button
                v-for="role in systemRoles"
                :key="role.role_id"
                @click="selectRole(role)"
                :class="[
                  'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors',
                  selectedRole?.role_id === role.role_id
                    ? 'bg-blue-100 dark:bg-blue-900/30'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                ]"
              >
                <span
                  class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm"
                  :style="{ backgroundColor: role.color }"
                >
                  {{ role.icon.charAt(0).toUpperCase() }}
                </span>
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-gray-900 dark:text-white truncate">
                    {{ role.display_name }}
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ role.user_count }} {{ $t('admin.roles.usersCount') }} · {{ role.permission_count }} {{ $t('admin.roles.permissionsCount') }}
                  </div>
                </div>
              </button>
            </div>
          </div>

          <!-- Custom Roles -->
          <div v-if="customRoles.length > 0">
            <h3 class="text-xs uppercase text-gray-500 font-medium mb-2">{{ $t('admin.roles.customRoles') }}</h3>
            <div class="space-y-1">
              <div
                v-for="role in customRoles"
                :key="role.role_id"
                @click="selectRole(role)"
                :class="[
                  'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors cursor-pointer',
                  selectedRole?.role_id === role.role_id
                    ? 'bg-blue-100 dark:bg-blue-900/30'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                ]"
              >
                <span
                  class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm"
                  :style="{ backgroundColor: role.color }"
                >
                  {{ role.icon.charAt(0).toUpperCase() }}
                </span>
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-gray-900 dark:text-white truncate">
                    {{ role.display_name }}
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ role.user_count }} {{ $t('admin.roles.usersCount') }} · {{ role.permission_count }} {{ $t('admin.roles.permissionsCount') }}
                  </div>
                </div>
                <button
                  @click.stop="deleteRole(role)"
                  class="p-1 text-gray-400 hover:text-red-500"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <!-- Role Details -->
      <div class="lg:col-span-2">
        <Card v-if="selectedRole" class="p-6">
          <div class="flex justify-between items-start mb-6">
            <div class="flex items-center gap-4">
              <span
                class="w-12 h-12 rounded-full flex items-center justify-center text-white text-xl"
                :style="{ backgroundColor: selectedRole.color }"
              >
                {{ selectedRole.icon.charAt(0).toUpperCase() }}
              </span>
              <div>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                  {{ selectedRole.display_name }}
                </h2>
                <p class="text-gray-500">{{ selectedRole.role_name }} · Level {{ selectedRole.hierarchy_level }}</p>
              </div>
            </div>
            <div class="flex gap-2">
              <Button
                v-if="!selectedRole.is_system"
                variant="secondary"
                size="sm"
                @click="openEditModal(selectedRole)"
              >
                {{ $t('common.edit') }}
              </Button>
            </div>
          </div>

          <p v-if="selectedRole.description" class="text-gray-600 dark:text-gray-400 mb-6">
            {{ selectedRole.description }}
          </p>

          <!-- Permissions Section -->
          <div class="mb-6">
            <div class="flex justify-between items-center mb-3">
              <h3 class="font-semibold text-gray-900 dark:text-white">{{ $t('admin.roles.permissions') }}</h3>
              <div v-if="!editingPermissions">
                <Button size="sm" variant="secondary" @click="startEditPermissions">
                  {{ $t('common.edit') }}
                </Button>
              </div>
              <div v-else class="flex gap-2">
                <Button size="sm" variant="secondary" @click="cancelEditPermissions">
                  {{ $t('common.cancel') }}
                </Button>
                <Button size="sm" @click="savePermissions">{{ $t('common.save') }}</Button>
              </div>
            </div>

            <!-- View mode -->
            <div v-if="!editingPermissions" class="flex flex-wrap gap-2">
              <span
                v-for="perm in selectedRole.permissions"
                :key="perm.permission_id"
                class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm rounded"
              >
                {{ perm.display_name }}
              </span>
              <span v-if="!selectedRole.permissions?.length" class="text-gray-500 text-sm">
                {{ $t('admin.roles.noPermissions') }}
              </span>
            </div>

            <!-- Edit mode -->
            <div v-else class="space-y-4 max-h-96 overflow-y-auto">
              <div v-for="(perms, category) in permissions" :key="category">
                <h4 class="font-medium text-gray-700 dark:text-gray-300 mb-2">{{ category }}</h4>
                <div class="grid grid-cols-2 gap-2">
                  <label
                    v-for="perm in perms"
                    :key="perm.permission_id"
                    class="flex items-center gap-2 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      :checked="selectedPermissionIds.includes(perm.permission_id)"
                      @change="togglePermission(perm.permission_id)"
                      class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    >
                    <span class="text-sm text-gray-700 dark:text-gray-300">
                      {{ perm.display_name }}
                    </span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Users Section -->
          <div>
            <h3 class="font-semibold text-gray-900 dark:text-white mb-3">
              {{ $t('admin.roles.usersWithRole', { count: roleUsers.length }) }}
            </h3>
            <div class="space-y-2 max-h-48 overflow-y-auto">
              <div
                v-for="user in roleUsers"
                :key="user.user_id"
                class="flex items-center gap-3 p-2 rounded bg-gray-50 dark:bg-gray-800"
              >
                <div class="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-sm font-medium">
                  {{ user.username.charAt(0).toUpperCase() }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-gray-900 dark:text-white truncate">
                    {{ user.username }}
                  </div>
                  <div class="text-xs text-gray-500 truncate">{{ user.email }}</div>
                </div>
                <span
                  :class="[
                    'px-2 py-0.5 text-xs rounded',
                    user.is_active
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                      : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300'
                  ]"
                >
                  {{ user.is_active ? $t('common.active') : $t('common.inactive') }}
                </span>
              </div>
              <p v-if="roleUsers.length === 0" class="text-gray-500 text-sm p-2">
                {{ $t('admin.roles.noUsersWithRole') }}
              </p>
            </div>
          </div>
        </Card>

        <!-- No role selected -->
        <Card v-else class="p-12 text-center">
          <div class="text-gray-400 mb-4">
            <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
            </svg>
          </div>
          <p class="text-gray-500">{{ $t('admin.roles.selectRoleHint') }}</p>
        </Card>
      </div>
    </div>

    <!-- Permissions Tab -->
    <div v-if="activeTab === 'permissions'">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card v-for="(perms, category) in permissions" :key="category" class="p-4">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3">{{ category }}</h3>
          <div class="space-y-2">
            <div
              v-for="perm in perms"
              :key="perm.permission_id"
              class="p-2 rounded bg-gray-50 dark:bg-gray-800"
            >
              <div class="font-medium text-sm text-gray-900 dark:text-white">
                {{ perm.display_name }}
              </div>
              <div class="text-xs text-gray-500">{{ perm.permission_key }}</div>
              <div v-if="perm.description" class="text-xs text-gray-400 mt-1">
                {{ perm.description }}
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Teleport to="body">
      <div
        v-if="showModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
        @click.self="showModal = false"
      >
        <Card class="w-full max-w-md p-6">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {{ modalMode === 'create' ? $t('admin.roles.createRole') : $t('admin.roles.editRole') }}
          </h2>

          <div class="space-y-4">
            <div v-if="modalMode === 'create'">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ $t('admin.roles.technicalName') }}
              </label>
              <Input v-model="modalForm.role_name" :placeholder="$t('admin.roles.technicalNamePlaceholder')" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ $t('admin.roles.displayName') }}
              </label>
              <Input v-model="modalForm.display_name" :placeholder="$t('admin.roles.displayNamePlaceholder')" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ $t('admin.roles.description') }}
              </label>
              <textarea
                v-model="modalForm.description"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                rows="2"
                :placeholder="$t('admin.roles.descriptionPlaceholder')"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ $t('admin.roles.hierarchyLevel') }}
              </label>
              <Input v-model.number="modalForm.hierarchy_level" type="number" min="1" max="9" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {{ $t('admin.roles.color') }}
              </label>
              <div class="flex gap-2 flex-wrap">
                <button
                  v-for="color in roleColors"
                  :key="color"
                  @click="modalForm.color = color"
                  :class="[
                    'w-8 h-8 rounded-full border-2 transition-all',
                    modalForm.color === color ? 'border-gray-900 dark:border-white scale-110' : 'border-transparent'
                  ]"
                  :style="{ backgroundColor: color }"
                />
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <Button variant="secondary" @click="showModal = false">{{ $t('common.cancel') }}</Button>
            <Button @click="saveRole">
              {{ modalMode === 'create' ? $t('common.create') : $t('common.save') }}
            </Button>
          </div>
        </Card>
      </div>
    </Teleport>
  </div>
</template>
