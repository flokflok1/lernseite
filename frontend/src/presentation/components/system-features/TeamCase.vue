<!--
  LearningMethod27Form - Team-Case-Study

  Gruppenarbeit an komplexen Fallstudien mit Rollenzuweisung.
  Teams bearbeiten gemeinsam realistische Szenarien.

  KI-Nutzung: Mittel - KI generiert Cases, gibt Feedback, bewertet Loesungen.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <!-- Fallstudie Titel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Fallstudie Titel *
        </label>
        <input
          v-model="methodData.case_title"
          type="text"
          placeholder="z.B. IT-Infrastruktur Migration, Netzwerk-Ausfall Analyse"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Szenario-Beschreibung -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Szenario-Beschreibung *
        </label>
        <textarea
          v-model="methodData.scenario_description"
          rows="4"
          placeholder="Beschreiben Sie das Szenario, das die Teams bearbeiten sollen..."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Rollen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Team-Rollen
        </label>
        <div class="space-y-2">
          <div
            v-for="(role, index) in methodData.roles"
            :key="index"
            class="flex gap-2"
          >
            <input
              v-model="role.name"
              type="text"
              placeholder="Rollenname (z.B. Projektleiter)"
              class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
            <input
              v-model="role.responsibility"
              type="text"
              placeholder="Verantwortung"
              class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
            <button
              v-if="methodData.roles.length > 2"
              @click="removeRole(index)"
              class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <button
          v-if="methodData.roles.length < 6"
          @click="addRole"
          class="mt-2 text-sm text-[var(--color-primary)] hover:underline"
        >
          + Rolle hinzufuegen
        </button>
      </div>

      <!-- Team-Einstellungen -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Team-Groesse
          </label>
          <select
            v-model="methodData.team_size"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option :value="3">3 Personen</option>
            <option :value="4">4 Personen</option>
            <option :value="5">5 Personen</option>
            <option :value="6">6 Personen</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Bearbeitungszeit
          </label>
          <select
            v-model="methodData.time_limit"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="30min">30 Minuten</option>
            <option value="1h">1 Stunde</option>
            <option value="2h">2 Stunden</option>
            <option value="1d">1 Tag</option>
            <option value="1w">1 Woche</option>
          </select>
        </div>
      </div>

      <!-- Deliverables -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Erwartete Ergebnisse (Deliverables)
        </label>
        <div class="space-y-2">
          <label
            v-for="deliverable in deliverableOptions"
            :key="deliverable.value"
            class="flex items-center gap-2 cursor-pointer"
          >
            <input
              v-model="methodData.deliverables"
              type="checkbox"
              :value="deliverable.value"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">{{ deliverable.label }}</span>
          </label>
        </div>
      </div>

      <!-- Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Optionen
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.allow_ai_hints"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">KI-Hinweise erlauben</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.peer_feedback"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Peer-Feedback zwischen Teams</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.presentation_required"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Praesentation erforderlich</span>
          </label>
        </div>
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-pink-50 dark:bg-pink-900/20 rounded-lg border border-pink-200 dark:border-pink-800">
        <p class="text-sm text-pink-800 dark:text-pink-200">
          <strong>Team-Case-Study:</strong> Teams arbeiten gemeinsam an realistischen Fallstudien.
          Jedes Teammitglied uebernimmt eine spezifische Rolle und traegt zum Gesamtergebnis bei.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/window.store'
import { BaseLearningMethodForm } from '@/presentation/components/content/admin/learning-methods/forms'

const METHOD_CODE = 27

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const deliverableOptions = [
  { value: 'documentation', label: 'Schriftliche Dokumentation' },
  { value: 'presentation', label: 'Praesentation/Slides' },
  { value: 'diagram', label: 'Diagramme/Visualisierungen' },
  { value: 'prototype', label: 'Prototyp/Demo' },
  { value: 'action_plan', label: 'Massnahmenplan' }
]

const methodData = ref({
  case_title: '',
  scenario_description: '',
  roles: [
    { name: 'Projektleiter', responsibility: 'Koordination und Zeitmanagement' },
    { name: 'Analyst', responsibility: 'Problemanalyse und Recherche' },
    { name: 'Techniker', responsibility: 'Technische Umsetzung' }
  ],
  team_size: 4,
  time_limit: '1h',
  deliverables: ['documentation'],
  allow_ai_hints: true,
  peer_feedback: false,
  presentation_required: false
})

const addRole = () => {
  if (methodData.value.roles.length < 6) {
    methodData.value.roles.push({ name: '', responsibility: '' })
  }
}

const removeRole = (index: number) => {
  if (methodData.value.roles.length > 2) {
    methodData.value.roles.splice(index, 1)
  }
}

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.case_title = existingData.case_title || ''
    methodData.value.scenario_description = existingData.scenario_description || ''
    methodData.value.roles = existingData.roles || methodData.value.roles
    methodData.value.team_size = existingData.team_size || 4
    methodData.value.time_limit = existingData.time_limit || '1h'
    methodData.value.deliverables = existingData.deliverables || ['documentation']
    methodData.value.allow_ai_hints = existingData.allow_ai_hints ?? true
    methodData.value.peer_feedback = existingData.peer_feedback ?? false
    methodData.value.presentation_required = existingData.presentation_required ?? false
  }
})
</script>
