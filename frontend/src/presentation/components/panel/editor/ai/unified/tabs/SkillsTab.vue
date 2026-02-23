<script setup lang="ts">
/**
 * SkillsTab — Skills catalog + execution flow
 */
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSkillExecution } from '../composables'
import { SkillCatalogPanel, SkillExecutionPanel } from '../panels'
import type { SkillConfig } from '../types'

interface Props {
  courseId: string
}

const props = defineProps<Props>()
const { t } = useI18n()

const skills = useSkillExecution()

onMounted(() => {
  skills.loadCatalog()
})

function handleSelectSkill(skill: SkillConfig) {
  skills.selectSkill(skill)
}

function handleExecute(params: Record<string, unknown>) {
  skills.execute(props.courseId, {
    parameters: params.parameters as Record<string, unknown>,
    promptOverride: params.promptOverride as string | undefined,
  })
}
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Skill Execution (when a skill is selected) -->
    <SkillExecutionPanel
      v-if="skills.selectedSkill.value"
      :skill="skills.selectedSkill.value"
      :course-id="courseId"
      :is-executing="skills.isExecuting.value"
      :result="skills.currentResult.value"
      :error="skills.error.value"
      @execute="handleExecute"
      @accept="skills.acceptResult"
      @reject="skills.rejectResult"
      @back="skills.clearSelection"
    />

    <!-- Skill Catalog (when no skill selected) -->
    <SkillCatalogPanel
      v-else
      :skills="skills.skills.value"
      :selected-skill-code="null"
      :is-loading="skills.isLoadingCatalog.value"
      @select-skill="handleSelectSkill"
    />
  </div>
</template>
