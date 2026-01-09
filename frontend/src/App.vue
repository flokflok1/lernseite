<template>
  <component :is="layout">
    <router-view />
  </component>

  <!-- Global 3D AI Tutor Companion - shown when logged in -->
  <TutorCompanion v-if="showTutor" />
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import BaseLayout from '@/layouts/BaseLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { TutorCompanion } from '@/components/system-features/tutor/user'
import { useAuthStore } from '@/store/auth.store'
import { useTutorStore } from '@/store/tutor.store'

const route = useRoute()
const authStore = useAuthStore()
const tutorStore = useTutorStore()

// Initialize tutor settings on mount
onMounted(() => {
  tutorStore.loadSettings()
})

// Show tutor only when logged in and not on excluded pages
const showTutor = computed(() => {
  // Must be authenticated
  if (!authStore.isAuthenticated) return false

  // Don't show on setup, login, register, or legal pages
  const excludedPaths = ['/setup', '/login', '/register', '/legal']
  if (excludedPaths.some(path => route.path.startsWith(path))) return false

  // Don't show on 404
  if (route.name === 'NotFound') return false

  return true
})

// Determine which layout to use based on route
const layout = computed(() => {
  // Setup route has NO global layout (SetupWizardPage uses SetupLayout internally)
  if (route.path.startsWith('/setup')) {
    return 'div'
  }

  // Auth routes use AuthLayout
  if (route.path.startsWith('/login') || route.path.startsWith('/register')) {
    return AuthLayout
  }

  // 404 page has no layout
  if (route.name === 'NotFound') {
    return 'div'
  }

  // Admin routes use their own AdminLayout - no BaseLayout wrapper!
  if (route.path.startsWith('/admin') || route.path.startsWith('/org')) {
    return 'div'
  }

  // Legal pages have their own layout with Footer
  if (route.path.startsWith('/legal')) {
    return 'div'
  }

  // All other routes use BaseLayout
  return BaseLayout
})
</script>
