<template>
  <div class="panel-translations-page p-6">
    <!-- Header -->
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-[var(--color-text-primary)]">{{ $t('panel.translations.title') }}</h1>
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ languages.length }} {{ $t('panel.translations.languages') }} · {{ totalKeys }} Keys
          <span v-if="isSyncing" class="ml-2 text-primary-500">• {{ $t('common.syncing') }}...</span>
        </p>
      </div>
      <button
        @click="forceResync"
        :disabled="isSyncing"
        class="px-4 py-2 border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] flex items-center gap-2 disabled:opacity-50"
      >
        <svg class="w-4 h-4" :class="{ 'animate-spin': isSyncing }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
        Sync
      </button>
    </div>

    <!-- Status Message -->
    <div v-if="statusMessage" class="mb-4 p-3 rounded-lg text-sm" :class="statusMessage.type === 'success' ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200' : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'">
      {{ statusMessage.text }}
    </div>

    <!-- Filters Row -->
    <div class="flex gap-3 mb-6 items-center flex-wrap">
      <!-- Language Dropdown -->
      <select
        v-model="selectedLanguage"
        class="px-3 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg"
      >
        <option v-for="lang in languages" :key="lang.language_code" :value="lang.language_code">
          {{ lang.native_name }} ({{ Math.round(lang.completion_percent) }}%)
        </option>
      </select>

      <!-- Category/Namespace Dropdown -->
      <select
        v-model="selectedNamespace"
        class="px-3 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg"
      >
        <option value="">{{ $t('panel.translations.allCategories') }}</option>
        <option v-for="ns in dbNamespaces" :key="ns.namespace_code" :value="ns.namespace_code">
          {{ ns.icon || '📁' }} {{ ns.name }} ({{ ns.key_count }})
        </option>
      </select>

      <!-- Search -->
      <div class="flex-1 min-w-[200px]">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('common.search') + '...'"
          class="w-full px-3 py-2 border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-primary)] rounded-lg"
        />
      </div>

      <!-- Stats -->
      <div class="text-sm text-[var(--color-text-secondary)] whitespace-nowrap">
        {{ filteredCount }} / {{ translations.length }}
      </div>
    </div>

    <!-- Translations List -->
    <div class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] overflow-hidden">
      <!-- Loading -->
      <div v-if="isLoading" class="p-8 text-center text-[var(--color-text-secondary)]">
        <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-3"></div>
        {{ $t('common.loading') }}...
      </div>

      <!-- Empty State -->
      <div v-else-if="paginatedTranslations.length === 0" class="p-8 text-center text-[var(--color-text-secondary)]">
        <p>{{ $t('panel.translations.noResults') }}</p>
        <button @click="forceResync" class="mt-2 text-primary-600 hover:text-primary-700 underline">
          {{ $t('panel.translations.syncNow') }}
        </button>
      </div>

      <!-- Translation Items grouped by namespace -->
      <div v-else>
        <template v-for="(group, namespace) in groupedTranslations" :key="namespace">
          <!-- Namespace Header -->
          <div class="px-4 py-2 bg-[var(--color-surface-secondary)] border-b border-[var(--color-border)] sticky top-0 z-10">
            <span class="font-medium text-[var(--color-text-primary)]">
              {{ getNamespaceIcon(namespace as string) }} {{ getNamespaceName(namespace as string) }}
            </span>
            <span class="text-sm text-[var(--color-text-secondary)] ml-2">({{ group.length }})</span>
          </div>

          <!-- Items in this namespace -->
          <div class="divide-y divide-[var(--color-border)]">
            <div
              v-for="item in group"
              :key="item.key_path"
              class="p-3 hover:bg-[var(--color-surface-secondary)] transition-colors"
            >
              <!-- Key (short) -->
              <div class="text-xs text-[var(--color-text-secondary)] mb-1 font-mono">
                {{ getShortKey(item.key_path, item.namespace) }}
              </div>

              <!-- Values Row -->
              <div class="flex gap-4 items-start">
                <!-- German (Source) -->
                <div class="flex-1 min-w-0">
                  <div class="text-sm text-[var(--color-text-primary)] truncate" :title="item.de_value">
                    {{ item.de_value || '—' }}
                  </div>
                </div>

                <!-- Arrow -->
                <div class="text-[var(--color-text-secondary)]">→</div>

                <!-- Selected Language -->
                <div class="flex-1 min-w-0">
                  <!-- Edit Mode -->
                  <div v-if="editingKey === item.key_path" class="flex gap-2">
                    <input
                      v-model="editValue"
                      type="text"
                      class="flex-1 px-2 py-1 text-sm border border-primary-500 bg-[var(--color-bg)] text-[var(--color-text-primary)] rounded"
                      @keyup.enter="saveTranslation(item)"
                      @keyup.escape="cancelEdit"
                      ref="editInput"
                    />
                    <button @click="saveTranslation(item)" class="px-2 py-1 bg-green-600 text-white rounded text-sm">✓</button>
                    <button @click="cancelEdit" class="px-2 py-1 bg-gray-500 text-white rounded text-sm">✕</button>
                  </div>

                  <!-- Display Mode -->
                  <div v-else class="flex items-center gap-2 group cursor-pointer" @click="startEdit(item)">
                    <span
                      class="text-sm truncate"
                      :class="item.translated_value ? 'text-[var(--color-text-primary)]' : 'text-red-500 italic'"
                      :title="item.translated_value || $t('panel.translations.notTranslated')"
                    >
                      {{ item.translated_value || $t('panel.translations.notTranslated') }}
                    </span>
                    <svg class="w-3 h-3 opacity-0 group-hover:opacity-100 text-primary-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="p-3 border-t border-[var(--color-border)] flex justify-center items-center gap-2 bg-[var(--color-surface-secondary)]">
        <button
          @click="currentPage = Math.max(1, currentPage - 1)"
          :disabled="currentPage === 1"
          class="px-3 py-1 border border-[var(--color-border)] rounded disabled:opacity-50 text-[var(--color-text-primary)]"
        >←</button>
        <span class="text-sm text-[var(--color-text-secondary)]">{{ currentPage }} / {{ totalPages }}</span>
        <button
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="px-3 py-1 border border-[var(--color-border)] rounded disabled:opacity-50 text-[var(--color-text-primary)]"
        >→</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/infrastructure/api/http'
import { i18n } from '@/infrastructure/plugins/i18n'

const { t } = useI18n()

// Locale imports for sync + fallback values
import deCommon from '@/infrastructure/i18n/locales/de/common'
import deErrors from '@/infrastructure/i18n/locales/de/errors'
import deDashboard from '@/infrastructure/i18n/locales/de/dashboard'
import deSetup from '@/infrastructure/i18n/locales/de/setup'
import deTutor from '@/infrastructure/i18n/locales/de/tutor'
import deLegal from '@/infrastructure/i18n/locales/de/legal'
import dePanel from '@/infrastructure/i18n/locales/de/panel'
import deAiEditor from '@/infrastructure/i18n/locales/de/panel/aiEditor'
import deCourses from '@/infrastructure/i18n/locales/de/courses'
import deFeatures from '@/infrastructure/i18n/locales/de/features'
import enCommon from '@/infrastructure/i18n/locales/en/common'
import enErrors from '@/infrastructure/i18n/locales/en/errors'
import enDashboard from '@/infrastructure/i18n/locales/en/dashboard'
import enSetup from '@/infrastructure/i18n/locales/en/setup'
import enTutor from '@/infrastructure/i18n/locales/en/tutor'
import enLegal from '@/infrastructure/i18n/locales/en/legal'
import enPanel from '@/infrastructure/i18n/locales/en/panel'
import enAiEditor from '@/infrastructure/i18n/locales/en/panel/aiEditor'
import enCourses from '@/infrastructure/i18n/locales/en/courses'
import enFeatures from '@/infrastructure/i18n/locales/en/features'
import plCommon from '@/infrastructure/i18n/locales/pl/common'
import plErrors from '@/infrastructure/i18n/locales/pl/errors'
import plDashboard from '@/infrastructure/i18n/locales/pl/dashboard'
import plSetup from '@/infrastructure/i18n/locales/pl/setup'
import plTutor from '@/infrastructure/i18n/locales/pl/tutor'
import plLegal from '@/infrastructure/i18n/locales/pl/legal'
import plPanel from '@/infrastructure/i18n/locales/pl/panel'
import plAiEditor from '@/infrastructure/i18n/locales/pl/panel/aiEditor'
import plCourses from '@/infrastructure/i18n/locales/pl/courses'
import plFeatures from '@/infrastructure/i18n/locales/pl/features'

const MODULES = [deCommon, deErrors, deDashboard, deSetup, deTutor, deLegal, dePanel, deAiEditor, deCourses, deFeatures]
const mergeAll = (...mods: Record<string, any>[]) => Object.assign({}, ...mods)
const deMessages = mergeAll(...MODULES)
const enMessages = mergeAll(enCommon, enErrors, enDashboard, enSetup, enTutor, enLegal, enPanel, enAiEditor, enCourses, enFeatures)
const plMessages = mergeAll(plCommon, plErrors, plDashboard, plSetup, plTutor, plLegal, plPanel, plAiEditor, plCourses, plFeatures)

interface Language {
  language_code: string; language_name: string; native_name: string
  flag_svg_code: string; completion_percent: number; translated_keys: number
  total_keys: number; active: boolean
}
interface Namespace {
  namespace_code: string; name: string; description: string
  icon: string; sort_order: number; key_count: number
}
interface TranslationItem {
  key_id: string | null; key_path: string; namespace: string
  de_value: string; translated_value: string
}

const languages = ref<Language[]>([])
const dbNamespaces = ref<Namespace[]>([])
const selectedLanguage = ref('en')
const selectedNamespace = ref('')
const translations = ref<TranslationItem[]>([])
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = 100
const totalKeys = ref(0)
const isLoading = ref(false)
const isSyncing = ref(false)
const statusMessage = ref<{ type: 'success' | 'error', text: string } | null>(null)
const editingKey = ref<string | null>(null)
const editValue = ref('')
const editInput = ref<HTMLInputElement | null>(null)

// Flatten helper
function flattenMessages(obj: Record<string, any>, prefix = ''): Record<string, string> {
  const result: Record<string, string> = {}
  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      Object.assign(result, flattenMessages(value, fullKey))
    } else if (typeof value === 'string') {
      result[fullKey] = value
    }
  }
  return result
}

const allLocaleMessages: Record<string, Record<string, string>> = {
  de: flattenMessages(deMessages),
  en: flattenMessages(enMessages),
  pl: flattenMessages(plMessages)
}

// Computed

const allFilteredTranslations = computed(() => {
  let items = translations.value

  if (selectedNamespace.value) {
    items = items.filter(item => item.namespace === selectedNamespace.value)
  }

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    items = items.filter(item =>
      item.key_path.toLowerCase().includes(q) ||
      item.de_value?.toLowerCase().includes(q) ||
      item.translated_value?.toLowerCase().includes(q)
    )
  }

  return items
})

const filteredCount = computed(() => allFilteredTranslations.value.length)

const paginatedTranslations = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return allFilteredTranslations.value.slice(start, start + pageSize)
})

const groupedTranslations = computed(() => {
  const groups: Record<string, TranslationItem[]> = {}
  paginatedTranslations.value.forEach(item => {
    if (!groups[item.namespace]) groups[item.namespace] = []
    groups[item.namespace].push(item)
  })
  return groups
})

const totalPages = computed(() => Math.ceil(filteredCount.value / pageSize))

// Methods
function getNamespaceIcon(ns: string): string {
  return dbNamespaces.value.find(n => n.namespace_code === ns)?.icon || '📁'
}

function getNamespaceName(ns: string): string {
  return dbNamespaces.value.find(n => n.namespace_code === ns)?.name || ns
}

function getShortKey(keyPath: string, namespace: string): string {
  // Strip the namespace prefix from the display key
  if (keyPath.startsWith(namespace + '.')) {
    return keyPath.slice(namespace.length + 1)
  }
  return keyPath
}

async function loadLanguages() {
  try {
    const response = await http.get('/i18n/languages')
    languages.value = response.data.data || []

    if (languages.value.length > 0) {
      const en = languages.value.find(l => l.language_code === 'en')
      const nonDe = languages.value.find(l => l.language_code !== 'de')
      selectedLanguage.value = en?.language_code || nonDe?.language_code || 'de'
    }
  } catch (error) {
    console.error('Failed to load languages:', error)
  }
}

async function loadNamespaces() {
  try {
    const response = await http.get('/i18n/admin/namespaces')
    dbNamespaces.value = response.data.data || []
  } catch (error) {
    console.error('Failed to load namespaces:', error)
  }
}

async function loadTranslations() {
  if (!selectedLanguage.value) return

  isLoading.value = true
  try {
    // Fetch ALL keys from DB + translation bundle for selected language
    const [keysResponse, bundleResponse] = await Promise.all([
      http.get('/i18n/admin/keys', { params: { limit: 10000 } }),
      http.get(`/i18n/bundle/${selectedLanguage.value}`)
    ])
    const dbKeys = keysResponse.data.data?.keys || []
    const dbBundle = flattenMessages(bundleResponse.data.data || {})

    // Also fetch German bundle if viewing non-German language
    let deBundle: Record<string, string> = {}
    if (selectedLanguage.value !== 'de') {
      const deBundleResp = await http.get('/i18n/bundle/de')
      deBundle = flattenMessages(deBundleResp.data.data || {})
    }

    const items: TranslationItem[] = []
    for (const key of dbKeys) {
      const keyPath = key.key_path
      const namespace = key.namespace_code || 'common'
      // Bundle keys now use key_path directly (matches $t() format)
      const deValue = (selectedLanguage.value === 'de' ? dbBundle[keyPath] : deBundle[keyPath])
        || allLocaleMessages.de[keyPath] || key.primary_value || key.default_value || ''

      let translatedValue = ''
      if (selectedLanguage.value === 'de') {
        translatedValue = deValue
      } else {
        // DB bundle is primary source, local JSON as fallback
        translatedValue = dbBundle[keyPath] || allLocaleMessages[selectedLanguage.value]?.[keyPath] || ''
      }

      items.push({
        key_id: key.key_id,
        key_path: keyPath,
        namespace,
        de_value: deValue,
        translated_value: translatedValue
      })
    }

    translations.value = items
    totalKeys.value = items.length
  } catch (error) {
    console.error('Failed to load translations:', error)
  } finally {
    isLoading.value = false
  }
}

function startEdit(item: TranslationItem) {
  if (!item.key_id) {
    statusMessage.value = { type: 'error', text: 'Key not synced to DB yet. Run Sync first.' }
    setTimeout(() => statusMessage.value = null, 3000)
    return
  }
  editingKey.value = item.key_path
  editValue.value = item.translated_value || ''
  nextTick(() => {
    const el = editInput.value
    if (Array.isArray(el)) {
      (el[0] as HTMLInputElement)?.focus()
    } else if (el) {
      el.focus()
    }
  })
}

function cancelEdit() {
  editingKey.value = null
  editValue.value = ''
}

async function saveTranslation(item: TranslationItem) {
  if (!item.key_id) return
  try {
    await http.put(`/i18n/admin/keys/${item.key_id}/translations/${selectedLanguage.value}`, {
      value: editValue.value
    })

    const idx = translations.value.findIndex(tr => tr.key_path === item.key_path)
    if (idx >= 0) translations.value[idx].translated_value = editValue.value

    // Live-refresh the app-wide i18n so $t() calls update immediately
    const lang = selectedLanguage.value
    const current = i18n.global.getLocaleMessage(lang) as Record<string, string>
    current[item.key_path] = editValue.value
    i18n.global.setLocaleMessage(lang, { ...current })

    statusMessage.value = { type: 'success', text: t('panel.translations.saved') }
    setTimeout(() => statusMessage.value = null, 2000)
  } catch {
    statusMessage.value = { type: 'error', text: t('panel.translations.saveFailed') }
  } finally {
    cancelEdit()
  }
}

async function forceResync() {
  isSyncing.value = true
  statusMessage.value = { type: 'success', text: t('common.syncing') + '...' }

  try {
    const response = await http.post('/i18n/admin/seed-all-locales', {
      locales: allLocaleMessages,
      primary_language: 'de'
    })

    const result = response.data.data
    statusMessage.value = {
      type: 'success',
      text: `Sync: ${result.keys_created} new, ${result.keys_updated} updated, ${result.translations_set} translations`
    }

    await Promise.all([loadLanguages(), loadNamespaces()])
    await loadTranslations()
  } catch (error: any) {
    console.error('Sync failed:', error)
    statusMessage.value = {
      type: 'error',
      text: `Sync failed: ${error.response?.data?.error?.message || error.message}`
    }
  } finally {
    isSyncing.value = false
    setTimeout(() => statusMessage.value = null, 5000)
  }
}

// Watch
watch(selectedLanguage, () => {
  currentPage.value = 1
  loadTranslations()
})

watch(selectedNamespace, () => { currentPage.value = 1 })

// Init
onMounted(async () => {
  await Promise.all([loadLanguages(), loadNamespaces()])

  if (languages.value.length === 0 || languages.value[0]?.total_keys === 0) {
    await forceResync()
  } else {
    await loadTranslations()
  }
})
</script>

<style scoped>
.panel-translations-page {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
