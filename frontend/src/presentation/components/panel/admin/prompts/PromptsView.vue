<template>
  <div class="panel-prompts-page p-6">
    <!-- Page Header -->
    <div class="flex justify-between items-start mb-6">
      <div>
        <h1 class="text-3xl font-bold text-[var(--color-text-primary)] mb-2">
          {{ $t('panel.prompts.pageTitle') }}
        </h1>
        <p class="text-[var(--color-text-secondary)]">
          {{ $t('panel.prompts.pageDescription') }}
        </p>
      </div>
      <button
        @click="openCreateModal"
        class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors flex items-center gap-2"
      >
        <span>+</span>
        <span>{{ $t('panel.prompts.newTemplate') }}</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <PromptStatsCards
      :stats="stats"
      :category-count="categories.length"
    />

    <!-- Filters -->
    <div class="flex gap-4 mb-6">
      <select
        v-model="selectedCategory"
        class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
      >
        <option value="">{{ $t('panel.prompts.filters.allCategories') }}</option>
        <option v-for="cat in categories" :key="cat" :value="cat">{{ categoryLabels[cat] || cat }}</option>
      </select>

      <select
        v-model="selectedStyle"
        class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
      >
        <option value="">{{ $t('panel.prompts.filters.allStyles') }}</option>
        <option v-for="style in availableStyles" :key="style" :value="style">{{ styleLabels[style] || style }}</option>
      </select>

      <input
        v-model="searchQuery"
        type="text"
        :placeholder="$t('panel.prompts.filters.searchPlaceholder')"
        class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] flex-1"
      />
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]"></div>
      <span class="ml-3 text-[var(--color-text-secondary)]">{{ $t('panel.prompts.loading') }}</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <p class="text-red-700">{{ error }}</p>
      <button @click="loadTemplates" class="mt-2 text-sm text-red-600 underline">
        {{ $t('panel.prompts.errorRetry') }}
      </button>
    </div>

    <!-- Templates List -->
    <PromptTemplateList
      v-else
      :templates="filteredTemplates"
      @preview="previewTemplate"
      @edit="editTemplate"
      @duplicate="duplicateTemplate"
      @delete="confirmDelete"
    />

    <!-- Edit/Create Modal -->
    <PromptEditModal
      v-if="showEditModal"
      :template="editingTemplate"
      :saving="saving"
      @close="closeModal"
      @save="saveTemplate"
    />

    <!-- Preview Modal -->
    <PromptPreviewModal
      v-if="showPreviewModal"
      :preview-data="previewData"
      @close="closePreview"
    />

    <!-- Delete Confirmation Modal -->
    <PromptDeleteModal
      v-if="showDeleteModal"
      :delete-target="deleteTarget"
      :deleting="deleting"
      @close="showDeleteModal = false"
      @confirm="deleteTemplate"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { CATEGORY_LABELS, STYLE_LABELS } from '@/presentation/components/panel/admin/prompts/types/prompt.types'
import { usePromptTemplates } from '@/presentation/components/panel/admin/prompts/composables/usePromptTemplates'
import PromptStatsCards from '@/presentation/components/panel/admin/prompts/PromptStatsCards.vue'
import PromptTemplateList from '@/presentation/components/panel/admin/prompts/PromptTemplateList.vue'
import PromptEditModal from '@/presentation/components/panel/admin/prompts/PromptEditModal.vue'
import PromptPreviewModal from '@/presentation/components/panel/admin/prompts/PromptPreviewModal.vue'
import PromptDeleteModal from '@/presentation/components/panel/admin/prompts/PromptDeleteModal.vue'

const { t } = useI18n()

const categoryLabels = CATEGORY_LABELS
const styleLabels = STYLE_LABELS

const {
  categories,
  availableStyles,
  loading,
  error,
  searchQuery,
  selectedCategory,
  selectedStyle,
  showEditModal,
  showPreviewModal,
  showDeleteModal,
  editingTemplate,
  previewData,
  deleteTarget,
  saving,
  deleting,
  stats,
  filteredTemplates,
  loadTemplates,
  loadStats,
  duplicateTemplate,
  previewTemplate,
  deleteTemplate,
  saveTemplate,
  openCreateModal,
  editTemplate,
  confirmDelete,
  closeModal,
  closePreview,
} = usePromptTemplates()

onMounted(() => {
  loadTemplates()
  loadStats()
})
</script>
