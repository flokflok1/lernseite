<!--
  Admin Categories Page

  Complete category management with flexible unlimited-depth hierarchy
  - Create, edit, delete categories
  - Move categories to new parents
  - Drag & drop reordering
  - Visual tree structure with path display
  - Category activation/deactivation
-->

<template>
  <div class="panel-categories-page">
    <!-- Page Header - Compact -->
    <div class="mb-4 flex justify-between items-center">
      <div>
        <h1 class="text-lg font-bold text-[var(--color-text-primary)]">{{ $t('panel.categories.title') }}</h1>
        <p class="text-xs text-[var(--color-text-secondary)]">{{ $t('panel.categories.subtitle') }}</p>
      </div>
      <button
        @click="openCreateModal"
        class="px-4 py-1.5 text-sm bg-[var(--color-primary)] text-white rounded hover:bg-[var(--color-primary-dark)] transition-colors font-medium"
      >
        + {{ $t('panel.categories.create') }}
      </button>
    </div>

    <!-- Category Tree -->
    <div class="bg-[var(--color-surface)] rounded-lg shadow-sm border border-[var(--color-border)] p-4">
      <div v-if="isLoading" class="text-center py-8">
        <p class="text-[var(--color-text-secondary)]">{{ $t('panel.categories.loading') }}</p>
      </div>

      <div v-else-if="error" class="text-center py-8">
        <p class="text-red-600">{{ error }}</p>
        <button
          @click="loadCategories"
          class="mt-4 px-4 py-2 text-sm bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-dark)]"
        >
          {{ $t('common.refresh') }}
        </button>
      </div>

      <div v-else-if="categoryTree.length === 0" class="text-center py-8">
        <p class="text-[var(--color-text-secondary)] mb-4">{{ $t('panel.categories.noCategories') }}</p>
        <button
          @click="openCreateModal"
          class="px-4 py-2 text-sm bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-dark)]"
        >
          {{ $t('panel.categories.createFirst') }}
        </button>
      </div>

      <div v-else class="space-y-2">
        <CategoryTreeNode
          v-for="category in categoryTree"
          :key="category.category_id"
          :category="category"
          :level="0"
          @edit="openEditModal"
          @delete="confirmDelete"
          @toggle-active="toggleActive"
          @create-child="openCreateChildModal"
        />
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <CategoryModal
      v-if="showModal"
      :category="editingCategory"
      :parent-id="selectedParentId"
      :all-categories="flatCategories"
      @close="closeModal"
      @save="handleSave"
    />

    <!-- Delete Confirmation -->
    <DeleteConfirmModal
      v-if="showDeleteConfirm"
      :category="deletingCategory"
      @confirm="handleDelete"
      @cancel="showDeleteConfirm = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/application/stores/panel.store'
import { CategoryTreeNode, CategoryModal } from '@/presentation/components/content/panel/categories'
import { DeleteConfirmModal } from '@/presentation/components/system/shared'

const { t } = useI18n()
const panelStore = usePanelStore()

// State
const isLoading = ref(false)
const error = ref('')
const showModal = ref(false)
const showDeleteConfirm = ref(false)
const editingCategory = ref(null)
const deletingCategory = ref(null)
const selectedParentId = ref(null)

// Computed
const categoryTree = computed(() => panelStore.categoryTree || [])

const flatCategories = computed(() => {
  const result = []
  const flatten = (nodes) => {
    for (const node of nodes) {
      result.push(node)
      if (node.children && node.children.length > 0) {
        flatten(node.children)
      }
    }
  }
  if (categoryTree.value && Array.isArray(categoryTree.value)) {
    flatten(categoryTree.value)
  }
  return result
})

// Methods
const loadCategories = async (forceReload = false) => {
  isLoading.value = true
  error.value = ''

  try {
    await panelStore.loadCategoryTree(false, forceReload) // Load all categories (including inactive)
  } catch (e) {
    error.value = e.message || t('panel.categories.loadError')
  } finally {
    isLoading.value = false
  }
}

const openCreateModal = () => {
  editingCategory.value = null
  selectedParentId.value = null
  showModal.value = true
}

const openCreateChildModal = (parentCategory) => {
  // Check if we can add another level (practical limit is 20)
  if (parentCategory.level >= 20) {
    alert(t('panel.categories.maxDepthReached'))
    return
  }

  editingCategory.value = null
  selectedParentId.value = parentCategory.category_id
  showModal.value = true
}

const openEditModal = (category) => {
  editingCategory.value = { ...category }
  selectedParentId.value = category.parent_id
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingCategory.value = null
  selectedParentId.value = null
}

const handleSave = async (categoryData) => {
  try {
    if (editingCategory.value) {
      // Update existing category
      await panelStore.updateCategory(editingCategory.value.category_id, categoryData)
    } else {
      // Create new category
      await panelStore.createCategory(categoryData)
    }

    closeModal()
    await loadCategories(true) // Force reload after save
  } catch (e) {
    alert(t('panel.categories.saveError') + ': ' + (e.message || t('common.unknownError')))
  }
}

const confirmDelete = (category) => {
  deletingCategory.value = category
  showDeleteConfirm.value = true
}

const handleDelete = async () => {
  if (!deletingCategory.value) return

  try {
    await panelStore.deleteCategory(deletingCategory.value.category_id)
    showDeleteConfirm.value = false
    deletingCategory.value = null
    await loadCategories(true) // Force reload after delete
  } catch (e) {
    alert(t('panel.categories.deleteError') + ': ' + (e.message || t('common.unknownError')))
  }
}

const toggleActive = async (category) => {
  if (!category || !category.category_id) {
    console.error('toggleActive: Invalid category object', category)
    alert(t('panel.categories.categoryIdNotFound'))
    return
  }

  try {
    await panelStore.updateCategory(category.category_id, {
      is_active: !category.is_active
    })
    await loadCategories(true) // Force reload after toggle
  } catch (e) {
    alert(t('panel.categories.updateError') + ': ' + (e.message || t('common.unknownError')))
  }
}

// Lifecycle
onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.panel-categories-page {
  padding: 1rem;
}
</style>
