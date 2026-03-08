<!--
  ExamGoalsManager - User interface for managing exam goals and viewing weakness profiles.

  Features:
  - Active goals list with status badges
  - Add Goal from available exam types
  - Weakness profile summary with score bars and trend indicators
  - Curriculum profile showing per-position performance
-->

<template>
  <div class="h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-4 py-3">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-bold text-[var(--color-text-primary)]">
            {{ t('panel.examGoals.title') }}
          </h2>
          <p class="text-sm text-[var(--color-text-secondary)]">
            {{ t('panel.examGoals.subtitle') }}
          </p>
        </div>
        <button
          @click="showAddDialog = true"
          class="px-3 py-1.5 text-sm text-white rounded transition-colors"
          style="background-color: var(--color-primary);"
        >
          {{ t('panel.examGoals.addGoal') }}
        </button>
      </div>
    </div>

    <!-- Add Goal Dialog -->
    <div v-if="showAddDialog" class="px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-surface)]">
      <h3 class="text-sm font-semibold text-[var(--color-text-primary)] mb-2">
        {{ t('panel.examGoals.availableTypes') }}
      </h3>
      <div v-if="loadingTypes" class="flex items-center gap-2 py-2">
        <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-[var(--color-primary)]"></div>
      </div>
      <div v-else-if="availableTypes.length === 0" class="text-sm text-[var(--color-text-secondary)] py-2">
        {{ t('panel.examGoals.noTypes') }}
      </div>
      <div v-else class="flex flex-wrap gap-2 mb-3">
        <button
          v-for="at in availableTypes"
          :key="at.exam_type"
          @click="selectedNewType = at.exam_type"
          class="px-3 py-1.5 text-sm rounded border transition-colors"
          :class="selectedNewType === at.exam_type
            ? 'border-[var(--color-primary)] bg-[var(--color-primary)] text-white'
            : 'border-[var(--color-border)] text-[var(--color-text-primary)] hover:border-[var(--color-primary)]'"
        >
          {{ at.display_name?.de || at.display_name?.en || at.exam_type }}
        </button>
      </div>
      <div class="mb-3">
        <label class="block text-xs text-[var(--color-text-secondary)] mb-1">
          {{ t('panel.examGoals.targetDate') }}
        </label>
        <input
          v-model="newTargetDate"
          type="date"
          class="px-2 py-1 text-sm border rounded bg-[var(--color-bg)] text-[var(--color-text-primary)] border-[var(--color-border)]"
        />
      </div>
      <div class="flex gap-2">
        <button
          @click="handleAddGoal"
          :disabled="!selectedNewType"
          class="px-3 py-1.5 text-sm text-white rounded transition-colors"
          :class="selectedNewType ? '' : 'opacity-50 cursor-not-allowed'"
          style="background-color: var(--color-success);"
        >
          {{ t('panel.examGoals.addGoal') }}
        </button>
        <button
          @click="showAddDialog = false"
          class="px-3 py-1.5 text-sm rounded border border-[var(--color-border)] text-[var(--color-text-secondary)]"
        >
          {{ t('actions.cancel') }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loadingGoals" class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[var(--color-primary)]"></div>
    </div>

    <!-- Goals List -->
    <div v-else class="flex-1 overflow-y-auto p-4">
      <!-- Empty State -->
      <div v-if="goals.length === 0" class="text-center py-12">
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
          {{ t('panel.examGoals.noGoals') }}
        </h3>
        <p class="text-sm text-[var(--color-text-secondary)] mb-4">
          {{ t('panel.examGoals.noGoalsDesc') }}
        </p>
      </div>

      <!-- Goal Cards -->
      <div v-else class="space-y-4">
        <div
          v-for="goal in goals"
          :key="goal.goal_id"
          class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] overflow-hidden"
        >
          <!-- Goal Header -->
          <div class="px-4 py-3 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span
                class="px-2 py-0.5 text-xs font-medium rounded-full"
                :class="statusClasses(goal.status)"
              >
                {{ t(`panel.examGoals.status.${goal.status}`) }}
              </span>
              <h4 class="text-sm font-semibold text-[var(--color-text-primary)]">
                {{ goal.display_name?.de || goal.display_name?.en || goal.exam_type }}
              </h4>
            </div>
            <div class="flex items-center gap-2">
              <span v-if="goal.target_date" class="text-xs text-[var(--color-text-secondary)]">
                {{ t('panel.examGoals.targetDate') }}: {{ formatDate(goal.target_date) }}
              </span>
              <select
                :value="goal.status"
                @change="handleStatusChange(goal.goal_id, ($event.target as HTMLSelectElement).value)"
                class="text-xs border rounded px-1 py-0.5 bg-[var(--color-bg)] text-[var(--color-text-primary)] border-[var(--color-border)]"
              >
                <option value="active">{{ t('panel.examGoals.status.active') }}</option>
                <option value="paused">{{ t('panel.examGoals.status.paused') }}</option>
                <option value="planned">{{ t('panel.examGoals.status.planned') }}</option>
                <option value="passed">{{ t('panel.examGoals.status.passed') }}</option>
              </select>
              <button
                @click="handleRemoveGoal(goal.goal_id)"
                class="text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-danger)] p-1"
                :title="t('panel.examGoals.removeGoal')"
              >
                &#10005;
              </button>
            </div>
          </div>

          <!-- Weakness Profile (for active goals) -->
          <div
            v-if="goal.status === 'active' && weaknessProfiles[goal.exam_type]"
            class="px-4 py-3 border-t border-[var(--color-border)]"
          >
            <div class="flex items-center justify-between mb-2">
              <h5 class="text-xs font-semibold text-[var(--color-text-secondary)] uppercase">
                {{ t('panel.examGoals.weakness.title') }}
              </h5>
              <span class="text-sm font-bold text-[var(--color-text-primary)]">
                {{ t('panel.examGoals.weakness.overallScore') }}:
                {{ weaknessProfiles[goal.exam_type].overall_score }}%
              </span>
            </div>

            <!-- Weakness Items -->
            <div
              v-if="weaknessProfiles[goal.exam_type].weaknesses.length > 0"
              class="space-y-2"
            >
              <div
                v-for="w in weaknessProfiles[goal.exam_type].weaknesses.slice(0, 5)"
                :key="w.topic_key"
                class="flex items-center gap-3"
              >
                <span class="text-xs text-[var(--color-text-primary)] w-32 truncate">
                  {{ w.topic_key }}
                </span>
                <div class="flex-1 h-2 bg-[var(--color-bg)] rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all"
                    :style="{ width: `${w.score}%`, backgroundColor: scoreColor(w.score) }"
                  ></div>
                </div>
                <span class="text-xs font-medium w-10 text-right" :style="{ color: scoreColor(w.score) }">
                  {{ w.score }}%
                </span>
                <span class="text-xs w-6" :class="trendClasses(w.trend)">
                  {{ trendIcon(w.trend) }}
                </span>
                <span class="text-xs text-[var(--color-text-secondary)] w-16">
                  {{ w.attempts }} {{ t('panel.examGoals.weakness.attempts') }}
                </span>
              </div>
            </div>
            <div v-else class="text-xs text-[var(--color-text-secondary)] py-2">
              {{ t('panel.examGoals.weakness.noData') }}
            </div>
          </div>

          <!-- Curriculum Profile (for active goals with linked framework) -->
          <div
            v-if="goal.status === 'active' && curriculumProfiles[goal.exam_type]"
            class="px-4 py-3 border-t border-[var(--color-border)]"
          >
            <div class="flex items-center justify-between mb-2">
              <h5 class="text-xs font-semibold text-[var(--color-text-secondary)] uppercase">
                {{ t('panel.examGoals.curriculum.title') }}
              </h5>
              <span class="text-xs text-[var(--color-text-secondary)]">
                {{ curriculumProfiles[goal.exam_type].framework_name }}
              </span>
            </div>

            <div
              v-if="curriculumProfiles[goal.exam_type].positions.length > 0"
              class="space-y-2"
            >
              <div
                v-for="pos in curriculumProfiles[goal.exam_type].positions"
                :key="pos.position_number"
                class="flex items-center gap-3"
              >
                <span class="text-xs font-medium text-[var(--color-text-primary)] w-12 shrink-0">
                  {{ pos.position_number }}
                </span>
                <span class="text-xs text-[var(--color-text-primary)] w-40 truncate" :title="pos.title">
                  {{ pos.title }}
                </span>
                <div class="flex-1 h-2 bg-[var(--color-bg)] rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all"
                    :style="{ width: `${pos.score_percent}%`, backgroundColor: scoreColor(pos.score_percent) }"
                  ></div>
                </div>
                <span class="text-xs font-medium w-10 text-right" :style="{ color: scoreColor(pos.score_percent) }">
                  {{ pos.score_percent }}%
                </span>
                <span class="text-xs text-[var(--color-text-secondary)] w-16">
                  {{ pos.correct_count }}/{{ pos.total_questions }}
                </span>
              </div>
            </div>
            <div v-else class="text-xs text-[var(--color-text-secondary)] py-2">
              {{ t('panel.examGoals.curriculum.noData') }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="px-4 py-2 border-t border-[var(--color-border)]">
      <div class="rounded p-2 text-sm" style="background-color: var(--color-danger); color: white;">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  fetchExamGoals,
  fetchAvailableTypes,
  createExamGoal,
  updateExamGoalStatus,
  deleteExamGoal,
  fetchWeaknessProfile,
  fetchCurriculumProfile,
  type ExamGoal,
  type WeaknessProfile,
  type CurriculumProfile
} from '@/infrastructure/api/clients/panel/user/exams/goals.api'

const { t } = useI18n()

// State
const goals = ref<ExamGoal[]>([])
const availableTypes = ref<any[]>([])
const weaknessProfiles = reactive<Record<string, WeaknessProfile>>({})
const curriculumProfiles = reactive<Record<string, CurriculumProfile>>({})
const loadingGoals = ref(false)
const loadingTypes = ref(false)
const error = ref<string | null>(null)
const showAddDialog = ref(false)
const selectedNewType = ref<string | null>(null)
const newTargetDate = ref('')

// Status badge classes
function statusClasses(status: string): string {
  switch (status) {
    case 'active':
      return 'bg-green-100 text-green-700'
    case 'passed':
      return 'bg-emerald-100 text-emerald-700'
    case 'paused':
      return 'bg-yellow-100 text-yellow-700'
    case 'planned':
      return 'bg-blue-100 text-blue-700'
    default:
      return 'bg-gray-100 text-gray-700'
  }
}

function scoreColor(score: number): string {
  if (score >= 75) return 'var(--color-success)'
  if (score >= 50) return 'var(--color-warning)'
  return 'var(--color-danger)'
}

function trendIcon(trend: string): string {
  switch (trend) {
    case 'improving': return '\u2191'
    case 'declining': return '\u2193'
    default: return '\u2192'
  }
}

function trendClasses(trend: string): string {
  switch (trend) {
    case 'improving': return 'text-green-600'
    case 'declining': return 'text-red-600'
    default: return 'text-gray-500'
  }
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString()
  } catch {
    return dateStr
  }
}

async function loadGoals(): Promise<void> {
  loadingGoals.value = true
  error.value = null
  try {
    goals.value = await fetchExamGoals()
    for (const goal of goals.value) {
      if (goal.status === 'active') {
        await loadWeaknessProfile(goal.exam_type)
        await loadCurriculumProfile(goal.exam_type)
      }
    }
  } catch (err: any) {
    console.error('Failed to load exam goals:', err)
    error.value = err.response?.data?.message || 'Failed to load goals'
  } finally {
    loadingGoals.value = false
  }
}

async function loadWeaknessProfile(examType: string): Promise<void> {
  try {
    weaknessProfiles[examType] = await fetchWeaknessProfile(examType)
  } catch (err: any) {
    console.error(`Failed to load weakness profile for ${examType}:`, err)
  }
}

async function loadCurriculumProfile(examType: string): Promise<void> {
  try {
    curriculumProfiles[examType] = await fetchCurriculumProfile(examType)
  } catch {
    // No curriculum framework linked — this is expected for some exam types
  }
}

async function loadAvailableTypes(): Promise<void> {
  loadingTypes.value = true
  try {
    availableTypes.value = await fetchAvailableTypes()
  } catch (err: any) {
    console.error('Failed to load available types:', err)
  } finally {
    loadingTypes.value = false
  }
}

async function handleAddGoal(): Promise<void> {
  if (!selectedNewType.value) return
  try {
    const payload: { exam_type: string; target_date?: string } = {
      exam_type: selectedNewType.value
    }
    if (newTargetDate.value) {
      payload.target_date = newTargetDate.value
    }
    await createExamGoal(payload)
    showAddDialog.value = false
    selectedNewType.value = null
    newTargetDate.value = ''
    await loadGoals()
  } catch (err: any) {
    console.error('Failed to add goal:', err)
    error.value = err.response?.data?.message || 'Failed to add goal'
  }
}

async function handleStatusChange(goalId: string, status: string): Promise<void> {
  try {
    await updateExamGoalStatus(goalId, status)
    await loadGoals()
  } catch (err: any) {
    console.error('Failed to update status:', err)
    error.value = err.response?.data?.message || 'Failed to update status'
  }
}

async function handleRemoveGoal(goalId: string): Promise<void> {
  if (!confirm(t('panel.examGoals.confirmRemove'))) return
  try {
    await deleteExamGoal(goalId)
    await loadGoals()
  } catch (err: any) {
    console.error('Failed to remove goal:', err)
    error.value = err.response?.data?.message || 'Failed to remove goal'
  }
}

onMounted(async () => {
  await loadGoals()
  await loadAvailableTypes()
})
</script>
