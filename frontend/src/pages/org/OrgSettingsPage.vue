<template>
  <AdminLayout :page-title="$t('admin.orgSettingsPage.title')" :page-subtitle="$t('admin.orgSettingsPage.subtitle')" :is-org-admin="true">
    <div class="bg-white rounded-lg shadow-sm p-8 text-center">
      <p class="text-gray-600">{{ $t('common.workInProgress') }}</p>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import AdminLayout from '@/layouts/AdminLayout.vue'
</script>
