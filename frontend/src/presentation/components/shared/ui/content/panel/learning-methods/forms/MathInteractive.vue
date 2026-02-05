<!--
  LearningMethod06Form - Beispiel-Szenario-Erklärung

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
          Thema / Konzept *
        </label>
        <input
          v-model="methodData.topic"
          type="text"
          placeholder="z.B. Subnetting in der Praxis, DSGVO-Umsetzung, Agile Methoden"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Branche/Kontext -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Branche / Kontext
        </label>
        <select
          v-model="methodData.industry_context"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="">Allgemein</option>
          <option value="it_admin">IT-Administration</option>
          <option value="software_dev">Softwareentwicklung</option>
          <option value="network">Netzwerktechnik</option>
          <option value="business">Betriebswirtschaft</option>
          <option value="finance">Finanzen/Buchhaltung</option>
          <option value="healthcare">Gesundheitswesen</option>
          <option value="education">Bildung</option>
          <option value="manufacturing">Produktion/Fertigung</option>
          <option value="retail">Handel</option>
          <option value="other">Sonstiges</option>
        </select>
      </div>

      <!-- Szenarien -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            Szenarien *
          </label>
          <button
            @click="addScenario"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            + Szenario hinzufügen
          </button>
        </div>

        <div v-if="methodData.scenarios.length === 0" class="text-sm text-[var(--color-text-secondary)] italic mb-3">
          Keine Szenarien vorhanden. Fügen Sie mindestens ein Szenario hinzu oder lassen Sie die KI generieren.
        </div>

        <div v-for="(scenario, index) in methodData.scenarios" :key="index" class="mb-4 p-4 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface-secondary)]">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-[var(--color-primary)]">
              Szenario {{ index + 1 }}
            </span>
            <button
              @click="removeScenario(index)"
              type="button"
              class="text-sm text-red-500 hover:underline"
            >
              Entfernen
            </button>
          </div>

          <div class="space-y-3">
            <!-- Szenario-Titel -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Titel *
              </label>
              <input
                v-model="scenario.title"
                type="text"
                placeholder="z.B. Netzwerkausfall im Rechenzentrum"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Ausgangssituation -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Ausgangssituation *
              </label>
              <textarea
                v-model="scenario.situation"
                rows="3"
                placeholder="Beschreiben Sie die Ausgangssituation des Szenarios..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Herausforderung/Problem -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Herausforderung / Problem
              </label>
              <textarea
                v-model="scenario.challenge"
                rows="2"
                placeholder="Welches Problem muss gelöst werden?"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Lösung/Erklärung -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Lösung / Erklärung *
              </label>
              <textarea
                v-model="scenario.solution"
                rows="4"
                placeholder="Wie wird das Konzept angewendet? Was ist die Lösung?"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Lernerkenntnis -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Lernerkenntnis
              </label>
              <input
                v-model="scenario.takeaway"
                type="text"
                placeholder="Was lernt man aus diesem Szenario?"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Schwierigkeitsgrad -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Komplexitätsgrad
        </label>
        <select
          v-model="methodData.complexity"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="simple">Einfach - Einzelne Konzepte</option>
          <option value="moderate">Moderat - Mehrere Konzepte</option>
          <option value="complex">Komplex - Vernetztes Wissen</option>
        </select>
      </div>

      <!-- Lernziel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Übergeordnetes Lernziel
        </label>
        <input
          v-model="methodData.learning_goal"
          type="text"
          placeholder="Was soll der Lernende durch diese Szenarien verstehen?"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- KI-Generierung Info -->
      <div class="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
        <p class="text-sm text-amber-800 dark:text-amber-200">
          <strong>KI-Unterstützung:</strong> Die KI kann passende Praxis-Szenarien basierend auf dem Thema generieren.
          Lassen Sie die Szenario-Liste leer für automatische Generierung.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxPanel } from '@/application/stores/modules/desktop'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 6

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
