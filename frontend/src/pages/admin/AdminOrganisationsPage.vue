<template>
  <div class="admin-organisations-page">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-[var(--color-text-primary)]">{{ $t('admin.organisations.title') }}</h1>
      <p class="text-[var(--color-text-secondary)] mt-1">{{ $t('admin.organisations.subtitle') }}</p>
    </div>

    <div class="bg-[var(--color-surface)] rounded-lg shadow-sm p-8 text-center border border-[var(--color-border)]">
      <p class="text-[var(--color-text-secondary)]">{{ $t('admin.organisations.workInProgress') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

useI18n()
</script>
