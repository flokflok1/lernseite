<!--
  System Features Tab - Feature-Aktivierung für Kurse

  Features:
  - Tutor-Agent: Sokratischer Dialog, NPC-Lecture
  - IT-Sandbox: Code Sandbox, Netzwerk-Sim, Szenarien, Fehleranalyse
  - Kollaboration: Peer Instruction, Team-Case, Peer Review, etc.
  - Visualisierung: Mindmap-Generator

  Hierarchie: Kurs → Kapitel → Lektion (mit Vererbung)
-->

<template>
  <div class="features-tab">
    <!-- No Course Selected -->
    <div v-if="!course" class="empty-state">
      <div class="empty-icon">🎛️</div>
      <h3>{{ $t('windows.aiStudioFeatures.selectCourse') }}</h3>
      <p>{{ $t('windows.aiStudioFeatures.selectCourseDesc') }}</p>
    </div>

    <!-- Main Content -->
    <div v-else class="features-content">
      <!-- Header -->
      <FeaturesHeader
        :course-title="course.title"
        :scope-label="scopeLabel"
        :enabled-count="enabledCount"
        :estimated-tokens="estimatedTokens"
      />

      <!-- Scope Selector -->
      <ScopeSelector
        v-model="currentScope"
        :chapter="chapter"
        :lesson="lesson"
      />

      <!-- Feature Groups -->
      <div class="feature-groups">
        <!-- Tutor Agent -->
        <FeatureGroup
          icon="🤖"
          :title="$t('windows.aiStudioFeatures.groups.tutor.title')"
          :description="$t('windows.aiStudioFeatures.groups.tutor.description')"
          :expanded="expandedGroups.has('tutor')"
          :group-enabled="isGroupEnabled('tutor')"
          @toggle="toggleGroup('tutor')"
          @toggle-all="toggleGroupEnabled('tutor')"
        >
          <FeatureToggle
            v-model="features.tutor_socratic_dialog"
            code="SF01"
            :label="$t('windows.aiStudioFeatures.features.socraticDialog.label')"
            :description="$t('windows.aiStudioFeatures.features.socraticDialog.description')"
            :token-cost="800"
            :inherited="getInheritedValue('tutor_socratic_dialog')"
          />
          <FeatureToggle
            v-model="features.tutor_npc_lecture"
            code="SF02"
            :label="$t('windows.aiStudioFeatures.features.npcLecture.label')"
            :description="$t('windows.aiStudioFeatures.features.npcLecture.description')"
            :token-cost="1200"
            :inherited="getInheritedValue('tutor_npc_lecture')"
          />
        </FeatureGroup>

        <!-- IT Sandbox -->
        <FeatureGroup
          icon="💻"
          :title="$t('windows.aiStudioFeatures.groups.it.title')"
          :description="$t('windows.aiStudioFeatures.groups.it.description')"
          :expanded="expandedGroups.has('it')"
          :group-enabled="isGroupEnabled('it')"
          :requirement-notice="$t('windows.aiStudioFeatures.requiresDocker')"
          @toggle="toggleGroup('it')"
          @toggle-all="toggleGroupEnabled('it')"
        >
          <FeatureToggle
            v-model="features.it_code_sandbox"
            code="SF03"
            :label="$t('windows.aiStudioFeatures.features.codeSandbox.label')"
            :description="$t('windows.aiStudioFeatures.features.codeSandbox.description')"
            :token-cost="500"
            :inherited="getInheritedValue('it_code_sandbox')"
          />
          <FeatureToggle
            v-model="features.it_network_sim"
            code="SF04"
            :label="$t('windows.aiStudioFeatures.features.networkSim.label')"
            :description="$t('windows.aiStudioFeatures.features.networkSim.description')"
            :token-cost="600"
            :inherited="getInheritedValue('it_network_sim')"
          />
          <FeatureToggle
            v-model="features.it_scenario"
            code="SF05"
            :label="$t('windows.aiStudioFeatures.features.itScenario.label')"
            :description="$t('windows.aiStudioFeatures.features.itScenario.description')"
            :token-cost="700"
            :inherited="getInheritedValue('it_scenario')"
          />
          <FeatureToggle
            v-model="features.it_error_analysis"
            code="SF06"
            :label="$t('windows.aiStudioFeatures.features.errorAnalysis.label')"
            :description="$t('windows.aiStudioFeatures.features.errorAnalysis.description')"
            :token-cost="400"
            :inherited="getInheritedValue('it_error_analysis')"
          />
        </FeatureGroup>

        <!-- Kollaboration -->
        <FeatureGroup
          icon="👥"
          :title="$t('windows.aiStudioFeatures.groups.collab.title')"
          :description="$t('windows.aiStudioFeatures.groups.collab.description')"
          :expanded="expandedGroups.has('collab')"
          :group-enabled="isGroupEnabled('collab')"
          @toggle="toggleGroup('collab')"
          @toggle-all="toggleGroupEnabled('collab')"
        >
          <FeatureToggle
            v-model="features.collab_peer_instruction"
            code="SF07"
            :label="$t('windows.aiStudioFeatures.features.peerInstruction.label')"
            :description="$t('windows.aiStudioFeatures.features.peerInstruction.description')"
            :token-cost="300"
            :inherited="getInheritedValue('collab_peer_instruction')"
          />
          <FeatureToggle
            v-model="features.collab_team_case"
            code="SF08"
            :label="$t('windows.aiStudioFeatures.features.teamCase.label')"
            :description="$t('windows.aiStudioFeatures.features.teamCase.description')"
            :token-cost="400"
            :inherited="getInheritedValue('collab_team_case')"
          />
          <FeatureToggle
            v-model="features.collab_peer_review"
            code="SF09"
            :label="$t('windows.aiStudioFeatures.features.peerReview.label')"
            :description="$t('windows.aiStudioFeatures.features.peerReview.description')"
            :token-cost="350"
            :inherited="getInheritedValue('collab_peer_review')"
          />
          <FeatureToggle
            v-model="features.collab_learning_diary"
            code="SF10"
            :label="$t('windows.aiStudioFeatures.features.learningDiary.label')"
            :description="$t('windows.aiStudioFeatures.features.learningDiary.description')"
            :token-cost="200"
            :inherited="getInheritedValue('collab_learning_diary')"
          />
          <FeatureToggle
            v-model="features.collab_portfolio"
            code="SF11"
            :label="$t('windows.aiStudioFeatures.features.portfolio.label')"
            :description="$t('windows.aiStudioFeatures.features.portfolio.description')"
            :token-cost="250"
            :inherited="getInheritedValue('collab_portfolio')"
          />
          <FeatureToggle
            v-model="features.collab_project_based"
            code="SF12"
            :label="$t('windows.aiStudioFeatures.features.projectBased.label')"
            :description="$t('windows.aiStudioFeatures.features.projectBased.description')"
            :token-cost="500"
            :inherited="getInheritedValue('collab_project_based')"
          />
          <FeatureToggle
            v-model="features.collab_inverted_classroom"
            code="SF13"
            :label="$t('windows.aiStudioFeatures.features.invertedClassroom.label')"
            :description="$t('windows.aiStudioFeatures.features.invertedClassroom.description')"
            :token-cost="300"
            :inherited="getInheritedValue('collab_inverted_classroom')"
          />
        </FeatureGroup>

        <!-- Visualisierung -->
        <FeatureGroup
          icon="🎨"
          :title="$t('windows.aiStudioFeatures.groups.viz.title')"
          :description="$t('windows.aiStudioFeatures.groups.viz.description')"
          :expanded="expandedGroups.has('viz')"
          :group-enabled="isGroupEnabled('viz')"
          @toggle="toggleGroup('viz')"
          @toggle-all="toggleGroupEnabled('viz')"
        >
          <FeatureToggle
            v-model="features.viz_mindmap"
            code="SF14"
            :label="$t('windows.aiStudioFeatures.features.mindmap.label')"
            :description="$t('windows.aiStudioFeatures.features.mindmap.description')"
            :token-cost="400"
            :inherited="getInheritedValue('viz_mindmap')"
          />
        </FeatureGroup>
      </div>

      <!-- Actions -->
      <ActionsBar
        :estimated-tokens="estimatedTokens"
        :is-saving="isSaving"
        @reset="resetToDefaults"
        @save="saveFeatures"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/api/http'
import {
  FeaturesHeader,
  ScopeSelector,
  FeatureGroup,
  FeatureToggle,
  ActionsBar
} from '@/components/assessment/admin/settings/exams'

const { t } = useI18n()

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

// Feature state
const features = reactive({
  tutor_socratic_dialog: false,
  tutor_npc_lecture: false,
  it_code_sandbox: false,
  it_network_sim: false,
  it_scenario: false,
  it_error_analysis: false,
  collab_peer_instruction: false,
  collab_team_case: false,
  collab_peer_review: false,
  collab_learning_diary: false,
  collab_portfolio: false,
  collab_project_based: false,
  collab_inverted_classroom: false,
  viz_mindmap: false
})

// Inherited values from parent scope
const inheritedFeatures = reactive<Record<string, boolean>>({})

// Computed
const scopeLabel = computed(() => {
  if (currentScope.value === 'lesson' && props.lesson) {
    return `${t('windows.aiStudioFeatures.scopeLesson')}: ${props.lesson.title}`
  }
  if (currentScope.value === 'chapter' && props.chapter) {
    return `${t('windows.aiStudioFeatures.scopeChapter')}: ${props.chapter.title}`
  }
  return t('windows.aiStudioFeatures.scopeCourseGlobal')
})

const enabledCount = computed(() => {
  return Object.values(features).filter(v => v).length
})

const estimatedTokens = computed(() => {
  const costs: Record<string, number> = {
    tutor_socratic_dialog: 800,
    tutor_npc_lecture: 1200,
    it_code_sandbox: 500,
    it_network_sim: 600,
    it_scenario: 700,
    it_error_analysis: 400,
    collab_peer_instruction: 300,
    collab_team_case: 400,
    collab_peer_review: 350,
    collab_learning_diary: 200,
    collab_portfolio: 250,
    collab_project_based: 500,
    collab_inverted_classroom: 300,
    viz_mindmap: 400
  }
  return Object.entries(features)
    .filter(([_, enabled]) => enabled)
    .reduce((sum, [key]) => sum + (costs[key] || 0), 0)
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
      return features.it_code_sandbox || features.it_network_sim ||
             features.it_scenario || features.it_error_analysis
    case 'collab':
      return features.collab_peer_instruction || features.collab_team_case ||
             features.collab_peer_review || features.collab_learning_diary ||
             features.collab_portfolio || features.collab_project_based ||
             features.collab_inverted_classroom
    case 'viz':
      return features.viz_mindmap
    default:
      return false
  }
}

function toggleGroupEnabled(groupId: string) {
  const enable = !isGroupEnabled(groupId)
  const groupFeatures: Record<string, (keyof typeof features)[]> = {
    tutor: ['tutor_socratic_dialog', 'tutor_npc_lecture'],
    it: ['it_code_sandbox', 'it_network_sim', 'it_scenario', 'it_error_analysis'],
    collab: ['collab_peer_instruction', 'collab_team_case', 'collab_peer_review',
             'collab_learning_diary', 'collab_portfolio', 'collab_project_based',
             'collab_inverted_classroom'],
    viz: ['viz_mindmap']
  }
  groupFeatures[groupId]?.forEach(key => { features[key] = enable })
}

function getInheritedValue(key: string): boolean | null {
  if (currentScope.value === 'course') return null
  return inheritedFeatures[key] ?? null
}

async function loadFeatures() {
  if (!props.course) return

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

    const response = await http.get(
      `/admin/courses/${props.course.course_id}/system-features?scope=${scopeType}&scope_id=${scopeId}`
    )

    if (response.data.success && response.data.data?.features) {
      const apiFeatures = response.data.data.features
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
    if (response.data.data?.inherited) {
      Object.assign(inheritedFeatures, response.data.data.inherited)
    }
  } catch (error) {
    console.error('Failed to load features:', error)
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
  } catch (error: any) {
    console.error('Failed to save features:', error)
    const message = error.response?.data?.error?.message || t('common.saveFailed')
    alert(`${t('common.error')}: ${message}`)
  } finally {
    isSaving.value = false
  }
}

function resetToDefaults() {
  Object.keys(features).forEach(key => {
    (features as Record<string, boolean>)[key] = false
  })
}

// Watch for course/chapter/lesson changes
watch(() => [props.course, props.chapter, props.lesson, currentScope.value], () => {
  loadFeatures()
}, { immediate: true })

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

.feature-groups {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
