<template>
  <div class="skeleton-grid">
    <aside class="skeleton-sidebar">
      <div class="skeleton-card">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-line w-60"></div>
        <div class="skeleton-line w-40"></div>
        <div class="skeleton-bar"></div>
        <div class="skeleton-stats">
          <div class="skeleton-stat-block"></div>
          <div class="skeleton-stat-block"></div>
        </div>
      </div>
    </aside>
    <main class="skeleton-main">
      <div class="skeleton-tabs">
        <div class="skeleton-tab"></div>
        <div class="skeleton-tab"></div>
        <div class="skeleton-tab"></div>
      </div>
      <div class="skeleton-quest"></div>
      <div class="skeleton-quest"></div>
      <div class="skeleton-quest"></div>
    </main>
    <aside class="skeleton-inventory">
      <div class="skeleton-card small"></div>
      <div class="skeleton-card small"></div>
    </aside>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.skeleton-grid {
  display: grid;
  grid-template-columns: 280px 1fr 300px;
  gap: 24px;
  align-items: start;
}

.skeleton-sidebar,
.skeleton-inventory {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-card.small {
  padding: 16px;
  min-height: 120px;
}

.skeleton-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--color-border);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-line {
  height: 14px;
  border-radius: 7px;
  background: var(--color-border);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-line.w-60 { width: 60%; }
.skeleton-line.w-40 { width: 40%; }

.skeleton-bar {
  height: 12px;
  border-radius: 6px;
  background: var(--color-border);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.skeleton-stat-block {
  height: 60px;
  border-radius: 12px;
  background: var(--color-border);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-tabs {
  display: flex;
  gap: 8px;
  padding: 4px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
}

.skeleton-tab {
  flex: 1;
  height: 44px;
  border-radius: 8px;
  background: var(--color-border);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-quest {
  height: 80px;
  border-radius: 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

@media (max-width: 1200px) {
  .skeleton-grid {
    grid-template-columns: 1fr 280px;
  }

  .skeleton-sidebar {
    grid-column: 1 / -1;
  }
}

@media (max-width: 900px) {
  .skeleton-grid {
    grid-template-columns: 1fr;
  }
}
</style>
