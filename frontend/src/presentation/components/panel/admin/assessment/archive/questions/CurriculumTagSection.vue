<!--
  CurriculumTagSection - Shows and manages curriculum objective tags for a question.
  Used inline within QuestionEditor.
-->

<template>
  <div class="space-y-2">
    <label class="block text-xs font-medium text-[var(--color-text-secondary)]">
      {{ t('panel.curriculum.tags.label') }}
    </label>

    <!-- Loading state -->
    <div v-if="loading" class="text-xs text-[var(--color-text-secondary)] italic" aria-live="polite">
      {{ t('common.loading') }}
    </div>

    <!-- Tags list -->
    <div v-else class="flex flex-wrap gap-1.5">
      <span
        v-for="tag in tags"
        :key="tag.objective_id"
        class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
      >
        {{ tag.code || `#${tag.objective_id}` }}
        <span v-if="tag.confidence < 1" class="text-[10px] opacity-60">
          ({{ Math.round(tag.confidence * 100) }}%)
        </span>
        <button
          @click="handleRemove(tag.objective_id)"
          class="hover:text-red-600 transition-colors"
          :aria-label="t('panel.curriculum.tags.remove')"
        >
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </span>

      <span
        v-if="tags.length === 0"
        class="text-xs text-[var(--color-text-secondary)] italic"
      >
        {{ t('panel.curriculum.tags.none') }}
      </span>
    </div>

    <!-- Add tag (simple objective ID input) -->
    <div class="flex items-center gap-2">
      <input
        v-model.number="newObjectiveId"
        type="number"
        min="1"
        class="w-32 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm px-2 py-1"
        :placeholder="t('panel.curriculum.tags.objectiveId')"
      />
      <button
        @click="handleAdd"
        :disabled="!newObjectiveId"
        class="px-2 py-1 text-xs rounded bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50 transition-colors"
      >
        {{ t('panel.curriculum.tags.add') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  fetchQuestionTags,
  addQuestionTag,
  removeQuestionTag,
  type CurriculumTag,
} from '@/infrastructure/api/clients/panel/admin/exams/curriculum.api'

const { t } = useI18n()

interface Props {
  questionId: string
}

interface TagDisplay extends CurriculumTag {
  code?: string
}

const props = defineProps<Props>()

const tags = ref<TagDisplay[]>([])
const loading = ref(false)
const newObjectiveId = ref<number | null>(null)

onMounted(loadTags)

async function loadTags() {
  loading.value = true
  try {
    tags.value = await fetchQuestionTags(props.questionId)
  } catch {
    tags.value = []
  } finally {
    loading.value = false
  }
}

async function handleAdd() {
  if (!newObjectiveId.value) return
  try {
    const tag = await addQuestionTag(props.questionId, newObjectiveId.value)
    tags.value.push(tag)
    newObjectiveId.value = null
  } catch {
    // Error handled silently — tag not added
  }
}

async function handleRemove(objectiveId: number) {
  try {
    await removeQuestionTag(props.questionId, objectiveId)
    tags.value = tags.value.filter((t) => t.objective_id !== objectiveId)
  } catch {
    // Error handled silently
  }
}
</script>
