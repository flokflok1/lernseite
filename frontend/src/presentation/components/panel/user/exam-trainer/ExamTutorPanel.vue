<script setup lang="ts">
/**
 * ExamTutorPanel — AI tutor chat for exam practice.
 * Knows the current question context and helps without revealing answers.
 */
import { ref, computed, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import DOMPurify from 'dompurify'
import { tutorChat } from '@/infrastructure/api/clients/public/learning/tutor/tutor.api'

interface Props {
  questionText: string
  scenarioTitle: string
  scenarioText: string
  solutionHint?: string  // NOT the full solution — just topic area
  questionType: string
  points: number | string
}

const props = defineProps<Props>()
const emit = defineEmits<{ close: [] }>()
const { t } = useI18n()

interface ChatMessage {
  role: 'user' | 'tutor'
  content: string
  timestamp: Date
}

const messages = ref<ChatMessage[]>([])
const userInput = ref('')
const isTyping = ref(false)
const chatContainer = ref<HTMLDivElement | null>(null)
const hintLevel = ref(0)

// Build exam-specific system prompt
const systemPrompt = computed(() => `Du bist ein IHK-Pruefungscoach fuer Fachinformatiker.
Der Pruefling bearbeitet gerade eine Aufgabe und braucht Hilfe.

DEINE METHODE — INTERAKTIVES RATE-SPIEL:
Du fuehrst den Pruefling wie bei einem Quiz Schritt fuer Schritt zur Antwort.

ABLAUF:
1. Zaehle wie viele Punkte die Aufgabe verlangt (z.B. "Du brauchst 4 Nennungen: je 2 interne und 2 externe")
2. Frag nach dem ERSTEN Punkt: "Fangen wir an — faellt dir eine externe Bezugsquelle ein?"
3. Wenn der Pruefling etwas nennt (auch umgangssprachlich):
   - Bestaetigung: "Richtig gedacht! 🎯"
   - Zeige die Pruefungsformulierung: "Schreib: **1. Internetrecherche (z.B. Suchmaschinen, Lieferantenportale)**"
   - Dann frag nach dem naechsten: "Weiter — noch eine externe?"
4. Wenn der Pruefling nicht weiterkommt:
   - Gib einen kleinen Tipp wie beim Galgenmaennchen: "Der Begriff beginnt mit F... und hat mit gedruckten Verzeichnissen zu tun..."
   - Wird es nicht: Noch ein Tipp: "Man kann sie in Buchhandlungen kaufen... Fach-K..."
   - Immer noch nicht: Loesung zeigen: "Das waere: **Fachkataloge (Branchenverzeichnisse)**"
5. Am Ende: "Fertig! Hier ist deine komplette Antwort zum Abschicken:" und zeige alle Punkte formatiert

FORMULIERUNGSREGELN fuer die Pruefung:
- Immer nummerieren: 1., 2., 3.
- Fachbegriff zuerst, Erklaerung in Klammern
- Beispiel: "1. Warenwirtschaftssystem (Lieferanten- und Warendatei)"
- NICHT: "wo man nachschauen kann wer frueher geliefert hat"

WICHTIG:
- Sei ermutigend bei jedem richtigen Ansatz, auch wenn die Wortwahl noch nicht perfekt ist
- "Google" → "Richtig! In der Pruefung heisst das: Internetrecherche"
- "Kataloge" → "Genau! Pruefungsbegriff: Fachkataloge"
- Verwende Emojis sparsam fuer Motivation (🎯 ✅ 💡)
- Sprich Deutsch, locker aber fachlich

AKTUELLE AUFGABE:
Typ: ${props.questionType} (${props.points} Punkte)
Szenario: ${props.scenarioTitle}
${props.scenarioText ? 'Kontext: ' + props.scenarioText.slice(0, 500) : ''}

Aufgabentext: ${props.questionText}

THEMENBEREICH: ${props.solutionHint || 'Allgemein'}`)

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const sendMessage = async (text?: string) => {
  const msg = text || userInput.value.trim()
  if (!msg || isTyping.value) return

  messages.value.push({ role: 'user', content: msg, timestamp: new Date() })
  userInput.value = ''
  isTyping.value = true
  await scrollToBottom()

  try {
    const history = messages.value.slice(-10).map(m => ({
      role: m.role === 'tutor' ? 'assistant' as const : 'user' as const,
      content: m.content,
    }))

    const response = await tutorChat({
      message: msg,
      systemPrompt: systemPrompt.value,
      history: history.slice(0, -1),
      context: `Pruefungstrainer: ${props.scenarioTitle} - ${props.questionType}`,
    })

    messages.value.push({
      role: 'tutor',
      content: response.message || t('panel.examTrainer.tutor.noResponse'),
      timestamp: new Date(),
    })
  } catch {
    messages.value.push({
      role: 'tutor',
      content: t('panel.examTrainer.tutor.error'),
      timestamp: new Date(),
    })
  } finally {
    isTyping.value = false
    await scrollToBottom()
  }
}

const startGuidedSolving = () => {
  sendMessage('Lass uns die Aufgabe zusammen lösen. Frag mich Schritt für Schritt nach jedem Punkt den ich nennen muss.')
}

const explainTopic = () => {
  sendMessage('Erkläre mir das Thema hinter dieser Aufgabe einfach und verständlich.')
}

const showFormattingHelp = () => {
  sendMessage('Zeig mir wie ich meine Antwort für die IHK-Prüfung richtig formatiere.')
}

const questionLabel = computed(() => {
  if (props.questionType === 'code') return t('panel.examTrainer.tutor.questionTypes.code')
  if (props.questionType === 'calculation') return t('panel.examTrainer.tutor.questionTypes.calculation')
  return t('panel.examTrainer.tutor.questionTypes.text')
})

// Auto-greet on first open
watch(messages, (val) => {
  if (val.length === 0) {
    messages.value.push({
      role: 'tutor',
      content: t('panel.examTrainer.tutor.greeting', {
        type: questionLabel.value,
        scenario: props.scenarioTitle,
      }),
      timestamp: new Date(),
    })
  }
}, { immediate: true })
</script>

<template>
  <div class="flex flex-col h-full max-h-[700px] min-h-[400px] rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] overflow-hidden">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-indigo-600 to-purple-600">
      <div class="flex items-center gap-2">
        <span class="font-semibold text-white text-sm">{{ t('panel.examTrainer.tutor.title') }}</span>
      </div>
      <button class="text-white/70 hover:text-white transition-colors" @click="emit('close')">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Quick actions -->
    <div class="flex gap-2 px-3 py-2 border-b border-[var(--color-border)] bg-[var(--color-background)]">
      <button
        class="px-2.5 py-1 text-xs rounded-lg bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 transition-colors"
        @click="startGuidedSolving"
      >
        🎯 Gemeinsam lösen
      </button>
      <button
        class="px-2.5 py-1 text-xs rounded-lg bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 transition-colors"
        @click="explainTopic"
      >
        📚 Thema erklären
      </button>
      <button
        class="px-2.5 py-1 text-xs rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 transition-colors"
        @click="showFormattingHelp"
      >
        ✍️ Formulierung
      </button>
    </div>

    <!-- Messages -->
    <div ref="chatContainer" class="flex-1 overflow-y-auto px-4 py-3 space-y-3">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="flex"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[90%] px-4 py-3 rounded-xl text-sm leading-relaxed"
          :class="msg.role === 'user'
            ? 'bg-blue-600 text-white rounded-br-sm'
            : 'bg-[var(--color-background)] text-[var(--color-text)] rounded-bl-sm border border-[var(--color-border)]'"
        >
          <div v-if="msg.role === 'tutor'" v-html="DOMPurify.sanitize(msg.content.replace(/\n/g, '<br>'))" />
          <span v-else>{{ msg.content }}</span>
        </div>
      </div>

      <!-- Typing indicator -->
      <div v-if="isTyping" class="flex justify-start">
        <div class="bg-[var(--color-background)] text-[var(--color-text-secondary)] px-4 py-2 rounded-xl rounded-bl-sm border border-[var(--color-border)] text-sm">
          <span class="inline-flex gap-1">
            <span class="animate-bounce" style="animation-delay: 0ms">.</span>
            <span class="animate-bounce" style="animation-delay: 150ms">.</span>
            <span class="animate-bounce" style="animation-delay: 300ms">.</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Input -->
    <div class="flex gap-2 px-3 py-3 border-t border-[var(--color-border)]">
      <input
        v-model="userInput"
        type="text"
        class="flex-1 px-3 py-2 text-sm rounded-lg border border-[var(--color-border)]
               bg-[var(--color-background)] text-[var(--color-text)]
               focus:outline-none focus:border-blue-500
               placeholder:text-[var(--color-text-secondary)]"
        :placeholder="t('panel.examTrainer.tutor.inputPlaceholder')"
        @keydown.enter="sendMessage()"
      />
      <button
        :disabled="!userInput.trim() || isTyping"
        class="px-3 py-2 rounded-lg bg-blue-600 text-white text-sm
               hover:bg-blue-700 disabled:opacity-40 transition-colors"
        @click="sendMessage()"
        :aria-label="t('panel.examTrainer.tutor.send')"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
        </svg>
      </button>
    </div>
  </div>
</template>
