<template>
  <div class="admin-user-group-management">
    <!-- Centered Container -->
    <div class="flex flex-col items-center justify-start pt-4 w-full h-full overflow-hidden">
      <!-- Page Header -->
      <div class="mb-6 text-center">
        <h1 class="text-2xl font-bold text-[var(--color-text-primary)] mb-2">
          {{ $t('admin.userGroupManagement.title') }}
        </h1>
        <p class="text-base text-[var(--color-text-secondary)]">
          {{ $t('admin.userGroupManagement.subtitle') }}
        </p>
      </div>

      <!-- Tabs Navigation -->
      <div class="flex gap-2 mb-6 border-b border-[var(--color-border)] w-full px-4">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-4 py-2 font-medium transition-all duration-200 border-b-2 -mb-[2px]',
            activeTab === tab.id
              ? 'text-[var(--color-primary)] border-[var(--color-primary)]'
              : 'text-[var(--color-text-secondary)] border-transparent hover:text-[var(--color-text-primary)]'
          ]"
        >
          <span class="mr-2">{{ tab.icon }}</span>
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab Content Container -->
      <div class="w-full flex-1 overflow-y-auto px-4">
        <!-- Users Tab -->
        <div v-if="activeTab === 'users'" class="tab-content">
          <AdminUsersContent />
        </div>

        <!-- Roles Tab -->
        <div v-if="activeTab === 'roles'" class="tab-content">
          <AdminGroupsContent />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminUsersContent from '@/presentation/components/admin/panels/users/AdminUsersContent.vue'
import AdminGroupsContent from '@/presentation/components/admin/panels/groups/roles-legacy/AdminGroupsContent.vue'

const { t } = useI18n()

const activeTab = ref('users')

interface Tab {
  id: 'users' | 'roles'
  icon: string
  label: string
}

const tabs: Tab[] = [
  {
    id: 'users',
    icon: '👥',
    label: t('admin.userGroupManagement.users')
  },
  {
    id: 'roles',
    icon: '🔐',
    label: t('admin.userGroupManagement.roles')
  }
]
</script>

<style scoped>
.admin-user-group-management {
  width: 100%;
  background: linear-gradient(135deg, var(--color-background) 0%, var(--color-surface) 100%);
  height: 100%;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  overflow: hidden;
}

.tab-content {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
