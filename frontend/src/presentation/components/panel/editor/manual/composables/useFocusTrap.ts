/**
 * useFocusTrap — lightweight keyboard focus trap for modal dialogs.
 *
 * Usage:
 *   const { trapRef } = useFocusTrap(visible)
 *   <div ref="trapRef"> ... focusable elements ... </div>
 */
import { ref, watch, nextTick, onBeforeUnmount, type Ref } from 'vue'

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'

export function useFocusTrap(active: Ref<boolean>) {
  const trapRef = ref<HTMLElement | null>(null)
  let previousFocus: HTMLElement | null = null

  const handleKeydown = (e: KeyboardEvent) => {
    if (e.key !== 'Tab' || !trapRef.value) return

    const focusable = Array.from(trapRef.value.querySelectorAll<HTMLElement>(FOCUSABLE))
    if (focusable.length === 0) return

    const first = focusable[0]
    const last = focusable[focusable.length - 1]

    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault()
        last.focus()
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }
  }

  watch(active, (isActive) => {
    if (isActive) {
      previousFocus = document.activeElement as HTMLElement
      nextTick(() => {
        if (!trapRef.value) return
        const first = trapRef.value.querySelector<HTMLElement>(FOCUSABLE)
        first?.focus()
        document.addEventListener('keydown', handleKeydown)
      })
    } else {
      document.removeEventListener('keydown', handleKeydown)
      previousFocus?.focus()
      previousFocus = null
    }
  })

  onBeforeUnmount(() => {
    document.removeEventListener('keydown', handleKeydown)
  })

  return { trapRef }
}
