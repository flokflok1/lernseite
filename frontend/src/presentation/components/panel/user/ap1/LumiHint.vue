<template>
  <div class="lumi-hint">
    <!-- Toggle Button -->
    <button
      @click="toggleOpen"
      class="lumi-btn"
      :class="isOpen ? 'lumi-btn-open' : ''"
    >
      <span class="lumi-avatar">🤖</span>
      <span v-if="!isOpen">Lumi fragen</span>
      <span v-else>Lumi schließen</span>
      <span v-if="hasNewMessage && !isOpen" class="lumi-dot"></span>
    </button>

    <!-- Inline Chat Panel -->
    <transition name="lumi-slide">
      <div v-if="isOpen" ref="panelRef" class="lumi-panel" :class="{'dragging': isDragging}" :style="panelStyle">
        <div class="lumi-panel-header" @mousedown.prevent="onHeaderMousedown">
          <div class="flex items-center gap-2">
            <span class="text-lg">🤖</span>
            <div>
              <div class="font-semibold text-white text-sm">Lumi – AP1 Tutor</div>
              <div class="text-indigo-300 text-xs">Ich helfe dir bei dieser Aufgabe</div>
            </div>
          </div>
          <button @click="isOpen = false" class="text-white/60 hover:text-white text-lg leading-none">✕</button>
        </div>

        <!-- Messages -->
        <div ref="msgContainer" class="lumi-messages">
          <div v-if="messages.length === 0 && !isLoading" class="lumi-welcome">
            <p style="font-size:14px;color:#9ca3af;line-height:1.6">{{ welcomeText }}</p>
          </div>
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="lumi-message"
            :class="msg.role === 'user' ? 'lumi-msg-user' : 'lumi-msg-lumi'"
          >
            <div class="lumi-bubble" :class="msg.role === 'user' ? 'lumi-bubble-user' : 'lumi-bubble-lumi'">
              {{ msg.content }}
            </div>
          </div>
          <div v-if="isLoading" class="flex justify-start">
            <div class="lumi-bubble lumi-bubble-lumi flex gap-1 items-center px-3 py-2">
              <span class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style="animation-delay:0ms"></span>
              <span class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style="animation-delay:150ms"></span>
              <span class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style="animation-delay:300ms"></span>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="lumi-input-area">
          <form @submit.prevent="sendMessage" class="flex gap-2">
            <input
              v-model="userInput"
              type="text"
              placeholder="Frag Lumi..."
              class="lumi-input"
              :disabled="isLoading"
              ref="inputEl"
            />
            <button
              type="submit"
              :disabled="!userInput.trim() || isLoading"
              class="lumi-send-btn"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
              </svg>
            </button>
          </form>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, computed } from 'vue'
import { tutorChat } from '@/infrastructure/api/clients/public/learning/tutor/tutor.api'

interface Props {
  context: string        // What exercise is this? E.g. "OSI-Modell Drag & Drop, Aufgabe: HTTP zuordnen"
  systemExtra?: string   // Optional extra system context
}

const props = defineProps<Props>()

interface Msg { id: string; role: 'user' | 'lumi'; content: string }

const isOpen = ref(false)
const messages = ref<Msg[]>([])
const userInput = ref('')
const isLoading = ref(false)
const hasNewMessage = ref(false)
const msgContainer = ref<HTMLDivElement | null>(null)
const inputEl = ref<HTMLInputElement | null>(null)
const panelRef = ref<HTMLDivElement | null>(null)
const isDragging = ref(false)
const panelFixed = ref(false)
const panelLeft = ref(0)
const panelTop = ref(0)
let dX=0,dY=0,dL=0,dT=0
const panelStyle = computed(()=>{
  if(!panelFixed.value) return {}
  return {position:'fixed',left:panelLeft.value+'px',top:panelTop.value+'px',right:'auto',bottom:'auto'}
})
function onHeaderMousedown(e:MouseEvent){
  if(!panelRef.value) return
  if(!panelFixed.value){
    const r=panelRef.value.getBoundingClientRect()
    panelLeft.value=r.left; panelTop.value=r.top; panelFixed.value=true
  }
  isDragging.value=true; dX=e.clientX; dY=e.clientY; dL=panelLeft.value; dT=panelTop.value
  window.addEventListener('mousemove',onDragMove)
  window.addEventListener('mouseup',onDragEnd)
}
function onDragMove(e:MouseEvent){
  panelLeft.value=dL+(e.clientX-dX); panelTop.value=dT+(e.clientY-dY)
}
function onDragEnd(){
  isDragging.value=false
  window.removeEventListener('mousemove',onDragMove)
  window.removeEventListener('mouseup',onDragEnd)
}

const welcomeText = 'Ich bin hier um zu helfen! Stell mir eine Frage zu dieser Aufgabe oder lass dir einen Tipp geben.'

const SYSTEM = `Du bist Lumi, ein kurzer und präziser AP1-Prüfungstutor (FISI BW).
Der Schüler Pascal (ADHS) braucht jetzt Hilfe bei einer konkreten Aufgabe.
Kontext der aktuellen Übung: ${props.context}
${props.systemExtra ?? ''}
WICHTIG: Gib NIEMALS direkt die Lösung oder Antwort! Stelle stattdessen Fragen die Pascal selbst draufkommen lassen.
Gib kurze Antworten (max 3 Sätze). Nutze Emojis. Antworte auf Deutsch.`

async function toggleOpen() {
  isOpen.value = !isOpen.value
  hasNewMessage.value = false
  if (!isOpen.value) { panelFixed.value = false }
  if (isOpen.value) {
    await nextTick()
    inputEl.value?.focus()
    if (messages.value.length === 0) {
      await autoGreet()
    }
  }
}

async function autoGreet() {
  isLoading.value = true
  try {
    const res = await tutorChat({
      message: `Begrüße Pascal kurz (1 Satz) und stelle dann EINE gezielte Frage zur Aufgabe die ihn zum Nachdenken bringt. Aufgabe: ${props.context}. Gib NICHT die Antwort!`,
      systemPrompt: SYSTEM,
    })
    messages.value.push({ id: Date.now().toString(), role: 'lumi', content: res.message })
    await scrollBottom()
  } catch {
    messages.value.push({ id: Date.now().toString(), role: 'lumi', content: '💡 Ich bin bereit! Stell mir eine Frage zu dieser Aufgabe.' })
  } finally {
    isLoading.value = false
  }
}

async function sendMessage() {
  if (!userInput.value.trim() || isLoading.value) return
  const q = userInput.value.trim()
  userInput.value = ''
  messages.value.push({ id: Date.now().toString(), role: 'user', content: q })
  isLoading.value = true
  await scrollBottom()
  try {
    const history = messages.value.slice(0, -1).map(m => ({
      role: m.role === 'user' ? 'user' as const : 'assistant' as const,
      content: m.content
    }))
    const res = await tutorChat({ message: q, systemPrompt: SYSTEM, history })
    messages.value.push({ id: (Date.now()+1).toString(), role: 'lumi', content: res.message })
    if (!isOpen.value) hasNewMessage.value = true
  } catch {
    messages.value.push({ id: (Date.now()+1).toString(), role: 'lumi', content: '⚠️ Fehler beim Laden. Bitte erneut versuchen.' })
  } finally {
    isLoading.value = false
    await scrollBottom()
  }
}

async function scrollBottom() {
  await nextTick()
  if (msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight
}
</script>

<style scoped>
.lumi-hint { position: relative; display: inline-block; }

.lumi-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white; border: none; cursor: pointer; position: relative;
  transition: all 0.2s; box-shadow: 0 2px 8px rgba(99,102,241,0.4);
}
.lumi-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(99,102,241,0.5); }
.lumi-btn-open { background: linear-gradient(135deg, #4f46e5, #7c3aed); }
.lumi-avatar { font-size: 16px; }
.lumi-dot {
  position: absolute; top: -3px; right: -3px;
  width: 10px; height: 10px; border-radius: 50%;
  background: #ef4444; border: 2px solid var(--color-surface, #1e293b);
}

.lumi-panel {
  position: absolute; top: calc(100% + 8px); right: 0; width: 480px; z-index: 1000;
  background: #1e1b4b; border: 1px solid #4338ca; border-radius: 12px;
  box-shadow: 0 8px 32px rgba(99,102,241,0.3); overflow: hidden;
  display: flex; flex-direction: column;
}
.lumi-panel-header {
  background: linear-gradient(135deg, #4338ca, #6d28d9);
  padding: 14px 18px; display: flex; justify-content: space-between; align-items: center;
}
.lumi-messages {
  flex: 1; overflow-y: auto; padding: 14px 16px; space-y: 8px;
  min-height: 200px; max-height: 400px; display: flex; flex-direction: column; gap: 10px;
}
.lumi-welcome { text-align: center; padding: 12px; }
.lumi-message { display: flex; }
.lumi-msg-user { justify-content: flex-end; }
.lumi-msg-lumi { justify-content: flex-start; }
.lumi-bubble {
  max-width: 85%; border-radius: 12px; padding: 12px 16px;
  font-size: 14px; line-height: 1.7; white-space: pre-wrap;
}
.lumi-bubble-user { background: #4f46e5; color: white; border-bottom-right-radius: 4px; }
.lumi-bubble-lumi { background: #312e81; color: #e0e7ff; border-bottom-left-radius: 4px; }
.lumi-input-area { padding: 12px 14px; border-top: 1px solid #3730a3; }
.lumi-input {
  flex: 1; padding: 8px 14px; border-radius: 20px; font-size: 14px;
  background: #312e81; color: white; border: 1px solid #4338ca;
  outline: none; min-width: 0;
}
.lumi-input:focus { border-color: #6366f1; }
.lumi-input-area form { display: flex; gap: 6px; }
.lumi-send-btn {
  padding: 6px 10px; border-radius: 50%; background: #6366f1; color: white;
  border: none; cursor: pointer; flex-shrink: 0; display: flex; align-items: center;
}
.lumi-send-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.lumi-send-btn:hover:not(:disabled) { background: #4f46e5; }

.lumi-slide-enter-active, .lumi-slide-leave-active { transition: all 0.2s ease; }
.lumi-slide-enter-from, .lumi-slide-leave-to { opacity: 0; transform: translateY(8px) scale(0.95); }

.lumi-panel { resize: both; overflow: hidden; min-width: 320px; min-height: 280px; }
.lumi-panel-header { cursor: grab; user-select: none; }
.dragging .lumi-panel-header { cursor: grabbing; }
.dragging { user-select: none; }
</style>
