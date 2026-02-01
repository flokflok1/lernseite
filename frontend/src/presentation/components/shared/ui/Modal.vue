<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="modal-overlay"
        @click="handleOverlayClick"
      >
        <div
          :class="modalClasses"
          role="dialog"
          aria-modal="true"
          @click.stop
        >
          <!-- Header -->
          <div v-if="$slots.header || title" class="modal-header">
            <slot name="header">
              <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
                {{ title }}
              </h3>
            </slot>
            <button
              v-if="closable"
              type="button"
              class="modal-close"
              @click="$emit('close')"
              aria-label="Close modal"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <slot />
          </div>

          <!-- Footer -->
          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'

interface Props {
  show: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  closable?: boolean
  closeOnOverlay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  closable: true,
  closeOnOverlay: true,
})

const emit = defineEmits<{
  close: []
}>()

const modalClasses = computed(() => {
  return [
    'modal-content',
    `modal-${props.size}`,
  ]
})

const handleOverlayClick = () => {
  if (props.closeOnOverlay && props.closable) {
    emit('close')
  }
}

// Lock body scroll when modal is open
watch(() => props.show, (newShow) => {
  if (newShow) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal-sm { max-width: 400px; width: 100%; }
.modal-md { max-width: 600px; width: 100%; }
.modal-lg { max-width: 800px; width: 100%; }
.modal-xl { max-width: 1200px; width: 100%; }
.modal-full { max-width: 95vw; width: 100%; }

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-close {
  color: var(--color-text-secondary);
  transition: color 0.2s;
}

.modal-close:hover {
  color: var(--color-text-primary);
}

.modal-body {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

/* Transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.95);
}
</style>
