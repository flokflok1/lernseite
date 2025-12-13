<template>
  <div class="min-h-screen bg-[var(--color-bg)] flex flex-col">
    <!-- Topbar -->
    <header class="bg-[var(--color-surface)] shadow-sm border-b border-[var(--color-border)] flex-shrink-0">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <div class="flex items-center">
            <router-link to="/dashboard" class="text-2xl font-bold text-primary-600">
              LernsystemX
            </router-link>
          </div>

          <!-- User Menu -->
          <div class="flex items-center space-x-4">
            <span class="text-sm text-[var(--color-text-primary)]">
              {{ authStore.fullName }}
            </span>
            <span class="px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded">
              {{ authStore.userRole }}
            </span>
            <button
              @click="handleLogout"
              class="btn btn-outline btn-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <div class="flex flex-1">
      <!-- Sidebar -->
      <aside class="w-64 bg-[var(--color-surface)] border-r border-[var(--color-border)] flex-shrink-0">
        <nav class="p-4 space-y-2">
          <router-link
            to="/dashboard"
            class="block px-4 py-2 rounded-lg hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] transition-colors"
            active-class="bg-primary-100 text-primary-700"
          >
            📊 Dashboard
          </router-link>
          <router-link
            to="/courses"
            class="block px-4 py-2 rounded-lg hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] transition-colors"
            active-class="bg-primary-100 text-primary-700"
          >
            📚 Kurse
          </router-link>
          <router-link
            to="/profile"
            class="block px-4 py-2 rounded-lg hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] transition-colors"
            active-class="bg-primary-100 text-primary-700"
          >
            👤 Profil
          </router-link>
          <router-link
            to="/settings"
            class="block px-4 py-2 rounded-lg hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] transition-colors"
            active-class="bg-primary-100 text-primary-700"
          >
            ⚙️ Einstellungen
          </router-link>
          <router-link
            v-if="authStore.isSystemAdmin"
            to="/admin"
            class="block px-4 py-2 rounded-lg hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] transition-colors"
            active-class="bg-primary-100 text-primary-700"
          >
            🔧 Admin Panel
          </router-link>
        </nav>
      </aside>

      <!-- Page Content -->
      <main class="flex-1 p-8 overflow-auto">
        <router-view />
      </main>
    </div>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/store/auth.store'
import { useRouter } from 'vue-router'
import Footer from '@/components/layout/Footer.vue'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
