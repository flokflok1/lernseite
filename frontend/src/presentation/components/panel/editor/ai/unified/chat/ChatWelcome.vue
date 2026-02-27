<template>
  <div class="chat-welcome">
    <div class="welcome-icon">AI</div>
    <h3 class="welcome-title">{{ $t('aiEditor.chat.welcome') }}</h3>
    <p class="welcome-desc">{{ $t('aiEditor.chat.welcomeDesc') }}</p>
    <div class="welcome-actions">
      <button class="welcome-btn primary" @click="$emit('newCourse')">
        {{ $t('aiEditor.chat.newCourse') }}
      </button>
      <button class="welcome-btn secondary" @click="$emit('loadCourse')">
        {{ $t('aiEditor.chat.loadCourse') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  newCourse: []
  loadCourse: []
}>()
</script>

<style scoped>
.chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  flex: 1;
}

.welcome-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.welcome-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
}

.welcome-desc {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin: 0 0 1.25rem;
  max-width: 280px;
}

.welcome-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  max-width: 220px;
}

.welcome-btn {
  padding: 0.625rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid transparent;
}

.welcome-btn.primary {
  background: var(--color-primary);
  color: white;
}

.welcome-btn.primary:hover {
  background: var(--color-primary-dark);
}

.welcome-btn.secondary {
  background: var(--color-surface-secondary);
  border-color: var(--color-border);
  color: var(--color-text-primary);
}

.welcome-btn.secondary:hover {
  border-color: var(--color-primary);
}
</style>
