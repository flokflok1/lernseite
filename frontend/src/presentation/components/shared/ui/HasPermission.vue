<script setup lang="ts">
import { computed } from 'vue'
import { usePermissions } from '@/application/composables/auth/usePermissions'

const props = defineProps<{
  permission?: string
  anyPermission?: string[]
}>()

const { hasPermission, hasAnyPermission } = usePermissions()

const hasAccess = computed(() => {
  if (props.permission) return hasPermission(props.permission)
  if (props.anyPermission) return hasAnyPermission(...props.anyPermission)
  return false
})
</script>

<template>
  <slot v-if="hasAccess" />
  <slot v-else name="fallback" />
</template>
