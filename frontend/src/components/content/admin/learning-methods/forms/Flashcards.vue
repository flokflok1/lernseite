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
    <template #method-fields="{ form }">
      <!-- Vorlesungsthema -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.lm07.lectureTopicLabel') }}
        </label>
        <input
          v-model="methodData.lecture_topic"
          type="text"
          :placeholder="$t('windows.lm07.lectureTopicPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Tutor-Persona -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.lm07.tutorPersonaLabel') }}
        </label>
        <select
          v-model="methodData.tutor_persona"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="professor">{{ $t('windows.lm07.tutorPersonaProfessor') }}</option>
          <option value="mentor">{{ $t('windows.lm07.tutorPersonaMentor') }}</option>
          <option value="expert">{{ $t('windows.lm07.tutorPersonaExpert') }}</option>
          <option value="coach">{{ $t('windows.lm07.tutorPersonaCoach') }}</option>
          <option value="colleague">{{ $t('windows.lm07.tutorPersonaColleague') }}</option>
        </select>
      </div>

      <!-- Vorlesungsstil -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.lm07.lectureStyleLabel') }}
        </label>
        <select
          v-model="methodData.lecture_style"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="structured">{{ $t('windows.lm07.lectureStyleStructured') }}</option>
          <option value="narrative">{{ $t('windows.lm07.lectureStyleNarrative') }}</option>
          <option value="interactive">{{ $t('windows.lm07.lectureStyleInteractive') }}</option>
          <option value="socratic">{{ $t('windows.lm07.lectureStyleSocratic') }}</option>
          <option value="practical">{{ $t('windows.lm07.lectureStylePractical') }}</option>
        </select>
      </div>

      <!-- Tiefe/Länge -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.lm07.lectureLengthLabel') }}
        </label>
        <select
          v-model="methodData.lecture_length"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="short">{{ $t('windows.lm07.lectureLengthShort') }}</option>
          <option value="medium">{{ $t('windows.lm07.lectureLengthMedium') }}</option>
          <option value="long">{{ $t('windows.lm07.lectureLengthLong') }}</option>
        </select>
      </div>

      <!-- Zielgruppen-Niveau -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.lm07.targetLevelLabel') }}
        </label>
        <select
          v-model="methodData.target_level"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="beginner">{{ $t('windows.lm07.targetLevelBeginner') }}</option>
          <option value="intermediate">{{ $t('windows.lm07.targetLevelIntermediate') }}</option>
          <option value="advanced">{{ $t('windows.lm07.targetLevelAdvanced') }}</option>
        </select>
      </div>

      <!-- Fokus-Bereiche -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.lm07.focusAreasLabel') }}
        </label>
        <textarea
          v-model="methodData.focus_areas"
          rows="2"
          :placeholder="$t('windows.lm07.focusAreasPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.lm07.lectureOptionsLabel') }}
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.include_summary"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">{{ $t('windows.lm07.includeSummary') }}</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.include_examples"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">{{ $t('windows.lm07.includeExamples') }}</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.include_questions"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">{{ $t('windows.lm07.includeQuestions') }}</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.include_analogies"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">{{ $t('windows.lm07.includeAnalogies') }}</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.allow_followup"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">{{ $t('windows.lm07.allowFollowup') }}</span>
          </label>
        </div>
      </div>

      <!-- Sprachstil -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.lm07.languageStyleLabel') }}
        </label>
        <select
          v-model="methodData.language_style"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="formal">{{ $t('windows.lm07.languageStyleFormal') }}</option>
          <option value="casual">{{ $t('windows.lm07.languageStyleCasual') }}</option>
          <option value="encouraging">{{ $t('windows.lm07.languageStyleEncouraging') }}</option>
          <option value="technical">{{ $t('windows.lm07.languageStyleTechnical') }}</option>
        </select>
      </div>

      <!-- Lernziel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.lm07.learningGoalLabel') }}
        </label>
        <input
          v-model="methodData.learning_goal"
          type="text"
          :placeholder="$t('windows.lm07.learningGoalPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
        <p class="text-sm text-purple-800 dark:text-purple-200">
          <strong>{{ $t('windows.lm07.aiHint') }}</strong>
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/store/modules/desktop'
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
