<!--
  LearningMethod02Form - Interaktive Theorie

  Theoretische Erklärung kombiniert mit eingebetteten Verständnisfragen.
  Der Lernende wird aktiv eingebunden, indem nach jedem Abschnitt
  Rückfragen gestellt werden.

  KI-Nutzung: Mittel - KI generiert Theorie-Blöcke und passende Rückfragen.
-->

<template>
  <BaseLearningMethodForm
    :panel="panel"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <!-- Thema -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.lm02.topicLabel') }}
        </label>
        <input
          v-model="methodData.topic"
          type="text"
          :placeholder="$t('features.lm02.topicPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Theorie-Abschnitte mit Fragen -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            {{ $t('features.lm02.sectionsLabel') }}
          </label>
          <button
            @click="addSection"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            {{ $t('features.lm02.addSection') }}
          </button>
        </div>

        <div v-if="methodData.sections.length === 0" class="text-sm text-[var(--color-text-secondary)] italic mb-3">
          {{ $t('features.lm02.noSections') }}
        </div>

        <div v-for="(section, index) in methodData.sections" :key="index" class="mb-4 p-4 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface-secondary)]">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-[var(--color-primary)]">
              {{ $t('features.lm02.sectionNumber', { n: index + 1 }) }}
            </span>
            <button
              @click="removeSection(index)"
              type="button"
              class="text-sm text-red-500 hover:underline"
            >
              {{ $t('features.lm02.removeSection') }}
            </button>
          </div>

          <div class="space-y-3">
            <!-- Abschnitt-Titel -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('features.lm02.sectionTitleLabel') }}
              </label>
              <input
                v-model="section.title"
                type="text"
                :placeholder="$t('features.lm02.sectionTitlePlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Theorie-Text -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('features.lm02.theoryLabel') }}
              </label>
              <textarea
                v-model="section.theory"
                rows="4"
                :placeholder="$t('features.lm02.theoryPlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Verständnisfrage -->
            <div class="border-t border-[var(--color-border)] pt-3 mt-3">
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('features.lm02.questionLabel') }}
              </label>
              <input
                v-model="section.question"
                type="text"
                :placeholder="$t('features.lm02.questionPlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Erwartete Antwort -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('features.lm02.answerLabel') }}
              </label>
              <input
                v-model="section.expected_answer"
                type="text"
                :placeholder="$t('features.lm02.answerPlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Abschlussfrage -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.lm02.finalQuestionLabel') }}
        </label>
        <textarea
          v-model="methodData.final_question"
          rows="2"
          :placeholder="$t('features.lm02.finalQuestionPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ref, onMounted } from 'vue'
import type { LsxPanel } from '@/store/modules/desktop'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const { t } = useI18n()

const METHOD_CODE = 2

interface Props {
  panel: LsxPanel
}

const props = defineProps<Props>()

interface Section {
  title: string
  theory: string
  question: string
  expected_answer: string
}

// Methoden-spezifische Daten
const methodData = ref({
  topic: '',
  sections: [] as Section[],
  final_question: ''
})

const addSection = () => {
  methodData.value.sections.push({
    title: '',
    theory: '',
    question: '',
    expected_answer: ''
  })
}

const removeSection = (index: number) => {
  methodData.value.sections.splice(index, 1)
}

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.panel.payload?.instanceData?.data
  if (existingData) {
    methodData.value.topic = existingData.topic || ''
    methodData.value.sections = existingData.sections || []
    methodData.value.final_question = existingData.final_question || ''
  }
})
</script>
