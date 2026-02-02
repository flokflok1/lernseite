<template>
  <Card class="p-4">
    <div class="flex justify-between items-center mb-4">
      <h2 class="font-semibold text-gray-900 dark:text-white">{{ $t('panel.groups.roles') }}</h2>
      <Button size="sm" @click="$emit('create')">+ {{ $t('panel.groups.newRole') }}</Button>
    </div>

    <!-- System Roles -->
    <div class="mb-4">
      <h3 class="text-xs uppercase text-gray-500 font-medium mb-2">{{ $t('panel.groups.systemRoles') }}</h3>
      <div class="space-y-1">
        <button
          v-for="role in systemRoles"
          :key="role.role_id"
          @click="$emit('select', role)"
          :class="[
            'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors',
            selectedRoleId === role.role_id
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
              {{ role.user_count }} {{ $t('panel.groups.usersCount') }} · {{ role.permission_count }} {{ $t('panel.groups.permissionsCount') }}
            </div>
          </div>
        </button>
      </div>
    </div>

    <!-- Custom Roles -->
    <div v-if="customRoles.length > 0">
      <h3 class="text-xs uppercase text-gray-500 font-medium mb-2">{{ $t('panel.groups.customRoles') }}</h3>
      <div class="space-y-1">
        <div
          v-for="role in customRoles"
          :key="role.role_id"
          @click="$emit('select', role)"
          :class="[
            'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors cursor-pointer',
            selectedRoleId === role.role_id
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
              {{ role.user_count }} {{ $t('panel.groups.usersCount') }} · {{ role.permission_count }} {{ $t('panel.groups.permissionsCount') }}
            </div>
          </div>
          <button
            @click.stop="handleDelete(role)"
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
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Card from '@/presentation/components/shared/ui/Card.vue'
import Button from '@/presentation/components/shared/ui/Button.vue'
import type { Role } from '@/application/services/api/admin'

const { t } = useI18n()

interface Props {
  systemRoles: Role[]
  customRoles: Role[]
  selectedRoleId?: number | null
}

defineProps<Props>()

const emit = defineEmits<{
  select: [role: Role]
  create: []
  delete: [role: Role]
}>()

function handleDelete(role: Role) {
  if (!confirm(t('panel.groups.deleteConfirm', { name: role.display_name }))) return
  emit('delete', role)
}
</script>
