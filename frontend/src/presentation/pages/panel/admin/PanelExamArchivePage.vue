<script setup lang="ts">
import { useRouter } from 'vue-router'
import FileExplorer from '@/presentation/components/panel/admin/assessment/archive/FileExplorer.vue'

const router = useRouter()

function goBack() {
  router.push({ name: 'PanelExams' })
}
</script>

<template>
  <FileExplorer class="h-full" @close="goBack" />
</template>
