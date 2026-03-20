<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  trainerBrowseQuestions,
  trainerGetDashboard,
  trainerListExams,
  type BrowseQuestion,
  type TrainerExam,
} from '@/infrastructure/api/clients/panel/user/exams'

const emit = defineEmits<{
  'practice-question': [questionId: string]
}>()

const { t, locale } = useI18n()

// State
const questions = ref<BrowseQuestion[]>([])
const total = ref(0)
const page = ref(1)
const perPage = ref(20)
const isLoading = ref(false)

// Filters
const selectedTopic = ref('')
const selectedExam = ref('')
const selectedStatus = ref<'all' | 'unseen' | 'weak' | 'mastered'>('all')

// Options for dropdowns
const topicOptions = ref<Array<{ key: string; label: string }>>([])
const examOptions = ref<TrainerExam[]>([])

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage.value)))

const statusTabs = computed(() => [
  { key: 'all' as const, label: t('panel.examTrainer.questionBrowser.statusAll') },
  { key: 'unseen' as const, label: t('panel.examTrainer.questionBrowser.statusUnseen') },
  { key: 'weak' as const, label: t('panel.examTrainer.questionBrowser.statusWeak') },
  { key: 'mastered' as const, label: t('panel.examTrainer.questionBrowser.statusMastered') },
])

onMounted(async () => {
  const [dashboard, exams] = await Promise.all([
    trainerGetDashboard(),
    trainerListExams(),
  ])
  topicOptions.value = (dashboard.topics || []).map((tp: { topic: string; display_name?: Record<string, string> }) => ({
    key: tp.topic,
    label: tp.display_name?.[locale.value] || tp.display_name?.de || tp.topic,
  }))
  examOptions.value = exams
  await loadQuestions()
})

const loadQuestions = async () => {
  isLoading.value = true
  try {
    const result = await trainerBrowseQuestions({
      topic: selectedTopic.value || undefined,
      exam_id: selectedExam.value || undefined,
      status: selectedStatus.value,
      page: page.value,
      per_page: perPage.value,
    })
    questions.value = result.questions
    total.value = result.total
  } finally {
    isLoading.value = false
  }
}

watch([selectedTopic, selectedExam, selectedStatus], () => {
  page.value = 1
  loadQuestions()
})

watch(page, () => loadQuestions())

const questionStatus = (q: BrowseQuestion) => {
  if (!q.times_seen) return 'unseen'
  const rate = (q.times_correct ?? 0) / Math.max(q.times_seen, 1)
  return rate >= 0.5 ? 'mastered' : 'weak'
}

const statusDotClass = (q: BrowseQuestion) => {
  const s = questionStatus(q)
  if (s === 'mastered') return 'bg-emerald-500'
  if (s === 'weak') return 'bg-red-500'
  return 'bg-gray-400'
}

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return ''
  const loc = locale.value === 'de' ? 'de-DE' : locale.value === 'pl' ? 'pl-PL' : 'en-US'
  return new Date(dateStr).toLocaleDateString(loc)
}

const truncate = (text: string, max: number = 120) => {
  if (!text) return ''
  const plain = text.replace(/<[^>]+>/g, '')
  return plain.length > max ? plain.slice(0, max) + '...' : plain
}

const correctPercent = (q: BrowseQuestion) => {
  if (!q.times_seen) return 0
  return Math.round((q.times_correct ?? 0) / Math.max(q.times_seen, 1) * 100)
}
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-[var(--color-text)]">
        {{ t('panel.examTrainer.questionBrowser.title') }}
      </h2>
      <span class="text-sm text-[var(--color-text-secondary)]">
        {{ t('panel.examTrainer.questionBrowser.questionCount', { total }) }}
      </span>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-3">
      <!-- Topic dropdown -->
      <select
        v-model="selectedTopic"
        class="px-3 py-2 text-sm rounded-lg border border-[var(--color-border)]
               bg-[var(--color-surface)] text-[var(--color-text)]"
      >
        <option value="">{{ t('panel.examTrainer.questionBrowser.allTopics') }}</option>
        <option v-for="opt in topicOptions" :key="opt.key" :value="opt.key">
          {{ opt.label }}
        </option>
      </select>

      <!-- Exam dropdown -->
      <select
        v-model="selectedExam"
        class="px-3 py-2 text-sm rounded-lg border border-[var(--color-border)]
               bg-[var(--color-surface)] text-[var(--color-text)]"
      >
        <option value="">{{ t('panel.examTrainer.questionBrowser.allExams') }}</option>
        <option v-for="ex in examOptions" :key="ex.exam_id" :value="ex.exam_id">
          {{ ex.title }} ({{ ex.year }})
        </option>
      </select>

      <!-- Status tabs -->
      <div class="flex rounded-lg border border-[var(--color-border)] overflow-hidden">
        <button
          v-for="tab in statusTabs"
          :key="tab.key"
          class="px-3 py-2 text-sm transition-colors"
          :class="selectedStatus === tab.key
            ? 'bg-blue-500/20 text-blue-400'
            : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-background)]'"
          @click="selectedStatus = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
    </div>

    <!-- Empty state -->
    <div
      v-else-if="questions.length === 0"
      class="text-center py-12 text-[var(--color-text-secondary)]"
    >
      {{ t('panel.examTrainer.questionBrowser.noResults') }}
    </div>

    <!-- Question list -->
    <div v-else class="space-y-2">
      <div
        v-for="q in questions"
        :key="q.question_id"
        class="p-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]
               hover:border-blue-500/30 transition-all cursor-pointer"
        @click="emit('practice-question', q.question_id)"
      >
        <div class="flex items-start gap-3">
          <!-- Status dot -->
          <span
            class="mt-1.5 w-2.5 h-2.5 rounded-full shrink-0"
            :class="statusDotClass(q)"
          />

          <div class="flex-1 min-w-0">
            <!-- Question header -->
            <div class="flex items-center gap-2 mb-1">
              <span class="text-xs font-mono text-[var(--color-text-secondary)]">
                {{ q.question_number || '#' }}
              </span>
              <span
                class="text-xs px-1.5 py-0.5 rounded
                       bg-[var(--color-background)] text-[var(--color-text-secondary)]"
              >
                {{ q.points }}P
              </span>
              <span
                v-if="q.scenario_title"
                class="text-xs text-[var(--color-text-secondary)] truncate"
              >
                {{ q.scenario_title }}
              </span>
            </div>

            <!-- Question text preview -->
            <p class="text-sm text-[var(--color-text)] line-clamp-2">
              {{ truncate(q.question_text) }}
            </p>

            <!-- Meta row -->
            <div class="flex items-center gap-3 mt-2 text-xs text-[var(--color-text-secondary)]">
              <span>{{ q.exam_title }} ({{ q.year }})</span>
              <span v-if="q.times_seen">
                {{ t('panel.examTrainer.questionBrowser.seen', { count: q.times_seen }) }}
                &middot;
                {{ t('panel.examTrainer.questionBrowser.correctRate', { rate: correctPercent(q) }) }}
              </span>
              <span v-else class="text-gray-500">
                {{ t('panel.examTrainer.questionBrowser.neverSeen') }}
              </span>
              <span v-if="q.last_seen_at">
                {{ t('panel.examTrainer.questionBrowser.lastSeen', { date: formatDate(q.last_seen_at) }) }}
              </span>
            </div>
          </div>

          <!-- Practice button -->
          <button
            class="shrink-0 px-3 py-1.5 text-xs rounded-lg bg-blue-500/10 text-blue-400
                   hover:bg-blue-500/20 transition-colors"
            @click.stop="emit('practice-question', q.question_id)"
          >
            {{ t('panel.examTrainer.questionBrowser.practice') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 pt-4">
      <button
        :disabled="page <= 1"
        class="px-3 py-1.5 text-sm rounded-lg border border-[var(--color-border)]
               text-[var(--color-text)] disabled:opacity-30"
        aria-label="Previous page"
        @click="page--"
      >
        &#8592;
      </button>
      <span class="text-sm text-[var(--color-text-secondary)]">
        {{ t('panel.examTrainer.questionBrowser.page', { page, pages: totalPages }) }}
      </span>
      <button
        :disabled="page >= totalPages"
        class="px-3 py-1.5 text-sm rounded-lg border border-[var(--color-border)]
               text-[var(--color-text)] disabled:opacity-30"
        aria-label="Next page"
        @click="page++"
      >
        &#8594;
      </button>
    </div>
  </div>
</template>
