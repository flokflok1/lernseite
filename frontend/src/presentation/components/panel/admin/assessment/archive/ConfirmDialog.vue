<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'

interface Props {
  visible: boolean
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: 'danger' | 'warning' | 'info' | 'create'
  icon?: string
  /** If set, shows a text input and emits its value with confirm */
  inputMode?: boolean
  inputPlaceholder?: string
  inputValue?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'danger',
  icon: '🗑',
  inputMode: false,
  inputPlaceholder: '',
  inputValue: '',
})

const emit = defineEmits<{
  confirm: [inputValue?: string]
  cancel: []
}>()

const { t } = useI18n()

const inputText = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

watch(() => props.visible, (v) => {
  if (v) {
    inputText.value = props.inputValue || ''
    nextTick(() => inputRef.value?.focus())
  }
})

function handleConfirm() {
  if (props.inputMode && !inputText.value.trim()) return
  emit('confirm', props.inputMode ? inputText.value.trim() : undefined)
}

const variantStyles = {
  danger: { bg: 'bg-red-500/15', btn: 'bg-red-600 hover:bg-red-500 text-white' },
  warning: { bg: 'bg-yellow-500/15', btn: 'bg-yellow-600 hover:bg-yellow-500 text-white' },
  info: { bg: 'bg-blue-500/15', btn: 'bg-blue-600 hover:bg-blue-500 text-white' },
  create: { bg: 'bg-indigo-500/15', btn: 'bg-indigo-600 hover:bg-indigo-500 text-white' },
}
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="visible"
        class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[10002]"
        @click.self="emit('cancel')"
      >
        <Transition name="scale">
          <div
            v-if="visible"
            class="bg-gray-800 border border-gray-600/50 rounded-2xl p-6 w-[420px] shadow-2xl"
          >
            <!-- Icon + Title -->
            <div class="flex items-start gap-4 mb-4">
              <div
                class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shrink-0"
                :class="variantStyles[variant].bg"
              >
                {{ icon }}
              </div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-white">{{ title }}</h3>
                <p class="text-sm text-gray-400 mt-1">{{ message }}</p>
              </div>
            </div>

            <!-- Optional Input -->
            <div v-if="inputMode" class="mt-4">
              <input
                ref="inputRef"
                v-model="inputText"
                :placeholder="inputPlaceholder"
                class="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-2.5
                       text-white outline-none focus:border-indigo-500 transition-colors"
                @keydown.enter="handleConfirm"
                @keydown.escape="emit('cancel')"
              />
            </div>

            <!-- Actions -->
            <div class="flex justify-end gap-3 mt-6">
              <button
                class="px-4 py-2 rounded-lg text-sm font-medium text-gray-300
                       hover:bg-gray-700 transition-colors"
                @click="emit('cancel')"
              >
                {{ cancelLabel || t('panel.examArchive.folderDialog.cancel') }}
              </button>
              <button
                class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                :class="variantStyles[variant].btn"
                :disabled="inputMode && !inputText.trim()"
                @click="handleConfirm"
              >
                {{ confirmLabel || t('panel.examArchive.folderDialog.save') }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.scale-enter-active { transition: transform 0.15s ease-out; }
.scale-leave-active { transition: transform 0.1s ease-in; }
.scale-enter-from { transform: scale(0.95); }
.scale-leave-to { transform: scale(0.95); }
button:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
