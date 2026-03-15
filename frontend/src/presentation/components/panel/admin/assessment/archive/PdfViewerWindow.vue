<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { archiveGetQuestions } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

interface Props {
  window: {
    payload?: {
      examId?: string
      pdfPath?: string
    }
  }
}

const props = defineProps<Props>()
const { t } = useI18n()

const questions = ref<any[]>([])
const loading = ref(false)

const examId = computed(() => props.window.payload?.examId)
const pdfPath = computed(() => props.window.payload?.pdfPath)

onMounted(async () => {
  if (examId.value) {
    loading.value = true
    try {
      const data = await archiveGetQuestions(examId.value)
      questions.value = data || []
    } catch {
      questions.value = []
    } finally {
      loading.value = false
    }
  }
})
</script>

<template>
  <div class="flex h-full bg-gray-900">
    <!-- PDF Viewer -->
    <div class="flex-1 flex items-center justify-center bg-gray-950">
      <iframe
        v-if="pdfPath"
        :src="`/api/v1/admin/exam-archive/file/${examId}`"
        class="w-full h-full border-0"
      />
      <div v-else class="text-gray-500 text-sm">
        {{ t('panel.examArchive.pdfViewer.noQuestions') }}
      </div>
    </div>

    <!-- Questions sidebar -->
    <div class="w-[320px] border-l border-gray-700/50 overflow-y-auto p-4">
      <h3 class="text-sm font-semibold text-gray-200 mb-3">
        {{ t('panel.examArchive.pdfViewer.questions') }}
        <span class="text-gray-500 font-normal">({{ questions.length }})</span>
      </h3>

      <div v-if="loading" class="flex justify-center py-8">
        <div class="animate-spin w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full" />
      </div>

      <div v-else-if="questions.length === 0" class="text-sm text-gray-500 py-4">
        {{ t('panel.examArchive.pdfViewer.noQuestions') }}
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="(q, idx) in questions"
          :key="q.question_id || idx"
          class="bg-gray-800/60 border border-gray-700/40 rounded-lg p-3"
        >
          <div class="text-xs text-indigo-400 mb-1">
            #{{ q.question_number || idx + 1 }}
            <span v-if="q.points" class="text-gray-500 ml-2">{{ q.points }} Pkt.</span>
          </div>
          <div class="text-sm text-gray-200 line-clamp-3">
            {{ q.question_text || q.scenario_title || 'Frage' }}
          </div>
          <div v-if="q.topics?.length" class="flex flex-wrap gap-1 mt-2">
            <span
              v-for="topic in q.topics.slice(0, 3)"
              :key="topic"
              class="text-[10px] px-1.5 py-0.5 rounded bg-gray-700 text-gray-300"
            >
              {{ topic }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
