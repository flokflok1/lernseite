<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getUserPrograms, type UserProgram } from '@/infrastructure/api/clients/panel/user/programs.api'
import ProgramSubSidebar from '@/presentation/components/panel/user/programs/ProgramSubSidebar.vue'
import ProgramTabs from '@/presentation/components/panel/user/programs/ProgramTabs.vue'
import LearningPathTab from '@/presentation/components/panel/user/programs/tabs/LearningPathTab.vue'
import TrainerTab from '@/presentation/components/panel/user/programs/tabs/TrainerTab.vue'
import PrognosisTab from '@/presentation/components/panel/user/programs/tabs/PrognosisTab.vue'
import ProgressTab from '@/presentation/components/panel/user/programs/tabs/ProgressTab.vue'

const route = useRoute()
const router = useRouter()
const { locale } = useI18n()

const programs = ref<UserProgram[]>([])
const activeProgram = ref<UserProgram | null>(null)
const activeTab = ref('trainer')
const isLoading = ref(true)

const displayName = (obj: Record<string, string>) =>
  obj[locale.value] || obj.de || ''

onMounted(async () => {
  programs.value = await getUserPrograms()
  const programId = Number(route.params.programId)
  activeProgram.value = programs.value.find(p => p.program_id === programId) || programs.value[0] || null
  isLoading.value = false
})

const selectProgram = (prog: UserProgram) => {
  activeProgram.value = prog
  router.replace(`/programs/${prog.program_id}`)
}

watch(() => route.params.programId, (newId) => {
  if (newId) {
    const prog = programs.value.find(p => p.program_id === Number(newId))
    if (prog) activeProgram.value = prog
  }
})
</script>

<template>
  <div v-if="isLoading" class="flex justify-center py-12">
    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
  </div>
  <div v-else class="flex h-full">
    <!-- Left: Sub-Sidebar -->
    <ProgramSubSidebar
      :programs="programs"
      :active-id="activeProgram?.program_id ?? null"
      @select="selectProgram"
    />

    <!-- Right: Content -->
    <div class="flex-1 flex flex-col min-h-0">
      <!-- Program title -->
      <div class="px-6 pt-4 pb-2">
        <h1 class="text-xl font-bold text-[var(--color-text)]">
          {{ activeProgram ? displayName(activeProgram.display_name) : '' }}
        </h1>
      </div>

      <!-- Tabs -->
      <ProgramTabs :active-tab="activeTab" @change="activeTab = $event" />

      <!-- Tab content -->
      <div class="flex-1 overflow-y-auto">
        <LearningPathTab
          v-if="activeTab === 'learning'"
          :course-id="activeProgram?.course_id ?? null"
        />
        <TrainerTab v-else-if="activeTab === 'trainer'" />
        <PrognosisTab v-else-if="activeTab === 'prognosis'" />
        <ProgressTab v-else-if="activeTab === 'progress'" />
      </div>
    </div>
  </div>
</template>
