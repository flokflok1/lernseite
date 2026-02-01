<script setup lang="ts">
import { onMounted } from 'vue'
import { useGroupManagement } from './composables'

const { groups, isLoading, error, fetchGroups } = useGroupManagement()

onMounted(() => {
  fetchGroups()
})
</script>

<template>
  <div class="groups-management">
    <h2>{{ $t('panel.groups.title') }}</h2>
    
    <div v-if="isLoading" class="loader">
      Loading groups...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else class="groups-list">
      <p v-if="groups.length === 0">{{ $t('panel.groups.empty') }}</p>
      <!-- Groups list will be implemented here -->
    </div>
  </div>
</template>

<style scoped>
.groups-management {
  padding: 20px;
}

.loader,
.error {
  padding: 20px;
  text-align: center;
}

.error {
  color: #d32f2f;
  background: #ffebee;
  border-radius: 4px;
}
</style>
