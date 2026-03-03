<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'

const router = useRouter()
const authStore = useAuthStore()

const navigation = [
  { name: '🏠 Dashboard', path: '/panel/user/dashboard' },
  { name: '👤 Profile', path: '/panel/user/profile' },
  { name: '📚 My Courses', path: '/panel/user/courses' },
  { name: '🎯 Progress', path: '/panel/user/progress' },
  { name: '💬 Social', path: '/panel/user/social' },
  { name: '📝 Exam Trainer', path: '/exam-trainer' },
  { name: '⚙️ Settings', path: '/panel/user/settings' },
]

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="user-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1>🎓 My Learning</h1>
      </div>
      
      <nav class="sidebar-nav">
        <router-link
          v-for="item in navigation"
          :key="item.path"
          :to="item.path"
          class="nav-item"
        >
          {{ item.name }}
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
.user-layout {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 220px;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.sidebar-header h1 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #111827;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.nav-item {
  display: block;
  padding: 0.75rem 1.25rem;
  color: #6b7280;
  text-decoration: none;
  transition: all 0.2s;
  margin: 0.125rem 0.5rem;
  border-radius: 0.375rem;
  font-weight: 500;
}

.nav-item:hover {
  background: #f3f4f6;
  color: #111827;
}

.nav-item.router-link-active {
  background: #eff6ff;
  color: #3b82f6;
  font-weight: 600;
  border-left: 3px solid #3b82f6;
  padding-left: calc(1.25rem - 3px);
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.logout-btn {
  width: 100%;
  padding: 0.625rem;
  background: #f3f4f6;
  color: #6b7280;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

.content {
  flex: 1;
  overflow-y: auto;
  background: #fafafa;
  padding: 2rem;
}
</style>
