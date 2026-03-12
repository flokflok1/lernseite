<template>
  <div class="curriculum-tree">
    <div v-if="!tree" class="text-gray-500 italic py-4">
      {{ $t('panel.curriculum.tree.noFramework') }}
    </div>

    <div v-else>
      <h3 class="text-lg font-semibold mb-4">
        {{ tree.name }}
        <span class="text-sm text-gray-500 ml-2">
          ({{ tree.framework_type }})
        </span>
      </h3>

      <div
        v-for="section in tree.sections"
        :key="section.section_id"
        class="mb-4"
      >
        <div
          class="flex items-center gap-2 p-2 bg-gray-100 dark:bg-gray-800 rounded cursor-pointer"
          @click="toggleSection(section.section_id)"
        >
          <span class="text-sm font-mono text-gray-500">
            {{ section.section_number }}
          </span>
          <span class="font-medium">{{ section.title }}</span>
          <span class="ml-auto text-xs text-gray-400">
            {{ section.positions?.length || 0 }}
            {{ $t('panel.curriculum.tree.positions') }}
          </span>
        </div>

        <div
          v-if="expandedSections.has(section.section_id)"
          class="ml-6 mt-2 space-y-2"
        >
          <div
            v-for="position in section.positions"
            :key="position.position_id"
            class="border-l-2 border-blue-300 pl-3"
          >
            <div
              class="flex items-center gap-2 cursor-pointer"
              @click="togglePosition(position.position_id)"
            >
              <span class="text-sm font-mono text-blue-600">
                {{ position.position_number }}
              </span>
              <span class="text-sm">{{ position.title }}</span>
              <span class="ml-auto text-xs text-gray-400">
                {{ position.objectives?.length || 0 }}
                {{ $t('panel.curriculum.tree.objectives') }}
              </span>
            </div>

            <div
              v-if="expandedPositions.has(position.position_id)"
              class="ml-4 mt-1 space-y-1"
            >
              <div
                v-for="obj in position.objectives"
                :key="obj.objective_id"
                class="flex items-start gap-2 text-sm py-1"
              >
                <span class="font-mono text-gray-400 shrink-0">
                  {{ obj.code }}
                </span>
                <span class="text-gray-700 dark:text-gray-300">
                  {{ obj.description_text }}
                </span>
                <span
                  v-if="obj.bloom_level"
                  class="shrink-0 px-1.5 py-0.5 rounded text-xs bg-purple-100 text-purple-700"
                >
                  {{ obj.bloom_level }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { CurriculumTree } from '@/infrastructure/api/clients/panel/admin/exams/curriculum.api'

interface Props {
  tree: CurriculumTree | null
}

defineProps<Props>()

const expandedSections = ref<Set<number>>(new Set())
const expandedPositions = ref<Set<number>>(new Set())

function toggleSection(id: number) {
  if (expandedSections.value.has(id)) {
    expandedSections.value.delete(id)
  } else {
    expandedSections.value.add(id)
  }
}

function togglePosition(id: number) {
  if (expandedPositions.value.has(id)) {
    expandedPositions.value.delete(id)
  } else {
    expandedPositions.value.add(id)
  }
}
</script>
