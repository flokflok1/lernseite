<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'

const router = useRouter()
const authStore = useAuthStore()

const navigation = [
  { name: '📚 My Courses', path: '/panel/editor/courses' },
  { name: '✨ AI Assistant', path: '/panel/editor/ai' },
  { name: '📊 Analytics', path: '/panel/editor/analytics' },
]

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="editor-layout">
    <header class="header">
      <div class="header-left">
        <h1>✍️ Course Editor</h1>
      </div>
      
      <nav class="header-nav">
        <router-link
          v-for="item in navigation"
          :key="item.path"
          :to="item.path"
          class="nav-item"
        >
          {{ item.name }}
        </router-link>
      </nav>
      
      <div class="header-right">
        <button @click="() => router.push('/panel/user/profile')" class="profile-btn">👤 Profile</button>
        <button @click="logout" class="logout-btn">🚪 Logout</button>
      </div>
    </header>
    
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.editor-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #fafafa;
}

.header {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem 2rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-left h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}

.header-nav {
  display: flex;
  gap: 0.5rem;
  flex: 1;
}

.nav-item {
  padding: 0.625rem 1.25rem;
  color: #6b7280;
  text-decoration: none;
  border-radius: 0.5rem;
  transition: all 0.2s;
  font-weight: 500;
}

.nav-item:hover {
  background: #f3f4f6;
  color: #111827;
}

.nav-item.router-link-active {
  background: #3b82f6;
  color: white;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.header-right {
  display: flex;
  gap: 0.5rem;
}

.profile-btn,
.logout-btn {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.profile-btn {
  background: #f3f4f6;
  color: #374151;
}

.profile-btn:hover {
  background: #e5e7eb;
}

.logout-btn {
  background: #ef4444;
  color: white;
}

.logout-btn:hover {
  background: #dc2626;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}
</style>
