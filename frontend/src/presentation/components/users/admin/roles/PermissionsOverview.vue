<template>
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
</template>

<script setup lang="ts">
import Card from '@/presentation/components/base/Card.vue'
import type { Permission } from '@/infrastructure/api/admin/roles.api'

interface Props {
  permissions: Record<string, Permission[]>
}

defineProps<Props>()
</script>
