<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Drag & Drop Aufgaben
          </label>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
            Elemente in richtige Reihenfolge/Kategorie ziehen
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Aufgabenstellung
          </label>
          <textarea
            v-model="methodData.instruction"
            rows="2"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Beschreiben Sie, was der Lernende zuordnen soll..."
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Aufgaben-Typ
          </label>
          <select
            v-model="methodData.task_type"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            required
          >
            <option value="">Typ wählen...</option>
            <option value="categorize">Kategorisieren (Elemente zu Kategorien zuordnen)</option>
            <option value="sequence">Sequenzieren (Elemente in Reihenfolge bringen)</option>
            <option value="match">Zuordnen (Paare bilden)</option>
            <option value="fill_slots">Lücken füllen (Elemente an Positionen ziehen)</option>
          </select>
        </div>

        <div v-if="methodData.task_type === 'categorize'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Kategorien
          </label>
          <div class="space-y-3">
            <div
              v-for="(category, catIndex) in methodData.categories"
              :key="catIndex"
              class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800"
            >
              <div class="flex items-center justify-between mb-3">
                <input
                  v-model="category.name"
                  type="text"
                  class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-medium"
                  placeholder="Kategorie-Name"
                  required
                />
                <button
                  type="button"
                  @click="removeCategory(catIndex)"
                  class="ml-2 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                  :disabled="methodData.categories.length <= 2"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div class="space-y-2">
                <div
                  v-for="(item, itemIndex) in category.items"
                  :key="itemIndex"
                  class="flex items-center space-x-2"
                >
                  <input
                    v-model="category.items[itemIndex]"
                    type="text"
                    class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    placeholder="Element"
                    required
                  />
                  <button
                    type="button"
                    @click="removeItemFromCategory(catIndex, itemIndex)"
                    class="text-gray-400 hover:text-red-600"
                    :disabled="category.items.length <= 1"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <button
                  type="button"
                  @click="addItemToCategory(catIndex)"
                  class="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  + Element hinzufügen
                </button>
              </div>
            </div>
          </div>
          <button
            type="button"
            @click="addCategory"
            class="mt-3 w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            + Kategorie hinzufügen
          </button>
        </div>

        <div v-if="methodData.task_type === 'sequence'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Elemente (in korrekter Reihenfolge)
          </label>
          <div class="space-y-2">
            <div
              v-for="(item, index) in methodData.sequence_items"
              :key="index"
              class="flex items-center space-x-2"
            >
              <span class="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded-full text-sm font-medium">
                {{ index + 1 }}
              </span>
              <input
                v-model="methodData.sequence_items[index]"
                type="text"
                class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Schritt"
                required
              />
              <button
                type="button"
                @click="removeSequenceItem(index)"
                class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                :disabled="methodData.sequence_items.length <= 2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <button
            type="button"
            @click="addSequenceItem"
            class="mt-2 w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            + Element hinzufügen
          </button>
        </div>

        <div v-if="methodData.task_type === 'match'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Zuordnungs-Paare
          </label>
          <div class="space-y-2">
            <div
              v-for="(pair, index) in methodData.match_pairs"
              :key="index"
              class="flex items-center space-x-2"
            >
              <input
                v-model="pair.left"
                type="text"
                class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Begriff"
                required
              />
              <span class="text-gray-400">↔</span>
              <input
                v-model="pair.right"
                type="text"
                class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Zuordnung"
                required
              />
              <button
                type="button"
                @click="removeMatchPair(index)"
                class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                :disabled="methodData.match_pairs.length <= 2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <button
            type="button"
            @click="addMatchPair"
            class="mt-2 w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            + Paar hinzufügen
          </button>
        </div>

        <div>
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.shuffle"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              Elemente mischen (Lernende sehen sie in zufälliger Reihenfolge)
            </span>
          </label>
        </div>

        <div>
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.show_feedback"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              Sofortiges Feedback anzeigen
            </span>
          </label>
        </div>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/store/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 14

interface Category {
  name: string
  items: string[]
}

interface MatchPair {
  left: string
  right: string
}

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const methodData = ref<{
  instruction: string
  task_type: string
  categories: Category[]
  sequence_items: string[]
  match_pairs: MatchPair[]
  shuffle: boolean
  show_feedback: boolean
}>({
  instruction: '',
  task_type: '',
  categories: [
    { name: '', items: [''] },
    { name: '', items: [''] }
  ],
  sequence_items: ['', ''],
  match_pairs: [
    { left: '', right: '' },
    { left: '', right: '' }
  ],
  shuffle: true,
  show_feedback: true
})

// Category methods
const addCategory = () => {
  methodData.value.categories.push({ name: '', items: [''] })
}

const removeCategory = (index: number) => {
  if (methodData.value.categories.length > 2) {
    methodData.value.categories.splice(index, 1)
  }
}

const addItemToCategory = (catIndex: number) => {
  methodData.value.categories[catIndex].items.push('')
}

const removeItemFromCategory = (catIndex: number, itemIndex: number) => {
  if (methodData.value.categories[catIndex].items.length > 1) {
    methodData.value.categories[catIndex].items.splice(itemIndex, 1)
  }
}

// Sequence methods
const addSequenceItem = () => {
  methodData.value.sequence_items.push('')
}

const removeSequenceItem = (index: number) => {
  if (methodData.value.sequence_items.length > 2) {
    methodData.value.sequence_items.splice(index, 1)
  }
}

// Match methods
const addMatchPair = () => {
  methodData.value.match_pairs.push({ left: '', right: '' })
}

const removeMatchPair = (index: number) => {
  if (methodData.value.match_pairs.length > 2) {
    methodData.value.match_pairs.splice(index, 1)
  }
}

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value = {
      instruction: existingData.instruction || '',
      task_type: existingData.task_type || '',
      categories: existingData.categories || [{ name: '', items: [''] }, { name: '', items: [''] }],
      sequence_items: existingData.sequence_items || ['', ''],
      match_pairs: existingData.match_pairs || [{ left: '', right: '' }, { left: '', right: '' }],
      shuffle: existingData.shuffle !== undefined ? existingData.shuffle : true,
      show_feedback: existingData.show_feedback !== undefined ? existingData.show_feedback : true
    }
  }
})
</script>
