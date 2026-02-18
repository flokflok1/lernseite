<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200 dark:border-gray-700">
      <h3 class="text-sm font-medium text-gray-900 dark:text-white">
        {{ $t('panel.languages.review.title') }}
      </h3>
      <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
        {{ $t('panel.languages.review.subtitle') }}
      </p>
    </div>

    <!-- Filters -->
    <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex flex-wrap items-end gap-3">
      <!-- Target Language -->
      <div class="w-40">
        <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">
          {{ $t('panel.languages.translate.targetLanguage') }}
        </label>
        <select
          v-model="filters.language"
          @change="loadReview(1)"
          class="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option v-for="lang in reviewLanguages" :key="lang.language_code" :value="lang.language_code">
            {{ lang.language_name }} ({{ lang.language_code }})
          </option>
        </select>
      </div>

      <!-- Namespace Filter -->
      <div class="w-44">
        <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">
          {{ $t('panel.languages.review.filterNamespace') }}
        </label>
        <select
          v-model="filters.namespace"
          @change="loadReview(1)"
          class="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="">{{ $t('panel.languages.review.filterAll') }}</option>
          <option v-for="ns in namespaces" :key="ns" :value="ns">{{ ns }}</option>
        </select>
      </div>

      <!-- Status Filter -->
      <div class="w-36">
        <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">
          {{ $t('panel.languages.review.filterStatus') }}
        </label>
        <select
          v-model="filters.status"
          @change="loadReview(1)"
          class="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="all">{{ $t('panel.languages.review.filterAll') }}</option>
          <option value="verified">{{ $t('panel.languages.review.verified') }}</option>
          <option value="unverified">{{ $t('panel.languages.review.unverified') }}</option>
        </select>
      </div>

      <!-- Search -->
      <div class="flex-1 min-w-[200px]">
        <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">
          {{ $t('panel.languages.review.search') }}
        </label>
        <input
          v-model="filters.search"
          @input="debouncedSearch"
          type="text"
          :placeholder="$t('panel.languages.review.search')"
          class="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      <!-- Bulk Verify -->
      <button
        v-if="selectedIds.length > 0"
        @click="handleBulkVerify"
        class="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors whitespace-nowrap"
      >
        {{ $t('panel.languages.review.verifySelected') }} ({{ selectedIds.length }})
      </button>
    </div>

    <!-- Loading -->
    <div v-if="reviewLoading" class="p-8 text-center text-gray-500 text-sm">
      {{ $t('panel.languages.loading') }}
    </div>

    <!-- Empty -->
    <div v-else-if="translations.length === 0" class="p-8 text-center text-gray-500 text-sm">
      {{ $t('panel.languages.review.noResults') }}
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 dark:bg-gray-900 text-left">
          <tr>
            <th class="px-3 py-2 w-8">
              <input
                type="checkbox"
                :checked="allSelected"
                @change="toggleSelectAll"
                class="rounded"
              />
            </th>
            <th class="px-3 py-2 font-medium text-gray-600 dark:text-gray-400 text-xs">Key</th>
            <th class="px-3 py-2 font-medium text-gray-600 dark:text-gray-400 text-xs">
              {{ $t('panel.languages.review.sourceValue') }}
            </th>
            <th class="px-3 py-2 font-medium text-gray-600 dark:text-gray-400 text-xs">
              {{ $t('panel.languages.review.translatedValue') }}
            </th>
            <th class="px-3 py-2 font-medium text-gray-600 dark:text-gray-400 text-xs">
              {{ $t('panel.languages.review.source') }}
            </th>
            <th class="px-3 py-2 font-medium text-gray-600 dark:text-gray-400 text-xs w-24">
              {{ $t('panel.languages.table.actions') }}
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="item in translations"
            :key="item.translation_id"
            class="hover:bg-gray-50 dark:hover:bg-gray-750"
          >
            <!-- Checkbox -->
            <td class="px-3 py-2">
              <input
                type="checkbox"
                :checked="selectedIds.includes(item.translation_id)"
                @change="toggleSelect(item.translation_id)"
                class="rounded"
              />
            </td>

            <!-- Key -->
            <td class="px-3 py-2 font-mono text-xs text-gray-700 dark:text-gray-300 max-w-[200px] truncate" :title="`${item.namespace_code}.${item.key_path}`">
              <span class="text-gray-400">{{ item.namespace_code }}.</span>{{ item.key_path }}
            </td>

            <!-- Source Value -->
            <td class="px-3 py-2 text-gray-600 dark:text-gray-400 max-w-[200px] truncate" :title="item.source_value">
              {{ item.source_value }}
            </td>

            <!-- Translated Value (inline edit) -->
            <td class="px-3 py-2 max-w-[250px]">
              <template v-if="editingId === item.translation_id">
                <div class="flex gap-1">
                  <input
                    v-model="editValue"
                    type="text"
                    class="flex-1 px-2 py-1 text-sm border border-blue-400 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    @keyup.enter="saveEdit(item.translation_id)"
                    @keyup.escape="cancelEdit"
                  />
                  <button @click="saveEdit(item.translation_id)" class="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700">
                    {{ $t('panel.languages.review.save') }}
                  </button>
                  <button @click="cancelEdit" class="px-2 py-1 text-xs text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                    {{ $t('panel.languages.review.cancel') }}
                  </button>
                </div>
              </template>
              <template v-else>
                <span class="text-gray-900 dark:text-white truncate block" :title="item.translated_value">
                  {{ item.translated_value }}
                </span>
              </template>
            </td>

            <!-- Source badge -->
            <td class="px-3 py-2">
              <span
                :class="[
                  'inline-flex px-1.5 py-0.5 rounded text-xs font-medium',
                  item.is_verified
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                ]"
              >
                {{ item.translation_source }}
              </span>
            </td>

            <!-- Actions -->
            <td class="px-3 py-2">
              <div class="flex items-center gap-1">
                <button
                  @click="startEdit(item)"
                  class="px-2 py-0.5 text-xs text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                >
                  {{ $t('panel.languages.review.edit') }}
                </button>
                <button
                  v-if="!item.is_verified"
                  @click="handleVerify(item.translation_id)"
                  class="px-2 py-0.5 text-xs text-green-600 hover:bg-green-50 dark:hover:bg-green-900/30 rounded transition-colors"
                >
                  {{ $t('panel.languages.review.verify') }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="p-3 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-xs text-gray-500">
      <span>{{ total }} {{ $t('panel.languages.review.title').toLowerCase() }}</span>
      <div class="flex gap-1">
        <button
          v-for="p in paginationRange"
          :key="p"
          @click="loadReview(p)"
          :class="[
            'px-2.5 py-1 rounded transition-colors',
            p === currentPage
              ? 'bg-blue-600 text-white'
              : 'hover:bg-gray-100 dark:hover:bg-gray-700'
          ]"
        >
          {{ p }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * TranslationReviewPanel
 *
 * Displays a paginated, filterable table of translations for review.
 * Supports inline editing, verification, and bulk verification.
 */
import { ref, computed, watch, onMounted } from 'vue'
import {
  languagesApi,
  type AdminLanguage,
  type ReviewTranslation
} from '@/infrastructure/api/clients/panel/admin/languages.api'
import { getNamespaces as fetchNamespaces } from '@/infrastructure/api/clients/public/i18n.api'

const props = defineProps<{
  languages: AdminLanguage[]
}>()

const emit = defineEmits<{
  refreshLanguages: []
}>()

// Namespaces loaded dynamically from DB
const namespaces = ref<string[]>([])

onMounted(async () => {
  try {
    const nsData = await fetchNamespaces()
    namespaces.value = nsData.map(ns => ns.namespace_code).sort()
  } catch (err: any) {
    console.error('Failed to load namespaces:', err.message)
  }
})

// All languages available for review (including primary)
const reviewLanguages = computed(() => props.languages)

// Filters
const filters = ref({
  language: '',
  namespace: '',
  status: 'all' as 'all' | 'verified' | 'unverified',
  search: ''
})

// Review data
const translations = ref<ReviewTranslation[]>([])
const reviewLoading = ref(false)
const currentPage = ref(1)
const total = ref(0)
const totalPages = ref(0)
const perPage = 20

// Selection
const selectedIds = ref<string[]>([])
const allSelected = computed(() =>
  translations.value.length > 0 && selectedIds.value.length === translations.value.length
)

// Inline editing
const editingId = ref<string | null>(null)
const editValue = ref('')

// Pagination range
const paginationRange = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

// Set default language when languages load (default to first non-primary, but all available)
watch(() => props.languages, (langs) => {
  if (langs.length > 0 && !filters.value.language) {
    const nonPrimary = langs.filter(l => !l.is_primary)
    filters.value.language = nonPrimary.length > 0
      ? nonPrimary[0].language_code
      : langs[0].language_code
    loadReview(1)
  }
}, { immediate: true })

// Debounced search
let searchTimeout: ReturnType<typeof setTimeout> | null = null
function debouncedSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => loadReview(1), 400)
}

async function loadReview(page: number) {
  if (!filters.value.language) return

  reviewLoading.value = true
  selectedIds.value = []
  currentPage.value = page

  try {
    const result = await languagesApi.getReviewTranslations({
      language: filters.value.language,
      namespace: filters.value.namespace || undefined,
      status: filters.value.status,
      search: filters.value.search || undefined,
      page,
      per_page: perPage
    })
    translations.value = result.data
    total.value = result.total
    totalPages.value = result.total_pages
  } catch (err: any) {
    console.error('Failed to load review:', err.message)
    translations.value = []
  } finally {
    reviewLoading.value = false
  }
}

function toggleSelect(id: string) {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = translations.value.map(t => t.translation_id)
  }
}

function startEdit(item: ReviewTranslation) {
  editingId.value = item.translation_id
  editValue.value = item.translated_value
}

function cancelEdit() {
  editingId.value = null
  editValue.value = ''
}

async function saveEdit(translationId: string) {
  try {
    await languagesApi.editTranslation(translationId, editValue.value)
    // Update local state
    const item = translations.value.find(t => t.translation_id === translationId)
    if (item) {
      item.translated_value = editValue.value
      item.translation_source = 'manual'
      item.is_verified = true
    }
    cancelEdit()
  } catch (err: any) {
    console.error('Edit failed:', err.message)
  }
}

async function handleVerify(translationId: string) {
  try {
    await languagesApi.verifyTranslation(translationId)
    const item = translations.value.find(t => t.translation_id === translationId)
    if (item) item.is_verified = true
  } catch (err: any) {
    console.error('Verify failed:', err.message)
  }
}

async function handleBulkVerify() {
  if (selectedIds.value.length === 0) return
  try {
    await languagesApi.bulkVerifyTranslations(selectedIds.value)
    // Update local state
    for (const id of selectedIds.value) {
      const item = translations.value.find(t => t.translation_id === id)
      if (item) item.is_verified = true
    }
    selectedIds.value = []
  } catch (err: any) {
    console.error('Bulk verify failed:', err.message)
  }
}
</script>
