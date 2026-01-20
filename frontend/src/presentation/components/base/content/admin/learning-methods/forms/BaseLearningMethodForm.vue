<!--
  Base Learning Method Form Component

  Basis-Komponente für alle 32 Lernmethoden-Formulare.
  Wird von den spezifischen Formularen (LearningMethod00Form.vue etc.) erweitert.
-->

<template>
  <div class="learning-method-form h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-4 py-3">
      <div class="flex items-center gap-3">
        <span class="text-3xl">{{ method?.icon }}</span>
        <div>
          <h2 class="text-lg font-bold text-[var(--color-text-primary)]">
            {{ method?.name }}
          </h2>
          <p class="text-sm text-[var(--color-text-secondary)]">
            {{ method?.description }}
          </p>
        </div>
      </div>
    </div>

    <!-- Scroll Content -->
    <div class="flex-1 overflow-y-auto p-6">
      <div class="space-y-6 max-w-2xl">
        <!-- Standard-Felder (alle Methoden haben diese) -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('admin.learningMethods.form.titleLabel') }}
          </label>
          <input
            v-model="form.title"
            type="text"
            :placeholder="$t('admin.learningMethods.form.titlePlaceholder')"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('admin.learningMethods.form.instructionsLabel') }}
          </label>
          <textarea
            v-model="form.instructions"
            rows="3"
            :placeholder="$t('admin.learningMethods.form.instructionsPlaceholder')"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
        </div>

        <!-- Slot für methoden-spezifische Felder -->
        <slot name="method-fields" :form="form"></slot>

        <!-- Dauer & Schwierigkeit -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ $t('admin.learningMethods.form.durationLabel') }}
            </label>
            <input
              v-model.number="form.duration_minutes"
              type="number"
              min="1"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ $t('admin.learningMethods.form.difficultyLabel') }}
            </label>
            <select
              v-model="form.difficulty"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            >
              <option value="easy">{{ $t('admin.learningMethods.form.difficultyEasy') }}</option>
              <option value="medium">{{ $t('admin.learningMethods.form.difficultyMedium') }}</option>
              <option value="hard">{{ $t('admin.learningMethods.form.difficultyHard') }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Actions -->
    <div class="bg-[var(--color-surface)] border-t border-[var(--color-border)] px-4 py-3">
      <div class="flex gap-3 justify-end">
        <button
          @click="close"
          class="px-4 py-2 border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] hover:bg-[var(--color-background)] transition-colors"
        >
          {{ $t('admin.learningMethods.form.cancelButton') }}
        </button>
        <button
          @click="save"
          :disabled="isSaving || !form.title"
          class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 transition-colors"
        >
          {{ isSaving ? $t('admin.learningMethods.form.savingButton') : (isEditMode ? $t('admin.learningMethods.form.updateButton') : $t('admin.learningMethods.form.createButton')) }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/application/stores/modules/desktop'
import type { LsxPanel } from '@/application/stores/modules/desktop'
import { getLearningMethodByCode, getTierFromCode } from '@/config/learningMethods'
import {
  adminCreateLearningMethod,
  adminUpdateLearningMethod
} from '@/infrastructure/api/clients/admin'

interface Props {
  panel: LsxPanel
  methodCode: number
  additionalData?: Record<string, any>
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
}>()

const panelStore = usePanelStore()

const method = computed(() => getLearningMethodByCode(props.methodCode))
const chapterId = computed(() => props.panel.payload?.chapterId as string)
const instanceId = computed(() => props.panel.payload?.instanceId as string | undefined)
const instanceData = computed(() => props.panel.payload?.instanceData as any)
const isEditMode = computed(() => !!instanceId.value)
const isSaving = ref(false)

// Basis-Formular
const form = ref({
  title: '',
  instructions: '',
  duration_minutes: 15,
  difficulty: 'medium' as 'easy' | 'medium' | 'hard',
  data: {} as Record<string, any>
})

// Exponiere form für Child-Komponenten
defineExpose({ form })

// Lade Daten im Edit-Mode
onMounted(() => {
  if (instanceData.value) {
    form.value.title = instanceData.value.title || ''
    form.value.instructions = instanceData.value.instructions || ''
    form.value.duration_minutes = instanceData.value.duration_minutes || 15
    form.value.difficulty = instanceData.value.difficulty || 'medium'
    form.value.data = instanceData.value.data || {}
  }
})

// Watch für zusätzliche Daten von Child-Komponenten
watch(() => props.additionalData, (newData) => {
  if (newData) {
    form.value.data = { ...form.value.data, ...newData }
  }
}, { deep: true })

const { t } = useI18n()

const save = async () => {
  if (!form.value.title.trim()) {
    alert(t('admin.learningMethods.form.emptyTitleError'))
    return
  }

  if (!chapterId.value) {
    alert(t('admin.learningMethods.form.noChapterIdError'))
    return
  }

  isSaving.value = true

  try {
    const data = {
      method_type: props.methodCode,
      title: form.value.title.trim(),
      instructions: form.value.instructions || undefined,
      duration_minutes: form.value.duration_minutes,
      difficulty: form.value.difficulty,
      tier: getTierFromCode(props.methodCode),
      data: { ...form.value.data, ...props.additionalData }
    }

    if (isEditMode.value && instanceId.value) {
      await adminUpdateLearningMethod(instanceId.value, data)
    } else {
      await adminCreateLearningMethod(chapterId.value, data)
    }

    // Event für Refresh
    window.dispatchEvent(new CustomEvent('learning-method-updated'))
    close()
  } catch (error: any) {
    console.error('Fehler beim Speichern:', error)
    alert(error.response?.data?.message || t('admin.learningMethods.form.saveErrorMessage'))
  } finally {
    isSaving.value = false
  }
}

const close = () => {
  panelStore.closePanel(props.panel.id)
}
</script>
