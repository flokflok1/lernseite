<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-primary-600 mb-4">404</h1>
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">{{ $t('errors.pageNotFound') }}</h2>
      <p class="text-gray-600 mb-8">
        {{ $t('errors.pageNotFoundDesc') }}
      </p>
      <router-link to="/dashboard" class="btn btn-primary">
        {{ $t('nav.back_to_dashboard') }}
      </router-link>
    </div>
  </div>
</template>
