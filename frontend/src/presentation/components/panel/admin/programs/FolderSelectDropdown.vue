<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { fetchSidebarTree } from '@/infrastructure/api/clients/panel/admin/exams/folders.api'
import type { ArchiveFolder } from '@/infrastructure/api/clients/panel/admin/exams/folders.api'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  modelValue: string | null
  programId: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string | null]
}>()

const { t } = useI18n()

interface FlatFolder {
  folder_id: string
  label: string
}

const folders = ref<FlatFolder[]>([])

function flattenTree(nodes: ArchiveFolder[], depth = 0): FlatFolder[] {
  const result: FlatFolder[] = []
  for (const node of nodes) {
    result.push({ folder_id: node.folder_id, label: '\u00a0\u00a0'.repeat(depth) + node.name })
    if (node.children?.length) {
      result.push(...flattenTree(node.children, depth + 1))
    }
  }
  return result
}

const loadFolders = async () => {
  try {
    const { data } = await fetchSidebarTree(String(props.programId))
    folders.value = flattenTree(data.tree || [])
  } catch {
    folders.value = []
  }
}

onMounted(loadFolders)
watch(() => props.programId, loadFolders)

const onChange = (e: Event) => {
  const val = (e.target as HTMLSelectElement).value
  emit('update:modelValue', val || null)
}
</script>

<template>
  <select
    :value="modelValue ?? ''"
    class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-background)] text-[var(--color-text)] text-sm"
    @change="onChange"
  >
    <option value="">— {{ t('panel.programs.admin.examTypes.noFolder') }} —</option>
    <option v-for="f in folders" :key="f.folder_id" :value="f.folder_id">{{ f.label }}</option>
  </select>
</template>
