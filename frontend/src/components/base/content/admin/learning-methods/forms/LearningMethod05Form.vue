<!--
  LearningMethod05Form - Mindmap-Generator

  Wissenskarte, die Beziehungen zwischen Konzepten zeigt.
  Visualisiert komplexe Zusammenhänge als interaktive Mindmap.

  KI-Nutzung: Hoch - KI strukturiert Wissen automatisch und erstellt Verbindungen.
-->

<template>
  <BaseLearningMethodForm
    :panel="panel"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <!-- Zentrales Thema -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.lm05.centralTopicLabel') }}
        </label>
        <input
          v-model="methodData.central_topic"
          type="text"
          :placeholder="$t('features.lm05.centralTopicPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Beschreibung/Kontext -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.lm05.contextLabel') }}
        </label>
        <textarea
          v-model="methodData.context"
          rows="2"
          :placeholder="$t('features.lm05.contextPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Tiefe der Mindmap -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.lm05.depthLevelLabel') }}
        </label>
        <select
          v-model="methodData.depth_level"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="shallow">{{ $t('features.lm05.depthLevelShallow') }}</option>
          <option value="medium">{{ $t('features.lm05.depthLevelMedium') }}</option>
          <option value="deep">{{ $t('features.lm05.depthLevelDeep') }}</option>
        </select>
      </div>

      <!-- Hauptzweige (optional manuell) -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            {{ $t('features.lm05.mainBranchesLabel') }}
          </label>
          <button
            @click="addBranch"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            {{ $t('features.lm05.addBranch') }}
          </button>
        </div>

        <p class="text-xs text-[var(--color-text-secondary)] mb-2">
          {{ $t('features.lm05.branchesHint') }}
        </p>

        <div v-for="(branch, index) in methodData.main_branches" :key="index" class="mb-2 flex gap-2">
          <input
            v-model="branch.name"
            type="text"
            :placeholder="$t('features.lm05.branchNamePlaceholder')"
            class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
          <input
            v-model="branch.description"
            type="text"
            :placeholder="$t('features.lm05.branchDescriptionPlaceholder')"
            class="flex-[2] px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
          <button
            @click="removeBranch(index)"
            type="button"
            class="px-2 text-red-500 hover:text-red-700"
          >
            ×
          </button>
        </div>
      </div>

      <!-- Visualisierungsstil -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.lm05.visualizationStyleLabel') }}
        </label>
        <select
          v-model="methodData.visualization_style"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="radial">{{ $t('features.lm05.visualizationStyleRadial') }}</option>
          <option value="hierarchical">{{ $t('features.lm05.visualizationStyleHierarchical') }}</option>
          <option value="network">{{ $t('features.lm05.visualizationStyleNetwork') }}</option>
        </select>
      </div>

      <!-- Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.lm05.optionsLabel') }}
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_descriptions"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">{{ $t('features.lm05.showDescriptionsLabel') }}</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_connections"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">{{ $t('features.lm05.showConnectionsLabel') }}</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.color_coded"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">{{ $t('features.lm05.colorCodedLabel') }}</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.interactive"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">{{ $t('features.lm05.interactiveLabel') }}</span>
          </label>
        </div>
      </div>

      <!-- Lernziel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.lm05.learningGoalLabel') }}
        </label>
        <input
          v-model="methodData.learning_goal"
          type="text"
          :placeholder="$t('features.lm05.learningGoalPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <p class="text-sm text-blue-800 dark:text-blue-200">
          <strong>{{ $t('features.lm05.aiHintTitle') }}:</strong> {{ $t('features.lm05.aiHintText') }}
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxPanel } from '@/store/modules/desktop'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const { t } = useI18n()
const METHOD_CODE = 5

interface Props {
  panel: LsxPanel
}

const props = defineProps<Props>()

interface Branch {
  name: string
  description: string
}

// Methoden-spezifische Daten
const methodData = ref({
  central_topic: '',
  context: '',
  depth_level: 'medium',
  main_branches: [] as Branch[],
  visualization_style: 'radial',
  show_descriptions: true,
  show_connections: true,
  color_coded: true,
  interactive: true,
  learning_goal: ''
})

const addBranch = () => {
  methodData.value.main_branches.push({
    name: '',
    description: ''
  })
}

const removeBranch = (index: number) => {
  methodData.value.main_branches.splice(index, 1)
}

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.panel.payload?.instanceData?.data
  if (existingData) {
    methodData.value.central_topic = existingData.central_topic || ''
    methodData.value.context = existingData.context || ''
    methodData.value.depth_level = existingData.depth_level || 'medium'
    methodData.value.main_branches = existingData.main_branches || []
    methodData.value.visualization_style = existingData.visualization_style || 'radial'
    methodData.value.show_descriptions = existingData.show_descriptions ?? true
    methodData.value.show_connections = existingData.show_connections ?? true
    methodData.value.color_coded = existingData.color_coded ?? true
    methodData.value.interactive = existingData.interactive ?? true
    methodData.value.learning_goal = existingData.learning_goal || ''
  }
})
</script>
