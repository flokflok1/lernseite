<template>
  <div
    ref="contentRef"
    :class="[
      'protected-content',
      { 'protected-content--no-select': disableSelect }
    ]"
    @contextmenu="handleContextMenu"
    @copy="handleCopy"
  >
    <slot />

    <!-- Copy Protection Toast -->
    <Transition name="fade">
      <div
        v-if="showToast"
        class="fixed bottom-4 right-4 bg-[var(--color-surface)] border border-[var(--color-border)] shadow-lg rounded-lg p-4 z-50 flex items-center gap-3"
        role="alert"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5 text-[var(--color-warning)]"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fill-rule="evenodd"
            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
            clip-rule="evenodd"
          />
        </svg>
        <span class="text-sm text-[var(--color-text-primary)]">
          {{ toastMessage }}
        </span>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { disableCopyProtection, enableCopyProtection } from '@/utils/copyProtection'

interface Props {
  disableRightClick?: boolean
  disableSelect?: boolean
  disableCopy?: boolean
  protectionMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  disableRightClick: true,
  disableSelect: true,
  disableCopy: true,
  protectionMessage: 'Dieser Inhalt ist urheberrechtlich geschützt.',
})

const contentRef = ref<HTMLElement | null>(null)
const showToast = ref(false)
const toastMessage = ref('')
let toastTimeout: ReturnType<typeof setTimeout> | null = null

const displayToast = (message: string) => {
  toastMessage.value = message
  showToast.value = true

  if (toastTimeout) {
    clearTimeout(toastTimeout)
  }

  toastTimeout = setTimeout(() => {
    showToast.value = false
  }, 3000)
}

const handleContextMenu = (event: MouseEvent) => {
  if (props.disableRightClick) {
    event.preventDefault()
    displayToast(props.protectionMessage)
  }
}

const handleCopy = (event: ClipboardEvent) => {
  if (props.disableCopy) {
    event.preventDefault()
    displayToast(props.protectionMessage)
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  // Block Ctrl+C, Ctrl+A, Ctrl+S, Ctrl+P
  if (props.disableCopy && event.ctrlKey) {
    const blockedKeys = ['c', 'a', 's', 'p']
    if (blockedKeys.includes(event.key.toLowerCase())) {
      event.preventDefault()
      displayToast(props.protectionMessage)
    }
  }
}

onMounted(() => {
  if (contentRef.value && props.disableCopy) {
    enableCopyProtection(contentRef.value)
  }

  if (props.disableCopy) {
    document.addEventListener('keydown', handleKeydown)
  }
})

onUnmounted(() => {
  if (contentRef.value) {
    disableCopyProtection(contentRef.value)
  }

  document.removeEventListener('keydown', handleKeydown)

  if (toastTimeout) {
    clearTimeout(toastTimeout)
  }
})
</script>

<style scoped>
.protected-content--no-select {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
