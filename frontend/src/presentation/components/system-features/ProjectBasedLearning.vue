<!--
  LearningMethod31Form - Projektbasiertes Lernen

  Laengerfristige Projekte mit Meilensteinen und KI-Coaching.
  Anwendungsorientiertes Lernen durch komplexe Aufgabenstellungen.

  KI-Nutzung: Mittel - KI gibt Projekt-Feedback und Coaching.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <!-- Projekt-Titel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Projekt-Titel *
        </label>
        <input
          v-model="methodData.project_title"
          type="text"
          placeholder="z.B. Firmennetzwerk aufbauen, Webshop entwickeln"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Projekt-Beschreibung -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Projektbeschreibung *
        </label>
        <textarea
          v-model="methodData.project_description"
          rows="4"
          placeholder="Beschreiben Sie das Projekt, das die Lernenden umsetzen sollen..."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Lernziele -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Lernziele
        </label>
        <textarea
          v-model="methodData.learning_objectives"
          rows="2"
          placeholder="Was sollen die Lernenden durch dieses Projekt lernen?"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Meilensteine -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Meilensteine
        </label>
        <div class="space-y-2">
          <div
            v-for="(milestone, index) in methodData.milestones"
            :key="index"
            class="flex gap-2"
          >
            <span class="w-8 h-10 flex items-center justify-center bg-[var(--color-primary)] text-white rounded text-sm font-medium">
              {{ index + 1 }}
            </span>
            <input
              v-model="milestone.title"
              type="text"
              placeholder="Meilenstein-Titel"
              class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
            <input
              v-model="milestone.deliverable"
              type="text"
              placeholder="Erwartetes Ergebnis"
              class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
            <button
              v-if="methodData.milestones.length > 1"
              @click="removeMilestone(index)"
              class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <button
          v-if="methodData.milestones.length < 10"
          @click="addMilestone"
          class="mt-2 text-sm text-[var(--color-primary)] hover:underline"
        >
          + Meilenstein hinzufuegen
        </button>
      </div>

      <!-- Zeitrahmen -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Projektdauer
          </label>
          <select
            v-model="methodData.duration"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="1w">1 Woche</option>
            <option value="2w">2 Wochen</option>
            <option value="1m">1 Monat</option>
            <option value="2m">2 Monate</option>
            <option value="semester">Semester</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Arbeitsform
          </label>
          <select
            v-model="methodData.work_mode"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="individual">Einzelarbeit</option>
            <option value="pair">Partnerarbeit</option>
            <option value="team">Teamarbeit (3-5)</option>
            <option value="flexible">Flexibel</option>
          </select>
        </div>
      </div>

      <!-- Ressourcen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Bereitgestellte Ressourcen
        </label>
        <textarea
          v-model="methodData.resources"
          rows="2"
          placeholder="Links, Dokumentation, Vorlagen, etc."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Optionen
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.ai_coaching"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">KI-Coaching bei Meilensteinen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.peer_review"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Peer-Review bei Meilensteinen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.progress_tracking"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Fortschritts-Tracking</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.final_presentation"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Abschlusspraesentation</span>
          </label>
        </div>
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-pink-50 dark:bg-pink-900/20 rounded-lg border border-pink-200 dark:border-pink-800">
        <p class="text-sm text-pink-800 dark:text-pink-200">
          <strong>Projektbasiertes Lernen:</strong> Durch komplexe, realitaetsnahe Projekte
          wenden Lernende ihr Wissen praktisch an. Die KI unterstuetzt mit Coaching und Feedback.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/window.store'
import { BaseLearningMethodForm } from '@/presentation/components/learning/editor/forms'

const METHOD_CODE = 31

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const methodData = ref({
  project_title: '',
  project_description: '',
  learning_objectives: '',
  milestones: [
    { title: 'Planung', deliverable: 'Projektplan' },
    { title: 'Umsetzung', deliverable: 'Erste Version' },
    { title: 'Abschluss', deliverable: 'Fertiges Projekt' }
  ],
  duration: '2w',
  work_mode: 'individual',
  resources: '',
  ai_coaching: true,
  peer_review: false,
  progress_tracking: true,
  final_presentation: false
})

const addMilestone = () => {
  if (methodData.value.milestones.length < 10) {
    methodData.value.milestones.push({ title: '', deliverable: '' })
  }
}

const removeMilestone = (index: number) => {
  if (methodData.value.milestones.length > 1) {
    methodData.value.milestones.splice(index, 1)
  }
}

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.project_title = existingData.project_title || ''
    methodData.value.project_description = existingData.project_description || ''
    methodData.value.learning_objectives = existingData.learning_objectives || ''
    methodData.value.milestones = existingData.milestones || methodData.value.milestones
    methodData.value.duration = existingData.duration || '2w'
    methodData.value.work_mode = existingData.work_mode || 'individual'
    methodData.value.resources = existingData.resources || ''
    methodData.value.ai_coaching = existingData.ai_coaching ?? true
    methodData.value.peer_review = existingData.peer_review ?? false
    methodData.value.progress_tracking = existingData.progress_tracking ?? true
    methodData.value.final_presentation = existingData.final_presentation ?? false
  }
})
</script>
