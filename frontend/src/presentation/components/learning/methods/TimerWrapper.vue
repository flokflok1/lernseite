<!--
  LearningMethod25Form - Kapitel-Abschlussprüfung

  Umfassende Prüfung am Ende eines Kapitels, die alle behandelten
  Themen abdeckt und verschiedene Aufgabentypen kombiniert.

  KI-Nutzung: Mittel - KI kann Prüfungen aus Kapitelinhalt generieren.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <!-- Prüfungstitel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Prüfungstitel *
        </label>
        <input
          v-model="methodData.exam_title"
          type="text"
          placeholder="z.B. Abschlusstest Kapitel 3: Netzwerktechnik"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Kapitel-Beschreibung -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Kapitelzusammenfassung
        </label>
        <textarea
          v-model="methodData.chapter_summary"
          rows="3"
          placeholder="Kurze Zusammenfassung der geprüften Themen..."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Bestehensgrenze -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Bestehensgrenze (%)
        </label>
        <div class="flex items-center gap-4">
          <input
            v-model.number="methodData.pass_threshold"
            type="range"
            min="50"
            max="100"
            step="5"
            class="flex-1"
          />
          <span class="text-sm font-medium text-[var(--color-text-primary)] w-12 text-center">
            {{ methodData.pass_threshold }}%
          </span>
        </div>
      </div>

      <!-- Prüfungsabschnitte -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            Prüfungsabschnitte *
          </label>
          <button
            @click="addSection"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            + Abschnitt hinzufügen
          </button>
        </div>

        <p class="text-xs text-[var(--color-text-secondary)] mb-2">
          Kombinieren Sie verschiedene Aufgabentypen für eine umfassende Prüfung.
        </p>

        <div v-if="methodData.sections.length === 0" class="text-sm text-[var(--color-text-secondary)] italic mb-3">
          Keine Abschnitte vorhanden. Fügen Sie Prüfungsabschnitte hinzu.
        </div>

        <div v-for="(section, index) in methodData.sections" :key="index" class="mb-4 p-4 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface-secondary)]">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-[var(--color-primary)]">
              Abschnitt {{ index + 1 }}
            </span>
            <div class="flex gap-2">
              <button
                @click="moveSectionUp(index)"
                :disabled="index === 0"
                type="button"
                class="text-sm text-[var(--color-primary)] hover:underline disabled:opacity-30"
              >
                ↑
              </button>
              <button
                @click="moveSectionDown(index)"
                :disabled="index === methodData.sections.length - 1"
                type="button"
                class="text-sm text-[var(--color-primary)] hover:underline disabled:opacity-30"
              >
                ↓
              </button>
              <button
                @click="removeSection(index)"
                type="button"
                class="text-sm text-red-500 hover:underline"
              >
                Entfernen
              </button>
            </div>
          </div>

          <div class="space-y-3">
            <!-- Abschnittstitel -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Abschnittstitel *
              </label>
              <input
                v-model="section.title"
                type="text"
                placeholder="z.B. Teil A: Multiple-Choice, Teil B: Freitext"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Aufgabentyp -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Aufgabentyp *
              </label>
              <select
                v-model="section.task_type"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              >
                <option value="multiple_choice">Multiple-Choice Fragen</option>
                <option value="true_false">Richtig/Falsch Aussagen</option>
                <option value="short_answer">Kurzantworten</option>
                <option value="fill_blank">Lückentext</option>
                <option value="matching">Zuordnungsaufgaben</option>
                <option value="ordering">Reihenfolge bestimmen</option>
                <option value="free_text">Freitext / Essay</option>
                <option value="calculation">Berechnungsaufgaben</option>
              </select>
            </div>

            <!-- Anzahl Aufgaben -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Anzahl Aufgaben
              </label>
              <input
                v-model.number="section.question_count"
                type="number"
                min="1"
                max="50"
                class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Punkte pro Aufgabe -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Punkte pro Aufgabe
              </label>
              <input
                v-model.number="section.points_per_question"
                type="number"
                min="1"
                max="50"
                class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Themenbereich -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Themenbereich
              </label>
              <input
                v-model="section.topic_area"
                type="text"
                placeholder="Optional: Spezifischer Themenbereich für diesen Abschnitt"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Zeitlimit -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Zeitlimit (Minuten)
        </label>
        <div class="flex items-center gap-4">
          <input
            v-model.number="methodData.time_limit"
            type="number"
            min="10"
            max="180"
            step="5"
            class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.time_limit_enabled"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Zeitlimit aktivieren</span>
          </label>
        </div>
      </div>

      <!-- Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Prüfungsoptionen
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.shuffle_sections"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Abschnitte zufällig mischen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.shuffle_questions"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Fragen innerhalb der Abschnitte mischen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.allow_review"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Überprüfung vor Abgabe erlauben</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_correct_answers"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Korrekte Antworten nach Abgabe zeigen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.certificate_on_pass"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Zertifikat bei Bestehen ausstellen</span>
          </label>
        </div>
      </div>

      <!-- Info -->
      <div class="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
        <p class="text-sm text-green-800 dark:text-green-200">
          <strong>Kapitelabschluss:</strong> Diese umfassende Prüfung testet alle wichtigen
          Konzepte des Kapitels. Bei Bestehen wird der Lernfortschritt als abgeschlossen markiert.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/desktop'
import { BaseLearningMethodForm } from '@/presentation/components/learning/editor/forms'

const METHOD_CODE = 25

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

interface Section {
  title: string
  task_type: string
  question_count: number
  points_per_question: number
  topic_area: string
}

// Methoden-spezifische Daten
const methodData = ref({
  exam_title: '',
  chapter_summary: '',
  pass_threshold: 60,
  sections: [] as Section[],
  time_limit: 60,
  time_limit_enabled: true,
  shuffle_sections: false,
  shuffle_questions: true,
  allow_review: true,
  show_correct_answers: true,
  certificate_on_pass: false
})

const addSection = () => {
  methodData.value.sections.push({
    title: '',
    task_type: 'multiple_choice',
    question_count: 5,
    points_per_question: 2,
    topic_area: ''
  })
}

const removeSection = (index: number) => {
  methodData.value.sections.splice(index, 1)
}

const moveSectionUp = (index: number) => {
  if (index > 0) {
    const temp = methodData.value.sections[index]
    methodData.value.sections[index] = methodData.value.sections[index - 1]
    methodData.value.sections[index - 1] = temp
  }
}

const moveSectionDown = (index: number) => {
  if (index < methodData.value.sections.length - 1) {
    const temp = methodData.value.sections[index]
    methodData.value.sections[index] = methodData.value.sections[index + 1]
    methodData.value.sections[index + 1] = temp
  }
}

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.exam_title = existingData.exam_title || ''
    methodData.value.chapter_summary = existingData.chapter_summary || ''
    methodData.value.pass_threshold = existingData.pass_threshold || 60
    methodData.value.sections = existingData.sections || []
    methodData.value.time_limit = existingData.time_limit || 60
    methodData.value.time_limit_enabled = existingData.time_limit_enabled ?? true
    methodData.value.shuffle_sections = existingData.shuffle_sections ?? false
    methodData.value.shuffle_questions = existingData.shuffle_questions ?? true
    methodData.value.allow_review = existingData.allow_review ?? true
    methodData.value.show_correct_answers = existingData.show_correct_answers ?? true
    methodData.value.certificate_on_pass = existingData.certificate_on_pass ?? false
  }
})
</script>
