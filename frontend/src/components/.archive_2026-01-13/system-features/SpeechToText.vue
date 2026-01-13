<!--
  LearningMethod24Form - Mündliche Erklärung Simulation

  Simulation einer mündlichen Prüfung, bei der der Lernende
  Konzepte verbal erklären und auf Nachfragen reagieren muss.

  KI-Nutzung: Sehr Hoch - KI simuliert Prüfer und bewertet Erklärungen.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <!-- Prüfungsthema -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Prüfungsthema *
        </label>
        <input
          v-model="methodData.topic"
          type="text"
          placeholder="z.B. OSI-Modell erklären, Datenbankdesign verteidigen"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Prüfungsformat -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Prüfungsformat
        </label>
        <select
          v-model="methodData.format"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="presentation">Präsentation - Freier Vortrag zu einem Thema</option>
          <option value="defense">Verteidigung - Konzept/Lösung verteidigen</option>
          <option value="interview">Interview - Frage-Antwort-Format</option>
          <option value="explanation">Erklärung - Konzept einem Laien erklären</option>
          <option value="discussion">Diskussion - Pro/Contra Argumente</option>
        </select>
      </div>

      <!-- Prüfer-Persona -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Prüfer-Persona
        </label>
        <select
          v-model="methodData.examiner_persona"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="formal">Formal - Strenger IHK-Prüfer</option>
          <option value="curious">Neugierig - Interessierter Fragensteller</option>
          <option value="skeptical">Skeptisch - Hinterfragt kritisch</option>
          <option value="supportive">Unterstützend - Hilft bei Schwierigkeiten</option>
          <option value="technical">Technisch - Fokus auf Details</option>
        </select>
      </div>

      <!-- Schwierigkeitsgrad -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Schwierigkeitsgrad
        </label>
        <select
          v-model="methodData.difficulty"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="easy">Einfach - Grundlegende Nachfragen</option>
          <option value="medium">Mittel - Vertiefende Fragen</option>
          <option value="hard">Schwer - Kritische Detailfragen</option>
          <option value="expert">Experte - Prüfungsrealistisch</option>
        </select>
      </div>

      <!-- Hauptfragen/Themenblöcke -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            Themenblöcke / Hauptfragen
          </label>
          <button
            @click="addTopicBlock"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            + Themenblock hinzufügen
          </button>
        </div>

        <p class="text-xs text-[var(--color-text-secondary)] mb-2">
          Optional: Definieren Sie Hauptthemen. Die KI generiert passende Nachfragen.
        </p>

        <div v-for="(block, index) in methodData.topic_blocks" :key="index" class="mb-3 p-3 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface-secondary)]">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-[var(--color-primary)]">Block {{ index + 1 }}</span>
            <button
              @click="removeTopicBlock(index)"
              type="button"
              class="text-xs text-red-500 hover:underline"
            >
              Entfernen
            </button>
          </div>
          <input
            v-model="block.topic"
            type="text"
            placeholder="Hauptthema oder Einstiegsfrage..."
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] mb-2"
          />
          <textarea
            v-model="block.key_points"
            rows="2"
            placeholder="Erwartete Kernpunkte (optional)..."
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
        </div>
      </div>

      <!-- Zeitrahmen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Prüfungsdauer (Minuten)
        </label>
        <input
          v-model.number="methodData.duration_minutes"
          type="number"
          min="5"
          max="60"
          class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Prüfungs-Optionen
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.allow_thinking_time"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Bedenkzeit vor der Antwort erlauben</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.allow_retry"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Neuformulierung bei Unklarheit erlauben</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.use_audio"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Sprachaufnahme (Speech-to-Text)</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_transcript"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Transkript nach Abschluss anzeigen</span>
          </label>
        </div>
      </div>

      <!-- Bewertungskriterien -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Bewertungskriterien
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.criteria.content"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Fachliche Korrektheit</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.criteria.structure"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Struktur und Gliederung</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.criteria.clarity"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Verständlichkeit</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.criteria.reactions"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Reaktion auf Nachfragen</span>
          </label>
        </div>
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
        <p class="text-sm text-purple-800 dark:text-purple-200">
          <strong>KI-Simulation:</strong> Die KI agiert als Prüfer, stellt Fragen,
          reagiert auf Antworten und gibt detailliertes Feedback zur Prüfungsleistung.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/store/modules/desktop'
import { BaseLearningMethodForm } from '@/components/base/content/admin/learning-methods/forms'

const METHOD_CODE = 24

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

interface TopicBlock {
  topic: string
  key_points: string
}

// Methoden-spezifische Daten
const methodData = ref({
  topic: '',
  format: 'interview',
  examiner_persona: 'formal',
  difficulty: 'medium',
  topic_blocks: [] as TopicBlock[],
  duration_minutes: 15,
  allow_thinking_time: true,
  allow_retry: false,
  use_audio: false,
  show_transcript: true,
  criteria: {
    content: true,
    structure: true,
    clarity: true,
    reactions: true
  }
})

const addTopicBlock = () => {
  methodData.value.topic_blocks.push({
    topic: '',
    key_points: ''
  })
}

const removeTopicBlock = (index: number) => {
  methodData.value.topic_blocks.splice(index, 1)
}

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.topic = existingData.topic || ''
    methodData.value.format = existingData.format || 'interview'
    methodData.value.examiner_persona = existingData.examiner_persona || 'formal'
    methodData.value.difficulty = existingData.difficulty || 'medium'
    methodData.value.topic_blocks = existingData.topic_blocks || []
    methodData.value.duration_minutes = existingData.duration_minutes || 15
    methodData.value.allow_thinking_time = existingData.allow_thinking_time ?? true
    methodData.value.allow_retry = existingData.allow_retry ?? false
    methodData.value.use_audio = existingData.use_audio ?? false
    methodData.value.show_transcript = existingData.show_transcript ?? true
    methodData.value.criteria = existingData.criteria || {
      content: true,
      structure: true,
      clarity: true,
      reactions: true
    }
  }
})
</script>
