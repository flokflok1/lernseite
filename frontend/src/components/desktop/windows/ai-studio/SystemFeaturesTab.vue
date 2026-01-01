<!--
  System Features Tab - Feature-Aktivierung für Kurse

  Features:
  - 🤖 Tutor-Agent: Sokratischer Dialog (LM04), NPC-Lecture (LM07)
  - 💻 IT-Sandbox: Code Sandbox (LM09), Netzwerk-Sim (LM10), Szenarien (LM11), Fehleranalyse (LM16)
  - 👥 Kollaboration: Peer Instruction (LM26), Team-Case (LM27), Peer Review (LM28), etc.
  - 🎨 Visualisierung: Mindmap-Generator (LM05)

  Hierarchie: Kurs → Kapitel → Lektion (mit Vererbung)
-->

<template>
  <div class="features-tab">
    <!-- No Course Selected -->
    <div v-if="!course" class="empty-state">
      <div class="empty-icon">🎛️</div>
      <h3>Kurs auswählen</h3>
      <p>Wähle einen Kurs aus, um System-Features zu konfigurieren.</p>
    </div>

    <!-- Main Content -->
    <div v-else class="features-content">
      <!-- Header -->
      <div class="features-header">
        <div class="header-icon">🎛️</div>
        <div class="header-info">
          <h2>System-Features</h2>
          <p>{{ course.title }} • {{ scopeLabel }}</p>
        </div>
        <div class="header-stats">
          <div class="stat">
            <span class="stat-value">{{ enabledCount }}</span>
            <span class="stat-label">Aktiviert</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ estimatedTokens.toLocaleString() }}</span>
            <span class="stat-label">Tokens/Lektion</span>
          </div>
        </div>
      </div>

      <!-- Scope Selector -->
      <div class="scope-selector">
        <button
          @click="currentScope = 'course'"
          class="scope-btn"
          :class="{ active: currentScope === 'course' }"
        >
          📚 Kurs-Ebene
        </button>
        <button
          v-if="chapter"
          @click="currentScope = 'chapter'"
          class="scope-btn"
          :class="{ active: currentScope === 'chapter' }"
        >
          📖 Kapitel: {{ chapter.title }}
        </button>
        <button
          v-if="lesson"
          @click="currentScope = 'lesson'"
          class="scope-btn"
          :class="{ active: currentScope === 'lesson' }"
        >
          📝 Lektion: {{ lesson.title }}
        </button>
      </div>

      <!-- Feature Groups -->
      <div class="feature-groups">
        <!-- Tutor Agent -->
        <div class="feature-group">
          <div class="group-header" @click="toggleGroup('tutor')">
            <div class="group-icon">🤖</div>
            <div class="group-info">
              <h3>Tutor-Agent</h3>
              <p>KI-gestützte Lernbegleitung mit Dialogen und Erklärungen</p>
            </div>
            <div class="group-toggle">
              <input
                type="checkbox"
                :checked="isGroupEnabled('tutor')"
                @click.stop="toggleGroupEnabled('tutor')"
                class="toggle-switch"
              />
            </div>
            <svg
              class="expand-icon"
              :class="{ rotated: expandedGroups.has('tutor') }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>

          <div v-if="expandedGroups.has('tutor')" class="group-features">
            <FeatureToggle
              v-model="features.tutor_socratic_dialog"
              code="LM04"
              label="Sokratischer Dialog"
              description="KI führt durch Fragen zum Verständnis"
              :token-cost="800"
              :inherited="getInheritedValue('tutor_socratic_dialog')"
            />
            <FeatureToggle
              v-model="features.tutor_npc_lecture"
              code="LM07"
              label="NPC-Tutor-Lecture"
              description="Animierter Tutor erklärt Inhalte mit TTS"
              :token-cost="1200"
              :inherited="getInheritedValue('tutor_npc_lecture')"
            />
          </div>
        </div>

        <!-- IT Sandbox -->
        <div class="feature-group">
          <div class="group-header" @click="toggleGroup('it')">
            <div class="group-icon">💻</div>
            <div class="group-info">
              <h3>IT-Sandbox</h3>
              <p>Interaktive Programmier- und Netzwerk-Umgebungen</p>
            </div>
            <div class="group-toggle">
              <input
                type="checkbox"
                :checked="isGroupEnabled('it')"
                @click.stop="toggleGroupEnabled('it')"
                class="toggle-switch"
              />
            </div>
            <svg
              class="expand-icon"
              :class="{ rotated: expandedGroups.has('it') }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>

          <div v-if="expandedGroups.has('it')" class="group-features">
            <div class="requirement-notice">
              ⚠️ Benötigt: Docker-Backend aktiviert
            </div>
            <FeatureToggle
              v-model="features.it_code_sandbox"
              code="LM09"
              label="Code/Config Sandbox"
              description="Ausführbare Code-Umgebung für praktische Übungen"
              :token-cost="500"
              :inherited="getInheritedValue('it_code_sandbox')"
            />
            <FeatureToggle
              v-model="features.it_network_sim"
              code="LM10"
              label="Netzwerk-Simulation"
              description="Virtuelle Netzwerk-Topologien erstellen und testen"
              :token-cost="600"
              :inherited="getInheritedValue('it_network_sim')"
            />
            <FeatureToggle
              v-model="features.it_scenario"
              code="LM11"
              label="IT-Szenario lösen"
              description="Komplexe IT-Problemstellungen interaktiv bearbeiten"
              :token-cost="700"
              :inherited="getInheritedValue('it_scenario')"
            />
            <FeatureToggle
              v-model="features.it_error_analysis"
              code="LM16"
              label="Fehleranalyse"
              description="Systematische Fehlersuche und Debugging"
              :token-cost="400"
              :inherited="getInheritedValue('it_error_analysis')"
            />
          </div>
        </div>

        <!-- Kollaboration -->
        <div class="feature-group">
          <div class="group-header" @click="toggleGroup('collab')">
            <div class="group-icon">👥</div>
            <div class="group-info">
              <h3>Kollaboration</h3>
              <p>Gemeinsames Lernen und Peer-Feedback</p>
            </div>
            <div class="group-toggle">
              <input
                type="checkbox"
                :checked="isGroupEnabled('collab')"
                @click.stop="toggleGroupEnabled('collab')"
                class="toggle-switch"
              />
            </div>
            <svg
              class="expand-icon"
              :class="{ rotated: expandedGroups.has('collab') }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>

          <div v-if="expandedGroups.has('collab')" class="group-features">
            <FeatureToggle
              v-model="features.collab_peer_instruction"
              code="LM26"
              label="Peer Instruction"
              description="Lernende erklären sich gegenseitig Konzepte"
              :token-cost="300"
              :inherited="getInheritedValue('collab_peer_instruction')"
            />
            <FeatureToggle
              v-model="features.collab_team_case"
              code="LM27"
              label="Team-Case / Gruppenfallarbeit"
              description="Fallstudien gemeinsam im Team bearbeiten"
              :token-cost="400"
              :inherited="getInheritedValue('collab_team_case')"
            />
            <FeatureToggle
              v-model="features.collab_peer_review"
              code="LM28"
              label="Peer Review"
              description="Gegenseitige Bewertung von Arbeiten"
              :token-cost="350"
              :inherited="getInheritedValue('collab_peer_review')"
            />
            <FeatureToggle
              v-model="features.collab_learning_diary"
              code="LM29"
              label="Lerntagebuch"
              description="Persönliche Reflexion des Lernfortschritts"
              :token-cost="200"
              :inherited="getInheritedValue('collab_learning_diary')"
            />
            <FeatureToggle
              v-model="features.collab_portfolio"
              code="LM30"
              label="Projekt-Portfolio"
              description="Sammlung von Projektarbeiten und Ergebnissen"
              :token-cost="250"
              :inherited="getInheritedValue('collab_portfolio')"
            />
            <FeatureToggle
              v-model="features.collab_project_based"
              code="LM31"
              label="Projektbasiertes Lernen"
              description="Lernen durch praktische Projektarbeit"
              :token-cost="500"
              :inherited="getInheritedValue('collab_project_based')"
            />
            <FeatureToggle
              v-model="features.collab_inverted_classroom"
              code="LM32"
              label="Inverted Classroom"
              description="Theorie zu Hause, Praxis in der Gruppe"
              :token-cost="300"
              :inherited="getInheritedValue('collab_inverted_classroom')"
            />
          </div>
        </div>

        <!-- Visualisierung -->
        <div class="feature-group">
          <div class="group-header" @click="toggleGroup('viz')">
            <div class="group-icon">🎨</div>
            <div class="group-info">
              <h3>Visualisierung</h3>
              <p>Grafische Darstellungen und Diagramme</p>
            </div>
            <div class="group-toggle">
              <input
                type="checkbox"
                :checked="isGroupEnabled('viz')"
                @click.stop="toggleGroupEnabled('viz')"
                class="toggle-switch"
              />
            </div>
            <svg
              class="expand-icon"
              :class="{ rotated: expandedGroups.has('viz') }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>

          <div v-if="expandedGroups.has('viz')" class="group-features">
            <FeatureToggle
              v-model="features.viz_mindmap"
              code="LM05"
              label="Mindmap-Generator"
              description="Automatische Erstellung von Mindmaps zu Themen"
              :token-cost="400"
              :inherited="getInheritedValue('viz_mindmap')"
            />
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions-bar">
        <div class="token-summary">
          <span class="summary-label">Geschätzte Tokens pro Lektion:</span>
          <span class="summary-value">{{ estimatedTokens.toLocaleString() }}</span>
          <span class="summary-cost">(~{{ (estimatedTokens * 0.00002).toFixed(4) }}€)</span>
        </div>
        <div class="action-buttons">
          <button @click="resetToDefaults" class="btn-secondary">
            🔄 Zurücksetzen
          </button>
          <button @click="saveFeatures" :disabled="isSaving" class="btn-primary">
            <span v-if="isSaving" class="spinner-small"></span>
            💾 Speichern
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive, onMounted } from 'vue'
import http from '@/api/http'

// Feature Toggle Sub-component
const FeatureToggle = {
  props: {
    modelValue: Boolean,
    code: String,
    label: String,
    description: String,
    tokenCost: Number,
    inherited: { type: Boolean, default: null }
  },
  emits: ['update:modelValue'],
  template: `
    <div class="feature-item" :class="{ enabled: modelValue, inherited: inherited !== null && modelValue === inherited }">
      <div class="feature-toggle">
        <input
          type="checkbox"
          :checked="modelValue"
          @change="$emit('update:modelValue', $event.target.checked)"
          class="feature-checkbox"
        />
      </div>
      <div class="feature-code">{{ code }}</div>
      <div class="feature-info">
        <div class="feature-label">{{ label }}</div>
        <div class="feature-desc">{{ description }}</div>
      </div>
      <div class="feature-cost">
        <span class="cost-value">{{ tokenCost }}</span>
        <span class="cost-label">Tokens</span>
      </div>
      <div v-if="inherited !== null" class="inherited-badge" :class="{ active: modelValue === inherited }">
        {{ modelValue === inherited ? '↓ Vererbt' : '✎ Überschrieben' }}
      </div>
    </div>
  `
}

interface Course {
  course_id: string
  title: string
}

interface Chapter {
  chapter_id: string
  title: string
}

interface Lesson {
  lesson_id: string
  title: string
}

interface Props {
  course?: Course | null
  chapter?: Chapter | null
  lesson?: Lesson | null
}

const props = withDefaults(defineProps<Props>(), {
  course: null,
  chapter: null,
  lesson: null
})

// State
const currentScope = ref<'course' | 'chapter' | 'lesson'>('course')
const expandedGroups = ref<Set<string>>(new Set(['tutor']))
const isSaving = ref(false)
const isLoading = ref(false)

// Feature state
const features = reactive({
  // Tutor Agent
  tutor_socratic_dialog: false,
  tutor_npc_lecture: false,
  // IT Sandbox
  it_code_sandbox: false,
  it_network_sim: false,
  it_scenario: false,
  it_error_analysis: false,
  // Kollaboration
  collab_peer_instruction: false,
  collab_team_case: false,
  collab_peer_review: false,
  collab_learning_diary: false,
  collab_portfolio: false,
  collab_project_based: false,
  collab_inverted_classroom: false,
  // Visualisierung
  viz_mindmap: false
})

// Inherited values from parent scope
const inheritedFeatures = reactive<Record<string, boolean>>({})

// Computed
const scopeLabel = computed(() => {
  if (currentScope.value === 'lesson' && props.lesson) return `Lektion: ${props.lesson.title}`
  if (currentScope.value === 'chapter' && props.chapter) return `Kapitel: ${props.chapter.title}`
  return 'Kurs-Ebene (Global)'
})

const enabledCount = computed(() => {
  return Object.values(features).filter(v => v).length
})

const estimatedTokens = computed(() => {
  let total = 0
  if (features.tutor_socratic_dialog) total += 800
  if (features.tutor_npc_lecture) total += 1200
  if (features.it_code_sandbox) total += 500
  if (features.it_network_sim) total += 600
  if (features.it_scenario) total += 700
  if (features.it_error_analysis) total += 400
  if (features.collab_peer_instruction) total += 300
  if (features.collab_team_case) total += 400
  if (features.collab_peer_review) total += 350
  if (features.collab_learning_diary) total += 200
  if (features.collab_portfolio) total += 250
  if (features.collab_project_based) total += 500
  if (features.collab_inverted_classroom) total += 300
  if (features.viz_mindmap) total += 400
  return total
})

// Methods
function toggleGroup(groupId: string) {
  if (expandedGroups.value.has(groupId)) {
    expandedGroups.value.delete(groupId)
  } else {
    expandedGroups.value.add(groupId)
  }
}

function isGroupEnabled(groupId: string): boolean {
  switch (groupId) {
    case 'tutor':
      return features.tutor_socratic_dialog || features.tutor_npc_lecture
    case 'it':
      return features.it_code_sandbox || features.it_network_sim || features.it_scenario || features.it_error_analysis
    case 'collab':
      return features.collab_peer_instruction || features.collab_team_case || features.collab_peer_review ||
             features.collab_learning_diary || features.collab_portfolio || features.collab_project_based ||
             features.collab_inverted_classroom
    case 'viz':
      return features.viz_mindmap
    default:
      return false
  }
}

function toggleGroupEnabled(groupId: string) {
  const enable = !isGroupEnabled(groupId)

  switch (groupId) {
    case 'tutor':
      features.tutor_socratic_dialog = enable
      features.tutor_npc_lecture = enable
      break
    case 'it':
      features.it_code_sandbox = enable
      features.it_network_sim = enable
      features.it_scenario = enable
      features.it_error_analysis = enable
      break
    case 'collab':
      features.collab_peer_instruction = enable
      features.collab_team_case = enable
      features.collab_peer_review = enable
      features.collab_learning_diary = enable
      features.collab_portfolio = enable
      features.collab_project_based = enable
      features.collab_inverted_classroom = enable
      break
    case 'viz':
      features.viz_mindmap = enable
      break
  }
}

function getInheritedValue(key: string): boolean | null {
  if (currentScope.value === 'course') return null
  return inheritedFeatures[key] ?? null
}

async function loadFeatures() {
  if (!props.course) return

  isLoading.value = true
  try {
    let scopeId = props.course.course_id
    let scopeType = 'course'

    if (currentScope.value === 'chapter' && props.chapter) {
      scopeId = props.chapter.chapter_id
      scopeType = 'chapter'
    } else if (currentScope.value === 'lesson' && props.lesson) {
      scopeId = props.lesson.lesson_id
      scopeType = 'lesson'
    }

    const response = await http.get(`/admin/courses/${props.course.course_id}/system-features?scope=${scopeType}&scope_id=${scopeId}`)
    const data = response.data

    if (data.success && data.data?.features) {
      // Map API response to component state
      const apiFeatures = data.data.features
      features.tutor_socratic_dialog = apiFeatures.socratic_dialog || false
      features.tutor_npc_lecture = apiFeatures.npc_tutor || false
      features.it_code_sandbox = apiFeatures.code_sandbox || false
      features.it_network_sim = apiFeatures.network_simulation || false
      features.it_scenario = apiFeatures.it_scenario || false
      features.it_error_analysis = apiFeatures.error_analysis || false
      features.collab_peer_instruction = apiFeatures.peer_instruction || false
      features.collab_team_case = apiFeatures.team_case || false
      features.collab_peer_review = apiFeatures.peer_review || false
      features.collab_learning_diary = apiFeatures.learning_journal || false
      features.collab_portfolio = apiFeatures.portfolio || false
      features.collab_project_based = apiFeatures.project_based || false
      features.collab_inverted_classroom = apiFeatures.inverted_classroom || false
      features.viz_mindmap = apiFeatures.mindmap_generator || false
    }
    if (data.data?.inherited) {
      Object.assign(inheritedFeatures, data.data.inherited)
    }
  } catch (error) {
    console.error('Failed to load features:', error)
  } finally {
    isLoading.value = false
  }
}

async function saveFeatures() {
  if (!props.course) return

  isSaving.value = true
  try {
    let scopeId = props.course.course_id
    let scopeType = 'course'

    if (currentScope.value === 'chapter' && props.chapter) {
      scopeId = props.chapter.chapter_id
      scopeType = 'chapter'
    } else if (currentScope.value === 'lesson' && props.lesson) {
      scopeId = props.lesson.lesson_id
      scopeType = 'lesson'
    }

    // Map component state to API format (feature_code -> boolean)
    const apiFeatures: Record<string, boolean> = {
      socratic_dialog: features.tutor_socratic_dialog,
      npc_tutor: features.tutor_npc_lecture,
      code_sandbox: features.it_code_sandbox,
      network_simulation: features.it_network_sim,
      it_scenario: features.it_scenario,
      error_analysis: features.it_error_analysis,
      peer_instruction: features.collab_peer_instruction,
      team_case: features.collab_team_case,
      peer_review: features.collab_peer_review,
      learning_journal: features.collab_learning_diary,
      portfolio: features.collab_portfolio,
      project_based: features.collab_project_based,
      inverted_classroom: features.collab_inverted_classroom,
      mindmap_generator: features.viz_mindmap
    }

    await http.put(`/admin/courses/${props.course.course_id}/system-features`, {
      scope: scopeType,
      scope_id: scopeId,
      features: apiFeatures
    })

    console.log('Features saved successfully')
  } catch (error: any) {
    console.error('Failed to save features:', error)
    const message = error.response?.data?.error?.message || 'Speichern fehlgeschlagen'
    alert(`Fehler: ${message}`)
  } finally {
    isSaving.value = false
  }
}

function resetToDefaults() {
  Object.keys(features).forEach(key => {
    (features as any)[key] = false
  })
}

// Watch for course/chapter/lesson changes
watch(() => [props.course, props.chapter, props.lesson, currentScope.value], () => {
  loadFeatures()
}, { immediate: true })

// Adjust scope when chapter/lesson selection changes
watch(() => props.chapter, (newChapter) => {
  if (newChapter && currentScope.value === 'course') {
    // Keep course scope unless explicitly changed
  }
})

watch(() => props.lesson, (newLesson) => {
  if (newLesson) {
    currentScope.value = 'lesson'
  } else if (props.chapter) {
    currentScope.value = 'chapter'
  } else {
    currentScope.value = 'course'
  }
})
</script>

<style scoped>
.features-tab {
  height: 100%;
  overflow-y: auto;
  padding: 1rem;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon { font-size: 4rem; margin-bottom: 1rem; }
.empty-state h3 { color: var(--color-text-primary); margin: 0 0 0.5rem; }
.empty-state p { color: var(--color-text-secondary); margin: 0; }

/* Header */
.features-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 1rem;
  margin-bottom: 1rem;
}

.header-icon {
  width: 56px; height: 56px;
  background: rgba(255,255,255,0.2);
  border-radius: 1rem;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.75rem;
}

.header-info { flex: 1; }
.header-info h2 { color: white; font-size: 1.25rem; font-weight: 700; margin: 0; }
.header-info p { color: rgba(255,255,255,0.8); font-size: 0.875rem; margin: 0.25rem 0 0; }

.header-stats { display: flex; gap: 1.5rem; }
.stat { text-align: center; }
.stat-value { display: block; font-size: 1.5rem; font-weight: 700; color: white; }
.stat-label { font-size: 0.75rem; color: rgba(255,255,255,0.7); }

/* Scope Selector */
.scope-selector {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: var(--color-surface);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
}

.scope-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.scope-btn:hover {
  background: var(--color-surface-secondary);
}

.scope-btn.active {
  background: var(--color-primary-subtle);
  border-color: var(--color-primary);
  color: var(--color-primary);
  font-weight: 600;
}

/* Feature Groups */
.feature-groups {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feature-group {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.group-header:hover {
  background: var(--color-surface-secondary);
}

.group-icon {
  width: 48px; height: 48px;
  background: var(--color-primary-subtle);
  border-radius: 0.75rem;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem;
}

.group-info { flex: 1; }
.group-info h3 { margin: 0; font-size: 1rem; color: var(--color-text-primary); }
.group-info p { margin: 0.25rem 0 0; font-size: 0.8125rem; color: var(--color-text-secondary); }

.group-toggle {
  padding: 0 0.5rem;
}

.toggle-switch {
  width: 44px;
  height: 24px;
  cursor: pointer;
}

.expand-icon {
  width: 20px; height: 20px;
  color: var(--color-text-tertiary);
  transition: transform 0.2s;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

/* Group Features */
.group-features {
  border-top: 1px solid var(--color-border);
  padding: 0.5rem;
}

.requirement-notice {
  padding: 0.75rem 1rem;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  color: #f59e0b;
  margin-bottom: 0.5rem;
}

/* Feature Item */
.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  transition: background 0.15s;
}

.feature-item:hover {
  background: var(--color-surface-secondary);
}

.feature-item.enabled {
  background: rgba(16, 185, 129, 0.05);
}

.feature-toggle {
  flex-shrink: 0;
}

.feature-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.feature-code {
  width: 48px;
  font-family: monospace;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-primary);
  background: var(--color-primary-subtle);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  text-align: center;
}

.feature-info {
  flex: 1;
  min-width: 0;
}

.feature-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.feature-desc {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  margin-top: 0.125rem;
}

.feature-cost {
  text-align: right;
  flex-shrink: 0;
}

.cost-value {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.cost-label {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
}

.inherited-badge {
  font-size: 0.625rem;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  background: var(--color-surface-secondary);
  color: var(--color-text-tertiary);
}

.inherited-badge.active {
  background: rgba(99, 102, 241, 0.1);
  color: var(--color-primary);
}

/* Actions Bar */
.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
}

.token-summary {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.summary-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.summary-cost {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
}

.btn-secondary {
  padding: 0.625rem 1rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.btn-secondary:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background: var(--color-primary);
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary:hover:not(:disabled) {
  filter: brightness(1.1);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
