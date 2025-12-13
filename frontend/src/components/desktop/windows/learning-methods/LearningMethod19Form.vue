<!--
  LearningMethod19Form - IHK/Kammer-Format

  Prüfungsfragen im Format der Industrie- und Handelskammer (IHK)
  sowie anderer Kammern. Bereitet auf offizielle Prüfungen vor.

  KI-Nutzung: Mittel - KI kann IHK-konforme Fragen generieren.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <!-- Prüfungsbereich -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Prüfungsbereich / Ausbildungsberuf *
        </label>
        <input
          v-model="methodData.exam_area"
          type="text"
          placeholder="z.B. Fachinformatiker Systemintegration, Kaufmann für Büromanagement"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Prüfungsteil -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Prüfungsteil
        </label>
        <select
          v-model="methodData.exam_part"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="">Bitte wählen...</option>
          <option value="ap1">Abschlussprüfung Teil 1 (AP1)</option>
          <option value="ap2">Abschlussprüfung Teil 2 (AP2)</option>
          <option value="gp1">Gestreckte Prüfung Teil 1 (GP1)</option>
          <option value="gp2">Gestreckte Prüfung Teil 2 (GP2)</option>
          <option value="zwischenpruefung">Zwischenprüfung</option>
          <option value="other">Sonstige Prüfung</option>
        </select>
      </div>

      <!-- Handlungsbereich/Themengebiet -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Handlungsbereich / Themengebiet
        </label>
        <input
          v-model="methodData.topic_area"
          type="text"
          placeholder="z.B. Einrichten eines IT-gestützten Arbeitsplatzes, Netzwerktechnik"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Aufgaben -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            Prüfungsaufgaben *
          </label>
          <button
            @click="addTask"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            + Aufgabe hinzufügen
          </button>
        </div>

        <div v-if="methodData.tasks.length === 0" class="text-sm text-[var(--color-text-secondary)] italic mb-3">
          Keine Aufgaben vorhanden. Fügen Sie IHK-konforme Aufgaben hinzu.
        </div>

        <div v-for="(task, index) in methodData.tasks" :key="index" class="mb-4 p-4 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface-secondary)]">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-[var(--color-primary)]">
              Aufgabe {{ index + 1 }}
            </span>
            <button
              @click="removeTask(index)"
              type="button"
              class="text-sm text-red-500 hover:underline"
            >
              Entfernen
            </button>
          </div>

          <div class="space-y-3">
            <!-- Aufgabentyp -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Aufgabentyp *
              </label>
              <select
                v-model="task.task_type"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              >
                <option value="situationsaufgabe">Situationsaufgabe</option>
                <option value="multiple_choice">Multiple-Choice (gebundene Aufgabe)</option>
                <option value="zuordnung">Zuordnungsaufgabe</option>
                <option value="lueckentext">Lückentext</option>
                <option value="reihenfolge">Reihenfolge bestimmen</option>
                <option value="berechnung">Berechnungsaufgabe</option>
                <option value="freitext">Offene Aufgabe (Freitext)</option>
              </select>
            </div>

            <!-- Situationsbeschreibung (bei Situationsaufgaben) -->
            <div v-if="task.task_type === 'situationsaufgabe'">
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Situationsbeschreibung
              </label>
              <textarea
                v-model="task.situation"
                rows="3"
                placeholder="Beschreiben Sie die betriebliche Situation (Handlungssituation)..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Aufgabenstellung -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Aufgabenstellung *
              </label>
              <textarea
                v-model="task.question"
                rows="3"
                placeholder="Formulieren Sie die Aufgabe im IHK-Stil..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Antwortoptionen (bei Multiple-Choice) -->
            <div v-if="task.task_type === 'multiple_choice'">
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Antwortoptionen (eine pro Zeile)
              </label>
              <textarea
                v-model="task.options"
                rows="4"
                placeholder="a) Option A
b) Option B
c) Option C
d) Option D"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] font-mono text-sm"
              />
            </div>

            <!-- Lösung -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Lösung / Erwartete Antwort
              </label>
              <textarea
                v-model="task.solution"
                rows="2"
                placeholder="Korrekte Antwort oder Lösungsweg..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Punktzahl -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Punkte
              </label>
              <input
                v-model.number="task.points"
                type="number"
                min="1"
                max="100"
                class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Prüfungsdauer -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Empfohlene Bearbeitungszeit (Minuten)
        </label>
        <input
          v-model.number="methodData.duration_minutes"
          type="number"
          min="5"
          max="300"
          step="5"
          class="w-32 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Info-Hinweis -->
      <div class="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
        <p class="text-sm text-amber-800 dark:text-amber-200">
          <strong>IHK-Format:</strong> Aufgaben sollten dem offiziellen IHK-Prüfungsformat entsprechen.
          Nutzen Sie handlungsorientierte Situationsaufgaben mit realistischen Betriebsszenarien.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/store/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 19

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

interface Task {
  task_type: string
  situation: string
  question: string
  options: string
  solution: string
  points: number
}

// Methoden-spezifische Daten
const methodData = ref({
  exam_area: '',
  exam_part: '',
  topic_area: '',
  tasks: [] as Task[],
  duration_minutes: 60
})

const addTask = () => {
  methodData.value.tasks.push({
    task_type: 'situationsaufgabe',
    situation: '',
    question: '',
    options: '',
    solution: '',
    points: 10
  })
}

const removeTask = (index: number) => {
  methodData.value.tasks.splice(index, 1)
}

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.exam_area = existingData.exam_area || ''
    methodData.value.exam_part = existingData.exam_part || ''
    methodData.value.topic_area = existingData.topic_area || ''
    methodData.value.tasks = existingData.tasks || []
    methodData.value.duration_minutes = existingData.duration_minutes || 60
  }
})
</script>
