<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex flex-col">
    <!-- Main Content -->
    <div class="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
      <div class="max-w-md w-full">
        <!-- Logo/Branding -->
        <div class="text-center mb-8">
          <h1 class="text-4xl font-bold text-primary-600">LernsystemX</h1>
          <p class="mt-2 text-gray-600">AI-Powered Learning Platform</p>
        </div>

        <!-- Content -->
        <div class="bg-white shadow-xl rounded-lg p-8">
          <router-view />
        </div>

        <!-- Mini Footer with Legal Links -->
        <div class="text-center mt-6 space-y-3">
          <p class="text-sm text-gray-500">
            &copy; {{ currentYear }} LernsystemX. Alle Rechte vorbehalten.
          </p>
          <div class="flex flex-wrap justify-center gap-4 text-xs text-gray-500">
            <router-link
              to="/legal/imprint"
              class="hover:text-primary-600 transition-colors"
            >
              Impressum
            </router-link>
            <router-link
              to="/legal/privacy"
              class="hover:text-primary-600 transition-colors"
            >
              Datenschutz
            </router-link>
            <router-link
              to="/legal/terms"
              class="hover:text-primary-600 transition-colors"
            >
              AGB
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())
</script>
