<!--
  LearningMethod01Form - Schritt-für-Schritt-Erklärung

  Sequenzielle Anleitung, die komplexe Prozesse in einzelne,
  nachvollziehbare Schritte zerlegt. Ideal für Anleitungen, Workflows
  und Prozessdokumentation.

  KI-Nutzung: Mittel - KI kann Prozesse automatisch in Schritte zerlegen.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <!-- Prozess-Titel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Prozess / Thema *
        </label>
        <input
          v-model="methodData.process_title"
          type="text"
          placeholder="z.B. Windows Server Installation, Git Workflow, Subnetting berechnen"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Einleitung -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Einleitung
        </label>
        <textarea
          v-model="methodData.introduction"
          rows="2"
          placeholder="Kurze Einführung in den Prozess (optional)..."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Schritte -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            Schritte *
          </label>
          <button
            @click="addStep"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            + Schritt hinzufügen
          </button>
        </div>

        <div v-if="methodData.steps.length === 0" class="text-sm text-[var(--color-text-secondary)] italic mb-3">
          Keine Schritte vorhanden. Fügen Sie mindestens einen Schritt hinzu.
        </div>

        <div v-for="(step, index) in methodData.steps" :key="index" class="mb-4 p-4 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface-secondary)]">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-[var(--color-primary)]">
              Schritt {{ index + 1 }}
            </span>
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
                Titel *
              </label>
              <input
                v-model="step.title"
                type="text"
                placeholder="z.B. Vorbereitung, Server konfigurieren..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Schritt-Beschreibung -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Beschreibung *
              </label>
              <textarea
                v-model="step.description"
                rows="3"
                placeholder="Detaillierte Anleitung für diesen Schritt..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Hinweis (optional) -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Hinweis / Tipp
              </label>
              <input
                v-model="step.hint"
                type="text"
                placeholder="Optional: Wichtiger Hinweis oder Tipp..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Zusammenfassung -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Zusammenfassung / Abschluss
        </label>
        <textarea
          v-model="methodData.summary"
          rows="2"
          placeholder="Optional: Abschließende Zusammenfassung oder nächste Schritte..."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 1

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

interface Step {
  title: string
  description: string
  hint: string
}

// Methoden-spezifische Daten
const methodData = ref({
  process_title: '',
  introduction: '',
  steps: [] as Step[],
  summary: ''
})

const addStep = () => {
  methodData.value.steps.push({
    title: '',
    description: '',
    hint: ''
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
    methodData.value.process_title = existingData.process_title || ''
    methodData.value.introduction = existingData.introduction || ''
    methodData.value.steps = existingData.steps || []
    methodData.value.summary = existingData.summary || ''
  }
})
</script>
