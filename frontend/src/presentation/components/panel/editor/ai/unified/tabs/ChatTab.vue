<!--
  ChatTab — Full-width chat panel (structure moved to persistent sidebar).
  Receives state via inject from UnifiedAIEditor.
-->
<template>
  <div class="chat-tab">
    <ChatPanel
      :has-session="chatSession.hasSession.value"
      :messages="chatSession.messages.value"
      :is-loading="chatSession.isLoading.value"
      :tokens-used="chatSession.tokensUsed.value"
      :token-budget="chatSession.tokenBudget.value"
      :usage-percent="chatSession.usagePercent.value"
      :context-label="structureView.contextLabel.value"
      :file-count="chatSession.selectedFileIds.value.length"
      @new-course="$emit('newCourse')"
      @load-course="$emit('loadCourse')"
      @send="$emit('send', $event)"
      @attach-file="$emit('attachFile')"
      @clear-context="structureView.clearContext()"
      @confirm="$emit('confirm', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import { inject } from 'vue'
import { ChatPanel } from '../chat'
import type { useChatSession } from '../composables/generation/useChatSession'
import type { useStructureView } from '../composables/editor/useStructureView'

const chatSession = inject<ReturnType<typeof useChatSession>>('chatSession')
const structureView = inject<ReturnType<typeof useStructureView>>('structureView')

if (!chatSession || !structureView) {
  throw new Error('[ChatTab] Missing required inject: chatSession or structureView. Must be used inside UnifiedAIEditor.')
}

defineEmits<{
  newCourse: []
  loadCourse: []
  send: [content: string]
  attachFile: []
  confirm: [confirmation: any]
}>()
</script>

<style scoped>
.chat-tab {
  display: flex;
  flex: 1;
  overflow: hidden;
  height: 100%;
}
</style>
