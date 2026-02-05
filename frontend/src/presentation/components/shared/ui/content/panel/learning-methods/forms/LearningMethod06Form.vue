<!--
  LearningMethod04Form - Beispiel-Szenario

  Reale Anwendungsfälle, Case Studies und praxisnahe Szenarien
  zur Veranschaulichung theoretischer Konzepte.

  KI-Nutzung: Mittel - KI kann passende Szenarien generieren.
-->

<template>
  <BaseLearningMethodForm
    :panel="panel"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <!-- Thema -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.learningMethods.lm04.topicLabel') }}
        </label>
        <input
          v-model="methodData.topic"
          type="text"
          :placeholder="$t('features.learningMethods.lm04.topicPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Branche/Kontext -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.learningMethods.lm04.industryContextLabel') }}
        </label>
        <select
          v-model="methodData.industry_context"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="">{{ $t('features.learningMethods.lm04.industryContextDefault') }}</option>
          <option value="it_admin">{{ $t('features.learningMethods.lm04.industryContextItAdmin') }}</option>
          <option value="software_dev">{{ $t('features.learningMethods.lm04.industryContextSoftwareDev') }}</option>
          <option value="network">{{ $t('features.learningMethods.lm04.industryContextNetwork') }}</option>
          <option value="business">{{ $t('features.learningMethods.lm04.industryContextBusiness') }}</option>
          <option value="finance">{{ $t('features.learningMethods.lm04.industryContextFinance') }}</option>
          <option value="healthcare">{{ $t('features.learningMethods.lm04.industryContextHealthcare') }}</option>
          <option value="education">{{ $t('features.learningMethods.lm04.industryContextEducation') }}</option>
          <option value="manufacturing">{{ $t('features.learningMethods.lm04.industryContextManufacturing') }}</option>
          <option value="retail">{{ $t('features.learningMethods.lm04.industryContextRetail') }}</option>
          <option value="other">{{ $t('features.learningMethods.lm04.industryContextOther') }}</option>
        </select>
      </div>

      <!-- Szenarien -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            {{ $t('features.learningMethods.lm04.scenariosLabel') }}
          </label>
          <button
            @click="addScenario"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            {{ $t('features.learningMethods.lm04.addScenario') }}
          </button>
        </div>

        <div v-if="methodData.scenarios.length === 0" class="text-sm text-[var(--color-text-secondary)] italic mb-3">
          {{ $t('features.learningMethods.lm04.noScenarios') }}
        </div>

        <div v-for="(scenario, index) in methodData.scenarios" :key="index" class="mb-4 p-4 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface-secondary)]">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-[var(--color-primary)]">
              {{ $t('features.learningMethods.lm04.scenarioNumber', { n: index + 1 }) }}
            </span>
            <button
              @click="removeScenario(index)"
              type="button"
              class="text-sm text-red-500 hover:underline"
            >
              {{ $t('features.learningMethods.lm04.removeScenario') }}
            </button>
          </div>

          <div class="space-y-3">
            <!-- Szenario-Titel -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('features.learningMethods.lm04.scenarioTitleLabel') }}
              </label>
              <input
                v-model="scenario.title"
                type="text"
                :placeholder="$t('features.learningMethods.lm04.scenarioTitlePlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Ausgangssituation -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('features.learningMethods.lm04.situationLabel') }}
              </label>
              <textarea
                v-model="scenario.situation"
                rows="3"
                :placeholder="$t('features.learningMethods.lm04.situationPlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Herausforderung/Problem -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('features.learningMethods.lm04.challengeLabel') }}
              </label>
              <textarea
                v-model="scenario.challenge"
                rows="2"
                :placeholder="$t('features.learningMethods.lm04.challengePlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Lösung/Erklärung -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('features.learningMethods.lm04.solutionLabel') }}
              </label>
              <textarea
                v-model="scenario.solution"
                rows="4"
                :placeholder="$t('features.learningMethods.lm04.solutionPlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Lernerkenntnis -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                {{ $t('features.learningMethods.lm04.takeawayLabel') }}
              </label>
              <input
                v-model="scenario.takeaway"
                type="text"
                :placeholder="$t('features.learningMethods.lm04.takeawayPlaceholder')"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Schwierigkeitsgrad -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.learningMethods.lm04.complexityLabel') }}
        </label>
        <select
          v-model="methodData.complexity"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="simple">{{ $t('features.learningMethods.lm04.complexitySimple') }}</option>
          <option value="moderate">{{ $t('features.learningMethods.lm04.complexityModerate') }}</option>
          <option value="complex">{{ $t('features.learningMethods.lm04.complexityComplex') }}</option>
        </select>
      </div>

      <!-- Lernziel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.learningMethods.lm04.learningGoalLabel') }}
        </label>
        <input
          v-model="methodData.learning_goal"
          type="text"
          :placeholder="$t('features.learningMethods.lm04.learningGoalPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- KI-Generierung Info -->
      <div class="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
        <p class="text-sm text-amber-800 dark:text-amber-200">
          <strong>{{ $t('features.learningMethods.lm04.aiSupportText') }}</strong>
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxPanel } from '@/application/stores/modules/desktop'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const { t } = useI18n()
const METHOD_CODE = 4

interface Props {
  panel: LsxPanel
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
  const existingData = props.panel.payload?.instanceData?.data
  if (existingData) {
    methodData.value.topic = existingData.topic || ''
    methodData.value.industry_context = existingData.industry_context || ''
    methodData.value.scenarios = existingData.scenarios || []
    methodData.value.complexity = existingData.complexity || 'moderate'
    methodData.value.learning_goal = existingData.learning_goal || ''
  }
})
</script>
