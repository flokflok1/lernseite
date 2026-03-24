<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  practiceGetQuestionCount,
  type PracticeSessionConfig,
} from '@/infrastructure/api/clients/panel/user/exams'

interface Props {
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  disabled: false,
})

const emit = defineEmits<{
  start: [config: PracticeSessionConfig]
}>()

const { t } = useI18n()

// State
const totalCount = ref(0)
const order = ref<'sequential' | 'mixed'>('mixed')
const mode = ref<'discover' | 'strengthen' | 'exam_ready'>('discover')
const selectedCount = ref<number | null>(20)
const timeLimit = ref<number | null>(null)
const isExpanded = ref(false)

// Question count options (null = endless)
const countOptions = computed(() => [
  { value: 10, label: '10' },
  { value: 20, label: '20' },
  { value: 40, label: '40' },
  { value: 100, label: '100' },
  { value: totalCount.value, label: t('panel.examTrainer.practice.countAll', { count: totalCount.value }) },
  { value: null, label: t('panel.examTrainer.practice.countEndless') },
])

const timeLimitOptions = [
  { value: null, label: 'panel.examTrainer.practice.timeLimitNone' },
  { value: 30, label: '30m' },
  { value: 45, label: '45m' },
  { value: 90, label: '90m' },
]

// Reset learning mode when switching to sequential
watch(order, (val) => {
  if (val === 'sequential') {
    mode.value = 'discover'
  }
})

onMounted(async () => {
  try {
    totalCount.value = await practiceGetQuestionCount()
  } catch {
    totalCount.value = 0
  }
})

const handleStart = () => {
  const config: PracticeSessionConfig = {
    mode: mode.value,
    order: order.value,
    question_count: selectedCount.value,
    time_limit_minutes: timeLimit.value,
  }
  emit('start', config)
}

const isActive = (current: unknown, target: unknown) =>
  current === target
    ? 'bg-blue-600 text-white border-blue-600'
    : 'bg-[var(--color-surface)] text-[var(--color-text)] border-[var(--color-border)] hover:border-blue-500/50'
</script>

<template>
  <div class="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] transition-all">
    <!-- Collapsed Header -->
    <button
      class="w-full p-5 text-left flex items-center gap-3 hover:bg-[var(--color-background)] rounded-xl transition-colors"
      :disabled="disabled"
      @click="isExpanded = !isExpanded"
    >
      <span class="text-2xl">&#x1F4D6;</span>
      <div class="flex-1">
        <div class="font-semibold text-[var(--color-text)]">
          {{ t('panel.examTrainer.practice.title') }}
        </div>
        <div class="text-sm text-[var(--color-text-secondary)]">
          {{ t('panel.examTrainer.adaptive.modePracticeDesc', { count: totalCount || '...' }) }}
        </div>
      </div>
      <svg
        class="w-5 h-5 text-[var(--color-text-secondary)] transition-transform"
        :class="{ 'rotate-180': isExpanded }"
        fill="none" stroke="currentColor" viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Expanded Config -->
    <div v-if="isExpanded" class="px-5 pb-5 space-y-4 border-t border-[var(--color-border)]">
      <!-- Question Count -->
      <div class="pt-4">
        <div class="text-sm font-medium text-[var(--color-text-secondary)] mb-2">
          {{ t('panel.examTrainer.practice.questionCount') }}
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="opt in countOptions"
            :key="String(opt.value)"
            class="px-3 py-1.5 text-sm rounded-lg border transition-colors"
            :class="isActive(selectedCount, opt.value)"
            @click="selectedCount = opt.value"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>

      <!-- Order -->
      <div>
        <div class="text-sm font-medium text-[var(--color-text-secondary)] mb-2">
          {{ t('panel.examTrainer.practice.filter') }}
        </div>
        <div class="flex gap-2">
          <button
            class="px-3 py-1.5 text-sm rounded-lg border transition-colors"
            :class="isActive(order, 'sequential')"
            @click="order = 'sequential'"
          >
            {{ t('panel.examTrainer.practice.orderSequential') }}
          </button>
          <button
            class="px-3 py-1.5 text-sm rounded-lg border transition-colors"
            :class="isActive(order, 'mixed')"
            @click="order = 'mixed'"
          >
            {{ t('panel.examTrainer.practice.orderMixed') }}
          </button>
        </div>
      </div>

      <!-- Learning Mode (only when mixed) -->
      <div v-if="order === 'mixed'">
        <div class="text-sm font-medium text-[var(--color-text-secondary)] mb-2">
          {{ t('panel.examTrainer.practice.learningMode') }}
        </div>
        <div class="flex gap-2">
          <button
            class="px-3 py-1.5 text-sm rounded-lg border transition-colors"
            :class="isActive(mode, 'discover')"
            @click="mode = 'discover'"
          >
            {{ t('panel.examTrainer.practice.modeDiscover') }}
          </button>
          <button
            class="px-3 py-1.5 text-sm rounded-lg border transition-colors"
            :class="isActive(mode, 'strengthen')"
            @click="mode = 'strengthen'"
          >
            {{ t('panel.examTrainer.practice.modeStrengthen') }}
          </button>
          <button
            class="px-3 py-1.5 text-sm rounded-lg border transition-colors"
            :class="isActive(mode, 'exam_ready')"
            @click="mode = 'exam_ready'"
          >
            {{ t('panel.examTrainer.practice.modeExamReady') }}
          </button>
        </div>
      </div>

      <!-- Time Limit -->
      <div>
        <div class="text-sm font-medium text-[var(--color-text-secondary)] mb-2">
          {{ t('panel.examTrainer.practice.timeLimit') }}
        </div>
        <div class="flex gap-2">
          <button
            v-for="opt in timeLimitOptions"
            :key="String(opt.value)"
            class="px-3 py-1.5 text-sm rounded-lg border transition-colors"
            :class="isActive(timeLimit, opt.value)"
            @click="timeLimit = opt.value"
          >
            {{ opt.value === null ? t(opt.label) : opt.label }}
          </button>
        </div>
      </div>

      <!-- Start Button -->
      <button
        class="w-full py-3 rounded-xl bg-blue-600 text-white font-semibold
               hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="disabled"
        @click="handleStart"
      >
        {{ t('panel.examTrainer.practice.startButton') }}
      </button>
    </div>
  </div>
</template>
