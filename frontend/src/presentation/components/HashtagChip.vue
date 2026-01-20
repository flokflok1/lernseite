<template>
  <div class="hashtagchip">
    <div class="coming-soon-container">
      <div class="icon">🚧</div>
      <h3>{{ $t('common.comingSoon') }}</h3>
      <p class="component-name">HashtagChip</p>
      <p class="description">Hashtag display chip</p>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * HashtagChip Component (Stub)
 * Hashtag display chip
 * 
 * TODO: Implement full functionality in future phase
 * Created: Wave 2 - Feature Domain Stubs
 */

// Component will be implemented when social/compliance/moderation features are built
</script>

<style scoped>
.coming-soon-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 1rem;
  color: white;
  text-align: center;
  min-height: 300px;
}

.icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.coming-soon-container h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.component-name {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  opacity: 0.9;
}

.description {
  font-size: 0.875rem;
  opacity: 0.8;
  max-width: 500px;
}
</style>
