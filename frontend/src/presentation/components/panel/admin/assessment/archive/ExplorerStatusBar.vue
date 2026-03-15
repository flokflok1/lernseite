<script setup lang="ts">
import { useI18n } from 'vue-i18n'

interface Props {
  folderCount: number
  examCount: number
  questionCount: number
}

defineProps<Props>()

const { t } = useI18n()
</script>

<template>
  <div class="flex items-center gap-4 px-5 py-1.5 border-t border-gray-700/50 bg-gray-900/60 text-[11px] text-gray-400">
    <span class="flex items-center gap-1.5">
      <span class="w-1.5 h-1.5 rounded-full bg-green-500" />
      {{ t('panel.examArchive.status.connected') }}
    </span>
    <span>
      {{ t('panel.examArchive.stats', { folders: folderCount, exams: examCount, questions: questionCount }) }}
    </span>
  </div>
</template>
