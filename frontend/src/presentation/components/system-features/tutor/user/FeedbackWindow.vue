<script setup lang="ts">
/**
 * FeedbackWindow - Separates Fenster für Nutzer-Feedback & Fragen
 *
 * Features:
 * - Nutzer können Fragen stellen
 * - Feedback zu Kursen/Lektionen geben
 * - Bug-Reports senden
 * - Verbesserungsvorschläge machen
 * - KI fasst alles zusammen für den Admin
 */

import { ref, computed, onMounted } from 'vue'
import http from '@/application/services/api/system'

// Props & Emits
const props = defineProps<{
  courseId?: string
  lessonId?: string
  context?: string
}>()

const emit = defineEmits<{
  close: []
  submitted: [feedbackId: string]
}>()

// Types
type FeedbackType = 'question' | 'bug' | 'suggestion' | 'praise' | 'other'

interface FeedbackCategory {
  id: FeedbackType
  name: string
  icon: string
  description: string
  placeholder: string
}

// State
const feedbackType = ref<FeedbackType>('question')
const title = ref('')
const message = ref('')
const email = ref('')
const isAnonymous = ref(false)
const isSubmitting = ref(false)
const isSubmitted = ref(false)
const submitError = ref<string | null>(null)
const feedbackId = ref<string | null>(null)

// Categories
const categories: FeedbackCategory[] = [
  {
    id: 'question',
    name: 'Frage',
    icon: '❓',
    description: 'Ich habe eine Frage zu...',
    placeholder: 'Beschreibe deine Frage so genau wie möglich...'
  },
  {
    id: 'bug',
    name: 'Problem',
    icon: '🐛',
    description: 'Etwas funktioniert nicht',
    placeholder: 'Was ist passiert? Was hast du erwartet? Welcher Browser/Gerät?'
  },
  {
    id: 'suggestion',
    name: 'Vorschlag',
    icon: '💡',
    description: 'Ich habe eine Idee',
    placeholder: 'Was würde die Plattform besser machen?'
  },
  {
    id: 'praise',
    name: 'Lob',
    icon: '⭐',
    description: 'Das finde ich super!',
    placeholder: 'Was gefällt dir besonders gut?'
  },
  {
    id: 'other',
    name: 'Sonstiges',
    icon: '📝',
    description: 'Etwas anderes',
    placeholder: 'Was möchtest du mitteilen?'
  }
]

// Computed
const selectedCategory = computed(() =>
  categories.find(c => c.id === feedbackType.value) || categories[0]
)

const canSubmit = computed(() =>
  message.value.trim().length >= 10 && !isSubmitting.value
)

const contextInfo = computed(() => {
  const parts = []
  if (props.courseId) parts.push(`Kurs: ${props.courseId}`)
  if (props.lessonId) parts.push(`Lektion: ${props.lessonId}`)
  if (props.context) parts.push(props.context)
  return parts.length > 0 ? parts.join(' | ') : 'Allgemein'
})

// Methods
const selectType = (type: FeedbackType) => {
  feedbackType.value = type
}

const submitFeedback = async () => {
  if (!canSubmit.value) return

  isSubmitting.value = true
  submitError.value = null

  try {
    const response = await http.post<{
      success: boolean
      data: { feedback_id: string; message: string }
    }>('/feedback/submit', {
      type: feedbackType.value,
      title: title.value || `${selectedCategory.value.name}: ${message.value.substring(0, 50)}...`,
      message: message.value,
      email: isAnonymous.value ? null : email.value || null,
      is_anonymous: isAnonymous.value,
      context: {
        course_id: props.courseId || null,
        lesson_id: props.lessonId || null,
        page_context: props.context || null,
        url: window.location.href,
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString()
      }
    })

    isSubmitted.value = true
    feedbackId.value = response.data.data.feedback_id
    emit('submitted', response.data.data.feedback_id)

  } catch (error: unknown) {
    console.error('Feedback submit error:', error)
    submitError.value = error instanceof Error ? error.message : 'Fehler beim Senden. Bitte versuche es erneut.'
  } finally {
    isSubmitting.value = false
  }
}

const resetForm = () => {
  feedbackType.value = 'question'
  title.value = ''
  message.value = ''
  email.value = ''
  isAnonymous.value = false
  isSubmitted.value = false
  submitError.value = null
  feedbackId.value = null
}

const close = () => {
  emit('close')
}

// Load saved email
onMounted(() => {
  const savedEmail = localStorage.getItem('feedback-email')
  if (savedEmail) {
    email.value = savedEmail
  }
})
</script>

<template>
  <div class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
    <div
      class="w-full max-w-lg bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden"
      @click.stop
    >
      <!-- Header -->
      <div class="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center text-xl">
            {{ selectedCategory.icon }}
          </div>
          <div>
            <h2 class="text-white font-semibold">Feedback & Fragen</h2>
            <p class="text-indigo-200 text-sm">{{ contextInfo }}</p>
          </div>
        </div>
        <button
          @click="close"
          class="p-2 rounded-lg hover:bg-white/20 transition-colors text-white"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Success State -->
      <div v-if="isSubmitted" class="p-8 text-center">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
          <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Vielen Dank!
        </h3>
        <p class="text-gray-600 dark:text-gray-400 mb-2">
          Dein Feedback wurde erfolgreich gesendet.
        </p>
        <p class="text-sm text-gray-500 dark:text-gray-500 mb-6">
          Referenz: #{{ feedbackId?.substring(0, 8) }}
        </p>
        <div class="flex gap-3 justify-center">
          <button
            @click="resetForm"
            class="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Weiteres Feedback
          </button>
          <button
            @click="close"
            class="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
          >
            Schließen
          </button>
        </div>
      </div>

      <!-- Form -->
      <div v-else class="p-6">
        <!-- Category Selection -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Was möchtest du mitteilen?
          </label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="category in categories"
              :key="category.id"
              @click="selectType(category.id)"
              class="px-3 py-2 rounded-lg border transition-all text-sm flex items-center gap-2"
              :class="[
                feedbackType === category.id
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300'
                  : 'border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:border-indigo-300'
              ]"
            >
              <span>{{ category.icon }}</span>
              <span>{{ category.name }}</span>
            </button>
          </div>
        </div>

        <!-- Title (optional) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Betreff (optional)
          </label>
          <input
            v-model="title"
            type="text"
            :placeholder="selectedCategory.description"
            class="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>

        <!-- Message -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Deine Nachricht *
          </label>
          <textarea
            v-model="message"
            :placeholder="selectedCategory.placeholder"
            rows="5"
            class="w-full px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
          ></textarea>
          <p class="mt-1 text-xs text-gray-500">
            {{ message.length }}/10 Zeichen (min. 10 benötigt)
          </p>
        </div>

        <!-- Email (optional) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            E-Mail für Rückfragen (optional)
          </label>
          <input
            v-model="email"
            type="email"
            placeholder="deine@email.de"
            :disabled="isAnonymous"
            class="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        <!-- Anonymous Toggle -->
        <div class="mb-6 flex items-center gap-3">
          <button
            @click="isAnonymous = !isAnonymous"
            class="relative w-10 h-5 rounded-full transition-colors"
            :class="isAnonymous ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600'"
          >
            <span
              class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform"
              :class="isAnonymous ? 'translate-x-5' : ''"
            ></span>
          </button>
          <span class="text-sm text-gray-600 dark:text-gray-400">
            Anonym senden (keine E-Mail, kein Account verknüpft)
          </span>
        </div>

        <!-- Error Message -->
        <div v-if="submitError" class="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-sm">
          {{ submitError }}
        </div>

        <!-- Submit Button -->
        <div class="flex gap-3">
          <button
            @click="close"
            class="flex-1 px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Abbrechen
          </button>
          <button
            @click="submitFeedback"
            :disabled="!canSubmit"
            class="flex-1 px-4 py-3 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <svg v-if="isSubmitting" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ isSubmitting ? 'Wird gesendet...' : 'Absenden' }}</span>
          </button>
        </div>

        <!-- Info -->
        <p class="mt-4 text-xs text-center text-gray-500 dark:text-gray-500">
          Dein Feedback hilft uns, LernsystemX besser zu machen.
          Es wird von KI zusammengefasst und an das Team weitergeleitet.
        </p>
      </div>
    </div>
  </div>
</template>
