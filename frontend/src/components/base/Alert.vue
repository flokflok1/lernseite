<template>
  <Transition name="alert">
    <div v-if="!dismissed" :class="alertClasses" role="alert">
      <div class="alert-icon">
        <svg v-if="type === 'success'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <svg v-else-if="type === 'error'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <svg v-else-if="type === 'warning'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>
      </div>

      <div class="alert-content">
        <h4 v-if="title" class="alert-title">{{ title }}</h4>
        <div class="alert-message">
          <slot>{{ message }}</slot>
        </div>
      </div>

      <button
        v-if="closable"
        type="button"
        class="alert-close"
        @click="handleClose"
        aria-label="Close alert"
      >
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { computed } from 'vue'

interface Props {
  type?: 'info' | 'success' | 'warning' | 'error'
  title?: string
  message?: string
  closable?: boolean
  variant?: 'filled' | 'outline' | 'subtle'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info',
  closable: true,
  variant: 'subtle',
})

const emit = defineEmits<{
  close: []
}>()

const dismissed = ref(false)

const alertClasses = computed(() => {
  return [
    'alert',
    `alert-${props.type}`,
    `alert-${props.variant}`,
  ]
})

const handleClose = () => {
  dismissed.value = true
  emit('close')
}
</script>

<style scoped>
.alert {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 0.5rem;
  position: relative;
}

.alert-icon {
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.alert-message {
  font-size: 0.875rem;
}

.alert-close {
  flex-shrink: 0;
  align-self: flex-start;
  color: inherit;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.alert-close:hover {
  opacity: 1;
}

/* Variants - Subtle */
.alert-subtle.alert-info {
  background-color: #dbeafe;
  color: #1e40af;
}

.alert-subtle.alert-success {
  background-color: #d1fae5;
  color: #065f46;
}

.alert-subtle.alert-warning {
  background-color: #fef3c7;
  color: #92400e;
}

.alert-subtle.alert-error {
  background-color: #fee2e2;
  color: #991b1b;
}

/* Variants - Filled */
.alert-filled {
  color: white;
}

.alert-filled.alert-info { background-color: #3b82f6; }
.alert-filled.alert-success { background-color: #10b981; }
.alert-filled.alert-warning { background-color: #f59e0b; }
.alert-filled.alert-error { background-color: #ef4444; }

/* Variants - Outline */
.alert-outline {
  border: 2px solid;
  background-color: transparent;
}

.alert-outline.alert-info {
  border-color: #3b82f6;
  color: #1e40af;
}

.alert-outline.alert-success {
  border-color: #10b981;
  color: #065f46;
}

.alert-outline.alert-warning {
  border-color: #f59e0b;
  color: #92400e;
}

.alert-outline.alert-error {
  border-color: #ef4444;
  color: #991b1b;
}

/* Transition */
.alert-enter-active,
.alert-leave-active {
  transition: all 0.3s ease;
}

.alert-enter-from {
  opacity: 0;
  transform: translateY(-0.5rem);
}

.alert-leave-to {
  opacity: 0;
  transform: translateX(1rem);
}
</style>
