<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          {{ $t('panel.languages.title') }}
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mt-1">
          {{ $t('panel.languages.subtitle') }}
        </p>
      </div>
      <button
        @click="openCreateModal"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
      >
        + {{ $t('panel.languages.actions.create') }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12 text-gray-500">
      {{ $t('panel.languages.loading') }}
    </div>

    <!-- Empty State -->
    <div v-else-if="languages.length === 0" class="text-center py-12 text-gray-500">
      {{ $t('panel.languages.empty') }}
    </div>

    <!-- Languages Table -->
    <div v-else class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 dark:bg-gray-900 text-left">
          <tr>
            <th class="px-4 py-3 font-medium text-gray-600 dark:text-gray-400">
              {{ $t('panel.languages.table.flag') }}
            </th>
            <th class="px-4 py-3 font-medium text-gray-600 dark:text-gray-400">
              {{ $t('panel.languages.table.code') }}
            </th>
            <th class="px-4 py-3 font-medium text-gray-600 dark:text-gray-400">
              {{ $t('panel.languages.table.name') }}
            </th>
            <th class="px-4 py-3 font-medium text-gray-600 dark:text-gray-400">
              {{ $t('panel.languages.table.nativeName') }}
            </th>
            <th class="px-4 py-3 font-medium text-gray-600 dark:text-gray-400">
              {{ $t('panel.languages.table.status') }}
            </th>
            <th class="px-4 py-3 font-medium text-gray-600 dark:text-gray-400">
              {{ $t('panel.languages.table.completion') }}
            </th>
            <th class="px-4 py-3 font-medium text-gray-600 dark:text-gray-400">
              {{ $t('panel.languages.table.actions') }}
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="lang in languages"
            :key="lang.language_code"
            class="hover:bg-gray-50 dark:hover:bg-gray-750"
          >
            <!-- Flag -->
            <td class="px-4 py-3 text-2xl">{{ lang.flag_emoji }}</td>

            <!-- Code -->
            <td class="px-4 py-3 font-mono text-gray-900 dark:text-white">
              {{ lang.language_code }}
            </td>

            <!-- Name -->
            <td class="px-4 py-3 text-gray-900 dark:text-white">
              {{ lang.language_name }}
            </td>

            <!-- Native Name -->
            <td class="px-4 py-3 text-gray-700 dark:text-gray-300">
              {{ lang.native_name }}
            </td>

            <!-- Status + Badges -->
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <span
                  :class="[
                    'inline-flex px-2 py-0.5 rounded-full text-xs font-medium',
                    lang.active
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                  ]"
                >
                  {{ lang.active ? $t('panel.languages.status.active') : $t('panel.languages.status.inactive') }}
                </span>
                <span
                  v-if="lang.is_primary"
                  class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                >
                  {{ $t('panel.languages.badges.primary') }}
                </span>
                <span
                  v-if="lang.rtl"
                  class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200"
                >
                  {{ $t('panel.languages.badges.rtl') }}
                </span>
              </div>
            </td>

            <!-- Completion -->
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <div class="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    class="h-2 rounded-full transition-all"
                    :class="lang.completion_percent >= 80 ? 'bg-green-500' : lang.completion_percent >= 50 ? 'bg-yellow-500' : 'bg-red-500'"
                    :style="{ width: `${lang.completion_percent}%` }"
                  />
                </div>
                <span class="text-xs text-gray-500 dark:text-gray-400 w-10 text-right">
                  {{ lang.completion_percent }}%
                </span>
              </div>
            </td>

            <!-- Actions -->
            <td class="px-4 py-3">
              <div class="flex items-center gap-1">
                <button
                  v-if="!lang.is_primary"
                  @click="handleSetPrimary(lang)"
                  class="px-2 py-1 text-xs text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded transition-colors"
                  :title="$t('panel.languages.actions.setPrimary')"
                >
                  {{ $t('panel.languages.actions.setPrimary') }}
                </button>
                <button
                  @click="handleToggleActive(lang)"
                  class="px-2 py-1 text-xs rounded transition-colors"
                  :class="lang.active
                    ? 'text-yellow-600 hover:bg-yellow-50 dark:hover:bg-yellow-900/30'
                    : 'text-green-600 hover:bg-green-50 dark:hover:bg-green-900/30'"
                >
                  {{ lang.active ? $t('panel.languages.actions.deactivate') : $t('panel.languages.actions.activate') }}
                </button>
                <button
                  @click="openEditModal(lang)"
                  class="px-2 py-1 text-xs text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                >
                  {{ $t('panel.languages.actions.edit') }}
                </button>
                <button
                  v-if="!lang.is_primary"
                  @click="handleDelete(lang)"
                  class="px-2 py-1 text-xs text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 rounded transition-colors"
                >
                  {{ $t('panel.languages.actions.delete') }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
          {{ modalMode === 'create' ? $t('panel.languages.modal.createTitle') : $t('panel.languages.modal.editTitle') }}
        </h3>

        <form @submit.prevent="handleSave" class="space-y-4">
          <!-- Language Code (only on create) -->
          <div v-if="modalMode === 'create'">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('panel.languages.modal.code') }}
            </label>
            <input
              v-model="form.language_code"
              type="text"
              :placeholder="$t('panel.languages.modal.codePlaceholder')"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              maxlength="10"
              required
            />
          </div>

          <!-- Language Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('panel.languages.modal.name') }}
            </label>
            <input
              v-model="form.language_name"
              type="text"
              :placeholder="$t('panel.languages.modal.namePlaceholder')"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              required
            />
          </div>

          <!-- Native Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('panel.languages.modal.nativeName') }}
            </label>
            <input
              v-model="form.native_name"
              type="text"
              :placeholder="$t('panel.languages.modal.nativeNamePlaceholder')"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              required
            />
          </div>

          <!-- Flag Emoji -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('panel.languages.modal.flag') }}
            </label>
            <input
              v-model="form.flag_emoji"
              type="text"
              :placeholder="$t('panel.languages.modal.flagPlaceholder')"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              required
            />
          </div>

          <!-- Priority -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('panel.languages.modal.priority') }}
            </label>
            <input
              v-model.number="form.priority"
              type="number"
              min="1"
              max="999"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            />
            <p class="text-xs text-gray-500 mt-1">{{ $t('panel.languages.modal.priorityHint') }}</p>
          </div>

          <!-- Toggles -->
          <div class="flex items-center gap-6">
            <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <input v-model="form.active" type="checkbox" class="rounded" />
              {{ $t('panel.languages.modal.active') }}
            </label>
            <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <input v-model="form.rtl" type="checkbox" class="rounded" />
              {{ $t('panel.languages.modal.rtl') }}
            </label>
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              @click="showModal = false"
              class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              {{ $t('panel.languages.modal.cancel') }}
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {{ $t('panel.languages.modal.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * PanelLanguagesPage
 * ==================
 * Admin page for managing system languages.
 * - View all languages (active + inactive) with translation progress
 * - Create, edit, delete languages
 * - Set default (primary) language
 * - Toggle active/inactive status
 */
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { languagesApi, type AdminLanguage } from '@/infrastructure/api/clients/admin/languages.api'

const { t } = useI18n()

// ============================================================================
// State
// ============================================================================

const languages = ref<AdminLanguage[]>([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const editingCode = ref<string | null>(null)

const form = ref({
  language_code: '',
  language_name: '',
  native_name: '',
  flag_emoji: '',
  active: true,
  rtl: false,
  priority: 100
})

// ============================================================================
// Data Loading
// ============================================================================

async function loadLanguages() {
  loading.value = true
  try {
    languages.value = await languagesApi.getAll()
  } catch (err: any) {
    console.error('Failed to load languages:', err.message)
  } finally {
    loading.value = false
  }
}

// ============================================================================
// Modal
// ============================================================================

function openCreateModal() {
  modalMode.value = 'create'
  editingCode.value = null
  form.value = {
    language_code: '',
    language_name: '',
    native_name: '',
    flag_emoji: '',
    active: true,
    rtl: false,
    priority: 100
  }
  showModal.value = true
}

function openEditModal(lang: AdminLanguage) {
  modalMode.value = 'edit'
  editingCode.value = lang.language_code
  form.value = {
    language_code: lang.language_code,
    language_name: lang.language_name,
    native_name: lang.native_name,
    flag_emoji: lang.flag_emoji,
    active: lang.active,
    rtl: lang.rtl,
    priority: lang.priority
  }
  showModal.value = true
}

async function handleSave() {
  saving.value = true
  try {
    if (modalMode.value === 'create') {
      await languagesApi.create(form.value)
    } else if (editingCode.value) {
      const { language_code: _, ...updateData } = form.value
      await languagesApi.update(editingCode.value, updateData)
    }
    showModal.value = false
    await loadLanguages()
  } catch (err: any) {
    console.error('Save failed:', err.message)
  } finally {
    saving.value = false
  }
}

// ============================================================================
// Actions
// ============================================================================

async function handleSetPrimary(lang: AdminLanguage) {
  if (!confirm(t('panel.languages.confirm.setPrimary', { name: lang.language_name }))) return
  try {
    await languagesApi.update(lang.language_code, { is_primary: true })
    await loadLanguages()
  } catch (err: any) {
    console.error('Set primary failed:', err.message)
  }
}

async function handleToggleActive(lang: AdminLanguage) {
  if (lang.active && !confirm(t('panel.languages.confirm.deactivate', { name: lang.language_name }))) return
  try {
    await languagesApi.update(lang.language_code, { active: !lang.active })
    await loadLanguages()
  } catch (err: any) {
    console.error('Toggle active failed:', err.message)
  }
}

async function handleDelete(lang: AdminLanguage) {
  if (!confirm(t('panel.languages.confirm.delete', { name: lang.language_name }))) return
  try {
    await languagesApi.delete(lang.language_code)
    await loadLanguages()
  } catch (err: any) {
    console.error('Delete failed:', err.message)
  }
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  loadLanguages()
})
</script>
