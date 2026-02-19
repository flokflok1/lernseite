/**
 * ChatInterface.vue - Chat with AI for content assistance
 */

<script setup lang="ts">
import { ref } from 'vue'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const _messages = ref<Message[]>([])
const inputText = ref('')

const sendMessage = async () => {
  if (!inputText.value.trim()) return

  // TODO: Send to AI service
  inputText.value = ''
}
</script>

<template>
  <div class="chat-interface">
    <div class="messages">
      <!-- TODO: Render messages -->
      <p class="placeholder">Chat messages will appear here</p>
    </div>
    <div class="input-area">
      <input v-model="inputText" placeholder="Ask AI for help..." />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<style scoped>
.chat-interface {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 12px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  background: #f9f9f9;
  border-radius: 8px;
  padding: 12px;
}

.placeholder {
  color: #999;
  text-align: center;
  padding: 20px;
}

.input-area {
  display: flex;
  gap: 8px;
}

.input-area input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.input-area button {
  padding: 10px 20px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
