<!--
  ExamUploadDialog - Community PDF upload with metadata form.
  Drag & drop or click to select PDF, fill exam metadata, submit for moderation.
-->

<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="$emit('close')"
  >
    <div class="bg-[var(--color-surface)] rounded-xl shadow-xl w-full max-w-lg mx-4 p-6">
      <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
        {{ t('panel.examArchive.upload.title') }}
      </h3>

      <!-- Drop Zone -->
      <div
        class="border-2 border-dashed rounded-lg p-6 text-center mb-4 transition-colors cursor-pointer"
        :class="dragOver
          ? 'border-[var(--color-primary)] bg-[var(--color-primary-bg,#ede9fe)]'
          : 'border-[var(--color-border)] hover:border-[var(--color-primary)]'"
        @dragover.prevent="dragOver = true"
        @dragleave="dragOver = false"
        @drop.prevent="handleDrop"
        @click="fileInput?.click()"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".pdf"
          class="hidden"
          @change="handleFileSelect"
        />
        <p v-if="!selectedFile" class="text-sm text-[var(--color-text-secondary)]">
          {{ t('panel.examArchive.upload.dropzone') }}
        </p>
        <p v-else class="text-sm text-[var(--color-text-primary)] font-medium">
          {{ selectedFile.name }}
          <span class="text-[var(--color-text-secondary)] ml-2">
            ({{ (selectedFile.size / 1024 / 1024).toFixed(1) }} MB)
          </span>
        </p>
      </div>

      <!-- Metadata Form -->
      <div class="space-y-3 mb-4">
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ t('panel.examArchive.part') }} ({{ t('panel.examArchive.upload.pdfOnly') }})
          </label>
          <select
            v-model="form.exam_type_key"
            class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm text-[var(--color-text-primary)]"
          >
            <option value="IHK_FISI">IHK FISI</option>
            <option value="IHK_FIAE">IHK FIAE</option>
            <option value="CompTIA_A+">CompTIA A+</option>
            <option value="CompTIA_Net+">CompTIA Network+</option>
            <option value="AWS_SAA">AWS SAA</option>
          </select>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              {{ t('panel.examArchive.semester') }}
            </label>
            <select
              v-model="form.season"
              class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm text-[var(--color-text-primary)]"
            >
              <option value="sommer">{{ t('panel.examArchive.session.season.sommer') }}</option>
              <option value="winter">{{ t('panel.examArchive.session.season.winter') }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              {{ t('panel.examArchive.semester') }} (Jahr)
            </label>
            <input
              v-model.number="form.year"
              type="number"
              min="2015"
              max="2030"
              class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm text-[var(--color-text-primary)]"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              Teil (optional)
            </label>
            <select
              v-model="form.part"
              class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm text-[var(--color-text-primary)]"
            >
              <option value="">—</option>
              <option value="GA1">GA1</option>
              <option value="GA2">GA2</option>
              <option value="WK">WK</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              Region (optional)
            </label>
            <select
              v-model="form.region"
              class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm text-[var(--color-text-primary)]"
            >
              <option value="alle">Alle</option>
              <option value="bw">Baden-Württemberg</option>
              <option value="bayern">Bayern</option>
              <option value="nrw">NRW</option>
              <option value="hessen">Hessen</option>
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
          {{ t('actions.delete') === 'Löschen' ? 'Abbrechen' : 'Cancel' }}
        </button>
        <button
          @click="handleSubmit"
          :disabled="!canSubmit || submitting"
          class="px-4 py-2 text-sm text-white rounded transition-colors"
          style="background-color: var(--color-primary, #7c3aed);"
          :class="{ 'opacity-50 cursor-not-allowed': !canSubmit || submitting }"
        >
          {{ submitting ? '...' : t('panel.examArchive.upload.submit') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { communityUploadExam } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

interface Props {
  visible: boolean
}

defineProps<Props>()
const emit = defineEmits<{
  close: []
  uploaded: [examId: string]
}>()

const { t } = useI18n()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const dragOver = ref(false)
const submitting = ref(false)
const error = ref('')

const form = ref({
  exam_type_key: 'IHK_FISI',
  season: 'sommer',
  year: new Date().getFullYear(),
  part: '',
  region: 'alle',
})

const canSubmit = computed(() =>
  selectedFile.value && form.value.exam_type_key && form.value.year && form.value.season
)

const handleDrop = (e: DragEvent) => {
  dragOver.value = false
  const file = e.dataTransfer?.files[0]
  if (file?.name.toLowerCase().endsWith('.pdf')) {
    selectedFile.value = file
    error.value = ''
  } else {
    error.value = t('panel.examArchive.upload.pdfOnly')
  }
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) {
    selectedFile.value = input.files[0]
    error.value = ''
  }
}

const handleSubmit = async () => {
  if (!selectedFile.value || !canSubmit.value) return

  submitting.value = true
  error.value = ''

  try {
    const result = await communityUploadExam(selectedFile.value, {
      exam_type_key: form.value.exam_type_key,
      year: form.value.year,
      season: form.value.season,
      part: form.value.part || undefined,
      region: form.value.region,
    })
    emit('uploaded', result.exam_id)
    emit('close')
  } catch (err: any) {
    const msg = err?.response?.data?.error || String(err)
    error.value = msg
  } finally {
    submitting.value = false
  }
}
</script>
