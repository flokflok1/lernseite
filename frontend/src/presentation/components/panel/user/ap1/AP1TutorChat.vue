<template>
  <div class="ap1-tutor">
    <!-- Intro Banner -->
    <div class="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-5 mb-5 text-white">
      <div class="flex items-center gap-3 mb-2">
        <div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center text-2xl">🤖</div>
        <div>
          <h2 class="text-xl font-bold">Lumi – dein AP1-Tutor</h2>
          <p class="text-indigo-200 text-sm">Spezialisiert auf FISI AP1 in Baden-Württemberg</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- Quick Topics Sidebar -->
      <div class="lg:col-span-1">
        <h3 class="font-semibold text-[var(--color-text-primary)] mb-3 text-sm uppercase tracking-wide">⚡ Schnell-Fragen</h3>
        <div class="space-y-2">
          <button
            v-for="q in quickQuestions"
            :key="q.label"
            @click="sendQuickQuestion(q.prompt)"
            class="w-full text-left px-3 py-2.5 rounded-lg border border-[var(--color-border)] hover:border-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-all text-sm"
            :class="isLoading ? 'opacity-50 cursor-not-allowed' : ''"
            :disabled="isLoading"
          >
            <span class="mr-2">{{ q.icon }}</span>{{ q.label }}
          </button>
        </div>

        <!-- Prüfungstipp des Tages -->
        <div class="mt-5 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-xl">
          <div class="text-sm font-semibold text-yellow-800 dark:text-yellow-300 mb-1">💡 Tipp des Tages</div>
          <p class="text-xs text-yellow-700 dark:text-yellow-400">{{ dailyTip }}</p>
        </div>
      </div>

      <!-- Chat Area -->
      <div class="lg:col-span-2 flex flex-col bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl overflow-hidden" style="height: 520px;">
        <!-- Chat Messages -->
        <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-3">
          <!-- Welcome -->
          <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center py-8">
            <div class="text-5xl mb-4">🎓</div>
            <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-2">Hallo Pascal! Ich bin Lumi.</h3>
            <p class="text-[var(--color-text-secondary)] text-sm max-w-xs">
              Ich bin dein persönlicher AP1-Tutor für die BW-Prüfung am <strong>14.04.2026</strong>.
              Frag mich alles — Netzwerke, SQL, Sicherheit, Kalkulation... ich erklär's dir!
            </p>
            <div class="mt-4 flex flex-wrap gap-2 justify-center">
              <span
                v-for="t in ['OSI-Modell', 'Subnetting', 'SQL', 'CIA-Triade', 'Kalkulation']"
                :key="t"
                class="px-2 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-full text-xs cursor-pointer hover:bg-indigo-200 transition-colors"
                @click="sendQuickQuestion(`Erkläre mir ${t} für die AP1-Prüfung kurz und verständlich.`)"
              >
                {{ t }}
              </span>
            </div>
          </div>

          <!-- Messages -->
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="flex"
            :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <!-- Tutor avatar -->
            <div v-if="msg.role === 'tutor'" class="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-sm mr-2 flex-shrink-0 mt-1">🤖</div>

            <div
              class="max-w-[80%] rounded-2xl px-4 py-3 text-sm"
              :class="msg.role === 'user'
                ? 'bg-indigo-600 text-white rounded-br-md'
                : 'bg-gray-100 dark:bg-gray-700 text-[var(--color-text-primary)] rounded-bl-md'"
            >
              <div class="whitespace-pre-wrap leading-relaxed">{{ msg.content }}</div>
              <div class="text-xs mt-1.5 opacity-60">{{ formatTime(msg.timestamp) }}</div>
            </div>
          </div>

          <!-- Typing indicator -->
          <div v-if="isLoading" class="flex justify-start">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center mr-2 flex-shrink-0">🤖</div>
            <div class="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-md px-4 py-3">
              <div class="flex gap-1 items-center">
                <span class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                <span class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                <span class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
                <span class="ml-2 text-xs text-gray-500 dark:text-gray-400">Lumi denkt nach...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="p-3 border-t border-[var(--color-border)]">
          <form @submit.prevent="sendMessage" class="flex gap-2">
            <input
              v-model="userInput"
              type="text"
              placeholder="Stell mir eine Frage zur AP1-Prüfung..."
              class="flex-1 px-4 py-2.5 rounded-full border border-[var(--color-border)] bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              :disabled="isLoading"
              ref="inputRef"
            />
            <button
              type="submit"
              :disabled="!userInput.trim() || isLoading"
              class="p-2.5 rounded-full bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex-shrink-0"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
            <button
              v-if="messages.length > 0"
              type="button"
              @click="clearChat"
              class="p-2.5 rounded-full border border-[var(--color-border)] hover:bg-red-50 dark:hover:bg-red-900/20 text-[var(--color-text-secondary)] hover:text-red-500 transition-colors flex-shrink-0"
              title="Chat leeren"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </form>
          <p class="text-center text-xs text-[var(--color-text-secondary)] mt-2">
            Powered by LernsystemX AI · Spezialisiert auf FISI AP1 BW
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { tutorChat } from '@/infrastructure/api/clients/public/learning/tutor/tutor.api'

interface Message {
  id: string
  role: 'user' | 'tutor'
  content: string
  timestamp: Date
}

const messages = ref<Message[]>([])
const userInput = ref('')
const isLoading = ref(false)
const chatContainer = ref<HTMLDivElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

const AP1_SYSTEM_PROMPT = `Du bist Lumi, ein freundlicher und motivierender AP1-Prüfungstutor für Pascal.

Pascal macht seine FISI (Fachinformatiker Systemintegration) Abschlussprüfung am 14.04.2026 bei der IHK Ulm in Baden-Württemberg (BW).

WICHTIGE BESONDERHEITEN FÜR BW:
- BW hat eine EIGENE AP1-Prüfung vom Kultusministerium (nicht die bundesweite IHK-Prüfung)
- SQL ist SEHR RELEVANT in BW (SELECT, INSERT, UPDATE, DELETE, JOIN, GROUP BY, HAVING)
- Viele Freitext-Aufgaben (keine reinen Multiple-Choice)
- Typische BW-Themen: Netzwerk/Subnetting, Datenbanken/SQL, IT-Sicherheit, Kalkulation/BWL, Programmierung, Organisation, Datenschutz

PASCAL HAT ADHS - erkläre deshalb:
- Kurz und prägnant (keine langen Texte)
- Mit klaren Struktur und Aufzählungen
- Mit konkreten Beispielen und Eselsbrücken
- Motivierend und positiv
- Wichtiges gerne mit 🎯, Beispiele mit 💡, Merkhilfen mit 🧠

DEINE AUFGABE:
- Erkläre Konzepte verständlich und prüfungsrelevant
- Gib Beispiele aus echten BW-AP1-Prüfungen
- Helfe bei Verständnisfragen zu allen AP1-Themen
- Gib Lernstrategien für ADHS
- Motiviere Pascal für seine bald stattfindende Prüfung!

Antworte IMMER auf Deutsch. Halte Antworten übersichtlich.`

const quickQuestions = [
  { icon: '🌐', label: 'OSI-Modell erklären', prompt: 'Erkläre mir das OSI-Modell für die AP1-Prüfung. Was muss ich auf jeden Fall wissen?' },
  { icon: '📍', label: 'Subnetting Formel', prompt: 'Erkläre mir Subnetting Schritt für Schritt mit einem Beispiel. Wie berechne ich Netzadresse, Broadcast und nutzbarte Hosts?' },
  { icon: '🗄️', label: 'SQL Basics', prompt: 'Welche SQL-Befehle kommen in der BW AP1-Prüfung vor? Gib mir die wichtigsten mit Beispielen.' },
  { icon: '🔒', label: 'CIA-Triade', prompt: 'Was ist die CIA-Triade? Erkläre Vertraulichkeit, Integrität und Verfügbarkeit mit Praxisbeispielen.' },
  { icon: '💰', label: 'Bezugskalkulation', prompt: 'Erkläre mir die Bezugskalkulation Schritt für Schritt. Was sind die typischen Aufgaben in der AP1?' },
  { icon: '⚡', label: 'Stromkosten rechnen', prompt: 'Wie berechne ich Stromkosten für Server? Gib mir die Formel und ein Beispiel wie in der Prüfung.' },
  { icon: '🛡️', label: 'DSGVO Grundlagen', prompt: 'Was muss ich zur DSGVO für die AP1-Prüfung wissen? Die wichtigsten Punkte bitte.' },
  { icon: '🧠', label: 'Lernstrategie ADHS', prompt: 'Gib mir eine ADHS-freundliche Lernstrategie für die letzten Tage vor der AP1-Prüfung am 14.04.' },
]

const tips = [
  'Subnetting: Merke dir /24 = 256 Adressen, /25 = 128, /26 = 64, /27 = 32, /28 = 16. Jedes Bit halbiert die Anzahl!',
  'Bei Freitext-Aufgaben: Immer Fachbegriffe verwenden! "Vertraulichkeit" statt "geheim halten".',
  'SQL JOIN: INNER JOIN = nur Übereinstimmungen, LEFT JOIN = alle aus der linken Tabelle.',
  'OSI-Merkhilfe: "Alle Päckchen Sollen Transportiert Werden Nicht Weg" (Anwendung→Bitübertragung)',
  'Bezugskalkulation: Listenpreis → Rabatt abziehen → Zieleinkaufspreis → Skonto abziehen → Bareinkaufspreis → Bezugskosten → Bezugspreis',
  'CIA: Confidentiality (Vertraulichkeit), Integrity (Integrität), Availability (Verfügbarkeit)',
  'Stromkosten: Watt ÷ 1000 × Stunden × Preis pro kWh. Einheiten immer prüfen!',
  'Bei DSGVO: Datensparsamkeit, Zweckbindung, Betroffenenrechte sind Kernprinzipien.',
]

const dailyTip = tips[new Date().getDate() % tips.length]

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const buildHistory = () => {
  return messages.value.map(m => ({
    role: m.role === 'tutor' ? 'assistant' as const : 'user' as const,
    content: m.content
  }))
}

const sendQuickQuestion = async (prompt: string) => {
  userInput.value = prompt
  await sendMessage()
}

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const userMsg: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: userInput.value.trim(),
    timestamp: new Date()
  }

  messages.value.push(userMsg)
  const question = userInput.value.trim()
  userInput.value = ''
  isLoading.value = true
  await scrollToBottom()

  try {
    const response = await tutorChat({
      message: question,
      systemPrompt: AP1_SYSTEM_PROMPT,
      history: buildHistory().slice(0, -1), // exclude last user msg (already sent as message)
    })

    const tutorMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'tutor',
      content: response.message,
      timestamp: new Date()
    }
    messages.value.push(tutorMsg)
  } catch (err) {
    const errorMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'tutor',
      content: '⚠️ Entschuldigung, ich konnte deine Frage gerade nicht beantworten. Bitte versuche es nochmal.',
      timestamp: new Date()
    }
    messages.value.push(errorMsg)
  } finally {
    isLoading.value = false
    await scrollToBottom()
    inputRef.value?.focus()
  }
}

const clearChat = () => {
  messages.value = []
}
</script>
