<!--
  LearningMethod05Form - Mindmap-Generator

  Wissenskarte, die Beziehungen zwischen Konzepten zeigt.
  Visualisiert komplexe Zusammenhänge als interaktive Mindmap.

  KI-Nutzung: Hoch - KI strukturiert Wissen automatisch und erstellt Verbindungen.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <!-- Zentrales Thema -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Zentrales Thema *
        </label>
        <input
          v-model="methodData.central_topic"
          type="text"
          placeholder="z.B. OSI-Modell, Datenbankdesign, Projektmanagement"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Beschreibung/Kontext -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Kontext / Fokus
        </label>
        <textarea
          v-model="methodData.context"
          rows="2"
          placeholder="Optional: Worauf soll die Mindmap fokussieren?"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Tiefe der Mindmap -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Tiefe der Mindmap
        </label>
        <select
          v-model="methodData.depth_level"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="shallow">Flach (2 Ebenen) - Überblick</option>
          <option value="medium">Mittel (3 Ebenen) - Detailliert</option>
          <option value="deep">Tief (4+ Ebenen) - Umfassend</option>
        </select>
      </div>

      <!-- Hauptzweige (optional manuell) -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            Hauptzweige (optional)
          </label>
          <button
            @click="addBranch"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            + Zweig hinzufügen
          </button>
        </div>

        <p class="text-xs text-[var(--color-text-secondary)] mb-2">
          Optional: Definieren Sie Hauptzweige, oder lassen Sie die KI diese automatisch generieren.
        </p>

        <div v-for="(branch, index) in methodData.main_branches" :key="index" class="mb-2 flex gap-2">
          <input
            v-model="branch.name"
            type="text"
            placeholder="Zweig-Name"
            class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
          <input
            v-model="branch.description"
            type="text"
            placeholder="Kurzbeschreibung (optional)"
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
          Visualisierungsstil
        </label>
        <select
          v-model="methodData.visualization_style"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="radial">Radial - Klassische Mindmap</option>
          <option value="hierarchical">Hierarchisch - Baumstruktur</option>
          <option value="network">Netzwerk - Verbindungsorientiert</option>
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
              v-model="methodData.show_descriptions"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Beschreibungen bei Hover anzeigen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_connections"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Querverbindungen zwischen Konzepten zeigen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.color_coded"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Farbcodierung nach Kategorien</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.interactive"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Interaktiv erweiterbar (Nodes aufklappen)</span>
          </label>
        </div>
      </div>

      <!-- Lernziel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Lernziel
        </label>
        <input
          v-model="methodData.learning_goal"
          type="text"
          placeholder="Was soll der Lernende durch diese Mindmap verstehen?"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <p class="text-sm text-blue-800 dark:text-blue-200">
          <strong>KI-generiert:</strong> Die Mindmap wird automatisch aus dem Kapitel-Inhalt erstellt.
          Die KI identifiziert Konzepte und deren Beziehungen.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 5

interface Props {
  window: LsxWindow
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
  const existingData = props.window.payload?.instanceData?.data
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
