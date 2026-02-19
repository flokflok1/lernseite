<template>
  <div class="space-y-4">
    <!-- Search & Filter -->
    <div class="flex flex-col sm:flex-row gap-3">
      <Input
        v-model="searchQuery"
        :placeholder="$t('panel.groups.searchPlaceholder')"
        class="flex-1"
      />
      <select
        v-model="selectedCategory"
        class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
      >
        <option value="">{{ $t('panel.groups.permissions.category') }}: {{ $t('panel.groups.allRoles') }}</option>
        <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-8 text-gray-500">
      {{ $t('panel.groups.loading') }}
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-8 text-red-500">
      {{ $t('panel.groups.permissions.loadError') }}
    </div>

    <!-- Empty -->
    <div v-else-if="groupedPermissions.size === 0" class="text-center py-8 text-gray-500">
      {{ $t('panel.groups.permissions.noPermissions') }}
    </div>

    <!-- Permissions Grid grouped by category -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card
        v-for="[category, perms] in groupedPermissions"
        :key="category"
        class="p-4"
      >
        <h3 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
          {{ category }}
          <span class="text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-0.5 rounded-full">
            {{ perms.length }}
          </span>
        </h3>
        <div class="space-y-2">
          <div
            v-for="perm in perms"
            :key="perm.id"
            class="p-2 rounded bg-gray-50 dark:bg-gray-800"
          >
            <div class="font-medium text-sm text-gray-900 dark:text-white">
              {{ perm.display_name }}
            </div>
            <div class="text-xs text-gray-500 font-mono">{{ perm.code }}</div>
            <div v-if="perm.description" class="text-xs text-gray-400 mt-1">
              {{ perm.description }}
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Stats footer -->
    <div v-if="allPermissions.length > 0" class="text-sm text-gray-500 text-right">
      {{ allPermissions.length }} {{ $t('panel.groups.permissionsLabel') }}
      · {{ categories.length }} {{ $t('panel.groups.permissions.category') }}
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Permissions Registry Overview (GBA)
 * Shows all available permissions from the global registry, grouped by category.
 * Self-contained: fetches its own data from GET /admin/groups/permissions/registry.
 */
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from '@/presentation/components/shared/ui/Card.vue'
import Input from '@/presentation/components/shared/ui/Input.vue'
import { fetchPermissionsRegistry } from '@/infrastructure/api/clients/panel/admin'
import type { RegistryPermission } from '@/presentation/components/panel/admin/groups/types'

const { t } = useI18n()

const allPermissions = ref<RegistryPermission[]>([])
const categories = ref<string[]>([])
const isLoading = ref(false)
const error = ref(false)

const searchQuery = ref('')
const selectedCategory = ref('')

/** Filter permissions by search and category */
const filteredPermissions = computed(() => {
  let result = allPermissions.value

  if (selectedCategory.value) {
    result = result.filter(p => p.category === selectedCategory.value)
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(p =>
      p.code.toLowerCase().includes(q) ||
      p.display_name.toLowerCase().includes(q) ||
      (p.description?.toLowerCase().includes(q) ?? false)
    )
  }

  return result
})

/** Group filtered permissions by category */
const groupedPermissions = computed(() => {
  const map = new Map<string, RegistryPermission[]>()

  for (const perm of filteredPermissions.value) {
    const cat = perm.category
    if (!map.has(cat)) {
      map.set(cat, [])
    }
    map.get(cat)!.push(perm)
  }

  return map
})

async function loadPermissions() {
  isLoading.value = true
  error.value = false

  try {
    const result = await fetchPermissionsRegistry()
    allPermissions.value = result.data
    categories.value = result.categories
  } catch {
    error.value = true
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadPermissions()
})
</script>
