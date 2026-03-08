<!--
  TopicTagSelector - Chip-based topic selector with suggestions for exam questions.
-->

<template>
  <div class="space-y-2">
    <!-- Selected topics as chips -->
    <div v-if="modelValue.length > 0" class="flex flex-wrap gap-1.5">
      <span
        v-for="topic in modelValue"
        :key="topic"
        class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
        style="background-color: var(--color-primary-bg, #ede9fe); color: var(--color-primary-text, #6d28d9);"
      >
        {{ topic }}
        <button
          type="button"
          class="ml-0.5 hover:opacity-70 transition-opacity"
          @click="removeTopic(topic)"
        >
          <svg class="w-3 h-3" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 3l6 6M9 3l-6 6" />
          </svg>
        </button>
      </span>
    </div>

    <!-- Input for adding new topics -->
    <div class="relative">
      <input
        v-model="inputValue"
        type="text"
        :placeholder="t('panel.examArchive.questionEditor.addTopic')"
        class="w-full px-3 py-1.5 text-sm rounded border border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text-primary)] placeholder-[var(--color-text-tertiary)] focus:outline-none focus:border-[var(--color-primary)]"
        @keydown.enter.prevent="addTopic(inputValue.trim())"
        @focus="showSuggestions = true"
        @blur="hideSuggestions"
      />

      <!-- Suggestions dropdown -->
      <div
        v-if="showSuggestions && filteredSuggestions.length > 0"
        class="absolute z-10 mt-1 w-full rounded border border-[var(--color-border)] bg-[var(--color-surface)] shadow-lg max-h-40 overflow-y-auto"
      >
        <div class="px-2 py-1 text-[10px] uppercase tracking-wider text-[var(--color-text-tertiary)]">
          {{ t('panel.examArchive.questionEditor.suggestions') }}
        </div>
        <button
          v-for="suggestion in filteredSuggestions"
          :key="suggestion"
          type="button"
          class="block w-full text-left px-3 py-1.5 text-sm text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] transition-colors"
          @mousedown.prevent="addTopic(suggestion)"
        >
          {{ suggestion }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface Props {
  modelValue: string[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const { t } = useI18n()

const inputValue = ref('')
const showSuggestions = ref(false)

const commonTopics = [
  'Netzwerktechnik',
  'IT-Sicherheit',
  'Datenbanken',
  'Programmierung',
  'Betriebssysteme',
  'Virtualisierung',
  'Cloud Computing',
  'RAID/Storage',
  'Projektmanagement',
  'Wirtschaft'
]

const filteredSuggestions = computed(() => {
  const query = inputValue.value.toLowerCase()
  return commonTopics.filter(
    (topic) =>
      !props.modelValue.includes(topic) &&
      (query === '' || topic.toLowerCase().includes(query))
  )
})

function addTopic(topic: string) {
  if (!topic || props.modelValue.includes(topic)) return
  emit('update:modelValue', [...props.modelValue, topic])
  inputValue.value = ''
}

function removeTopic(topic: string) {
  emit('update:modelValue', props.modelValue.filter((t) => t !== topic))
}

function hideSuggestions() {
  setTimeout(() => {
    showSuggestions.value = false
  }, 150)
}
</script>
