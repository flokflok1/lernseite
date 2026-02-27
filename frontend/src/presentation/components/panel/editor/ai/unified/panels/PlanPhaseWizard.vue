<script setup lang="ts">
/**
 * PlanPhaseWizard — Container for the 4-phase plan wizard.
 *
 * Renders the correct phase component + chat + navigation.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { WizardPhase, CourseMeta, ChapterDraft, PlanChatMessage, ContentPlan } from '../types'

import PlanCourseCard from './PlanCourseCard.vue'
import PlanChapterList from './PlanChapterList.vue'
import PlanModePanel from './PlanModePanel.vue'
import PlanChat from './PlanChat.vue'

interface Props {
  currentPhase: WizardPhase
  plan: ContentPlan | null
  courseMeta: CourseMeta | null
  chapters: ChapterDraft[]
  chatMessages: PlanChatMessage[]
  isCreating: boolean
  isExecuting: boolean
  isChatting: boolean
  hasFiles: boolean
  fileIds?: string[]
  isDraft: boolean
  isApproved: boolean
  totalSteps: number
  completedSteps: number
}

const props = defineProps<Props>()
const { t } = useI18n()

const emit = defineEmits<{
  generatePhase1: [topic?: string, fileIds?: string[]]
  confirmPhase: []
  goBack: [phase: WizardPhase]
  sendChat: [message: string]
  execute: []
  discard: []
  finalizePlan: []
}>()

const phaseLabels = computed(() => [
  { num: 1 as WizardPhase, label: t('aiEditor.planWizard.phase1Title') },
  { num: 2 as WizardPhase, label: t('aiEditor.planWizard.phase2Title') },
  { num: 3 as WizardPhase, label: t('aiEditor.planWizard.phase3Title') },
  { num: 4 as WizardPhase, label: t('aiEditor.planWizard.phase4Title') },
])

const canGoBack = computed(() => props.currentPhase > 1 && props.currentPhase < 4)

const canConfirm = computed(() => {
  if (props.isCreating || props.isChatting) return false
  if (props.currentPhase === 1) return !!props.courseMeta?.title
  if (props.currentPhase === 2) return props.chapters.length > 0
  if (props.currentPhase === 3) return !!props.plan?.phases?.length
  return false
})
</script>

<template>
  <div class="flex flex-col h-full min-h-0">
    <!-- Phase Indicator (fixed top) -->
    <div class="flex items-center justify-between px-2 pb-3 flex-shrink-0">
      <template v-for="(p, idx) in phaseLabels" :key="p.num">
        <div
          class="flex items-center gap-1.5 cursor-pointer select-none"
          :class="{
            'opacity-100': p.num === currentPhase,
            'opacity-70': p.num < currentPhase,
            'opacity-40 cursor-default': p.num > currentPhase,
          }"
          @click="p.num < currentPhase ? emit('goBack', p.num) : undefined"
        >
          <span
            class="flex items-center justify-center w-7 h-7 rounded-full text-xs font-semibold"
            :class="{
              'bg-blue-600 text-white': p.num === currentPhase,
              'bg-green-600 text-white': p.num < currentPhase,
              'bg-gray-700 text-gray-400': p.num > currentPhase,
            }"
          >
            <span v-if="p.num < currentPhase" aria-hidden="true">✓</span>
            <span v-else>{{ p.num }}</span>
          </span>
          <span class="text-xs text-gray-300">{{ p.label }}</span>
        </div>
        <div
          v-if="idx < phaseLabels.length - 1"
          class="flex-1 h-px mx-2"
          :class="p.num < currentPhase ? 'bg-green-600' : 'bg-gray-700'"
        />
      </template>
    </div>

    <!-- Phase Content (scrollable) -->
    <div class="flex-1 min-h-0 overflow-y-auto plan-scroll">
      <PlanCourseCard
        v-if="currentPhase === 1"
        :course-meta="courseMeta"
        :is-creating="isCreating"
        :has-files="hasFiles"
        :file-ids="fileIds"
        @generate="(topic, fIds) => emit('generatePhase1', topic, fIds)"
      />

      <PlanChapterList
        v-else-if="currentPhase === 2"
        :chapters="chapters"
        :is-creating="isCreating"
      />

      <PlanModePanel
        v-else-if="currentPhase >= 3"
        :plan="plan"
        :is-creating="isCreating"
        :is-draft="isDraft"
        :is-approved="isApproved"
        :is-executing="isExecuting"
        :total-steps="totalSteps"
        :completed-steps="completedSteps"
        @approve="emit('confirmPhase')"
        @save-plan="emit('confirmPhase')"
        @execute="emit('execute')"
        @discard="emit('discard')"
        @finalize-plan="emit('finalizePlan')"
      />
    </div>

    <!-- Chat (Phase 1-3, fixed bottom) -->
    <div v-if="currentPhase < 4 && plan" class="flex-shrink-0 pt-3">
      <PlanChat
        :messages="chatMessages"
        :is-loading="isChatting"
        :current-phase="currentPhase"
        @send="(msg) => emit('sendChat', msg)"
      />
    </div>

    <!-- Navigation (fixed bottom) -->
    <div v-if="currentPhase < 4" class="flex items-center gap-3 pt-3 border-t border-gray-700 flex-shrink-0">
      <button
        v-if="canGoBack"
        class="px-3 py-1.5 text-sm text-gray-300 hover:text-white rounded border border-gray-600 hover:border-gray-500 transition-colors"
        @click="emit('goBack', (currentPhase - 1) as WizardPhase)"
      >
        {{ t('aiEditor.planWizard.backPrev') }}
      </button>
      <div class="flex-1" />
      <button
        class="px-4 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-500 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        :disabled="!canConfirm"
        @click="emit('confirmPhase')"
      >
        {{ isCreating ? t('aiEditor.planWizard.generating') : t('aiEditor.planWizard.confirmNext') }}
      </button>
    </div>

    <!-- Phase 4: Execute Button (fixed bottom) -->
    <div v-if="currentPhase === 4 && isApproved && !isExecuting" class="flex justify-end pt-3 border-t border-gray-700 flex-shrink-0">
      <button
        class="px-4 py-1.5 text-sm font-medium text-white bg-green-600 hover:bg-green-500 rounded transition-colors"
        @click="emit('execute')"
      >
        {{ t('aiEditor.planWizard.execute') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.plan-scroll {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.08) transparent;
}
.plan-scroll:hover {
  scrollbar-color: rgba(255, 255, 255, 0.15) transparent;
}
.plan-scroll::-webkit-scrollbar {
  width: 4px;
}
.plan-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.plan-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
}
.plan-scroll:hover::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
}
</style>
