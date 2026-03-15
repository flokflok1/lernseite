<script setup lang="ts">
import { useI18n } from 'vue-i18n'

interface BreadcrumbItem {
  folder_id: string
  name: string
  icon: string | null
  program_id: number
}

interface Props {
  breadcrumb: BreadcrumbItem[]
  programName?: string
  viewMode: 'grid' | 'list'
}

defineProps<Props>()

const emit = defineEmits<{
  navigate: [folderId: string | null]
  toggleView: []
}>()

const { t } = useI18n()
</script>

<template>
  <div class="flex items-center gap-2 px-5 py-2.5 border-b border-gray-700/50 min-h-[44px]">
    <!-- Breadcrumb path -->
    <nav class="flex items-center gap-1 text-sm flex-1 overflow-hidden">
      <button
        class="text-indigo-400 hover:bg-gray-700/50 px-1 py-0.5 rounded shrink-0"
        @click="emit('navigate', null)"
      >
        {{ t('panel.examArchive.title') }}
      </button>

      <template v-if="programName">
        <span class="text-gray-500 text-[11px] shrink-0">/</span>
        <button
          class="text-indigo-400 hover:bg-gray-700/50 px-1 py-0.5 rounded shrink-0"
          @click="emit('navigate', null)"
        >
          {{ programName }}
        </button>
      </template>

      <template v-for="(item, idx) in breadcrumb" :key="item.folder_id">
        <span class="text-gray-500 text-[11px] shrink-0">/</span>
        <button
          v-if="idx < breadcrumb.length - 1"
          class="text-indigo-400 hover:bg-gray-700/50 px-1 py-0.5 rounded truncate max-w-[150px]"
          @click="emit('navigate', item.folder_id)"
        >
          {{ item.name }}
        </button>
        <span
          v-else
          class="text-white font-semibold truncate max-w-[200px]"
        >
          {{ item.name }}
        </span>
      </template>
    </nav>

    <!-- View toggle -->
    <div class="flex gap-0.5 bg-gray-800 rounded-md p-0.5 shrink-0">
      <button
        class="px-2 py-1 rounded text-xs transition-colors"
        :class="viewMode === 'grid'
          ? 'bg-gray-700 text-white'
          : 'text-gray-400 hover:text-white'"
        @click="emit('toggleView')"
      >
        ▦ {{ t('panel.examArchive.grid') }}
      </button>
      <button
        class="px-2 py-1 rounded text-xs transition-colors"
        :class="viewMode === 'list'
          ? 'bg-gray-700 text-white'
          : 'text-gray-400 hover:text-white'"
        @click="emit('toggleView')"
      >
        ☰ {{ t('panel.examArchive.list') }}
      </button>
    </div>
  </div>
</template>
