<!--
  LearningMethod06Form - Beispiel-Szenario-Erklärung

  Reale Anwendungsfälle, Case Studies und praxisnahe Szenarien
  zur Veranschaulichung theoretischer Konzepte.

  KI-Nutzung: Mittel - KI kann passende Szenarien generieren.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <!-- Thema -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('learningMethods.lm06.topicLabel') }}
        </label>
        <input
          v-model="methodData.topic"
          type="text"
          :placeholder="$t('learningMethods.lm06.topicPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Branche/Kontext -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('learningMethods.lm06.industryContextLabel') }}
        </label>
        <select
          v-model="methodData.industry_context"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="">{{ $t('learningMethods.lm06.industryContextDefault') }}</option>
          <option value="it_admin">{{ $t('learningMethods.lm06.industryContextItAdmin') }}</option>
          <option value="software_dev">{{ $t('learningMethods.lm06.industryContextSoftwareDev') }}</option>
          <option value="network">{{ $t('learningMethods.lm06.industryContextNetwork') }}</option>
          <option value="business">{{ $t('learningMethods.lm06.industryContextBusiness') }}</option>
          <option value="finance">{{ $t('learningMethods.lm06.industryContextFinance') }}</option>
          <option value="healthcare">{{ $t('learningMethods.lm06.industryContextHealthcare') }}</option>
          <option value="education">{{ $t('learningMethods.lm06.industryContextEducation') }}</option>
          <option value="manufacturing">{{ $t('learningMethods.lm06.industryContextManufacturing') }}</option>
          <option value="retail">{{ $t('learningMethods.lm06.industryContextRetail') }}</option>
          <option value="other">{{ $t('learningMethods.lm06.industryContextOther') }}</option>
        </select>
      </div>

      <!-- Szenarien -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            {{ $t('learningMethods.lm06.scenariosLabel') }}
          </label>
          <button
            @click="addScenario"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            {{ $t('learningMethods.lm06.addScenario') }}
          </button>
        </div>

        <div v-if="methodData.scenarios.length === 0" class="text-sm text-[var(--color-text-secondary)] italic mb-3">
          {{ $t('learningMethods.lm06.noScenarios') }}
        </div>

        <div v-for="(scenario, index) in methodData.scenarios" :key="index" class="mb-4 p-4 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface-secondary)]">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-[var(--color-primary)]">
              {{ $t('learningMethods.lm06.scenarioNumber', { n: index + 1 }) }}
            </span>
            <button
              @click="removeScenario(index)"
              type="button"
              class="text-sm text-red-500 hover:underline"
            >
              {{ $t('learningMethods.lm06.removeScenario') }}
            </button>
          </div>

          <div class="space-y-3">
            <!-- Szenario-Titel -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('learningMethods.lm06.scenarioTitleLabel') }}
              </label>
              <input
                v-model="scenario.title"
                type="text"
                :placeholder="$t('learningMethods.lm06.scenarioTitlePlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Ausgangssituation -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('learningMethods.lm06.situationLabel') }}
              </label>
              <textarea
                v-model="scenario.situation"
                rows="3"
                :placeholder="$t('learningMethods.lm06.situationPlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Herausforderung/Problem -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('learningMethods.lm06.challengeLabel') }}
              </label>
              <textarea
                v-model="scenario.challenge"
                rows="2"
                :placeholder="$t('learningMethods.lm06.challengePlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Lösung/Erklärung -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('learningMethods.lm06.solutionLabel') }}
              </label>
              <textarea
                v-model="scenario.solution"
                rows="4"
                :placeholder="$t('learningMethods.lm06.solutionPlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Lernerkenntnis -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('learningMethods.lm06.takeawayLabel') }}
              </label>
              <input
                v-model="scenario.takeaway"
                type="text"
                :placeholder="$t('learningMethods.lm06.takeawayPlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Schwierigkeitsgrad -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('learningMethods.lm06.complexityLabel') }}
        </label>
        <select
          v-model="methodData.complexity"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="simple">{{ $t('learningMethods.lm06.complexitySimple') }}</option>
          <option value="moderate">{{ $t('learningMethods.lm06.complexityModerate') }}</option>
          <option value="complex">{{ $t('learningMethods.lm06.complexityComplex') }}</option>
        </select>
      </div>

      <!-- Lernziel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('learningMethods.lm06.learningGoalLabel') }}
        </label>
        <input
          v-model="methodData.learning_goal"
          type="text"
          :placeholder="$t('learningMethods.lm06.learningGoalPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- KI-Generierung Info -->
      <div class="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
        <p class="text-sm text-amber-800 dark:text-amber-200">
          <strong>{{ $t('learningMethods.lm06.aiSupportText') }}</strong>
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxWindow } from '@/application/stores/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const { t } = useI18n()
const METHOD_CODE = 6

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

interface Scenario {
  title: string
  situation: string
  challenge: string
  solution: string
  takeaway: string
}

// Methoden-spezifische Daten
const methodData = ref({
  topic: '',
  industry_context: '',
  scenarios: [] as Scenario[],
  complexity: 'moderate',
  learning_goal: ''
})

const addScenario = () => {
  methodData.value.scenarios.push({
    title: '',
    situation: '',
    challenge: '',
    solution: '',
    takeaway: ''
  })
}

const removeScenario = (index: number) => {
  methodData.value.scenarios.splice(index, 1)
}

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.topic = existingData.topic || ''
    methodData.value.industry_context = existingData.industry_context || ''
    methodData.value.scenarios = existingData.scenarios || []
    methodData.value.complexity = existingData.complexity || 'moderate'
    methodData.value.learning_goal = existingData.learning_goal || ''
  }
})
</script>
