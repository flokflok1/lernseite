<!--
  LearningMethod32Form - Inverted Classroom

  Vorbereitung zu Hause, Vertiefung in der Gruppe.
  Flipped Learning Konzept mit strukturierter Vor- und Nachbereitung.

  KI-Nutzung: Mittel - KI erstellt Vorbereitungsmaterial und moderiert Diskussionen.
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
          Thema *
        </label>
        <input
          v-model="methodData.topic"
          type="text"
          placeholder="z.B. OSI-Modell, Projektmanagement-Methoden"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
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
          placeholder="Was sollen die Lernenden am Ende koennen?"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Phase 1: Vorbereitung -->
      <div class="p-4 border border-blue-200 dark:border-blue-800 rounded-lg bg-blue-50 dark:bg-blue-900/20">
        <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-3">Phase 1: Vorbereitung (zu Hause)</h4>

        <!-- Vorbereitungsmaterial -->
        <div class="mb-3">
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Vorbereitungsmaterial
          </label>
          <div class="space-y-2">
            <label
              v-for="material in materialTypes"
              :key="material.value"
              class="flex items-center gap-2 cursor-pointer"
            >
              <input
                v-model="methodData.preparation_materials"
                type="checkbox"
                :value="material.value"
                class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
              />
              <span class="text-sm text-[var(--color-text-primary)]">{{ material.label }}</span>
            </label>
          </div>
        </div>

        <!-- Vorbereitungszeit -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Empfohlene Vorbereitungszeit
          </label>
          <select
            v-model="methodData.preparation_time"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="15min">15 Minuten</option>
            <option value="30min">30 Minuten</option>
            <option value="45min">45 Minuten</option>
            <option value="60min">1 Stunde</option>
            <option value="90min">1,5 Stunden</option>
          </select>
        </div>
      </div>

      <!-- Vorbereitungs-Quiz -->
      <div>
        <label class="flex items-center gap-2 cursor-pointer mb-2">
          <input
            v-model="methodData.has_prep_quiz"
            type="checkbox"
            class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
          />
          <span class="text-sm font-medium text-[var(--color-text-primary)]">Verstaendnis-Check vor Praesenzphase</span>
        </label>
        <p v-if="methodData.has_prep_quiz" class="text-xs text-[var(--color-text-secondary)] ml-6">
          Lernende muessen einen kurzen Quiz bestehen, bevor sie zur Praesenzphase zugelassen werden.
        </p>
      </div>

      <!-- Phase 2: Praesenz/Vertiefung -->
      <div class="p-4 border border-green-200 dark:border-green-800 rounded-lg bg-green-50 dark:bg-green-900/20">
        <h4 class="font-medium text-green-800 dark:text-green-200 mb-3">Phase 2: Praesenz/Vertiefung (Gruppe)</h4>

        <!-- Praesenz-Aktivitaeten -->
        <div class="mb-3">
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Aktivitaeten
          </label>
          <div class="space-y-2">
            <label
              v-for="activity in presenceActivities"
              :key="activity.value"
              class="flex items-center gap-2 cursor-pointer"
            >
              <input
                v-model="methodData.presence_activities"
                type="checkbox"
                :value="activity.value"
                class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
              />
              <span class="text-sm text-[var(--color-text-primary)]">{{ activity.label }}</span>
            </label>
          </div>
        </div>

        <!-- Praesenzzeit -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Praesenzzeit
          </label>
          <select
            v-model="methodData.presence_duration"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="30min">30 Minuten</option>
            <option value="45min">45 Minuten</option>
            <option value="60min">1 Stunde</option>
            <option value="90min">1,5 Stunden</option>
            <option value="120min">2 Stunden</option>
          </select>
        </div>
      </div>

      <!-- Gruppengroesse -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Gruppengroesse fuer Praesenzphase
        </label>
        <select
          v-model="methodData.group_size"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option :value="2">2 Personen (Partnerarbeit)</option>
          <option :value="3">3-4 Personen</option>
          <option :value="5">5-6 Personen</option>
          <option :value="0">Gesamte Klasse</option>
        </select>
      </div>

      <!-- Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Optionen
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.ai_moderation"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">KI moderiert Diskussion</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.track_preparation"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Vorbereitungs-Fortschritt tracken</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.allow_questions"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Fragen vor Praesenz sammeln</span>
          </label>
        </div>
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-pink-50 dark:bg-pink-900/20 rounded-lg border border-pink-200 dark:border-pink-800">
        <p class="text-sm text-pink-800 dark:text-pink-200">
          <strong>Inverted Classroom:</strong> Lernende bereiten sich zu Hause vor (Videos, Texte),
          die gemeinsame Zeit wird fuer Vertiefung, Uebung und Diskussion genutzt.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxPanel } from '@/store/modules/desktop'
import { BaseLearningMethodForm } from '@/components/base/content/admin/learning-methods/forms'

const METHOD_CODE = 32

const { t } = useI18n()

interface Props {
  panel: LsxPanel
}

const props = defineProps<Props>()

const materialTypes = computed(() => [
  { value: 'video', label: t('admin.systemFeatures.invertedClassroom.videos') },
  { value: 'text', label: 'Texte/Artikel' },
  { value: 'slides', label: 'Praesentationen' },
  { value: 'podcast', label: 'Audio/Podcast' },
  { value: 'interactive', label: 'Interaktive Inhalte' }
])

const presenceActivities = [
  { value: 'discussion', label: 'Diskussion' },
  { value: 'exercises', label: 'Praktische Uebungen' },
  { value: 'case_study', label: 'Fallstudien' },
  { value: 'peer_teaching', label: 'Peer Teaching' },
  { value: 'problem_solving', label: 'Problemloesung' },
  { value: 'qa_session', label: 'Q&A Session' }
]

const methodData = ref({
  topic: '',
  learning_objectives: '',
  preparation_materials: ['video', 'text'],
  preparation_time: '30min',
  has_prep_quiz: true,
  presence_activities: ['discussion', 'exercises'],
  presence_duration: '60min',
  group_size: 3,
  ai_moderation: false,
  track_preparation: true,
  allow_questions: true
})

onMounted(() => {
  const existingData = props.panel.payload?.instanceData?.data
  if (existingData) {
    methodData.value.topic = existingData.topic || ''
    methodData.value.learning_objectives = existingData.learning_objectives || ''
    methodData.value.preparation_materials = existingData.preparation_materials || ['video', 'text']
    methodData.value.preparation_time = existingData.preparation_time || '30min'
    methodData.value.has_prep_quiz = existingData.has_prep_quiz ?? true
    methodData.value.presence_activities = existingData.presence_activities || ['discussion', 'exercises']
    methodData.value.presence_duration = existingData.presence_duration || '60min'
    methodData.value.group_size = existingData.group_size || 3
    methodData.value.ai_moderation = existingData.ai_moderation ?? false
    methodData.value.track_preparation = existingData.track_preparation ?? true
    methodData.value.allow_questions = existingData.allow_questions ?? true
  }
})
</script>
