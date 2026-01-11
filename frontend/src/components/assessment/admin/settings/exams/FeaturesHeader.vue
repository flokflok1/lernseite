<!--
  FeaturesHeader - Header with Stats
  Sub-component of SystemFeaturesTab
-->

<template>
  <div class="features-header">
    <div class="header-icon">🎛️</div>
    <div class="header-info">
      <h2>{{ $t('windows.aiStudioFeatures.title') }}</h2>
      <p>{{ courseTitle }} • {{ scopeLabel }}</p>
    </div>
    <div class="header-stats">
      <div class="stat">
        <span class="stat-value">{{ enabledCount }}</span>
        <span class="stat-label">{{ $t('windows.aiStudioFeatures.activated') }}</span>
      </div>
      <div class="stat">
        <span class="stat-value">{{ estimatedTokens.toLocaleString() }}</span>
        <span class="stat-label">{{ $t('windows.aiStudioFeatures.tokensPerLesson') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  courseTitle: string
  scopeLabel: string
  enabledCount: number
  estimatedTokens: number
}>()
</script>

<style scoped>
.features-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 1rem;
  margin-bottom: 1rem;
}

.header-icon {
  width: 56px;
  height: 56px;
  background: rgba(255,255,255,0.2);
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
}

.header-info { flex: 1; }
.header-info h2 { color: white; font-size: 1.25rem; font-weight: 700; margin: 0; }
.header-info p { color: rgba(255,255,255,0.8); font-size: 0.875rem; margin: 0.25rem 0 0; }

.header-stats { display: flex; gap: 1.5rem; }
.stat { text-align: center; }
.stat-value { display: block; font-size: 1.5rem; font-weight: 700; color: white; }
.stat-label { font-size: 0.75rem; color: rgba(255,255,255,0.7); }
</style>
