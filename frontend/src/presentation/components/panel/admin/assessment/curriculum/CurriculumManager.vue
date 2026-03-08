<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold">
          {{ $t('panel.curriculum.title') }}
        </h2>
        <p class="text-sm text-gray-500 mt-1">
          {{ $t('panel.curriculum.subtitle') }}
        </p>
      </div>
      <div class="flex gap-2">
        <button
          class="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
          @click="showImport = true"
        >
          {{ $t('panel.curriculum.importPdf') }}
        </button>
        <button
          class="px-4 py-2 text-sm border rounded hover:bg-gray-50 dark:hover:bg-gray-800"
          @click="showCreate = !showCreate"
        >
          {{ $t('panel.curriculum.createManual') }}
        </button>
      </div>
    </div>

    <!-- Create form (inline) -->
    <div
      v-if="showCreate"
      class="border rounded p-4 space-y-3 bg-gray-50 dark:bg-gray-800"
    >
      <h3 class="font-medium">{{ $t('panel.curriculum.createTitle') }}</h3>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-sm mb-1">{{ $t('panel.curriculum.name') }}</label>
          <input
            v-model="createForm.name"
            type="text"
            class="w-full border rounded p-2 text-sm dark:bg-gray-700"
          />
        </div>
        <div>
          <label class="block text-sm mb-1">{{ $t('panel.curriculum.type') }}</label>
          <select
            v-model="createForm.framework_type"
            class="w-full border rounded p-2 text-sm dark:bg-gray-700"
          >
            <option value="ihk_ausbildung">IHK Ausbildung</option>
            <option value="hochschule">Hochschule</option>
            <option value="zertifizierung">Zertifizierung</option>
            <option value="custom">Custom</option>
          </select>
        </div>
      </div>
      <div class="flex gap-2">
        <button
          class="px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          :disabled="!createForm.name || loading"
          @click="handleCreate"
        >
          {{ $t('common.create') }}
        </button>
        <button
          class="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700"
          @click="showCreate = false"
        >
          {{ $t('common.cancel') }}
        </button>
      </div>
    </div>

    <!-- Error banner -->
    <div
      v-if="error"
      class="bg-red-50 dark:bg-red-900/20 p-3 rounded text-sm text-red-700 dark:text-red-400"
    >
      {{ error }}
    </div>

    <!-- Loading -->
    <div
      v-if="loading && !frameworks.length"
      class="text-center py-8 text-gray-500"
      aria-live="polite"
    >
      {{ $t('common.loading') }}
    </div>

    <!-- Framework list -->
    <div v-if="frameworks.length" class="space-y-4">
      <div
        v-for="fw in frameworks"
        :key="fw.framework_id"
        class="border rounded-lg overflow-hidden"
      >
        <div
          class="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800"
          @click="selectFramework(fw.framework_id)"
        >
          <div>
            <h3 class="font-medium">{{ fw.name }}</h3>
            <p class="text-xs text-gray-500">
              {{ fw.framework_type }}
              <span v-if="fw.source_document"> &middot; {{ fw.source_document }}</span>
            </p>
          </div>
          <div class="flex items-center gap-2">
            <button
              class="px-2 py-1 text-xs text-red-600 hover:bg-red-50 rounded"
              @click.stop="handleDelete(fw.framework_id)"
            >
              {{ $t('common.delete') }}
            </button>
            <span class="text-gray-400 text-sm">
              {{ selectedId === fw.framework_id ? '&#9660;' : '&#9654;' }}
            </span>
          </div>
        </div>

        <!-- Expanded tree + coverage -->
        <div
          v-if="selectedId === fw.framework_id"
          class="border-t p-4 space-y-4"
        >
          <!-- Coverage stats -->
          <div
            v-if="coverage"
            class="grid grid-cols-3 gap-4 text-center"
          >
            <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded">
              <div class="text-2xl font-bold text-blue-600">
                {{ coverage.total_objectives }}
              </div>
              <div class="text-xs text-gray-500">
                {{ $t('panel.curriculum.coverage.totalObjectives') }}
              </div>
            </div>
            <div class="bg-green-50 dark:bg-green-900/20 p-3 rounded">
              <div class="text-2xl font-bold text-green-600">
                {{ coverage.mapped_objectives }}
              </div>
              <div class="text-xs text-gray-500">
                {{ $t('panel.curriculum.coverage.mapped') }}
              </div>
            </div>
            <div class="bg-orange-50 dark:bg-orange-900/20 p-3 rounded">
              <div class="text-2xl font-bold text-orange-600">
                {{ coverage.coverage_percent }}%
              </div>
              <div class="text-xs text-gray-500">
                {{ $t('panel.curriculum.coverage.percent') }}
              </div>
            </div>
          </div>

          <CurriculumTreeView :tree="activeTree" />
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-if="!loading && !frameworks.length"
      class="text-center py-12 text-gray-500"
    >
      <p class="text-lg mb-2">{{ $t('panel.curriculum.empty.title') }}</p>
      <p class="text-sm">{{ $t('panel.curriculum.empty.hint') }}</p>
    </div>

    <!-- Import dialog -->
    <CurriculumImportDialog
      ref="importDialogRef"
      :visible="showImport"
      :loading="loading"
      :error="error"
      @close="showImport = false"
      @parse="handleParse"
      @confirm="handleConfirm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCurriculum } from '../composables'
import CurriculumTreeView from './CurriculumTreeView.vue'
import CurriculumImportDialog from './CurriculumImportDialog.vue'

const {
  frameworks,
  activeTree,
  coverage,
  loading,
  error,
  loadFrameworks,
  loadTree,
  loadCoverage,
  addFramework,
  removeFramework,
  parsePdf,
  confirmImport,
} = useCurriculum()

const showImport = ref(false)
const showCreate = ref(false)
const selectedId = ref<number | null>(null)
const importDialogRef = ref<InstanceType<typeof CurriculumImportDialog> | null>(null)

const createForm = ref({
  name: '',
  framework_type: 'ihk_ausbildung',
})

onMounted(() => {
  loadFrameworks()
})

async function selectFramework(id: number) {
  if (selectedId.value === id) {
    selectedId.value = null
    return
  }
  selectedId.value = id
  await Promise.all([loadTree(id), loadCoverage(id)])
}

async function handleCreate() {
  const result = await addFramework(createForm.value)
  if (result) {
    showCreate.value = false
    createForm.value = { name: '', framework_type: 'ihk_ausbildung' }
  }
}

async function handleDelete(frameworkId: number) {
  await removeFramework(frameworkId)
  if (selectedId.value === frameworkId) {
    selectedId.value = null
  }
}

async function handleParse(pdfText: string) {
  const preview = await parsePdf(pdfText)
  if (preview && importDialogRef.value) {
    importDialogRef.value.setPreview(preview)
  }
}

async function handleConfirm(sourceDocument?: string) {
  const result = await confirmImport(sourceDocument)
  if (result) {
    showImport.value = false
    importDialogRef.value?.reset()
  }
}
</script>
