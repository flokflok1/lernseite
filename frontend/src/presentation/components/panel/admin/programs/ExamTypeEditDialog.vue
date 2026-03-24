<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import FolderSelectDropdown from './FolderSelectDropdown.vue'
import { createExamType, updateExamType } from '@/infrastructure/api/clients/panel/admin/programs.api'
import type { ExamType } from '@/infrastructure/api/clients/panel/admin/programs.api'

const props = defineProps<{
  programId: number
  examType: ExamType | null
}>()

const emit = defineEmits<{
  saved: []
  cancelled: []
}>()

const { t } = useI18n()

const emptyForm = () => ({
  exam_type: '',
  display_name: { de: '', en: '', pl: '' },
  passing_score: 50,
  applies_to: '',
  sort_order: 0,
  archive_folder_id: null as string | null,
})

const form = ref(emptyForm())
const saving = ref(false)
const error = ref<string | null>(null)

watch(() => props.examType, (et) => {
  if (et) {
    form.value = {
      exam_type: et.exam_type,
      display_name: { de: et.display_name.de ?? '', en: et.display_name.en ?? '', pl: et.display_name.pl ?? '' },
      passing_score: et.passing_score,
      applies_to: (et.applies_to || []).join(','),
      sort_order: et.sort_order,
      archive_folder_id: et.archive_folder_id,
    }
  } else {
    form.value = emptyForm()
  }
}, { immediate: true })

const inputCls = 'w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-background)] text-[var(--color-text)] text-sm'
const labelCls = 'block text-xs text-[var(--color-text-secondary)] mb-1'

const handleSave = async () => {
  saving.value = true
  error.value = null
  try {
    const payload: Record<string, unknown> = {
      display_name: form.value.display_name,
      passing_score: form.value.passing_score,
      applies_to: form.value.applies_to
        ? form.value.applies_to.split(',').map((s) => s.trim()).filter(Boolean)
        : [],
      sort_order: form.value.sort_order,
      archive_folder_id: form.value.archive_folder_id || null,
      program_id: props.programId,
    }
    if (props.examType) {
      await updateExamType(props.examType.exam_type, payload)
    } else {
      await createExamType({ ...payload, exam_type: form.value.exam_type })
    }
    emit('saved')
  } catch (e) {
    error.value = String(e)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="emit('cancelled')">
    <div class="bg-[var(--color-surface)] rounded-xl shadow-xl w-full max-w-lg mx-4 p-6 space-y-4">
      <h3 class="text-lg font-semibold text-[var(--color-text)]">
        {{ examType ? t('panel.programs.admin.examTypes.edit') : t('panel.programs.admin.examTypes.create') }}
      </h3>

      <div v-if="error" class="p-2 bg-red-100 text-red-800 rounded text-sm">{{ error }}</div>

      <div class="grid grid-cols-2 gap-3">
        <div v-if="!examType" class="col-span-2">
          <label :class="labelCls">{{ t('panel.programs.admin.examTypes.fields.examType') }}</label>
          <input v-model="form.exam_type" :class="inputCls" placeholder="z.B. FI_AP1" />
        </div>
        <div>
          <label :class="labelCls">{{ t('panel.programs.admin.examTypes.fields.displayName') }} (DE)</label>
          <input v-model="form.display_name.de" :class="inputCls" />
        </div>
        <div>
          <label :class="labelCls">{{ t('panel.programs.admin.examTypes.fields.displayName') }} (EN)</label>
          <input v-model="form.display_name.en" :class="inputCls" />
        </div>
        <div>
          <label :class="labelCls">{{ t('panel.programs.admin.examTypes.fields.displayName') }} (PL)</label>
          <input v-model="form.display_name.pl" :class="inputCls" />
        </div>
        <div>
          <label :class="labelCls">{{ t('panel.programs.admin.examTypes.fields.passingScore') }}</label>
          <input v-model.number="form.passing_score" :class="inputCls" type="number" min="0" max="100" />
        </div>
        <div>
          <label :class="labelCls">{{ t('panel.programs.admin.examTypes.fields.appliesTo') }}</label>
          <input v-model="form.applies_to" :class="inputCls" placeholder="FISI,FIAE" />
        </div>
        <div>
          <label :class="labelCls">{{ t('panel.programs.admin.examTypes.fields.sortOrder') }}</label>
          <input v-model.number="form.sort_order" :class="inputCls" type="number" />
        </div>
        <div class="col-span-2">
          <label :class="labelCls">{{ t('panel.programs.admin.examTypes.fields.archiveFolder') }}</label>
          <FolderSelectDropdown v-model="form.archive_folder_id" :program-id="programId" />
        </div>
      </div>

      <div class="flex gap-2 pt-2">
        <button
          class="px-4 py-2 bg-primary-600 text-white rounded text-sm hover:bg-primary-700 transition-colors disabled:opacity-50"
          :disabled="saving"
          @click="handleSave"
        >{{ saving ? t('common.loading') : t('actions.save') }}</button>
        <button
          class="px-4 py-2 border border-[var(--color-border)] rounded text-sm text-[var(--color-text-secondary)] hover:bg-[var(--color-background)] transition-colors"
          @click="emit('cancelled')"
        >{{ t('actions.cancel') }}</button>
      </div>
    </div>
  </div>
</template>
