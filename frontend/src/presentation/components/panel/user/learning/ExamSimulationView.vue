<script setup lang="ts">
/**
 * KI-Prufungssimulation Page
 *
 * Allows users to:
 * - View detected exam context (profession, level, weak/strong topics)
 * - Configure exam simulation (smart/manual mode)
 * - Generate AI-powered exams
 * - Take exam attempts and view results
 */

import ExamContextSidebar from '@/presentation/components/panel/user/learning/exam/ExamContextSidebar.vue'
import ExamQuestionPlayer from '@/presentation/components/panel/user/learning/exam/ExamQuestionPlayer.vue'
import ExamResultsView from '@/presentation/components/panel/user/learning/exam/ExamResultsView.vue'
import { useExamSimulation } from '@/presentation/components/panel/user/learning/composables/useExamSimulation'

const {
  // Route/Auth
  isCreator,
  isStudent,

  // State
  loading,
  generating,
  examContext,
  simulations,
  currentSimulation,
  currentAttempt,
  questions,
  userAnswers,
  showResults,
  attemptResult,
  error,

  // Configuration
  mode,
  difficulty,
  timeLimit,
  customFocus,

  // UI State
  activeTab,
  currentQuestionIndex,

  // Actions
  createNewSimulation,
  startExam,
  submitExam,
  selectSimulation,
  goBack,
  dismissError,
  returnToOverview,

  // Utilities
  getDifficultyLabel,
  getStatusLabel,
  getStatusColor
} = useExamSimulation()
</script>

<template>
  <div class="exam-simulation-page min-h-screen bg-gray-50 py-8">
    <div class="max-w-6xl mx-auto px-4">
      <!-- Header -->
      <div class="mb-8">
        <button
          @click="goBack"
          class="text-gray-600 hover:text-gray-900 mb-4 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ $t('examSimulation.backToCourse') }}
        </button>
        <h1 class="text-3xl font-bold text-gray-900">{{ $t('examSimulation.title') }}</h1>
        <p class="text-gray-600 mt-2">{{ $t('examSimulation.description') }}</p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <p class="text-red-800">{{ error }}</p>
        <button @click="dismissError" class="text-red-600 hover:text-red-800 mt-2 text-sm">
          {{ $t('examSimulation.close') }}
        </button>
      </div>

      <!-- Main Content -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Sidebar -->
        <ExamContextSidebar :exam-context="examContext" />

        <!-- Main Content Area -->
        <div class="lg:col-span-2">
          <!-- Student Notice -->
          <div v-if="isStudent && simulations.length === 0" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6 text-center">
            <h3 class="text-lg font-semibold text-yellow-800 mb-2">{{ $t('examSimulation.noExamsAvailable') }}</h3>
            <p class="text-yellow-700">{{ $t('examSimulation.noExamsAvailableDesc') }}</p>
          </div>

          <!-- Tabs -->
          <div v-if="isCreator || simulations.length > 0" class="bg-white rounded-lg shadow mb-6">
            <div class="border-b flex">
              <button
                @click="activeTab = 'overview'"
                :class="['px-6 py-4 text-sm font-medium', activeTab === 'overview' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700']"
              >
                {{ $t('examSimulation.tabs.overview') }}
              </button>
              <button
                v-if="isCreator"
                @click="activeTab = 'config'"
                :class="['px-6 py-4 text-sm font-medium', activeTab === 'config' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700']"
              >
                {{ $t('examSimulation.tabs.newSimulation') }}
              </button>
              <button
                v-if="currentSimulation?.status === 'ready'"
                @click="activeTab = 'exam'"
                :class="['px-6 py-4 text-sm font-medium', activeTab === 'exam' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700']"
              >
                {{ $t('examSimulation.tabs.exam') }}
              </button>
              <button
                @click="activeTab = 'history'"
                :class="['px-6 py-4 text-sm font-medium', activeTab === 'history' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700']"
              >
                {{ $t('examSimulation.tabs.history') }}
              </button>
            </div>

            <!-- Tab Content -->
            <div class="p-6">
              <!-- Overview Tab -->
              <div v-if="activeTab === 'overview'">
                <h3 class="text-lg font-semibold mb-4">{{ $t('examSimulation.overview.title') }}</h3>

                <div v-if="simulations.length === 0" class="text-center py-10">
                  <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p class="text-gray-500 mb-4">{{ $t('examSimulation.overview.noSimulations') }}</p>
                  <button @click="activeTab = 'config'" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    {{ $t('examSimulation.overview.createFirst') }}
                  </button>
                </div>

                <div v-else class="space-y-4">
                  <div
                    v-for="sim in simulations"
                    :key="sim.simulation_id"
                    @click="selectSimulation(sim)"
                    class="border rounded-lg p-4 cursor-pointer hover:border-blue-500 transition-colors"
                    :class="{ 'border-blue-500 bg-blue-50': currentSimulation?.simulation_id === sim.simulation_id }"
                  >
                    <div class="flex items-start justify-between">
                      <div>
                        <h4 class="font-medium">{{ sim.title }}</h4>
                        <p class="text-sm text-gray-500">{{ new Date(sim.created_at).toLocaleDateString('de-DE') }}</p>
                      </div>
                      <span :class="['px-2 py-1 text-xs rounded-full', getStatusColor(sim.status)]">
                        {{ getStatusLabel(sim.status) }}
                      </span>
                    </div>
                    <div class="mt-2 flex items-center gap-4 text-sm text-gray-600">
                      <span>{{ getDifficultyLabel(sim.config.difficulty) }}</span>
                      <span>{{ sim.config.time_limit_minutes }} {{ $t('examSimulation.overview.minutes') }}</span>
                      <span v-if="sim.attempt_count > 0">{{ $t('examSimulation.overview.attempts', { count: sim.attempt_count }) }}</span>
                      <span v-if="sim.best_score" class="text-green-600 font-medium">{{ $t('examSimulation.overview.best') }} {{ Math.round(sim.best_score) }}%</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Config Tab -->
              <div v-else-if="activeTab === 'config'">
                <h3 class="text-lg font-semibold mb-6">{{ $t('examSimulation.config.title') }}</h3>

                <!-- Mode Selection -->
                <div class="mb-6">
                  <label class="block text-sm font-medium text-gray-700 mb-3">{{ $t('examSimulation.config.mode') }}</label>
                  <div class="grid grid-cols-2 gap-4">
                    <button
                      @click="mode = 'smart'"
                      :class="['p-4 border-2 rounded-lg text-left transition-colors', mode === 'smart' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300']"
                    >
                      <div class="font-medium">{{ $t('examSimulation.config.smartMode') }}</div>
                      <p class="text-sm text-gray-500 mt-1">{{ $t('examSimulation.config.smartModeDesc') }}</p>
                    </button>
                    <button
                      @click="mode = 'manual'"
                      :class="['p-4 border-2 rounded-lg text-left transition-colors', mode === 'manual' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300']"
                    >
                      <div class="font-medium">{{ $t('examSimulation.config.manualMode') }}</div>
                      <p class="text-sm text-gray-500 mt-1">{{ $t('examSimulation.config.manualModeDesc') }}</p>
                    </button>
                  </div>
                </div>

                <!-- Difficulty -->
                <div class="mb-6">
                  <label class="block text-sm font-medium text-gray-700 mb-3">{{ $t('examSimulation.config.difficulty') }}</label>
                  <div class="flex gap-4">
                    <button
                      v-for="diff in ['easy', 'realistic', 'hard'] as const"
                      :key="diff"
                      @click="difficulty = diff"
                      :class="['flex-1 py-3 px-4 border-2 rounded-lg text-center transition-colors', difficulty === diff ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300']"
                    >
                      {{ getDifficultyLabel(diff) }}
                    </button>
                  </div>
                </div>

                <!-- Time Limit -->
                <div class="mb-6">
                  <label class="block text-sm font-medium text-gray-700 mb-3">
                    {{ $t('examSimulation.config.timeLimit', { minutes: timeLimit }) }}
                  </label>
                  <input type="range" v-model="timeLimit" min="15" max="180" step="15" class="w-full" />
                  <div class="flex justify-between text-xs text-gray-500 mt-1">
                    <span>15 {{ $t('examSimulation.overview.minutes') }}</span>
                    <span>90 {{ $t('examSimulation.overview.minutes') }}</span>
                    <span>180 {{ $t('examSimulation.overview.minutes') }}</span>
                  </div>
                </div>

                <!-- Manual Focus Distribution -->
                <div v-if="mode === 'manual' && Object.keys(customFocus).length > 0" class="mb-6">
                  <label class="block text-sm font-medium text-gray-700 mb-3">
                    {{ $t('examSimulation.config.topicDistribution') }}
                  </label>
                  <div class="space-y-3">
                    <div v-for="(percent, topic) in customFocus" :key="topic" class="flex items-center gap-3">
                      <span class="w-32 text-sm">{{ topic }}</span>
                      <input type="range" v-model.number="customFocus[topic]" min="0" max="100" step="5" class="flex-1" />
                      <span class="w-12 text-sm font-medium text-right">{{ percent }}%</span>
                    </div>
                  </div>
                </div>

                <!-- Generate Button -->
                <button
                  @click="createNewSimulation"
                  :disabled="generating"
                  class="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <template v-if="generating">
                    <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    {{ $t('examSimulation.config.generating') }}
                  </template>
                  <template v-else>
                    {{ $t('examSimulation.config.generateExam') }}
                  </template>
                </button>
              </div>

              <!-- Exam Tab -->
              <div v-else-if="activeTab === 'exam' && currentSimulation?.status === 'ready'">
                <!-- Not Started -->
                <div v-if="!currentAttempt && !showResults" class="text-center py-10">
                  <h3 class="text-xl font-semibold mb-2">{{ currentSimulation.title }}</h3>
                  <p class="text-gray-500 mb-6">
                    {{ currentSimulation.result?.questions?.length || 0 }} {{ $t('examSimulation.exam.questions') }} |
                    {{ currentSimulation.result?.total_points || 100 }} {{ $t('examSimulation.exam.points') }} |
                    {{ currentSimulation.config.time_limit_minutes }} {{ $t('examSimulation.overview.minutes') }}
                  </p>
                  <button @click="startExam" class="bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 text-lg">
                    {{ $t('examSimulation.exam.startExam') }}
                  </button>
                </div>

                <!-- Exam in Progress -->
                <ExamQuestionPlayer
                  v-else-if="currentAttempt && !showResults"
                  :questions="questions"
                  :current-question-index="currentQuestionIndex"
                  :user-answers="userAnswers"
                  @update:current-question-index="currentQuestionIndex = $event"
                  @update:user-answers="userAnswers = $event"
                  @submit="submitExam"
                />

                <!-- Results -->
                <ExamResultsView
                  v-else-if="showResults && attemptResult"
                  :attempt-result="attemptResult"
                  @back-to-overview="returnToOverview"
                />
              </div>

              <!-- History Tab -->
              <div v-else-if="activeTab === 'history'">
                <h3 class="text-lg font-semibold mb-4">{{ $t('examSimulation.history.title') }}</h3>

                <div v-if="simulations.length === 0" class="text-center py-10 text-gray-500">
                  {{ $t('examSimulation.history.noExams') }}
                </div>

                <div v-else class="space-y-4">
                  <div
                    v-for="sim in simulations.filter(s => s.attempt_count > 0)"
                    :key="sim.simulation_id"
                    class="border rounded-lg p-4"
                  >
                    <div class="flex items-start justify-between mb-2">
                      <h4 class="font-medium">{{ sim.title }}</h4>
                      <span class="text-sm text-gray-500">{{ $t('examSimulation.history.attempts', { count: sim.attempt_count }) }}</span>
                    </div>
                    <div class="flex items-center gap-6 text-sm">
                      <div>
                        <span class="text-gray-500">{{ $t('examSimulation.history.best') }}</span>
                        <span class="font-medium text-green-600 ml-1">{{ sim.best_score ? Math.round(sim.best_score) + '%' : '-' }}</span>
                      </div>
                      <div>
                        <span class="text-gray-500">{{ $t('examSimulation.history.average') }}</span>
                        <span class="font-medium ml-1">{{ sim.avg_score ? Math.round(sim.avg_score) + '%' : '-' }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.exam-simulation-page {
  font-family: 'Inter', system-ui, sans-serif;
}

input[type="range"] {
  @apply h-2 rounded-lg appearance-none cursor-pointer bg-gray-200;
}

input[type="range"]::-webkit-slider-thumb {
  @apply w-4 h-4 bg-blue-600 rounded-full appearance-none cursor-pointer;
}
</style>
