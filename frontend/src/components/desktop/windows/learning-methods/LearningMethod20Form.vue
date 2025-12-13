<!--
  LearningMethod20Form - Multi-Step-Klausur

  Aufeinander aufbauende Prüfungsaufgaben, bei denen das Ergebnis
  einer Aufgabe die Grundlage für die nächste bildet.

  KI-Nutzung: Mittel - KI kann verkettete Aufgaben generieren.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <!-- Klausur-Thema -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Klausur-Thema *
        </label>
        <input
          v-model="methodData.exam_topic"
          type="text"
          placeholder="z.B. Netzwerk-Design Projekt, Datenbank-Entwicklung, Geschäftsprozesse"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Szenario-Beschreibung -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Übergreifendes Szenario *
        </label>
        <textarea
          v-model="methodData.scenario"
          rows="4"
          placeholder="Beschreiben Sie das durchgängige Szenario, das alle Aufgabenschritte verbindet (z.B. Ein Unternehmen plant die Einführung eines neuen Netzwerks...)..."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Aufgabenschritte -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            Aufgabenschritte *
          </label>
          <button
            @click="addStep"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            + Schritt hinzufügen
          </button>
        </div>

        <p class="text-xs text-[var(--color-text-secondary)] mb-2">
          Die Schritte bauen aufeinander auf. Das Ergebnis von Schritt N wird in Schritt N+1 verwendet.
        </p>

        <div v-if="methodData.steps.length === 0" class="text-sm text-[var(--color-text-secondary)] italic mb-3">
          Keine Schritte vorhanden. Fügen Sie mindestens zwei verkettete Schritte hinzu.
        </div>

        <div v-for="(step, index) in methodData.steps" :key="index" class="mb-4 p-4 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface-secondary)]">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <span class="text-sm font-bold text-[var(--color-primary)]">
                Schritt {{ index + 1 }}
              </span>
              <span v-if="index > 0" class="text-xs text-[var(--color-text-secondary)]">
                (basiert auf Schritt {{ index }})
              </span>
            </div>
            <div class="flex gap-2">
              <button
                @click="moveStepUp(index)"
                :disabled="index === 0"
                type="button"
                class="text-sm text-[var(--color-primary)] hover:underline disabled:opacity-30 disabled:cursor-not-allowed"
              >
                ↑
              </button>
              <button
                @click="moveStepDown(index)"
                :disabled="index === methodData.steps.length - 1"
                type="button"
                class="text-sm text-[var(--color-primary)] hover:underline disabled:opacity-30 disabled:cursor-not-allowed"
              >
                ↓
              </button>
              <button
                @click="removeStep(index)"
                type="button"
                class="text-sm text-red-500 hover:underline"
              >
                Entfernen
              </button>
            </div>
          </div>

          <div class="space-y-3">
            <!-- Schritt-Titel -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Schritt-Titel *
              </label>
              <input
                v-model="step.title"
                type="text"
                placeholder="z.B. Anforderungsanalyse, Netzwerkplanung, Implementierung"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Aufgabenstellung -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Aufgabenstellung *
              </label>
              <textarea
                v-model="step.task"
                rows="3"
                placeholder="Beschreiben Sie die Aufgabe für diesen Schritt..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Erwartetes Ergebnis -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Erwartetes Ergebnis
              </label>
              <textarea
                v-model="step.expected_result"
                rows="2"
                placeholder="Was soll der Lernende in diesem Schritt produzieren?"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Hilfsmittel -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Hilfsmittel / Materialien
              </label>
              <input
                v-model="step.resources"
                type="text"
                placeholder="z.B. Tabellenkalkulation, Diagramm-Tool, Referenztabellen"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Punktzahl -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Punkte
              </label>
              <input
                v-model.number="step.points"
                type="number"
                min="1"
                max="100"
                class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Gesamtzeit -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Gesamtbearbeitungszeit (Minuten)
        </label>
        <input
          v-model.number="methodData.total_duration"
          type="number"
          min="15"
          max="300"
          step="5"
          class="w-32 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Optionen
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.allow_step_back"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Zurücknavigation zu vorherigen Schritten erlauben</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_progress"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Fortschrittsanzeige einblenden</span>
          </label>
        </div>
      </div>

      <!-- Info -->
      <div class="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
        <p class="text-sm text-green-800 dark:text-green-200">
          <strong>Multi-Step:</strong> Diese Klausurform simuliert realistische Projektarbeit.
          Die Ergebnisse jedes Schritts fließen in den nächsten ein - wie in der Praxis.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/store/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 20

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

interface Step {
  title: string
  task: string
  expected_result: string
  resources: string
  points: number
}

// Methoden-spezifische Daten
const methodData = ref({
  exam_topic: '',
  scenario: '',
  steps: [] as Step[],
  total_duration: 90,
  allow_step_back: false,
  show_progress: true
})

const addStep = () => {
  methodData.value.steps.push({
    title: '',
    task: '',
    expected_result: '',
    resources: '',
    points: 20
  })
}

const removeStep = (index: number) => {
  methodData.value.steps.splice(index, 1)
}

const moveStepUp = (index: number) => {
  if (index > 0) {
    const temp = methodData.value.steps[index]
    methodData.value.steps[index] = methodData.value.steps[index - 1]
    methodData.value.steps[index - 1] = temp
  }
}

const moveStepDown = (index: number) => {
  if (index < methodData.value.steps.length - 1) {
    const temp = methodData.value.steps[index]
    methodData.value.steps[index] = methodData.value.steps[index + 1]
    methodData.value.steps[index + 1] = temp
  }
}

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.exam_topic = existingData.exam_topic || ''
    methodData.value.scenario = existingData.scenario || ''
    methodData.value.steps = existingData.steps || []
    methodData.value.total_duration = existingData.total_duration || 90
    methodData.value.allow_step_back = existingData.allow_step_back ?? false
    methodData.value.show_progress = existingData.show_progress ?? true
  }
})
</script>
