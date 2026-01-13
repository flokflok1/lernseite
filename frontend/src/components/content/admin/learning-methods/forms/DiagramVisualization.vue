<!--
  LearningMethod03Form - Diagramm/Visualisierung

  Visuelle Darstellung von Konzepten, z.B. Netzwerktopologien, Flussdiagramme,
  UML, ER-Diagramme. Unterstützt das Verständnis durch grafische Aufbereitung.

  KI-Nutzung: Mittel - KI kann Diagramm-Beschreibungen generieren oder
  Mermaid/PlantUML-Code erstellen.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <!-- Diagramm-Titel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.learningMethods.lm03.diagramTitleLabel') }}
        </label>
        <input
          v-model="methodData.diagram_title"
          type="text"
          :placeholder="$t('windows.learningMethods.lm03.diagramTitlePlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Diagramm-Typ -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.learningMethods.lm03.diagramTypeLabel') }}
        </label>
        <select
          v-model="methodData.diagram_type"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        >
          <option value="">{{ $t('windows.learningMethods.lm03.diagramTypeDefault') }}</option>
          <option value="flowchart">{{ $t('windows.learningMethods.lm03.diagramTypeFlowchart') }}</option>
          <option value="network">{{ $t('windows.learningMethods.lm03.diagramTypeNetwork') }}</option>
          <option value="uml_class">{{ $t('windows.learningMethods.lm03.diagramTypeUmlClass') }}</option>
          <option value="uml_sequence">{{ $t('windows.learningMethods.lm03.diagramTypeUmlSequence') }}</option>
          <option value="uml_usecase">{{ $t('windows.learningMethods.lm03.diagramTypeUmlUsecase') }}</option>
          <option value="er_diagram">{{ $t('windows.learningMethods.lm03.diagramTypeErDiagram') }}</option>
          <option value="hierarchy">{{ $t('windows.learningMethods.lm03.diagramTypeHierarchy') }}</option>
          <option value="timeline">{{ $t('windows.learningMethods.lm03.diagramTypeTimeline') }}</option>
          <option value="process">{{ $t('windows.learningMethods.lm03.diagramTypeProcess') }}</option>
          <option value="architecture">{{ $t('windows.learningMethods.lm03.diagramTypeArchitecture') }}</option>
          <option value="other">{{ $t('windows.learningMethods.lm03.diagramTypeOther') }}</option>
        </select>
      </div>

      <!-- Beschreibung -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.learningMethods.lm03.descriptionLabel') }}
        </label>
        <textarea
          v-model="methodData.description"
          rows="3"
          :placeholder="$t('windows.learningMethods.lm03.descriptionPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Mermaid/PlantUML Code -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.learningMethods.lm03.diagramCodeLabel') }}
        </label>
        <textarea
          v-model="methodData.diagram_code"
          rows="8"
          placeholder="graph TD
    A[Start] --> B{Entscheidung}
    B -->|Ja| C[Aktion 1]
    B -->|Nein| D[Aktion 2]
    C --> E[Ende]
    D --> E"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] font-mono text-sm"
        />
        <p class="mt-1 text-xs text-[var(--color-text-secondary)]">
          {{ $t('windows.learningMethods.lm03.diagramCodeHint') }}
        </p>
      </div>

      <!-- Elemente-Liste -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            {{ $t('windows.learningMethods.lm03.elementsLabel') }}
          </label>
          <button
            @click="addElement"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            {{ $t('windows.learningMethods.lm03.addElement') }}
          </button>
        </div>

        <p class="text-xs text-[var(--color-text-secondary)] mb-2">
          {{ $t('windows.learningMethods.lm03.elementsHint') }}
        </p>

        <div v-for="(element, index) in methodData.elements" :key="index" class="mb-2 flex gap-2">
          <input
            v-model="element.name"
            type="text"
            :placeholder="$t('windows.learningMethods.lm03.elementNamePlaceholder')"
            class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
          <input
            v-model="element.description"
            type="text"
            :placeholder="$t('windows.learningMethods.lm03.elementDescriptionPlaceholder')"
            class="flex-[2] px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
          <button
            @click="removeElement(index)"
            type="button"
            class="px-2 text-red-500 hover:text-red-700"
          >
            ×
          </button>
        </div>
      </div>

      <!-- Lernziel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('windows.learningMethods.lm03.learningGoalLabel') }}
        </label>
        <input
          v-model="methodData.learning_goal"
          type="text"
          :placeholder="$t('windows.learningMethods.lm03.learningGoalPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxWindow } from '@/store/modules/desktop'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const { t } = useI18n()
const METHOD_CODE = 3

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

interface DiagramElement {
  name: string
  description: string
}

// Methoden-spezifische Daten
const methodData = ref({
  diagram_title: '',
  diagram_type: '',
  description: '',
  diagram_code: '',
  elements: [] as DiagramElement[],
  learning_goal: ''
})

const addElement = () => {
  methodData.value.elements.push({
    name: '',
    description: ''
  })
}

const removeElement = (index: number) => {
  methodData.value.elements.splice(index, 1)
}

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.diagram_title = existingData.diagram_title || ''
    methodData.value.diagram_type = existingData.diagram_type || ''
    methodData.value.description = existingData.description || ''
    methodData.value.diagram_code = existingData.diagram_code || ''
    methodData.value.elements = existingData.elements || []
    methodData.value.learning_goal = existingData.learning_goal || ''
  }
})
</script>
