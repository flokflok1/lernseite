<template>
  <!-- Maintenance Message Overlay (when backend is down after setup) -->
  <div
    v-if="showMaintenanceMessage"
    class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/95 backdrop-blur-sm"
  >
    <div class="max-w-md mx-4 p-8 bg-white rounded-lg shadow-2xl text-center">
      <div class="mb-4">
        <svg class="w-16 h-16 mx-auto text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h2 class="text-2xl font-bold text-gray-900 mb-2">
        {{ $t('maintenance.title') }}
      </h2>
      <p class="text-gray-600 mb-6">
        {{ $t('maintenance.description') }}
      </p>
      <button
        @click="retryConnection"
        :disabled="isChecking"
        class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="!isChecking">{{ $t('maintenance.retry') }}</span>
        <span v-else>{{ $t('maintenance.checking') }}</span>
      </button>
    </div>
  </div>

  <!-- Normal App Content -->
  <div v-else>
    <component :is="layout">
      <router-view />
    </component>

    <!-- Global 3D AI Tutor Companion - shown when logged in -->
    <!-- TODO: Restore TutorCompanion when component is migrated -->
    <!-- <TutorCompanion v-if="showTutor" /> -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import BaseLayout from '@/presentation/layouts/BaseLayout.vue'
import AuthLayout from '@/presentation/layouts/AuthLayout.vue'
// import { TutorCompanion } from '@/presentation/components/studio/system-features/tutor/user'
import { useAuthStore } from '@/application/stores/modules/core'
import { useAppStore } from '@/application/stores/app.store'
// import { useTutorStore } from '@/application/stores/modules/learning'

const route = useRoute()
const authStore = useAuthStore()
const appStore = useAppStore()
const { t } = useI18n()
// const tutorStore = useTutorStore()

// State for backend health check
const isBackendReachable = ref(true)
const isChecking = ref(false)
let healthCheckInterval: number | null = null
let lastBackendStatus = true // Track last status to avoid log spam
let currentCheckInterval = 1000 // Dynamic interval (1s when UP, 5s when DOWN)

// Initialize tutor settings on mount
// onMounted(() => {
//   tutorStore.loadSettings()
// })

/**
 * Check if backend is reachable (lightweight health check)
 */
const checkBackendHealth = async (): Promise<boolean> => {
  try {
    // HEAD request instead of GET (less prominent in browser console)
    const response = await fetch('/health', {
      method: 'HEAD',
      cache: 'no-cache',
      signal: AbortSignal.timeout(3000) // 3 second timeout
    })
    return response.ok
  } catch (error) {
    // Backend is unreachable (suppress error logging to avoid console spam)
    return false
  }
}

/**
 * Restart health check with new interval
 */
const restartHealthCheckWithInterval = (interval: number) => {
  if (currentCheckInterval === interval) return // No change needed

  currentCheckInterval = interval

  // Clear existing interval
  if (healthCheckInterval !== null) {
    clearInterval(healthCheckInterval)
  }

  // Start new interval
  healthCheckInterval = window.setInterval(async () => {
    const reachable = await checkBackendHealth()

    // Only log when status CHANGES (avoid console spam)
    if (reachable !== lastBackendStatus) {
      if (!reachable) {
        console.warn('[App] ⚠️ Backend went DOWN - showing maintenance message')
        // Switch to slower checks when backend is down (reduce console spam)
        restartHealthCheckWithInterval(5000)
      } else {
        console.log('[App] ✅ Backend is UP again - hiding maintenance message')
        // Switch back to fast checks when backend is up
        restartHealthCheckWithInterval(1000)
      }
      lastBackendStatus = reachable
    }

    isBackendReachable.value = reachable
  }, interval)
}

/**
 * Start continuous health check (dynamic interval: 1s when UP, 5s when DOWN)
 */
const startHealthCheck = () => {
  // Initial check
  checkBackendHealth().then((reachable) => {
    isBackendReachable.value = reachable
    lastBackendStatus = reachable

    if (!reachable) {
      console.warn('[App] Backend unreachable - showing maintenance message')
      // Start with slow checks if backend is initially down
      restartHealthCheckWithInterval(5000)
    } else {
      console.log('[App] Backend health check started - backend is reachable')
      // Start with fast checks if backend is initially up
      restartHealthCheckWithInterval(1000)
    }
  })
}

/**
 * Stop health check interval
 */
const stopHealthCheck = () => {
  if (healthCheckInterval !== null) {
    clearInterval(healthCheckInterval)
    healthCheckInterval = null
  }
}

// Start health check on mount
onMounted(() => {
  const setupCompleted = localStorage.getItem('lsx-setup-completed') === 'true'

  // Only start health check if setup was completed
  // (No need to check if setup was never done)
  if (setupCompleted) {
    console.log('[App] Starting dynamic backend health check (1s when UP, 5s when DOWN)')
    startHealthCheck()
  }
})

// Stop health check on unmount
onUnmounted(() => {
  stopHealthCheck()
})

// Show maintenance message when backend is down after setup completion
const showMaintenanceMessage = computed(() => {
  // Only show maintenance if setup was completed (localStorage check)
  const setupCompleted = localStorage.getItem('lsx-setup-completed') === 'true'

  // And backend is currently unreachable
  return setupCompleted && !isBackendReachable.value
})

// Retry connection to backend
const retryConnection = async () => {
  isChecking.value = true
  try {
    const reachable = await checkBackendHealth()
    isBackendReachable.value = reachable

    if (reachable) {
      console.log('[App] Backend is reachable again!')
      // Also refresh installation status
      await appStore.checkInstallationStatus()
    }
  } catch (error) {
    console.error('[App] Failed to check backend health:', error)
  } finally {
    isChecking.value = false
  }
}

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
  if (route.path.startsWith('/admin')) {
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
