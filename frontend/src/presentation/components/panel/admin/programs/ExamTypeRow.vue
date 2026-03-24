<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExamType } from '@/infrastructure/api/clients/panel/admin/programs.api'

const props = defineProps<{ examType: ExamType }>()
const emit = defineEmits<{
  edit: [examType: ExamType]
  delete: [examType: ExamType]
}>()

const { t, locale } = useI18n()
const dn = (obj: Record<string, string>) => obj[locale.value] || obj.de || Object.values(obj)[0] || ''
</script>

<template>
  <tr class="border-b border-[var(--color-border)] text-sm hover:bg-[var(--color-background)] transition-colors">
    <td class="px-3 py-2 font-mono text-xs text-[var(--color-text-secondary)]">{{ examType.exam_type }}</td>
    <td class="px-3 py-2 text-[var(--color-text)]">{{ dn(examType.display_name) }}</td>
    <td class="px-3 py-2 text-[var(--color-text-secondary)] text-center">{{ examType.passing_score }}%</td>
    <td class="px-3 py-2 text-[var(--color-text-secondary)] text-xs">
      {{ (examType.applies_to || []).join(', ') || '—' }}
    </td>
    <td class="px-3 py-2 text-[var(--color-text-secondary)] text-xs">
      <span v-if="examType.exam_count">
        {{ t('panel.programs.admin.examTypes.stats.exams', { count: examType.exam_count }) }}
      </span>
      <span v-else class="opacity-40">—</span>
    </td>
    <td class="px-3 py-2 text-right space-x-3">
      <button class="text-primary-600 hover:text-primary-800 text-xs" @click="emit('edit', examType)">
        {{ t('panel.programs.admin.examTypes.edit') }}
      </button>
      <button class="text-red-600 hover:text-red-800 text-xs" @click="emit('delete', examType)">
        {{ t('panel.programs.admin.examTypes.delete') }}
      </button>
    </td>
  </tr>
</template>
