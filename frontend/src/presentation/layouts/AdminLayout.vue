<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'

const router = useRouter()
const authStore = useAuthStore()

const navigation = computed(() => [
  { name: 'Dashboard', path: '/panel/admin', icon: '📊' },
  { name: 'Users', path: '/panel/admin/users', icon: '👥', permission: 'admin.users:read' },
  { name: 'Groups', path: '/panel/admin/groups', icon: '👨‍👩‍👧', permission: 'admin.groups:read' },
  { name: 'AI Settings', path: '/panel/admin/ai', icon: '🤖', permission: 'admin.ai-providers:read' },
  { name: 'Categories', path: '/panel/admin/categories', icon: '📁', permission: 'admin.categories:read' },
  { name: 'i18n', path: '/panel/admin/i18n', icon: '🌍', permission: 'admin.i18n:read' },
  { name: 'Analytics', path: '/panel/admin/analytics', icon: '📈', permission: 'admin.dashboard:read' },
  { name: 'Billing', path: '/panel/admin/billing', icon: '💰', permission: 'admin.billing:read' },
  { name: 'Settings', path: '/panel/admin/settings', icon: '⚙️', permission: 'admin.settings:read' },
])

const canAccess = (permission?: string) => {
  if (!permission) return true
  return authStore.hasPermission?.(permission) ?? false
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1>⚡ Admin Panel</h1>
      </div>
      
      <nav class="sidebar-nav">
        <router-link
          v-for="item in navigation"
          :key="item.path"
          v-show="canAccess(item.permission)"
          :to="item.path"
          class="nav-item"
        >
          <span class="icon">{{ item.icon }}</span>
          <span>{{ item.name }}</span>
        </router-link>
      </nav>
      
      <div class="sidebar-footer">
        <button @click="logout" class="logout-btn">🚪 Logout</button>
      </div>
    </aside>
    
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background: #0f172a;
}

.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  color: white;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #334155;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #334155;
}

.sidebar-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  color: #cbd5e1;
  text-decoration: none;
  transition: all 0.2s;
  margin: 0.25rem 0.5rem;
  border-radius: 0.5rem;
}

.nav-item .icon {
  font-size: 1.25rem;
}

.nav-item:hover {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.nav-item.router-link-active {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #334155;
}

.logout-btn {
  width: 100%;
  padding: 0.75rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.content {
  flex: 1;
  overflow-y: auto;
  background: #f8fafc;
}
</style>
