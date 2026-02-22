/**
 * useConfirmDialog — singleton composable for promise-based confirm & prompt dialogs.
 *
 * Replaces native window.confirm() and window.prompt() with styled in-app dialogs.
 * Mount ConfirmDialog.vue once in the root container, then call
 * confirm('message') or prompt('label', 'placeholder') from any child component.
 */
import { ref } from 'vue'

export type DialogMode = 'confirm' | 'prompt'

// Module-level singleton state — shared across all callers.
// Mount ConfirmDialog.vue once; all confirm()/prompt() calls share this state.
const visible = ref(false)
const dialogMode = ref<DialogMode>('confirm')
const message = ref('')
const inputValue = ref('')
const inputPlaceholder = ref('')

let resolveConfirm: ((value: boolean) => void) | null = null
let resolvePrompt: ((value: string | null) => void) | null = null

export function useConfirmDialog() {
  const confirm = (msg: string): Promise<boolean> => {
    dialogMode.value = 'confirm'
    message.value = msg
    inputValue.value = ''
    visible.value = true
    return new Promise<boolean>((resolve) => {
      resolveConfirm = resolve
      resolvePrompt = null
    })
  }

  const prompt = (msg: string, placeholder = ''): Promise<string | null> => {
    dialogMode.value = 'prompt'
    message.value = msg
    inputValue.value = ''
    inputPlaceholder.value = placeholder
    visible.value = true
    return new Promise<string | null>((resolve) => {
      resolvePrompt = resolve
      resolveConfirm = null
    })
  }

  const handleConfirm = () => {
    visible.value = false
    if (resolveConfirm) {
      resolveConfirm(true)
      resolveConfirm = null
    }
    if (resolvePrompt) {
      resolvePrompt(inputValue.value.trim() || null)
      resolvePrompt = null
    }
  }

  const handleCancel = () => {
    visible.value = false
    if (resolveConfirm) {
      resolveConfirm(false)
      resolveConfirm = null
    }
    if (resolvePrompt) {
      resolvePrompt(null)
      resolvePrompt = null
    }
  }

  return {
    visible,
    dialogMode,
    message,
    inputValue,
    inputPlaceholder,
    confirm,
    prompt,
    handleConfirm,
    handleCancel,
  }
}
