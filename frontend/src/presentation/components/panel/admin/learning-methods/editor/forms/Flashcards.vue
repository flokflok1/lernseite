<!--
  LearningMethod07Form - NPC-Tutor-Lecture

  Virtueller KI-Tutor erklärt Kapitel-Inhalte als interaktive Vorlesung.
  Vollständig KI-generiert mit optionalen Personalisierungseinstellungen.

  KI-Nutzung: Sehr Hoch - Vollständig KI-generierte Vorlesungen.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <!-- Vorlesungsthema -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Vorlesungsthema *
        </label>
        <input
          v-model="methodData.lecture_topic"
          type="text"
          placeholder="z.B. Einführung in TCP/IP, Grundlagen der Buchhaltung"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Tutor-Persona -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Tutor-Persona
        </label>
        <select
          v-model="methodData.tutor_persona"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="professor">Professor - Akademisch und detailliert</option>
          <option value="mentor">Mentor - Freundlich und ermutigend</option>
          <option value="expert">Experte - Praxisorientiert aus der Branche</option>
          <option value="coach">Coach - Motivierend und interaktiv</option>
          <option value="colleague">Kollege - Locker und auf Augenhöhe</option>
        </select>
      </div>

      <!-- Vorlesungsstil -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Vorlesungsstil
        </label>
        <select
          v-model="methodData.lecture_style"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="structured">Strukturiert - Klar gegliedert mit Abschnitten</option>
          <option value="narrative">Erzählend - Wie eine Geschichte</option>
          <option value="interactive">Interaktiv - Mit Zwischenfragen</option>
          <option value="socratic">Sokratisch - Durch Fragen leiten</option>
          <option value="practical">Praktisch - Mit vielen Beispielen</option>
        </select>
      </div>

      <!-- Tiefe/Länge -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Vorlesungslänge
        </label>
        <select
          v-model="methodData.lecture_length"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="short">Kurz (5-10 Min) - Schneller Überblick</option>
          <option value="medium">Mittel (15-20 Min) - Ausführliche Erklärung</option>
          <option value="long">Lang (30+ Min) - Tiefgehende Vorlesung</option>
        </select>
      </div>

      <!-- Zielgruppen-Niveau -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Zielgruppen-Niveau
        </label>
        <select
          v-model="methodData.target_level"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="beginner">Anfänger - Keine Vorkenntnisse nötig</option>
          <option value="intermediate">Fortgeschritten - Grundlagen bekannt</option>
          <option value="advanced">Experte - Tiefes Fachwissen</option>
        </select>
      </div>

      <!-- Fokus-Bereiche -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Fokus-Bereiche (optional)
        </label>
        <textarea
          v-model="methodData.focus_areas"
          rows="2"
          placeholder="Besondere Aspekte, die der Tutor betonen soll (kommagetrennt)..."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Vorlesungs-Optionen
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.include_summary"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Zusammenfassung am Ende</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.include_examples"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Praxisbeispiele einbauen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.include_questions"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Verständnisfragen stellen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.include_analogies"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Analogien und Vergleiche nutzen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.allow_followup"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Rückfragen erlauben (Chat-Modus)</span>
          </label>
        </div>
      </div>

      <!-- Sprachstil -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Sprachstil
        </label>
        <select
          v-model="methodData.language_style"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="formal">Formal - Sachlich und präzise</option>
          <option value="casual">Locker - Umgangssprachlich</option>
          <option value="encouraging">Motivierend - Positiv und ermutigend</option>
          <option value="technical">Technisch - Fachsprache-orientiert</option>
        </select>
      </div>

      <!-- Lernziel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Lernziel
        </label>
        <input
          v-model="methodData.learning_goal"
          type="text"
          placeholder="Was soll der Lernende nach der Vorlesung können/wissen?"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
        <p class="text-sm text-purple-800 dark:text-purple-200">
          <strong>Vollständig KI-generiert:</strong> Der virtuelle Tutor erstellt eine personalisierte Vorlesung
          basierend auf dem Kapitel-Inhalt und Ihren Einstellungen. Der Lernende kann mit dem Tutor interagieren.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 7

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

// Methoden-spezifische Daten
const methodData = ref({
  lecture_topic: '',
  tutor_persona: 'mentor',
  lecture_style: 'structured',
  lecture_length: 'medium',
  target_level: 'intermediate',
  focus_areas: '',
  include_summary: true,
  include_examples: true,
  include_questions: true,
  include_analogies: true,
  allow_followup: true,
  language_style: 'encouraging',
  learning_goal: ''
})

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.lecture_topic = existingData.lecture_topic || ''
    methodData.value.tutor_persona = existingData.tutor_persona || 'mentor'
    methodData.value.lecture_style = existingData.lecture_style || 'structured'
    methodData.value.lecture_length = existingData.lecture_length || 'medium'
    methodData.value.target_level = existingData.target_level || 'intermediate'
    methodData.value.focus_areas = existingData.focus_areas || ''
    methodData.value.include_summary = existingData.include_summary ?? true
    methodData.value.include_examples = existingData.include_examples ?? true
    methodData.value.include_questions = existingData.include_questions ?? true
    methodData.value.include_analogies = existingData.include_analogies ?? true
    methodData.value.allow_followup = existingData.allow_followup ?? true
    methodData.value.language_style = existingData.language_style || 'encouraging'
    methodData.value.learning_goal = existingData.learning_goal || ''
  }
})
</script>
