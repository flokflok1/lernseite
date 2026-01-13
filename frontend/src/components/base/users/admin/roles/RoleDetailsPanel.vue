<template>
  <!-- Has role selected -->
  <Card v-if="role" class="p-6">
    <div class="flex justify-between items-start mb-6">
      <div class="flex items-center gap-4">
        <span
          class="w-12 h-12 rounded-full flex items-center justify-center text-white text-xl"
          :style="{ backgroundColor: role.color }"
        >
          {{ role.icon.charAt(0).toUpperCase() }}
        </span>
        <div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ role.display_name }}
          </h2>
          <p class="text-gray-500">{{ role.role_name }} · Level {{ role.hierarchy_level }}</p>
        </div>
      </div>
      <div class="flex gap-2">
        <Button
          v-if="!role.is_system"
          variant="secondary"
          size="sm"
          @click="$emit('edit', role)"
        >
          {{ $t('common.edit') }}
        </Button>
      </div>
    </div>

    <p v-if="role.description" class="text-gray-600 dark:text-gray-400 mb-6">
      {{ role.description }}
    </p>

    <!-- Permissions Section -->
    <div class="mb-6">
      <div class="flex justify-between items-center mb-3">
        <h3 class="font-semibold text-gray-900 dark:text-white">{{ $t('admin.roles.permissions') }}</h3>
        <div v-if="!editingPermissions">
          <Button size="sm" variant="secondary" @click="startEditing">
            {{ $t('common.edit') }}
          </Button>
        </div>
        <div v-else class="flex gap-2">
          <Button size="sm" variant="secondary" @click="cancelEditing">
            {{ $t('common.cancel') }}
          </Button>
          <Button size="sm" @click="savePermissions">{{ $t('common.save') }}</Button>
        </div>
      </div>

      <!-- View mode -->
      <div v-if="!editingPermissions" class="flex flex-wrap gap-2">
        <span
          v-for="perm in role.permissions"
          :key="perm.permission_id"
          class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm rounded"
        >
          {{ perm.display_name }}
        </span>
        <span v-if="!role.permissions?.length" class="text-gray-500 text-sm">
          {{ $t('admin.roles.noPermissions') }}
        </span>
      </div>

      <!-- Edit mode -->
      <div v-else class="space-y-4 max-h-96 overflow-y-auto">
        <div v-for="(perms, category) in availablePermissions" :key="category">
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
        {{ $t('admin.roles.usersWithRole', { count: users.length }) }}
      </h3>
      <div class="space-y-2 max-h-48 overflow-y-auto">
        <div
          v-for="user in users"
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
        <p v-if="users.length === 0" class="text-gray-500 text-sm p-2">
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
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from '@/components/base/Card.vue'
import Button from '@/components/base/Button.vue'
import type { Role, Permission, RoleUser } from '@/api/admin/roles.api'

const { t } = useI18n()

interface Props {
  role: Role | null
  users: RoleUser[]
  availablePermissions: Record<string, Permission[]>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  edit: [role: Role]
  savePermissions: [permissionIds: number[]]
}>()

// Permission editing state
const editingPermissions = ref(false)
const selectedPermissionIds = ref<number[]>([])

function startEditing() {
  editingPermissions.value = true
  selectedPermissionIds.value = props.role?.permissions?.map(p => p.permission_id) || []
}

function togglePermission(permId: number) {
  const idx = selectedPermissionIds.value.indexOf(permId)
  if (idx >= 0) {
    selectedPermissionIds.value.splice(idx, 1)
  } else {
    selectedPermissionIds.value.push(permId)
  }
}

function savePermissions() {
  emit('savePermissions', selectedPermissionIds.value)
  editingPermissions.value = false
}

function cancelEditing() {
  editingPermissions.value = false
  selectedPermissionIds.value = props.role?.permissions?.map(p => p.permission_id) || []
}

// Reset editing state when role changes
watch(() => props.role, () => {
  editingPermissions.value = false
})
</script>
