<template>
  <BaseLearningMethodForm
    :panel="panel"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('features.lm08.whiteboardTitle') }}
          </label>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
            {{ $t('features.lm08.whiteboardDescription') }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('features.lm08.instructionLabel') }}
          </label>
          <textarea
            v-model="methodData.instruction"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            :placeholder="$t('features.lm08.instructionPlaceholder')"
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('features.lm08.taskTypeLabel') }}
          </label>
          <select
            v-model="methodData.task_type"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            required
          >
            <option value="">{{ $t('features.lm08.taskTypeDefault') }}</option>
            <option value="diagram">{{ $t('features.lm08.taskTypeDiagram') }}</option>
            <option value="flowchart">{{ $t('features.lm08.taskTypeFlowchart') }}</option>
            <option value="network">{{ $t('features.lm08.taskTypeNetwork') }}</option>
            <option value="uml">{{ $t('features.lm08.taskTypeUml') }}</option>
            <option value="mindmap">{{ $t('features.lm08.taskTypeMindmap') }}</option>
            <option value="architecture">{{ $t('features.lm08.taskTypeArchitecture') }}</option>
            <option value="freeform">{{ $t('features.lm08.taskTypeFreeform') }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('features.lm08.expectedElementsLabel') }}
          </label>
          <textarea
            v-model="methodData.expected_elements"
            rows="5"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            :placeholder="$t('features.lm08.expectedElementsPlaceholder')"
          ></textarea>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {{ $t('features.lm08.expectedElementsHint') }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('features.lm08.evaluationCriteriaLabel') }}
          </label>
          <div class="space-y-2">
            <label class="flex items-center space-x-2">
              <input
                v-model="methodData.check_completeness"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">
                {{ $t('features.lm08.checkCompletenessLabel') }}
              </span>
            </label>
            <label class="flex items-center space-x-2">
              <input
                v-model="methodData.check_connections"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">
                {{ $t('features.lm08.checkConnectionsLabel') }}
              </span>
            </label>
            <label class="flex items-center space-x-2">
              <input
                v-model="methodData.check_labels"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">
                {{ $t('features.lm08.checkLabelsLabel') }}
              </span>
            </label>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('features.lm08.referenceImageLabel') }}
          </label>
          <input
            v-model="methodData.reference_image"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            :placeholder="$t('features.lm08.referenceImagePlaceholder')"
          />
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {{ $t('features.lm08.referenceImageHint') }}
          </p>
        </div>

        <div>
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.allow_ai_feedback"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              {{ $t('features.lm08.aiFeatureLabel') }}
            </span>
          </label>
        </div>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxPanel } from '@/application/stores/modules/desktop'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 8

interface Props {
  panel: LsxPanel
}

const props = defineProps<Props>()

const methodData = ref<{
  instruction: string
  task_type: string
  expected_elements: string
  check_completeness: boolean
  check_connections: boolean
  check_labels: boolean
  reference_image: string
  allow_ai_feedback: boolean
}>({
  instruction: '',
  task_type: '',
  expected_elements: '',
  check_completeness: true,
  check_connections: true,
  check_labels: false,
  reference_image: '',
  allow_ai_feedback: true
})

onMounted(() => {
  const existingData = props.panel.payload?.instanceData?.data
  if (existingData) {
    methodData.value = {
      instruction: existingData.instruction || '',
      task_type: existingData.task_type || '',
      expected_elements: existingData.expected_elements || '',
      check_completeness: existingData.check_completeness !== undefined ? existingData.check_completeness : true,
      check_connections: existingData.check_connections !== undefined ? existingData.check_connections : true,
      check_labels: existingData.check_labels !== undefined ? existingData.check_labels : false,
      reference_image: existingData.reference_image || '',
      allow_ai_feedback: existingData.allow_ai_feedback !== undefined ? existingData.allow_ai_feedback : true
    }
  }
})
</script>
