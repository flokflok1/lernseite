<template>
  <div class="admin-user-group-management-window">
    <!-- Tab Navigation -->
    <div class="border-b border-[var(--color-border)] bg-[var(--color-surface)]">
      <div class="flex gap-1 p-4">
        <button
          @click="activeTab = 'users'"
          :class="[
            'px-4 py-2 rounded-lg font-medium transition-all duration-200',
            activeTab === 'users'
              ? 'bg-blue-600 text-white'
              : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-border)]'
          ]"
        >
          👥 {{ $t('admin.userGroupManagement.users') }}
        </button>
        <button
          @click="activeTab = 'roles'"
          :class="[
            'px-4 py-2 rounded-lg font-medium transition-all duration-200',
            activeTab === 'roles'
              ? 'bg-purple-600 text-white'
              : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-border)]'
          ]"
        >
          🛡️ {{ $t('admin.userGroupManagement.roles') }}
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="flex-1 overflow-y-auto">
      <!-- Users Tab -->
      <div v-if="activeTab === 'users'" class="h-full">
        <AdminUsersContent />
      </div>

      <!-- Roles Tab -->
      <div v-if="activeTab === 'roles'" class="h-full">
        <AdminGroupsContent />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AdminUsersContent from '@/presentation/components/admin/panels/users/AdminUsersContent.vue'
import AdminGroupsContent from '@/presentation/components/admin/panels/groups/roles-legacy/roles/AdminGroupsContent.vue'

/**
 * Admin User & Group Management Window
 *
 * Unified window-based interface for managing users and roles
 * with tab navigation for switching between views.
 *
 * Features:
 * - Tab-based navigation between Users and Roles
 * - Unified window with drag/resize capability
 * - All user and role management functions
 */

// Active tab state
const activeTab = ref<'users' | 'roles'>('users')
</script>

<style scoped>
.admin-user-group-management-window {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  color: var(--color-text-primary);
}
</style>
