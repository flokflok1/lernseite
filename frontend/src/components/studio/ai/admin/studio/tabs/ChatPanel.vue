<!--
  Chat Panel - Collapsible AI Assistant Chat

  Features:
  - Einklappbares Chat-Panel
  - KI-Assistent für Fragen
  - Kontext-bezogene Hilfe
  - Schnellaktionen
  - Chat-Historie
-->

<template>
  <div
    class="chat-panel h-full flex flex-col bg-[var(--color-surface)] border-l border-[var(--color-border)]"
    :class="{ 'w-80': isExpanded, 'w-12': !isExpanded }"
  >
    <!-- Toggle Button (when collapsed) -->
    <button
      v-if="!isExpanded"
      @click="togglePanel"
      class="h-full w-full flex flex-col items-center justify-center gap-2 hover:bg-[var(--color-surface-secondary)] transition-colors"
    >
      <span class="text-2xl">💬</span>
      <span class="text-xs text-[var(--color-text-tertiary)] writing-mode-vertical">{{ $t('features.aiEditorChat.title') }}</span>
    </button>

    <!-- Expanded Panel -->
    <template v-else>
      <!-- Header -->
      <div class="flex items-center justify-between p-3 border-b border-[var(--color-border)]">
        <div class="flex items-center gap-2">
          <span class="text-xl">🤖</span>
          <div>
            <h3 class="font-medium text-[var(--color-text-primary)] text-sm">{{ $t('features.aiEditorChat.assistant') }}</h3>
            <p class="text-xs text-[var(--color-text-tertiary)]">
              <span class="w-2 h-2 bg-green-500 rounded-full inline-block mr-1"></span>
              {{ $t('features.aiEditorChat.online') }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-1">
          <button
            @click="clearChat"
            class="p-1.5 hover:bg-[var(--color-surface-secondary)] rounded transition-colors"
            :title="$t('features.aiEditorChat.clearChat')"
          >
            🗑️
          </button>
          <button
            @click="togglePanel"
            class="p-1.5 hover:bg-[var(--color-surface-secondary)] rounded transition-colors"
            :title="$t('features.aiEditorChat.collapse')"
          >
            ›
          </button>
        </div>
      </div>

      <!-- Quick Actions - Loaded from DB -->
      <div class="p-2 border-b border-[var(--color-border)]">
        <div v-if="actionsLoading" class="text-xs text-center text-[var(--color-text-tertiary)] py-1">
          {{ $t('features.aiEditorChat.loadingActions') }}
        </div>
        <div v-else class="flex flex-wrap gap-1">
          <button
            v-for="action in quickActions"
            :key="action.action_id"
            @click="executeAction(action)"
            class="px-2 py-1 text-xs bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] rounded-lg hover:bg-[var(--color-primary-subtle)] hover:text-[var(--color-primary)] transition-colors"
          >
            {{ action.icon }} {{ action.label }}
          </button>
        </div>
      </div>

      <!-- Context Info -->
      <div v-if="currentContext" class="p-2 bg-[var(--color-primary-subtle)] text-xs">
        <div class="flex items-center gap-2">
          <span class="text-[var(--color-primary)]">📍</span>
          <span class="text-[var(--color-text-secondary)]">{{ $t('features.aiEditorChat.context') }}: {{ currentContext }}</span>
        </div>
      </div>

      <!-- Messages -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto p-3 space-y-3">
        <!-- Welcome Message -->
        <div v-if="messages.length === 0" class="text-center py-6">
          <span class="text-4xl mb-3 block">👋</span>
          <h4 class="font-medium text-[var(--color-text-primary)] mb-1">{{ $t('features.aiEditorChat.welcomeTitle') }}</h4>
          <p class="text-sm text-[var(--color-text-secondary)]">
            {{ $t('features.aiEditorChat.welcomeText') }}
          </p>
        </div>

        <!-- Chat Messages -->
        <div
          v-for="message in messages"
          :key="message.id"
          class="flex gap-2"
          :class="{ 'flex-row-reverse': message.role === 'user' }"
        >
          <!-- Avatar -->
          <div
            class="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-sm"
            :class="message.role === 'user'
              ? 'bg-[var(--color-primary)] text-white'
              : 'bg-[var(--color-surface-secondary)]'"
          >
            {{ message.role === 'user' ? '👤' : '🤖' }}
          </div>

          <!-- Message Bubble -->
          <div
            class="max-w-[85%] p-2.5 rounded-xl text-sm"
            :class="message.role === 'user'
              ? 'bg-[var(--color-primary)] text-white rounded-tr-sm'
              : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] rounded-tl-sm'"
          >
            <p class="whitespace-pre-wrap">{{ message.content }}</p>
            <span
              class="text-xs mt-1 block"
              :class="message.role === 'user' ? 'text-white/70' : 'text-[var(--color-text-tertiary)]'"
            >
              {{ message.time }}
            </span>
          </div>
        </div>

        <!-- Typing Indicator -->
        <div v-if="isTyping" class="flex gap-2">
          <div class="w-7 h-7 rounded-full bg-[var(--color-surface-secondary)] flex items-center justify-center text-sm">
            🤖
          </div>
          <div class="bg-[var(--color-surface-secondary)] rounded-xl rounded-tl-sm p-2.5">
            <div class="flex gap-1">
              <span class="w-2 h-2 bg-[var(--color-text-tertiary)] rounded-full animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-2 h-2 bg-[var(--color-text-tertiary)] rounded-full animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-2 h-2 bg-[var(--color-text-tertiary)] rounded-full animate-bounce" style="animation-delay: 300ms"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Suggestions -->
      <div v-if="suggestions.length > 0" class="p-2 border-t border-[var(--color-border)]">
        <p class="text-xs text-[var(--color-text-tertiary)] mb-1">{{ $t('features.aiEditorChat.suggestions') }}</p>
        <div class="flex flex-wrap gap-1">
          <button
            v-for="suggestion in suggestions"
            :key="suggestion"
            @click="sendSuggestion(suggestion)"
            class="px-2 py-1 text-xs bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] rounded-lg hover:bg-[var(--color-primary-subtle)] hover:text-[var(--color-primary)] transition-colors"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>

      <!-- Input Area -->
      <div class="p-3 border-t border-[var(--color-border)]">
        <div class="flex gap-2">
          <textarea
            v-model="inputMessage"
            @keydown.enter.prevent="sendMessage"
            class="flex-1 px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg text-sm text-[var(--color-text-primary)] resize-none focus:outline-none focus:border-[var(--color-primary)]"
            :placeholder="$t('features.aiEditorChat.placeholder')"
            rows="2"
          ></textarea>
          <button
            @click="sendMessage"
            :disabled="!inputMessage.trim() || isTyping"
            class="px-3 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            📤
          </button>
        </div>
        <div class="flex items-center justify-between mt-2 text-xs text-[var(--color-text-tertiary)]">
          <span>{{ $t('features.aiEditorChat.enterToSend') }}</span>
          <span>{{ inputMessage.length }}/500</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getActionsByCategory, type AuthoringAction } from '@/api/ai-authoring.api'

const { t } = useI18n()

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  time: string
}

interface QuickAction {
  action_id: string
  action_key: string
  label: string
  icon: string
  prompt_template: string
}

interface Props {
  lessonTitle?: string
  courseTitle?: string
}

const props = defineProps<Props>()

// State
const isExpanded = ref(true)
const inputMessage = ref('')
const messages = ref<Message[]>([])
const isTyping = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const actionsLoading = ref(false)

// Quick Actions - loaded from database
const quickActions = ref<QuickAction[]>([])

// Fallback actions if DB is not available
const fallbackActions: QuickAction[] = [
  { action_id: 'fb-1', action_key: 'explain', label: t('features.aiEditorChat.fallbackActions.explain.label'), icon: '📖', prompt_template: t('features.aiEditorChat.fallbackActions.explain.prompt') },
  { action_id: 'fb-2', action_key: 'improve', label: t('features.aiEditorChat.fallbackActions.improve.label'), icon: '✨', prompt_template: t('features.aiEditorChat.fallbackActions.improve.prompt') },
  { action_id: 'fb-3', action_key: 'quiz_create', label: t('features.aiEditorChat.fallbackActions.quiz.label'), icon: '❓', prompt_template: t('features.aiEditorChat.fallbackActions.quiz.prompt') },
  { action_id: 'fb-4', action_key: 'summarize', label: t('features.aiEditorChat.fallbackActions.summarize.label'), icon: '📝', prompt_template: t('features.aiEditorChat.fallbackActions.summarize.prompt') }
]

// Load actions from database
async function loadQuickActions() {
  actionsLoading.value = true
  try {
    const actions = await getActionsByCategory('chat')
    if (actions && actions.length > 0) {
      quickActions.value = actions.map(a => ({
        action_id: a.action_id,
        action_key: a.action_key,
        label: a.label,
        icon: a.icon || '📋',
        prompt_template: a.prompt_template
      }))
    } else {
      quickActions.value = fallbackActions
    }
  } catch (err) {
    console.warn('Failed to load chat actions from DB, using fallback:', err)
    quickActions.value = fallbackActions
  } finally {
    actionsLoading.value = false
  }
}

// Suggestions based on context
const suggestions = ref<string[]>([
  t('features.aiEditorChat.defaultSuggestions.teachingSteps'),
  t('features.aiEditorChat.defaultSuggestions.videoGeneration'),
  t('features.aiEditorChat.defaultSuggestions.modelComparison')
])

// Current Context
const currentContext = ref<string | null>(null)

// Watch for context changes
watch(() => props.lessonTitle, (newTitle) => {
  if (newTitle) {
    currentContext.value = newTitle
  }
}, { immediate: true })

// Methods
function togglePanel() {
  isExpanded.value = !isExpanded.value
}

function clearChat() {
  if (messages.value.length === 0 || confirm(t('features.aiEditorChat.confirmClear'))) {
    messages.value = []
  }
}

async function sendMessage() {
  if (!inputMessage.value.trim() || isTyping.value) return

  const userMessage: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: inputMessage.value.trim(),
    time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
  }

  messages.value.push(userMessage)
  const question = inputMessage.value
  inputMessage.value = ''

  await scrollToBottom()

  // Simulate AI response
  isTyping.value = true

  try {
    await new Promise(resolve => setTimeout(resolve, 1500))

    const aiResponse: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: generateResponse(question),
      time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
    }

    messages.value.push(aiResponse)
    await scrollToBottom()

  } finally {
    isTyping.value = false
  }
}

function sendSuggestion(suggestion: string) {
  inputMessage.value = suggestion
  sendMessage()
}

function executeAction(action: QuickAction) {
  inputMessage.value = action.prompt_template
  sendMessage()
}

function generateResponse(question: string): string {
  // Simple mock responses - in real implementation, this would call the AI API
  const lowerQuestion = question.toLowerCase()

  if (lowerQuestion.includes('teaching steps')) {
    return 'Teaching Steps sind einzelne Lernschritte, die der KI-Tutor im Video durchgeht. Jeder Step enthält:\n\n• Speech: Was der Tutor sagt\n• Animation: Wie er sich bewegt\n• Whiteboard: Was auf der Tafel erscheint\n\nDu kannst sie manuell erstellen oder automatisch mit KI generieren lassen.'
  }

  if (lowerQuestion.includes('video')) {
    return 'Um ein Video zu generieren:\n\n1. Wähle eine Lektion aus\n2. Gehe zum Video-Tab\n3. Wähle Avatar-Stil und Sora-Modell\n4. Klicke auf "Video generieren"\n\nSora 2 erstellt Video UND Audio synchron - kein separates TTS nötig!'
  }

  if (lowerQuestion.includes('modell') || lowerQuestion.includes('model')) {
    return 'Sora 2 vs Sora 2 Pro:\n\n🟢 Sora 2:\n• Schneller (~30s Generation)\n• Günstiger ($0.10/s)\n• Gute Qualität\n\n🟣 Sora 2 Pro:\n• Höchste Qualität\n• Längere Videos möglich\n• Teurer ($0.20/s)\n\nFür die meisten Lektionen reicht Sora 2!'
  }

  if (lowerQuestion.includes('verbessern') || lowerQuestion.includes('improve')) {
    return 'Hier sind Tipps zur Content-Verbesserung:\n\n1. Klare, kurze Sätze verwenden\n2. Beispiele hinzufügen\n3. Visualisierungen nutzen\n4. Teaching Steps logisch aufbauen\n5. Am Ende eine Zusammenfassung\n\nSoll ich den aktuellen Content analysieren?'
  }

  return 'Das ist eine interessante Frage! Im KI-Studio Pro kannst du:\n\n• Content mit KI generieren\n• Videos erstellen (Sora 2)\n• Prompts verwalten\n• Assets hochladen\n• Statistiken einsehen\n\nWas möchtest du genauer wissen?'
}

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Mount
onMounted(async () => {
  await loadQuickActions()
})
</script>

<style scoped>
.chat-panel {
  transition: width 0.3s ease;
}

.writing-mode-vertical {
  writing-mode: vertical-rl;
  text-orientation: mixed;
}
</style>
