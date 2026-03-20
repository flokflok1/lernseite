<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  getUserPrograms, getAvailablePrograms, enrollInProgram,
  type UserProgram,
} from '@/infrastructure/api/clients/panel/user/programs.api'

const router = useRouter()
const { t, locale } = useI18n()
const enrolled = ref<UserProgram[]>([])
const available = ref<UserProgram[]>([])
const isLoading = ref(true)

const displayName = (obj: Record<string, string>) =>
  obj[locale.value] || obj.de || ''

onMounted(async () => {
  enrolled.value = await getUserPrograms()
  if (enrolled.value.length === 1) {
    router.replace(`/programs/${enrolled.value[0].program_id}`)
    return
  }
  if (enrolled.value.length === 0) {
    available.value = await getAvailablePrograms()
  }
  isLoading.value = false
})

const handleEnroll = async (prog: UserProgram) => {
  await enrollInProgram(prog.program_id)
  enrolled.value = await getUserPrograms()
  if (enrolled.value.length === 1) {
    router.replace(`/programs/${enrolled.value[0].program_id}`)
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto p-6">
    <div v-if="isLoading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>

    <!-- Enrolled programs -->
    <template v-else-if="enrolled.length > 0">
      <h1 class="text-2xl font-bold text-[var(--color-text)] mb-6">
        {{ t('panel.programs.nav.myProgram') }}
      </h1>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <router-link
          v-for="prog in enrolled"
          :key="prog.program_id"
          :to="`/programs/${prog.program_id}`"
          class="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]
                 hover:shadow-lg hover:border-blue-500/50 transition-all"
        >
          <div class="flex items-center gap-3 mb-3">
            <span v-if="prog.icon" class="text-2xl">{{ prog.icon }}</span>
            <h3 class="text-lg font-semibold text-[var(--color-text)]">
              {{ displayName(prog.display_name) }}
            </h3>
          </div>
          <div class="text-sm text-[var(--color-text-secondary)] space-y-1">
            <p>{{ t('panel.programs.catalog.questions', { count: prog.total_questions }) }}</p>
            <p>{{ t('panel.programs.catalog.exams', { count: prog.exam_count }) }}</p>
          </div>
          <div class="mt-4 h-2 bg-[var(--color-background)] rounded-full overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full"
              :style="{ width: (prog.total_questions > 0 ? Math.round(prog.mastered_questions / prog.total_questions * 100) : 0) + '%' }"
            />
          </div>
        </router-link>
      </div>
    </template>

    <!-- Catalog (no enrollments) -->
    <template v-else>
      <h1 class="text-2xl font-bold text-[var(--color-text)] mb-2">
        {{ t('panel.programs.catalog.title') }}
      </h1>
      <p class="text-[var(--color-text-secondary)] mb-6">
        {{ t('panel.programs.catalog.search') }}
      </p>
      <div v-if="available.length === 0" class="text-center py-12 text-[var(--color-text-secondary)]">
        {{ t('panel.programs.catalog.noPrograms') }}
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="prog in available"
          :key="prog.program_id"
          class="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]"
        >
          <div class="flex items-center gap-3 mb-3">
            <span v-if="prog.icon" class="text-2xl">{{ prog.icon }}</span>
            <h3 class="text-lg font-semibold text-[var(--color-text)]">
              {{ displayName(prog.display_name) }}
            </h3>
          </div>
          <button
            class="mt-4 px-4 py-2 text-sm rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors"
            @click="handleEnroll(prog)"
          >
            {{ t('panel.programs.catalog.enroll') }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>
