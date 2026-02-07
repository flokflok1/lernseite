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
        @click="activeTab = 'groups'"
        :class="[
          'px-4 py-2 font-medium border-b-2 -mb-px transition-colors',
          activeTab === 'groups'
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

    <!-- Groups Tab (GBA) -->
    <div v-if="activeTab === 'groups'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Groups List -->
      <div class="lg:col-span-1">
        <GroupsListView
          :system-groups="systemGroups"
          :custom-groups="customGroups"
          :selected-group-id="selectedGroup?.id"
          @select="selectGroup"
          @create="openCreateModal"
          @delete="handleDeleteGroup"
        />
      </div>

      <!-- Group Details -->
      <div class="lg:col-span-2">
        <GroupDetailsPanel
          :group="selectedGroup"
          :users="groupMembers"
          :available-permissions="groupPermissions"
          @edit="openEditModal"
          @save-permissions="handleSavePermissions"
        />
      </div>
    </div>

    <!-- Permissions Tab (self-contained, fetches from registry) -->
    <PermissionsOverview
      v-if="activeTab === 'permissions'"
    />

    <!-- Create/Edit Modal (GBA) -->
    <GroupEditModal
      :show="showModal"
      :mode="modalMode"
      :group="selectedGroup"
      @close="showModal = false"
      @save="handleSaveGroup"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * Admin Groups & Permissions Page (GBA)
 * ======================================
 * Orchestrator page for groups management.
 * Uses GBA (Group-Based Access) system.
 */
import { ref, onMounted } from 'vue'
import {
  GroupsListView,
  GroupDetailsPanel,
  GroupEditModal,
  PermissionsOverview,
  useGroupsManagement
} from '@/presentation/components/users/panel/groups'
import type { Group } from '@/presentation/components/panel/groups/types/group.types'

// GBA Form Data type
interface GroupFormData {
  name: string
  slug: string
  type: 'system_admin' | 'org_admin' | 'custom'
  description?: string
}

const {
  // State
  selectedGroup,
  groupMembers,
  groupPermissions,
  // Computed
  systemGroups,
  customGroups,
  // Methods
  selectGroup,
  createGroup,
  updateGroup,
  deleteGroup,
  grantPermission,
  revokePermission,
  initialize
} = useGroupsManagement()

const activeTab = ref<'groups' | 'permissions'>('groups')

// Modal state
const showModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')

function openCreateModal() {
  modalMode.value = 'create'
  showModal.value = true
}

function openEditModal(group: Group) {
  // Protected groups cannot be edited
  if (group.is_protected) return
  modalMode.value = 'edit'
  showModal.value = true
}

async function handleSaveGroup(data: GroupFormData) {
  let success = false

  if (modalMode.value === 'create') {
    success = await createGroup(data)
  } else if (selectedGroup.value) {
    success = await updateGroup(selectedGroup.value.id, data)
  }

  if (success) {
    showModal.value = false
  }
}

async function handleDeleteGroup(group: Group) {
  await deleteGroup(group)
}

async function handleSavePermissions(permissionCodes: string[]) {
  if (!selectedGroup.value) return
  const groupId = selectedGroup.value.id

  // Get current permissions
  const currentPerms = groupPermissions.value.map(p => p.permission)

  // Revoke removed permissions
  for (const perm of groupPermissions.value) {
    if (!permissionCodes.includes(perm.permission)) {
      await revokePermission(groupId, perm.id)
    }
  }

  // Grant new permissions
  for (const code of permissionCodes) {
    if (!currentPerms.includes(code)) {
      await grantPermission(groupId, code)
    }
  }
}

// Initialize on mount
onMounted(() => {
  initialize()
})
</script>
