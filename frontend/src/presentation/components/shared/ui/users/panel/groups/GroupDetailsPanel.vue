<template>
  <!-- Has group selected (GBA) -->
  <Card v-if="group" class="p-6">
    <div class="flex justify-between items-start mb-6">
      <div class="flex items-center gap-4">
        <span
          class="w-12 h-12 rounded-full flex items-center justify-center text-white text-xl"
          :class="groupColorClass"
        >
          {{ group.name.charAt(0).toUpperCase() }}
        </span>
        <div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ group.name }}
          </h2>
          <p class="text-gray-500">{{ group.slug }} · {{ groupTypeLabel }}</p>
        </div>
      </div>
      <div class="flex gap-2">
        <Button
          v-if="group.type !== 'system_admin'"
          variant="secondary"
          size="sm"
          @click="$emit('edit', group)"
        >
          {{ $t('common.edit') }}
        </Button>
      </div>
    </div>

    <!-- Permissions Section (GBA) -->
    <div class="mb-6">
      <div class="flex justify-between items-center mb-3">
        <h3 class="font-semibold text-gray-900 dark:text-white">{{ $t('panel.groups.permissions') }}</h3>
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
          v-for="perm in availablePermissions"
          :key="perm.id"
          class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm rounded"
        >
          {{ perm.permission }}
        </span>
        <span v-if="!availablePermissions?.length" class="text-gray-500 text-sm">
          {{ $t('panel.groups.noPermissions') }}
        </span>
      </div>

      <!-- Edit mode (GBA - permission code input) -->
      <div v-else class="space-y-4">
        <div class="flex flex-wrap gap-2">
          <span
            v-for="code in selectedPermissionCodes"
            :key="code"
            class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm rounded flex items-center gap-1"
          >
            {{ code }}
            <button @click="removePermission(code)" class="text-blue-500 hover:text-blue-700">×</button>
          </span>
        </div>
        <div class="flex gap-2">
          <input
            v-model="newPermissionCode"
            type="text"
            class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
            :placeholder="$t('panel.groups.addPermissionPlaceholder')"
            @keyup.enter="addPermission"
          />
          <Button size="sm" @click="addPermission">{{ $t('common.add') }}</Button>
        </div>
      </div>
    </div>

    <!-- Members Section (GBA) -->
    <div>
      <h3 class="font-semibold text-gray-900 dark:text-white mb-3">
        {{ $t('panel.groups.membersCount', { count: users.length }) }}
      </h3>
      <div class="space-y-2 max-h-48 overflow-y-auto">
        <div
          v-for="member in users"
          :key="member.id"
          class="flex items-center gap-3 p-2 rounded bg-gray-50 dark:bg-gray-800"
        >
          <div class="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-sm font-medium">
            {{ member.user_id.charAt(0).toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-medium text-gray-900 dark:text-white truncate">
              {{ member.user_id }}
            </div>
            <div class="text-xs text-gray-500 truncate">{{ member.role }}</div>
          </div>
        </div>
        <p v-if="users.length === 0" class="text-gray-500 text-sm p-2">
          {{ $t('panel.groups.noMembers') }}
        </p>
      </div>
    </div>
  </Card>

  <!-- No group selected -->
  <Card v-else class="p-12 text-center">
    <div class="text-gray-400 mb-4">
      <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
      </svg>
    </div>
    <p class="text-gray-500">{{ $t('panel.groups.selectGroupHint') }}</p>
  </Card>
</template>

<script setup lang="ts">
/**
 * Group Details Panel (GBA)
 * Shows group details, permissions, and members.
 */
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from '@/presentation/components/shared/ui/Card.vue'
import Button from '@/presentation/components/shared/ui/Button.vue'
import type { Group, GroupMember, GroupPermission } from '@/presentation/components/panel/groups/types/group.types'

const { t } = useI18n()

interface Props {
  group: Group | null
  users: GroupMember[]
  availablePermissions: GroupPermission[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  edit: [group: Group]
  savePermissions: [permissionCodes: string[]]
}>()

// Computed
const groupColorClass = computed(() => {
  if (!props.group) return 'bg-gray-600'
  switch (props.group.type) {
    case 'system_admin': return 'bg-red-600'
    case 'org_admin': return 'bg-blue-600'
    default: return 'bg-green-600'
  }
})

const groupTypeLabel = computed(() => {
  if (!props.group) return ''
  switch (props.group.type) {
    case 'system_admin': return t('panel.groups.typeSystem')
    case 'org_admin': return t('panel.groups.typeOrg')
    default: return t('panel.groups.typeCustom')
  }
})

// Permission editing state
const editingPermissions = ref(false)
const selectedPermissionCodes = ref<string[]>([])
const newPermissionCode = ref('')

function startEditing() {
  editingPermissions.value = true
  selectedPermissionCodes.value = props.availablePermissions?.map(p => p.permission) || []
}

function addPermission() {
  const code = newPermissionCode.value.trim()
  if (code && !selectedPermissionCodes.value.includes(code)) {
    selectedPermissionCodes.value.push(code)
    newPermissionCode.value = ''
  }
}

function removePermission(code: string) {
  selectedPermissionCodes.value = selectedPermissionCodes.value.filter(c => c !== code)
}

function savePermissions() {
  emit('savePermissions', selectedPermissionCodes.value)
  editingPermissions.value = false
}

function cancelEditing() {
  editingPermissions.value = false
  selectedPermissionCodes.value = props.availablePermissions?.map(p => p.permission) || []
}

// Reset editing state when group changes
watch(() => props.group, () => {
  editingPermissions.value = false
})
</script>
