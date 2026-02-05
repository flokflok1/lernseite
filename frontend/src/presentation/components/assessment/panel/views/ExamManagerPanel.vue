<!--
  Admin Exam Manager Panel - Phase C1.3

  Exam management for courses:
  - List all exams for a course
  - Create manual exams
  - Generate AI exams
  - Edit/Delete exams
-->

<template>
  <div class="admin-exam-manager-panel h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header with Course Context -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-4 py-3">
      <p class="text-sm text-[var(--color-text-secondary)]">
        Kurs: <span class="font-medium text-[var(--color-text-primary)]">{{ courseTitle }}</span>
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[var(--color-primary)] mx-auto mb-3"></div>
        <p class="text-sm text-[var(--color-text-secondary)]">Lade Prüfungen...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 p-6">
      <div class="rounded-lg p-4 border" style="background-color: var(--color-error-bg, #fee); border-color: var(--color-error-border, #fcc);">
        <p style="color: var(--color-error-text, #c00);">{{ error }}</p>
        <button
          @click="loadExams"
          class="mt-3 px-3 py-1.5 text-white text-sm rounded transition-colors"
          style="background-color: var(--color-error, #dc2626);"
        >
          Erneut versuchen
        </button>
      </div>
    </div>

    <!-- Exam List -->
    <div v-else class="flex-1 flex flex-col overflow-hidden">
      <!-- Action Bar -->
      <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-4 py-3">
        <div class="flex items-center justify-between">
          <p class="text-sm font-medium text-[var(--color-text-primary)]">
            {{ exams.length }} {{ exams.length === 1 ? 'Prüfung' : 'Prüfungen' }}
          </p>
          <div class="flex gap-2">
            <button
              @click="showCreateDialog = true"
              class="px-3 py-1.5 text-white rounded text-sm transition-colors flex items-center gap-1"
              style="background-color: var(--color-success, #16a34a);"
            >
              <span>+</span>
              <span>Manuelle Prüfung</span>
            </button>
            <button
              @click="showGenerateDialog = true"
              class="px-3 py-1.5 text-white rounded text-sm transition-colors flex items-center gap-1"
              style="background-color: var(--color-primary, #7c3aed);"
            >
              <span>🤖</span>
              <span>KI-Prüfung generieren</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Exams List -->
      <div class="flex-1 overflow-y-auto p-4">
        <!-- Empty State -->
        <div v-if="exams.length === 0" class="text-center py-12">
          <div class="text-6xl mb-4 opacity-30">📝</div>
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-2">Keine Prüfungen vorhanden</h3>
          <p class="text-sm text-[var(--color-text-secondary)] mb-4">
            Erstellen Sie eine manuelle Prüfung oder generieren Sie eine mit KI.
          </p>
        </div>

        <!-- Exam Cards -->
        <div v-else class="space-y-3">
          <div
            v-for="exam in exams"
            :key="exam.exam_id"
            class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)] hover:border-[var(--color-primary)] transition-colors"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <h3 class="font-semibold text-[var(--color-text-primary)]">{{ exam.title }}</h3>
                  <!-- AI Badge -->
                  <span
                    v-if="exam.generated_by_ai"
                    class="px-2 py-0.5 rounded text-xs"
                    style="background-color: var(--color-primary-bg, #ede9fe); color: var(--color-primary-text, #6d28d9);"
                  >
                    🤖 KI-generiert
                  </span>
                  <!-- Published Badge -->
                  <span
                    v-if="exam.published"
                    class="px-2 py-0.5 rounded text-xs"
                    style="background-color: var(--color-success-bg, #dcfce7); color: var(--color-success-text, #15803d);"
                  >
                    ✓ Veröffentlicht
                  </span>
                  <span
                    v-else
                    class="px-2 py-0.5 rounded text-xs"
                    style="background-color: var(--color-warning-bg, #fef3c7); color: var(--color-warning-text, #92400e);"
                  >
                    Entwurf
                  </span>
                </div>

                <p v-if="exam.description" class="text-sm text-[var(--color-text-secondary)] mb-3">
                  {{ exam.description }}
                </p>

                <div class="flex flex-wrap gap-4 text-xs text-[var(--color-text-secondary)]">
                  <div class="flex items-center gap-1">
                    <span>📝</span>
                    <span>{{ exam.question_count }} Fragen</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <span>⏱️</span>
                    <span>{{ exam.duration_minutes }} Min.</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <span>✓</span>
                    <span>{{ exam.passing_score }}% zum Bestehen</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <span>📊</span>
                    <span>{{ exam.total_points }} Punkte</span>
                  </div>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex gap-1 ml-4">
                <button
                  @click="deleteExam(exam)"
                  class="px-2 py-1 text-xs rounded transition-colors"
                  style="color: var(--color-error, #dc2626);"
                  :title="t('panel.actions.delete')"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Exam Dialog -->
    <div v-if="showCreateDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showCreateDialog = false">
      <div class="bg-[var(--color-surface)] rounded-lg p-6 max-w-md w-full mx-4 border border-[var(--color-border)]">
        <h3 class="text-lg font-bold text-[var(--color-text-primary)] mb-4">Manuelle Prüfung erstellen</h3>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Titel *</label>
            <input
              v-model="createForm.title"
              type="text"
              required
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
              placeholder="z.B. Abschlussprüfung Modul 1-3"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Beschreibung</label>
            <textarea
              v-model="createForm.description"
              rows="3"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
              placeholder="Beschreibung der Prüfung..."
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Dauer (Min)</label>
              <input
                v-model.number="createForm.duration_minutes"
                type="number"
                min="5"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Bestehen (%)</label>
              <input
                v-model.number="createForm.passing_score"
                type="number"
                min="0"
                max="100"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
              />
            </div>
          </div>
        </div>

        <div class="flex gap-2 mt-6">
          <button
            @click="createExam"
            :disabled="!createForm.title"
            class="flex-1 px-4 py-2 text-white rounded transition-colors"
            style="background-color: var(--color-success, #16a34a);"
            :class="{ 'opacity-50 cursor-not-allowed': !createForm.title }"
          >
            Erstellen
          </button>
          <button
            @click="showCreateDialog = false"
            class="px-4 py-2 border border-[var(--color-border)] rounded text-[var(--color-text-primary)] transition-colors"
          >
            Abbrechen
          </button>
        </div>
      </div>
    </div>

    <!-- Generate Exam Dialog (AI) -->
    <div v-if="showGenerateDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showGenerateDialog = false">
      <div class="bg-[var(--color-surface)] rounded-lg p-6 max-w-2xl w-full mx-4 border border-[var(--color-border)] max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-bold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
          <span>🤖</span>
          <span>KI-Prüfung generieren</span>
        </h3>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Titel *</label>
            <input
              v-model="generateForm.title"
              type="text"
              required
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
              placeholder="z.B. IHK FISI AP1 Simulation"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Prüfungsstandard *</label>
            <select
              v-model="generateForm.exam_standard"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
            >
              <option value="IHK_FISI_AP1">IHK FISI AP1</option>
              <option value="IHK_FIAE_AP1">IHK FIAE AP1</option>
              <option value="CompTIA_A+">CompTIA A+</option>
              <option value="CompTIA_Network+">CompTIA Network+</option>
              <option value="Abitur_Informatik">Abitur Informatik</option>
              <option value="Custom">Custom</option>
            </select>
          </div>

          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Schwierigkeit</label>
              <select
                v-model="generateForm.difficulty"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
              >
                <option value="beginner">Einsteiger</option>
                <option value="intermediate">Fortgeschritten</option>
                <option value="advanced">Experte</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Dauer (Min)</label>
              <input
                v-model.number="generateForm.duration_minutes"
                type="number"
                min="30"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Bestehen (%)</label>
              <input
                v-model.number="generateForm.passing_score"
                type="number"
                min="0"
                max="100"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">Fragetypen-Verteilung</label>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs text-[var(--color-text-secondary)]">Multiple Choice</label>
                <input
                  v-model.number="generateForm.question_distribution.mcq"
                  type="number"
                  min="0"
                  class="w-full px-2 py-1 text-sm border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
                />
              </div>
              <div>
                <label class="text-xs text-[var(--color-text-secondary)]">Lückentexte</label>
                <input
                  v-model.number="generateForm.question_distribution.fill_blanks"
                  type="number"
                  min="0"
                  class="w-full px-2 py-1 text-sm border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
                />
              </div>
              <div>
                <label class="text-xs text-[var(--color-text-secondary)]">Kurzantworten</label>
                <input
                  v-model.number="generateForm.question_distribution.short_answer"
                  type="number"
                  min="0"
                  class="w-full px-2 py-1 text-sm border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
                />
              </div>
              <div>
                <label class="text-xs text-[var(--color-text-secondary)]">Fallstudien</label>
                <input
                  v-model.number="generateForm.question_distribution.case_study"
                  type="number"
                  min="0"
                  class="w-full px-2 py-1 text-sm border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
                />
              </div>
            </div>
            <p class="text-xs text-[var(--color-text-secondary)] mt-1">
              Gesamt: {{ totalQuestions }} Fragen
            </p>
          </div>
        </div>

        <div class="flex gap-2 mt-6">
          <button
            @click="generateExam"
            :disabled="!generateForm.title || totalQuestions < 5"
            class="flex-1 px-4 py-2 text-white rounded transition-colors flex items-center justify-center gap-2"
            style="background-color: var(--color-primary, #7c3aed);"
            :class="{ 'opacity-50 cursor-not-allowed': !generateForm.title || totalQuestions < 5 }"
          >
            <span>🤖</span>
            <span>Generierung starten</span>
          </button>
          <button
            @click="showGenerateDialog = false"
            class="px-4 py-2 border border-[var(--color-border)] rounded text-[var(--color-text-primary)] transition-colors"
          >
            Abbrechen
          </button>
        </div>

        <div class="mt-4 rounded-lg p-3 border text-xs" style="background-color: var(--color-info-bg, #eff6ff); border-color: var(--color-info-border, #bfdbfe);">
          <p style="color: var(--color-info-text, #1e40af);">
            <strong>Hinweis:</strong> Die KI-Generierung kann 2-5 Minuten dauern. Sie werden benachrichtigt, sobald die Prüfung fertig ist.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  adminListExams,
  adminCreateExam,
  adminDeleteExam,
  adminGenerateExam,
  type Exam,
  type ExamCreateRequest,
  type ExamGenerateRequest
} from '@/application/services/api/admin'

const { t } = useI18n()

interface Props {
  courseId: string
  courseTitle: string
}

const props = defineProps<Props>()

// State
const exams = ref<Exam[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const showCreateDialog = ref(false)
const showGenerateDialog = ref(false)

// Create Form
const createForm = ref<ExamCreateRequest>({
  title: '',
  description: '',
  exam_type: 'practice',
  duration_minutes: 60,
  passing_score: 50,
  total_points: 100,
  published: false
})

// Generate Form
const generateForm = ref<ExamGenerateRequest>({
  title: '',
  description: '',
  exam_standard: 'IHK_FISI_AP1',
  difficulty: 'intermediate',
  duration_minutes: 90,
  passing_score: 50,
  total_points: 100,
  question_distribution: {
    mcq: 20,
    fill_blanks: 8,
    short_answer: 2,
    case_study: 0
  }
})

// Computed
const totalQuestions = computed(() => {
  return Object.values(generateForm.value.question_distribution).reduce((a, b) => a + b, 0)
})

// Methods
const loadExams = async () => {
  loading.value = true
  error.value = null

  try {
    exams.value = await adminListExams(props.courseId)
  } catch (err: any) {
    console.error('Error loading exams:', err)
    error.value = err.response?.data?.message || 'Fehler beim Laden der Prüfungen'
  } finally {
    loading.value = false
  }
}

const createExam = async () => {
  if (!createForm.value.title) return

  try {
    await adminCreateExam(props.courseId, createForm.value)
    showCreateDialog.value = false

    // Reset form
    createForm.value = {
      title: '',
      description: '',
      exam_type: 'practice',
      duration_minutes: 60,
      passing_score: 50,
      total_points: 100,
      published: false
    }

    await loadExams()
  } catch (err: any) {
    console.error('Error creating exam:', err)
    error.value = err.response?.data?.message || t('common.errors.createFailed')
  }
}

const generateExam = async () => {
  if (!generateForm.value.title || totalQuestions.value < 5) return

  try {
    const _result = await adminGenerateExam(props.courseId, generateForm.value)
    showGenerateDialog.value = false

    // Reset form
    generateForm.value = {
      title: '',
      description: '',
      exam_standard: 'IHK_FISI_AP1',
      difficulty: 'intermediate',
      duration_minutes: 90,
      passing_score: 50,
      total_points: 100,
      question_distribution: {
        mcq: 20,
        fill_blanks: 8,
        short_answer: 2,
        case_study: 0
      }
    }

    // Reload in 5 seconds to show placeholder
    setTimeout(() => loadExams(), 5000)
  } catch (err: any) {
    console.error('Error generating exam:', err)
    error.value = err.response?.data?.message || t('common.errors.generateFailed')
  }
}

const deleteExam = async (exam: Exam) => {
  if (!confirm(t('panel.exams.confirmDelete', { title: exam.title }))) return

  try {
    await adminDeleteExam(exam.exam_id)
    await loadExams()
  } catch (err: any) {
    console.error('Error deleting exam:', err)
    error.value = err.response?.data?.message || t('common.errors.deleteFailed')
  }
}

// Lifecycle
onMounted(() => {
  loadExams()
})
</script>
