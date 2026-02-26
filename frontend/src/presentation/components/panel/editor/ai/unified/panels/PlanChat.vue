<script setup lang="ts">
/**
 * PlanChat — Lightweight chat for plan refinement.
 *
 * Shows conversation history + input for discussing changes
 * with the AI during plan phases 1-3.
 */
import { ref, computed, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { PlanChatMessage, WizardPhase } from '../types'

interface Props {
  messages: PlanChatMessage[]
  isLoading: boolean
  currentPhase: WizardPhase
}

const props = defineProps<Props>()
const { t } = useI18n()

const emit = defineEmits<{
  send: [message: string]
}>()

const inputText = ref('')
const chatContainer = ref<HTMLElement | null>(null)

const placeholder = computed(() => {
  const key = `planWizard.chatPlaceholder${props.currentPhase}` as const
  return t(key)
})

function handleSend() {
  const msg = inputText.value.trim()
  if (!msg || props.isLoading) return
  emit('send', msg)
  inputText.value = ''
}

watch(() => props.messages.length, async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
})
</script>

<template>
  <div class="flex flex-col border border-gray-700 rounded-lg bg-gray-900/50">
    <!-- Messages -->
    <div
      ref="chatContainer"
      class="flex flex-col gap-2 p-3 max-h-[200px] overflow-y-auto"
    >
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        class="flex"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[80%] px-3 py-1.5 rounded-lg text-sm"
          :class="msg.role === 'user'
            ? 'bg-blue-600/30 text-blue-100'
            : 'bg-gray-800 text-gray-200'"
        >
          {{ msg.content }}
        </div>
      </div>

      <div v-if="isLoading" class="flex justify-start">
        <div class="px-3 py-1.5 rounded-lg bg-gray-800 text-gray-400 text-sm">
          <span class="animate-pulse">...</span>
        </div>
      </div>

      <p v-if="messages.length === 0 && !isLoading" class="text-xs text-gray-600 text-center py-2">
        {{ t('planWizard.chatHint') }}
      </p>
    </div>

    <!-- Input -->
    <div class="flex gap-2 p-2 border-t border-gray-700">
      <input
        v-model="inputText"
        type="text"
        :placeholder="placeholder"
        class="flex-1 px-3 py-1.5 bg-gray-800 border border-gray-600 rounded text-sm text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
        :disabled="isLoading"
        @keydown.enter="handleSend"
      />
      <button
        class="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-500 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        :disabled="!inputText.trim() || isLoading"
        @click="handleSend"
      >
        {{ t('planWizard.send') }}
      </button>
    </div>
  </div>
</template>
