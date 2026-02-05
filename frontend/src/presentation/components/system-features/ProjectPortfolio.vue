<!--
  LearningMethod30Form - Portfolio

  Sammlung von Arbeitsproben mit Selbstreflexion.
  Dokumentiert den Lernfortschritt ueber Zeit.

  KI-Nutzung: Niedrig - KI gibt optionales Feedback auf Einreichungen.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <!-- Portfolio-Titel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Portfolio-Titel *
        </label>
        <input
          v-model="methodData.portfolio_title"
          type="text"
          placeholder="z.B. Mein IT-Portfolio, Netzwerk-Projekte Sammlung"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Beschreibung -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Portfolio-Beschreibung
        </label>
        <textarea
          v-model="methodData.description"
          rows="2"
          placeholder="Was soll in diesem Portfolio gesammelt werden?"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Artefakt-Typen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Erlaubte Artefakt-Typen
        </label>
        <div class="grid grid-cols-2 gap-2">
          <label
            v-for="artifactType in artifactTypes"
            :key="artifactType.value"
            class="flex items-center gap-2 cursor-pointer"
          >
            <input
              v-model="methodData.allowed_artifacts"
              type="checkbox"
              :value="artifactType.value"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">{{ artifactType.label }}</span>
          </label>
        </div>
      </div>

      <!-- Min/Max Artefakte -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Mindestanzahl Artefakte
          </label>
          <input
            v-model.number="methodData.min_artifacts"
            type="number"
            min="1"
            max="20"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Maximale Artefakte
          </label>
          <input
            v-model.number="methodData.max_artifacts"
            type="number"
            min="1"
            max="50"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
        </div>
      </div>

      <!-- Reflexions-Anforderungen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Reflexion pro Artefakt
        </label>
        <select
          v-model="methodData.reflection_requirement"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="none">Keine Reflexion erforderlich</option>
          <option value="short">Kurze Reflexion (50 Woerter)</option>
          <option value="medium">Mittlere Reflexion (100 Woerter)</option>
          <option value="detailed">Ausfuehrliche Reflexion (200+ Woerter)</option>
        </select>
      </div>

      <!-- Reflexions-Leitfragen -->
      <div v-if="methodData.reflection_requirement !== 'none'">
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Reflexions-Leitfragen
        </label>
        <div class="space-y-2">
          <div
            v-for="(question, index) in methodData.reflection_prompts"
            :key="index"
            class="flex gap-2"
          >
            <input
              v-model="methodData.reflection_prompts[index]"
              type="text"
              placeholder="z.B. Was zeigt dieses Artefakt ueber meinen Lernfortschritt?"
              class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
            <button
              v-if="methodData.reflection_prompts.length > 1"
              @click="removePrompt(index)"
              class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <button
          v-if="methodData.reflection_prompts.length < 5"
          @click="addPrompt"
          class="mt-2 text-sm text-[var(--color-primary)] hover:underline"
        >
          + Frage hinzufuegen
        </button>
      </div>

      <!-- Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Optionen
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.public_portfolio"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Portfolio oeffentlich sichtbar</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.ai_feedback"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">KI-Feedback auf Artefakte</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.peer_comments"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Peer-Kommentare erlauben</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_timeline"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Zeitliche Entwicklung anzeigen</span>
          </label>
        </div>
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-pink-50 dark:bg-pink-900/20 rounded-lg border border-pink-200 dark:border-pink-800">
        <p class="text-sm text-pink-800 dark:text-pink-200">
          <strong>Portfolio:</strong> Eine Sammlung von Arbeitsproben dokumentiert den
          Lernfortschritt und ermoeglicht Selbstreflexion ueber die eigene Entwicklung.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/window.store'
import { BaseLearningMethodForm } from '@/presentation/components/learning/editor/forms'

const METHOD_CODE = 30

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const artifactTypes = [
  { value: 'document', label: 'Dokumente (PDF, Word)' },
  { value: 'code', label: 'Code/Skripte' },
  { value: 'diagram', label: 'Diagramme' },
  { value: 'screenshot', label: 'Screenshots' },
  { value: 'video', label: 'Videos' },
  { value: 'presentation', label: 'Praesentationen' },
  { value: 'config', label: 'Konfigurationsdateien' },
  { value: 'other', label: 'Sonstiges' }
]

const methodData = ref({
  portfolio_title: '',
  description: '',
  allowed_artifacts: ['document', 'code', 'screenshot'],
  min_artifacts: 3,
  max_artifacts: 10,
  reflection_requirement: 'short',
  reflection_prompts: [
    'Was zeigt dieses Artefakt ueber meinen Lernfortschritt?',
    'Was wuerde ich beim naechsten Mal anders machen?'
  ],
  public_portfolio: false,
  ai_feedback: false,
  peer_comments: false,
  show_timeline: true
})

const addPrompt = () => {
  if (methodData.value.reflection_prompts.length < 5) {
    methodData.value.reflection_prompts.push('')
  }
}

const removePrompt = (index: number) => {
  if (methodData.value.reflection_prompts.length > 1) {
    methodData.value.reflection_prompts.splice(index, 1)
  }
}

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.portfolio_title = existingData.portfolio_title || ''
    methodData.value.description = existingData.description || ''
    methodData.value.allowed_artifacts = existingData.allowed_artifacts || methodData.value.allowed_artifacts
    methodData.value.min_artifacts = existingData.min_artifacts || 3
    methodData.value.max_artifacts = existingData.max_artifacts || 10
    methodData.value.reflection_requirement = existingData.reflection_requirement || 'short'
    methodData.value.reflection_prompts = existingData.reflection_prompts || methodData.value.reflection_prompts
    methodData.value.public_portfolio = existingData.public_portfolio ?? false
    methodData.value.ai_feedback = existingData.ai_feedback ?? false
    methodData.value.peer_comments = existingData.peer_comments ?? false
    methodData.value.show_timeline = existingData.show_timeline ?? true
  }
})
</script>
