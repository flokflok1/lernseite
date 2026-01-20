<template>
  <div class="min-h-screen bg-[#0a0e1a]">
    <!-- Header -->
    <header class="border-b shadow-sm bg-[#1a1f35] border-[#2a3350]">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-xl">LSX</span>
            </div>
            <div>
              <h1 class="text-xl font-bold text-white">
                LernsystemX
              </h1>
              <p class="text-sm text-gray-400">
                Setup Wizard
              </p>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <LanguageSelector :show-label="false" :show-request-option="false" />
            <div class="text-sm text-gray-400">
              Installation v1.0
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="mt-auto py-6">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <p class="text-center text-sm text-gray-400">
          LernsystemX &copy; {{ currentYear }} - AI-Powered Learning Platform
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { LanguageSelector } from '@/presentation/components/layout/i18n'

const currentYear = computed(() => new Date().getFullYear())

// Apply dark mode class on mount (permanent)
onMounted(() => {
  document.documentElement.classList.add('dark')
})
</script>
