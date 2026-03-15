<script setup lang="ts">
import { useI18n } from 'vue-i18n'

interface Props {
  visible: boolean
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: 'danger' | 'warning' | 'info'
  icon?: string
}

withDefaults(defineProps<Props>(), {
  variant: 'danger',
  icon: '🗑',
})

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const { t } = useI18n()
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
                :class="{
                  'bg-red-500/15': variant === 'danger',
                  'bg-yellow-500/15': variant === 'warning',
                  'bg-blue-500/15': variant === 'info',
                }"
              >
                {{ icon }}
              </div>
              <div>
                <h3 class="text-lg font-semibold text-white">{{ title }}</h3>
                <p class="text-sm text-gray-400 mt-1">{{ message }}</p>
              </div>
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
                :class="{
                  'bg-red-600 hover:bg-red-500 text-white': variant === 'danger',
                  'bg-yellow-600 hover:bg-yellow-500 text-white': variant === 'warning',
                  'bg-blue-600 hover:bg-blue-500 text-white': variant === 'info',
                }"
                @click="emit('confirm')"
              >
                {{ confirmLabel || t('panel.examArchive.contextMenu.delete') }}
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
</style>
