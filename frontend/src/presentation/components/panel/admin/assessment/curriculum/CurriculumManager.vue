<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-[var(--color-text-primary)]">
          {{ $t('panel.curriculum.title') }}
        </h2>
        <p class="text-sm text-[var(--color-text-secondary)] mt-1">
          {{ $t('panel.curriculum.subtitle') }}
        </p>
      </div>
      <div class="flex gap-2">
        <button
          class="px-4 py-2 text-sm text-white rounded transition-colors"
          style="background-color: var(--color-primary, #7c3aed);"
          @click="showImport = true"
        >
          {{ $t('panel.curriculum.importPdf') }}
        </button>
        <button
          class="px-4 py-2 text-sm rounded border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] transition-colors"
          @click="showCreate = !showCreate"
        >
          {{ $t('panel.curriculum.createManual') }}
        </button>
      </div>
    </div>

    <!-- Create form (inline) -->
    <div
      v-if="showCreate"
      class="border border-[var(--color-border)] rounded-lg p-4 space-y-3 bg-[var(--color-surface-secondary)]"
    >
      <h3 class="font-medium text-[var(--color-text-primary)]">{{ $t('panel.curriculum.createTitle') }}</h3>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-sm mb-1 text-[var(--color-text-secondary)]">{{ $t('panel.curriculum.name') }}</label>
          <input
            v-model="createForm.name"
            type="text"
            class="w-full border border-[var(--color-border)] rounded p-2 text-sm bg-[var(--color-surface)] text-[var(--color-text-primary)]"
          />
        </div>
        <div>
          <label class="block text-sm mb-1 text-[var(--color-text-secondary)]">{{ $t('panel.curriculum.type') }}</label>
          <select
            v-model="createForm.framework_type"
            class="w-full border border-[var(--color-border)] rounded p-2 text-sm bg-[var(--color-surface)] text-[var(--color-text-primary)]"
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
          class="px-3 py-1.5 text-sm text-white rounded transition-colors disabled:opacity-50"
          style="background-color: var(--color-success, #16a34a);"
          :disabled="!createForm.name || loading"
          @click="handleCreate"
        >
          {{ $t('common.create') }}
        </button>
        <button
          class="px-3 py-1.5 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
          @click="showCreate = false"
        >
          {{ $t('common.cancel') }}
        </button>
      </div>
    </div>

    <!-- Error banner -->
    <div
      v-if="error"
      class="p-3 rounded-lg text-sm border"
      style="background-color: var(--color-error-bg, #fef2f2); border-color: var(--color-error-border, #fecaca); color: var(--color-error-text, #dc2626);"
    >
      {{ error }}
    </div>

    <!-- Loading -->
    <div
      v-if="loading && !frameworks.length"
      class="flex justify-center py-8"
      aria-live="polite"
    >
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]" />
    </div>

    <!-- Framework list -->
    <div v-if="frameworks.length" class="space-y-3">
      <div
        v-for="fw in frameworks"
        :key="fw.framework_id"
        class="border border-[var(--color-border)] rounded-lg overflow-hidden bg-[var(--color-surface)]"
      >
        <div
          class="flex items-center justify-between p-4 cursor-pointer hover:bg-[var(--color-surface-secondary)] transition-colors"
          @click="selectFramework(fw.framework_id)"
        >
          <div>
            <h3 class="font-medium text-[var(--color-text-primary)]">{{ fw.name }}</h3>
            <p class="text-xs text-[var(--color-text-secondary)] mt-0.5">
              {{ fw.framework_type }}
              <span v-if="fw.source_document"> &middot; {{ fw.source_document }}</span>
            </p>
          </div>
          <div class="flex items-center gap-3">
            <button
              class="px-2 py-1 text-xs rounded transition-colors"
              style="color: var(--color-error-text, #dc2626);"
              @click.stop="handleDelete(fw.framework_id)"
            >
              {{ $t('common.delete') }}
            </button>
            <svg
              class="w-4 h-4 text-[var(--color-text-secondary)] transition-transform"
              :class="{ 'rotate-180': selectedId === fw.framework_id }"
              fill="none" viewBox="0 0 24 24" stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>

        <!-- Expanded content -->
        <div
          v-if="selectedId === fw.framework_id"
          class="border-t border-[var(--color-border)] p-4 space-y-4"
        >
          <!-- Tab navigation -->
          <div class="flex gap-1 border-b border-[var(--color-border)]">
            <button
              v-for="tab in ['structure', 'mapping'] as const"
              :key="tab"
              class="px-4 py-2 text-sm font-medium transition-colors -mb-px"
              :class="activeTab === tab
                ? 'border-b-2 border-[var(--color-primary,#7c3aed)] text-[var(--color-primary,#7c3aed)]'
                : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'"
              @click="activeTab = tab"
            >
              {{ $t(`panel.curriculum.tabs.${tab}`) }}
            </button>
          </div>

          <!-- Structure tab -->
          <template v-if="activeTab === 'structure'">
            <!-- Coverage stats -->
            <div
              v-if="coverage"
              class="grid grid-cols-3 gap-4 text-center"
            >
              <div class="p-3 rounded-lg" style="background-color: var(--color-info-bg, #eff6ff);">
                <div class="text-2xl font-bold" style="color: var(--color-info-text, #2563eb);">
                  {{ coverage.total_objectives }}
                </div>
                <div class="text-xs text-[var(--color-text-secondary)]">
                  {{ $t('panel.curriculum.coverage.totalObjectives') }}
                </div>
              </div>
              <div class="p-3 rounded-lg" style="background-color: var(--color-success-bg, #dcfce7);">
                <div class="text-2xl font-bold" style="color: var(--color-success-text, #15803d);">
                  {{ coverage.mapped_objectives }}
                </div>
                <div class="text-xs text-[var(--color-text-secondary)]">
                  {{ $t('panel.curriculum.coverage.mapped') }}
                </div>
              </div>
              <div class="p-3 rounded-lg" style="background-color: var(--color-warning-bg, #fef3c7);">
                <div class="text-2xl font-bold" style="color: var(--color-warning-text, #92400e);">
                  {{ coverage.coverage_percent }}%
                </div>
                <div class="text-xs text-[var(--color-text-secondary)]">
                  {{ $t('panel.curriculum.coverage.percent') }}
                </div>
              </div>
            </div>

            <CurriculumTreeView :tree="activeTree" />
          </template>

          <!-- Mapping & Relevance tab -->
          <CurriculumMappingPanel
            v-if="activeTab === 'mapping'"
            :framework-id="fw.framework_id"
            @refresh="() => loadCoverage(fw.framework_id)"
          />
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-if="!loading && !frameworks.length"
      class="text-center py-16"
    >
      <div class="text-5xl mb-4 opacity-30">📋</div>
      <p class="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
        {{ $t('panel.curriculum.empty.title') }}
      </p>
      <p class="text-sm text-[var(--color-text-secondary)]">
        {{ $t('panel.curriculum.empty.hint') }}
      </p>
    </div>

    <!-- Import dialog -->
    <CurriculumImportDialog
      ref="importDialogRef"
      :visible="showImport"
      :loading="loading"
      :error="error"
      :progress="importProgress"
      @close="showImport = false"
      @parse="handleParse"
      @parse-file="handleParseFile"
      @confirm="handleConfirm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCurriculum } from '../composables'
import CurriculumTreeView from './CurriculumTreeView.vue'
import CurriculumImportDialog from './CurriculumImportDialog.vue'
import CurriculumMappingPanel from './CurriculumMappingPanel.vue'

const {
  frameworks,
  activeTree,
  coverage,
  loading,
  error,
  importProgress,
  loadFrameworks,
  loadCoverage,
  loadStructureData,
  addFramework,
  removeFramework,
  parsePdf,
  parsePdfFile,
  confirmImport,
} = useCurriculum()

const showImport = ref(false)
const showCreate = ref(false)
const selectedId = ref<number | null>(null)
const activeTab = ref<'structure' | 'mapping'>('structure')
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
  activeTab.value = 'structure'
  await loadStructureData(id)
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

async function handleParse(pdfText: string, provider: string, model: string) {
  const preview = await parsePdf(pdfText, provider || undefined, model || undefined)
  if (preview && importDialogRef.value) {
    importDialogRef.value.setPreview(preview)
  }
}

async function handleParseFile(file: File, provider: string, model: string) {
  const preview = await parsePdfFile(file, provider || undefined, model || undefined)
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
