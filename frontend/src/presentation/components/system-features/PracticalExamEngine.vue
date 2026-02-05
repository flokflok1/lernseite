<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Flashcards (Karteikarten)
          </label>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
            Karteikarten mit Spaced-Repetition-Vorbereitung
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Karteikarten
          </label>
          <div class="space-y-3">
            <div
              v-for="(card, index) in methodData.cards"
              :key="index"
              class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800"
            >
              <div class="flex items-center justify-between mb-3">
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Karte {{ index + 1 }}
                </span>
                <button
                  type="button"
                  @click="removeCard(index)"
                  class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                  :disabled="methodData.cards.length <= 1"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div class="space-y-3">
                <div>
                  <label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Vorderseite (Frage)
                  </label>
                  <textarea
                    v-model="card.front"
                    rows="2"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    placeholder="Frage oder Begriff eingeben..."
                    required
                  ></textarea>
                </div>
                <div>
                  <label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Rückseite (Antwort)
                  </label>
                  <textarea
                    v-model="card.back"
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    placeholder="Antwort oder Definition eingeben..."
                    required
                  ></textarea>
                </div>
              </div>
            </div>
          </div>
          <button
            type="button"
            @click="addCard"
            class="mt-3 w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            + Weitere Karteikarte hinzufügen
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
              Karteikarten in zufälliger Reihenfolge anzeigen
            </span>
          </label>
        </div>

        <div>
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.spaced_repetition"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              Spaced Repetition aktivieren (optimierte Wiederholungsintervalle)
            </span>
          </label>
        </div>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/window.store'
import { BaseLearningMethodForm } from '@/presentation/components/learning/editor/forms'

const METHOD_CODE = 13

interface Card {
  front: string
  back: string
}

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const methodData = ref<{
  cards: Card[]
  shuffle: boolean
  spaced_repetition: boolean
}>({
  cards: [
    { front: '', back: '' }
  ],
  shuffle: false,
  spaced_repetition: true
})

const addCard = () => {
  methodData.value.cards.push({ front: '', back: '' })
}

const removeCard = (index: number) => {
  if (methodData.value.cards.length > 1) {
    methodData.value.cards.splice(index, 1)
  }
}

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value = {
      cards: existingData.cards || [{ front: '', back: '' }],
      shuffle: existingData.shuffle || false,
      spaced_repetition: existingData.spaced_repetition !== undefined ? existingData.spaced_repetition : true
    }
  }
})
</script>
