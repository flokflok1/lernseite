import { computed } from 'vue'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'

export function usePermissions() {
  const authStore = useAuthStore()

  const hasPermission = (code: string): boolean => {
    return authStore.hasPermission?.(code) ?? false
  }

  const hasAnyPermission = (...codes: string[]): boolean => {
    return authStore.hasAnyPermission?.(...codes) ?? false
  }

  return {
    hasPermission,
    hasAnyPermission,
    
    // Domain helpers
    canManageUsers: computed(() => hasPermission('admin.users:read')),
    canManageGroups: computed(() => hasPermission('admin.groups:read')),
    canManageAI: computed(() => hasPermission('admin.ai-providers:read')),
    canEditCourses: computed(() => hasPermission('editor.courses:write')),
    canPublishCourses: computed(() => hasPermission('editor.courses:publish')),
    canManageBilling: computed(() => hasPermission('admin.billing:read')),
    canManageI18n: computed(() => hasPermission('admin.i18n:read')),
  }
}
