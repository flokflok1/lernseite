<!--
  CreateSessionDialog - Create a new exam session (folder) in the archive.
  Selects program → exam type → year + season, then calls archiveCreateSession().
-->

<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="$emit('close')"
  >
    <div class="bg-[var(--color-surface)] rounded-xl shadow-xl w-full max-w-md mx-4 p-6">
      <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
        {{ t('panel.examArchive.crud.createFolder') }}
      </h3>

      <!-- Program Select -->
      <div class="space-y-3 mb-4">
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ t('panel.examArchive.crud.selectProgram') }}
          </label>
          <select
            v-model="selectedProgramKey"
            class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm text-[var(--color-text-primary)]"
          >
            <option value="" disabled>—</option>
            <option v-for="p in programs" :key="p.program_key" :value="p.program_key">
              {{ p.provider ? `${p.provider} ` : '' }}{{ p.display_name?.[locale] || p.display_name?.de || p.program_key }}
            </option>
          </select>
        </div>

        <!-- Exam Type Select (filtered by selected program) -->
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ t('panel.examArchive.crud.selectExamType') }}
          </label>
          <select
            v-model="form.exam_type_key"
            :disabled="!selectedProgramKey"
            class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm text-[var(--color-text-primary)] disabled:opacity-50"
          >
            <option value="" disabled>—</option>
            <option v-for="et in filteredTypes" :key="et.exam_type" :value="et.exam_type">
              {{ et.display_name?.[locale] || et.display_name?.de || et.exam_type }}
            </option>
          </select>
        </div>

        <!-- Year + Season -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              {{ t('panel.examArchive.crud.year') }}
            </label>
            <input
              v-model.number="form.year"
              type="number"
              min="2015"
              max="2035"
              class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm text-[var(--color-text-primary)]"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              {{ t('panel.examArchive.crud.season') }}
            </label>
            <select
              v-model="form.season"
              class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm text-[var(--color-text-primary)]"
            >
              <option value="sommer">{{ t('panel.examArchive.session.season.sommer') }}</option>
              <option value="winter">{{ t('panel.examArchive.session.season.winter') }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Error -->
      <div
        v-if="error"
        class="mb-3 p-2 rounded text-sm border"
        style="background-color: var(--color-error-bg, #fee2e2); border-color: var(--color-error-border, #fecaca); color: var(--color-error-text, #dc2626);"
      >
        {{ error }}
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-2">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-sm border border-[var(--color-border)] rounded text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)]"
        >
          {{ t('panel.examArchive.crud.cancel') }}
        </button>
        <button
          @click="handleCreate"
          :disabled="!canSubmit || submitting"
          class="px-4 py-2 text-sm text-white rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          style="background-color: var(--color-primary, #7c3aed);"
        >
          {{ submitting ? '...' : t('panel.examArchive.crud.create') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchPrograms, type ExamProgram } from '@/infrastructure/api/clients/panel/admin/exams/intelligence.api'
import { archiveCreateSession } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

interface Props {
  visible: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  created: [sessionId: string]
}>()

const { t, locale } = useI18n()

const programs = ref<ExamProgram[]>([])
const selectedProgramKey = ref('')
const submitting = ref(false)
const error = ref('')

const form = ref({
  exam_type_key: '',
  season: 'sommer',
  year: new Date().getFullYear(),
})

const filteredTypes = computed(() => {
  const prog = programs.value.find(p => p.program_key === selectedProgramKey.value)
  return prog?.parts || []
})

// Reset exam type when program changes
watch(selectedProgramKey, () => {
  form.value.exam_type_key = ''
})

// Reset form when dialog opens
watch(() => props.visible, (val) => {
  if (val) {
    error.value = ''
    submitting.value = false
  }
})

const canSubmit = computed(() =>
  form.value.exam_type_key && form.value.year && form.value.season
)

onMounted(async () => {
  try {
    programs.value = await fetchPrograms()
  } catch {
    // dropdown stays empty
  }
})

const handleCreate = async () => {
  if (!canSubmit.value) return
  submitting.value = true
  error.value = ''

  try {
    const result = await archiveCreateSession(
      form.value.exam_type_key,
      form.value.year,
      form.value.season
    )
    emit('created', result.session_id)
    emit('close')
  } catch (err: any) {
    error.value = err?.response?.data?.error || t('panel.examArchive.crud.createError')
  } finally {
    submitting.value = false
  }
}
</script>
