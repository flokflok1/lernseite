<!--
  Method Execution Panel - Aufgaben-Panel

  Features:
  - Aufgaben-Zähler (generierte / gesamt)
  - Generierte laden Button (aus DB)
  - Neue erstellen Button
  - Alle anzeigen / Zufällig Modus
  - Dark Mode Support
  - IHK Prüfungsstil
-->

<template>
  <div class="method-panel">
    <!-- Header -->
    <div class="panel-header">
      <div class="header-content">
        <span class="header-icon">📚</span>
        <div>
          <h3 class="header-title">Aufgaben</h3>
          <p class="header-subtitle">Interaktive Übungen zur Lektion</p>
        </div>
      </div>
    </div>

    <!-- Token Balance -->
    <div class="token-section">
      <div class="token-row">
        <span class="token-label">Token-Guthaben</span>
        <span class="token-value" :class="tokenColorClass">
          {{ tokenBalance.toLocaleString() }}
        </span>
      </div>
      <div class="token-bar-bg">
        <div
          class="token-bar-fill"
          :class="tokenBarClass"
          :style="{ width: `${Math.min(tokenBalance / 100, 100)}%` }"
        ></div>
      </div>
      <p v-if="tokenBalance < 500" class="token-warning">
        ⚠️ Tokens fast aufgebraucht!
      </p>
    </div>

    <!-- Task Stats -->
    <div class="stats-section">
      <div class="stats-row">
        <div class="stat-box">
          <span class="stat-number">{{ generatedTasks.length }}</span>
          <span class="stat-label">Generiert</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-box">
          <span class="stat-number">{{ completedCount }}</span>
          <span class="stat-label">Gelöst</span>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-row">
        <button
          @click="loadSavedTasks"
          class="action-btn"
          :disabled="loadingTasks"
        >
          <span v-if="loadingTasks">⏳</span>
          <span v-else>📥</span>
          Gespeicherte laden
        </button>
        <button
          v-if="generatedTasks.length > 0"
          @click="openAllTasksModal"
          class="action-btn"
        >
          📋 Alle ({{ generatedTasks.length }})
        </button>
        <button
          v-if="generatedTasks.length > 1"
          @click="openRandomTask"
          class="action-btn"
        >
          🎲 Zufällig
        </button>
      </div>

    </div>

    <!-- Methods List -->
    <div class="methods-section">
      <div v-if="methods.length === 0" class="empty-message">
        <span class="empty-icon">📭</span>
        <p>Keine Lernmethoden verfügbar</p>
      </div>

      <div
        v-for="method in methods"
        :key="method.method_id"
        class="method-card"
        :class="{
          'method-card--disabled': !canExecute(method),
          'method-card--selected': selectedMethod?.method_id === method.method_id
        }"
      >
        <div class="method-top">
          <div class="method-title-row">
            <span class="method-icon">{{ method.icon || getMethodIcon(method.method_type) }}</span>
            <span class="method-name">{{ cleanMethodTitle(method.method_name, method.method_type) }}</span>
          </div>
          <span class="method-badge method-badge--type">
            LM{{ String(method.method_type).padStart(2, '0') }}
          </span>
        </div>

        <p class="method-desc">{{ getMethodTypeName(method.method_type) }}</p>

        <div class="method-bottom">
          <div class="method-meta">
            <span v-if="method.requires_ai" class="meta-tag">
              🤖 {{ method.token_cost }} Tokens
            </span>
            <span v-if="method.is_premium" class="meta-tag meta-premium">
              ⭐ Premium
            </span>
          </div>
          <button
            class="generate-btn"
            :disabled="!canExecute(method) || isExecuting"
            @click="generateTask(method)"
          >
            <span v-if="isExecuting && selectedMethod?.method_id === method.method_id" class="spinner"></span>
            <span v-else>➕ Neue Aufgabe</span>
          </button>
        </div>

        <p v-if="!canExecute(method)" class="method-error">
          {{ getError(method) }}
        </p>
      </div>
    </div>

    <!-- Recent Tasks Preview -->
    <div v-if="generatedTasks.length > 0" class="recent-section">
      <h4 class="recent-title">Letzte Aufgaben</h4>
      <div class="recent-list">
        <button
          v-for="(task, idx) in recentTasks"
          :key="idx"
          class="recent-item"
          @click="openTask(generatedTasks.length - 1 - idx)"
        >
          <span class="recent-num">{{ generatedTasks.length - idx }}</span>
          <span class="recent-text">{{ truncateText(task.data.question, 35) }}</span>
          <span class="recent-status">{{ task.completed ? '✅' : '⏳' }}</span>
        </button>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="isExecuting" class="loading-overlay">
      <div class="loading-box">
        <div class="loading-spinner"></div>
        <p class="loading-title">Aufgabe wird generiert...</p>
        <p class="loading-hint">Dies kann einige Sekunden dauern</p>
      </div>
    </div>

    <!-- Error Message -->
    <Transition name="slide-up">
      <div v-if="errorMessage" class="error-bar">
        <span>❌ {{ errorMessage }}</span>
        <button @click="errorMessage = null" class="error-close">✕</button>
      </div>
    </Transition>

    <!-- Task Modal -->
    <MathTaskModal
      v-if="showModal && currentTask"
      :task-data="currentTask.data"
      :method-name="currentTask.methodName"
      :tokens-used="currentTask.tokensUsed"
      :task-number="currentTaskIdx + 1"
      :total-tasks="generatedTasks.length"
      @close="closeModal"
      @new-task="generateNewFromModal"
    />

    <!-- All Tasks Modal (Enhanced) -->
    <Teleport to="body">
      <div v-if="showAllModal" class="overlay" @click.self="showAllModal = false">
        <div class="all-modal all-modal--large">
          <div class="all-modal-header">
            <h3>📋 Aufgaben-Manager ({{ generatedTasks.length }})</h3>
            <button @click="showAllModal = false" class="modal-close">✕</button>
          </div>

          <!-- Toolbar -->
          <div class="modal-toolbar">
            <div class="toolbar-left">
              <button
                @click="selectAllTasks"
                class="toolbar-btn"
                :class="{ 'toolbar-btn--active': selectedTaskIds.size === generatedTasks.length && generatedTasks.length > 0 }"
              >
                {{ selectedTaskIds.size === generatedTasks.length && generatedTasks.length > 0 ? '☑️' : '☐' }}
                Alle
              </button>
              <button
                @click="toggleShuffle"
                class="toolbar-btn"
                :class="{ 'toolbar-btn--active': shuffleMode }"
              >
                🔀 Mischen {{ shuffleMode ? 'An' : 'Aus' }}
              </button>
            </div>
            <div class="toolbar-right">
              <span v-if="selectedTaskIds.size > 0" class="selection-info">
                {{ selectedTaskIds.size }} ausgewählt
              </span>
              <button
                v-if="selectedTaskIds.size > 0"
                @click="startRandomFromSelected"
                class="toolbar-btn toolbar-btn--primary"
              >
                🎲 Zufällig starten
              </button>
              <button
                v-if="selectedTaskIds.size > 0"
                @click="deleteSelectedTasks"
                class="toolbar-btn toolbar-btn--danger"
              >
                🗑️ Löschen
              </button>
            </div>
          </div>

          <!-- Task List -->
          <div class="all-modal-body">
            <div v-if="generatedTasks.length === 0" class="empty-tasks">
              <span class="empty-icon">📭</span>
              <p>Keine Aufgaben vorhanden</p>
              <p class="empty-hint">Generiere neue Aufgaben oder lade gespeicherte</p>
            </div>

            <div
              v-for="(task, idx) in generatedTasks"
              :key="idx"
              class="task-row-enhanced"
              :class="{
                'task-row--done': task.completed,
                'task-row--selected': selectedTaskIds.has(idx)
              }"
            >
              <label class="task-checkbox" @click.stop>
                <input
                  type="checkbox"
                  :checked="selectedTaskIds.has(idx)"
                  @change="toggleTaskSelection(idx)"
                />
                <span class="checkmark"></span>
              </label>

              <div class="task-content" @click="openTaskFromAll(idx)">
                <span class="task-num">{{ idx + 1 }}</span>
                <div class="task-details">
                  <p class="task-question">{{ truncateText(task.data.question, 80) }}</p>
                  <div class="task-meta">
                    <span class="meta-method">{{ task.methodName }}</span>
                    <span class="meta-tokens">{{ task.tokensUsed }} Tokens</span>
                    <span class="meta-date">{{ formatDate(task.createdAt) }}</span>
                  </div>
                </div>
                <span class="task-status">{{ task.completed ? '✅' : '⏳' }}</span>
              </div>

              <button
                @click.stop="deleteTask(idx)"
                class="task-delete"
                :disabled="deletingTaskId === (task as any).executionId"
              >
                {{ deletingTaskId === (task as any).executionId ? '⏳' : '🗑️' }}
              </button>
            </div>
          </div>

          <!-- Footer -->
          <div class="all-modal-footer">
            <div class="footer-stats">
              <span>✅ {{ completedCount }} gelöst</span>
              <span>⏳ {{ generatedTasks.length - completedCount }} offen</span>
            </div>
            <button @click="showAllModal = false" class="close-btn">Schließen</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePlayerStore } from '@/store/player.store'
import { useAuthStore } from '@/store/auth.store'
import * as tokensApi from '@/api/tokens.api'
import { getLessonExecutions, deleteExecution, type LearningMethod, type SavedTaskExecution } from '@/api/player.api'
import MathTaskModal from './MathTaskModal.vue'

// Types
interface TaskData {
  title?: string
  question: string
  steps?: any[]
  solution: string
  explanation?: string
}

interface GeneratedTask {
  data: TaskData
  methodName: string
  tokensUsed: number
  completed: boolean
  createdAt: Date
}

// Props
interface Props {
  lessonId: string | number
  methods: LearningMethod[]
}

const props = defineProps<Props>()

// Stores
const playerStore = usePlayerStore()
const authStore = useAuthStore()

// State
const tokenBalance = ref(0)
const selectedMethod = ref<LearningMethod | null>(null)
const generatedTasks = ref<GeneratedTask[]>([])
const currentTaskIdx = ref(0)
const showModal = ref(false)
const showAllModal = ref(false)
const errorMessage = ref<string | null>(null)
const loadingTasks = ref(false)
const shuffleMode = ref(false)
const selectedTaskIds = ref<Set<number>>(new Set())
const deletingTaskId = ref<string | null>(null)

// Computed
const isExecuting = computed(() => playerStore.methodExecuting)

const tokenColorClass = computed(() => {
  if (tokenBalance.value < 500) return 'color-red'
  if (tokenBalance.value < 2000) return 'color-yellow'
  return 'color-green'
})

const tokenBarClass = computed(() => {
  if (tokenBalance.value < 500) return 'bar-red'
  if (tokenBalance.value < 2000) return 'bar-yellow'
  return 'bar-green'
})

const completedCount = computed(() => generatedTasks.value.filter(t => t.completed).length)

const currentTask = computed(() => generatedTasks.value[currentTaskIdx.value] || null)

const recentTasks = computed(() => generatedTasks.value.slice(-3).reverse())

// Tasks for display in modal (shuffled or normal order)
const displayTasks = computed(() => {
  if (!shuffleMode.value) return generatedTasks.value
  // Create shuffled copy
  const shuffled = [...generatedTasks.value]
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
  }
  return shuffled
})

// Method Icons & Names
const methodIcons: Record<number, string> = {
  0: '📖', 1: '📝', 2: '🔄', 3: '📊', 4: '💭', 6: '🎯',
  8: '✏️', 9: '💻', 10: '🌐', 11: '🔧', 12: '🔢', 13: '🃏',
  14: '🎯', 15: '📝', 16: '🔍', 17: '🛠️', 18: '✍️', 19: '📋',
  20: '📑', 21: '⏱️', 22: '❓', 23: '✅', 24: '🎤', 25: '🏆',
  26: '👥', 27: '🤝', 28: '📊', 29: '📓', 30: '📁', 31: '🎓', 32: '🔄'
}

const methodNames: Record<number, string> = {
  0: 'Tiefgehende Erklärung', 1: 'Schritt-für-Schritt', 2: 'Interaktive Theorie',
  3: 'Diagramm/Visualisierung', 4: 'Sokratischer Dialog', 6: 'Beispiel-Szenario',
  8: 'Whiteboard-Aufgabe', 9: 'Code Sandbox', 10: 'Netzwerk-Simulation',
  11: 'IT-Szenario', 12: 'Mathe-Interaktiv', 13: 'Flashcards', 14: 'Drag & Drop',
  15: 'Lückentext', 16: 'Fehleranalyse', 17: 'Hands-on Lab', 18: 'Freitext',
  19: 'IHK-Stil Aufgaben', 20: 'Multi-Step Prüfung', 21: 'Zeitlimit-Training',
  22: 'Prüfungs-Quiz', 23: 'Verständnis-Check', 24: 'Mündliche Erklärung',
  25: 'Kapitel-Endprüfung', 26: 'Peer Instruction', 27: 'Team-Case',
  28: 'Peer Review', 29: 'Lerntagebuch', 30: 'Portfolio', 31: 'Projektbasiert',
  32: 'Inverted Classroom'
}

const getMethodIcon = (type: number | string | undefined): string => {
  if (type === undefined || type === null) return '📚'
  const t = typeof type === 'string' ? parseInt(type, 10) : type
  return isNaN(t) ? '📚' : (methodIcons[t] || '📚')
}

const getMethodTypeName = (type: number | string | undefined): string => {
  if (type === undefined || type === null) return 'Lernmethode'
  const t = typeof type === 'string' ? parseInt(type, 10) : type
  return isNaN(t) ? 'Lernmethode' : (methodNames[t] || `Lernmethode ${t}`)
}

const cleanMethodTitle = (title: string | undefined, methodType: number | string | undefined): string => {
  if (!title) return 'Aufgabe'
  // Remove "LM12:", "LM22:", etc. prefix from title
  const t = typeof methodType === 'string' ? parseInt(methodType, 10) : methodType
  if (t !== undefined && !isNaN(t)) {
    const prefix = `LM${String(t).padStart(2, '0')}:`
    if (title.startsWith(prefix)) {
      return title.substring(prefix.length).trim()
    }
  }
  return title
}

// Methods
const getBadgeClass = (category: string) => {
  const map: Record<string, string> = {
    basis: 'badge-basis',
    premium: 'badge-premium',
    pro: 'badge-pro'
  }
  return map[category] || 'badge-default'
}

const canExecute = (method: LearningMethod): boolean => {
  if (method.is_premium && !authStore.isPremium) return false
  if (method.requires_ai && method.token_cost > tokenBalance.value) return false
  return true
}

const getError = (method: LearningMethod): string => {
  if (method.is_premium && !authStore.isPremium) return '🔒 Premium erforderlich'
  if (method.requires_ai && method.token_cost > tokenBalance.value) {
    return `💰 Nicht genug Tokens (${method.token_cost} benötigt)`
  }
  return ''
}

const generateTask = async (method: LearningMethod) => {
  if (!canExecute(method) || isExecuting.value) return

  selectedMethod.value = method
  errorMessage.value = null

  try {
    const response = await playerStore.executeLearningMethod({
      lesson_id: props.lessonId,
      method_id: method.method_id
    })

    if (playerStore.methodResult) {
      const parsed = parseResult(playerStore.methodResult)
      if (parsed) {
        generatedTasks.value.push({
          data: parsed,
          methodName: method.method_name,
          tokensUsed: response?.tokens_used || 0,
          completed: false,
          createdAt: new Date()
        })
        currentTaskIdx.value = generatedTasks.value.length - 1
        showModal.value = true
      }
    }

    await loadTokenBalance()
  } catch (err: any) {
    errorMessage.value = err.message || 'Fehler beim Generieren'
  }
}

const parseResult = (result: any): TaskData | null => {
  if (!result) return null

  if (typeof result === 'object' && result !== null) {
    if (result.question || result.title || result.steps || result.aufgabe) {
      return {
        title: result.title || result.aufgabe || 'Rechenaufgabe',
        question: result.question || result.aufgabe || result.aufgabenstellung || '',
        steps: result.steps || result.schritte || result.loesung_schritte || [],
        solution: result.solution || result.loesung || result.ergebnis || '',
        explanation: result.explanation || result.erklaerung || null
      }
    }
  }

  if (typeof result === 'string') {
    const match = result.match(/```(?:json)?\s*([\s\S]*?)```/) || result.match(/\{[\s\S]*\}/)
    if (match) {
      try {
        const parsed = JSON.parse(match[1] || match[0])
        return {
          title: parsed.title || parsed.aufgabe || 'Rechenaufgabe',
          question: parsed.question || parsed.aufgabe || parsed.aufgabenstellung || '',
          steps: parsed.steps || parsed.schritte || [],
          solution: parsed.solution || parsed.loesung || parsed.ergebnis || '',
          explanation: parsed.explanation || parsed.erklaerung || null
        }
      } catch (e) {
        // Parse failed
      }
    }
    return { title: 'Aufgabe', question: result, steps: [], solution: '', explanation: null }
  }

  return null
}

const loadSavedTasks = async () => {
  loadingTasks.value = true
  errorMessage.value = null

  try {
    const lessonIdStr = String(props.lessonId)
    const executions = await getLessonExecutions(lessonIdStr)

    if (executions.length === 0) {
      errorMessage.value = 'Keine gespeicherten Aufgaben gefunden. Generiere neue!'
      return
    }

    // Convert saved executions to GeneratedTask format
    for (const exec of executions) {
      // Check if already loaded (by execution_id)
      const exists = generatedTasks.value.some(t =>
        (t as any).executionId === exec.execution_id
      )
      if (exists) continue

      // Parse the AI response
      const parsed = parseResult(exec.ai_response)
      if (parsed) {
        generatedTasks.value.push({
          data: parsed,
          methodName: exec.method_name || 'Rechenaufgabe',
          tokensUsed: exec.total_tokens || 0,
          completed: false,
          createdAt: new Date(exec.executed_at),
          executionId: exec.execution_id  // Store for deduplication
        } as GeneratedTask & { executionId: string })
      }
    }

    if (generatedTasks.value.length > 0) {
      // Success message
      console.log(`Loaded ${executions.length} saved tasks`)
    } else {
      errorMessage.value = 'Keine auswertbaren Aufgaben gefunden.'
    }
  } catch (err: any) {
    console.error('Failed to load saved tasks:', err)
    errorMessage.value = err.message || 'Fehler beim Laden der gespeicherten Aufgaben'
  } finally {
    loadingTasks.value = false
  }
}

const openTask = (idx: number) => {
  currentTaskIdx.value = idx
  showModal.value = true
}

const openTaskFromAll = (idx: number) => {
  currentTaskIdx.value = idx
  showAllModal.value = false
  showModal.value = true
}

const openAllTasksModal = () => {
  showAllModal.value = true
}

const openRandomTask = () => {
  if (generatedTasks.value.length > 0) {
    currentTaskIdx.value = Math.floor(Math.random() * generatedTasks.value.length)
    showModal.value = true
  }
}

const toggleShuffle = () => {
  shuffleMode.value = !shuffleMode.value
}

const toggleTaskSelection = (idx: number) => {
  if (selectedTaskIds.value.has(idx)) {
    selectedTaskIds.value.delete(idx)
  } else {
    selectedTaskIds.value.add(idx)
  }
  // Force reactivity
  selectedTaskIds.value = new Set(selectedTaskIds.value)
}

const selectAllTasks = () => {
  if (selectedTaskIds.value.size === generatedTasks.value.length) {
    selectedTaskIds.value.clear()
  } else {
    selectedTaskIds.value = new Set(generatedTasks.value.map((_, i) => i))
  }
}

const deleteTask = async (idx: number) => {
  const task = generatedTasks.value[idx] as GeneratedTask & { executionId?: string }
  if (!task) return

  // If it has an executionId (from DB), delete from server
  if (task.executionId) {
    deletingTaskId.value = task.executionId
    try {
      await deleteExecution(task.executionId)
    } catch (err) {
      console.error('Failed to delete from server:', err)
    }
    deletingTaskId.value = null
  }

  // Remove from local array
  generatedTasks.value.splice(idx, 1)
  selectedTaskIds.value.delete(idx)
  // Re-index remaining selections
  const newSelected = new Set<number>()
  selectedTaskIds.value.forEach(id => {
    if (id < idx) newSelected.add(id)
    else if (id > idx) newSelected.add(id - 1)
  })
  selectedTaskIds.value = newSelected
}

const deleteSelectedTasks = async () => {
  const indices = Array.from(selectedTaskIds.value).sort((a, b) => b - a)  // Delete from end
  for (const idx of indices) {
    await deleteTask(idx)
  }
  selectedTaskIds.value.clear()
}

const startRandomFromSelected = () => {
  const indices = Array.from(selectedTaskIds.value)
  if (indices.length === 0) {
    openRandomTask()
    return
  }
  currentTaskIdx.value = indices[Math.floor(Math.random() * indices.length)]
  showAllModal.value = false
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const generateNewFromModal = async () => {
  showModal.value = false
  if (selectedMethod.value) {
    await generateTask(selectedMethod.value)
  }
}

const truncateText = (text: string, len: number): string => {
  if (!text) return ''
  return text.length > len ? text.substring(0, len) + '...' : text
}

const formatDate = (date: Date): string => {
  if (!date) return ''
  const d = new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const mins = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (mins < 1) return 'Gerade eben'
  if (mins < 60) return `vor ${mins} Min.`
  if (hours < 24) return `vor ${hours} Std.`
  if (days < 7) return `vor ${days} Tag${days > 1 ? 'en' : ''}`
  return d.toLocaleDateString('de-DE')
}

const loadTokenBalance = async () => {
  try {
    const data = await tokensApi.getMyTokens()
    tokenBalance.value = data.available || 0
  } catch (err) {
    console.error('Token load failed:', err)
  }
}

// Lifecycle
onMounted(async () => {
  if (!authStore.profile) {
    await authStore.loadProfile().catch(() => {})
  }
  await loadTokenBalance()
})
</script>

<style scoped>
/* Base Panel */
.method-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text-primary, #111827);
  position: relative;
  overflow: hidden;
}

/* Header */
.panel-header {
  padding: 1rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, var(--color-surface, #ffffff) 100%);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  font-size: 1.5rem;
}

.header-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0;
}

.header-subtitle {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

/* Token Section */
.token-section {
  padding: 1rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-surface-secondary, #f9fafb);
}

.token-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.token-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
}

.token-value {
  font-size: 0.875rem;
  font-weight: 700;
}

.token-value.color-red { color: #ef4444; }
.token-value.color-yellow { color: #f59e0b; }
.token-value.color-green { color: #10b981; }

.token-bar-bg {
  height: 6px;
  background-color: var(--color-border, #e5e7eb);
  border-radius: 3px;
  overflow: hidden;
}

.token-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.token-bar-fill.bar-red { background-color: #ef4444; }
.token-bar-fill.bar-yellow { background-color: #f59e0b; }
.token-bar-fill.bar-green { background-color: #10b981; }

.token-warning {
  font-size: 0.75rem;
  color: #f59e0b;
  margin: 0.5rem 0 0;
}

/* Stats Section */
.stats-section {
  padding: 1rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-surface, #ffffff);
}

.stats-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  margin-bottom: 1rem;
}

.stat-box {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-primary, #3b82f6);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
}

.stat-divider {
  width: 1px;
  height: 40px;
  background-color: var(--color-border, #e5e7eb);
}

.action-row {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 100px;
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 0.5rem;
  background-color: var(--color-surface-secondary, #f9fafb);
  color: var(--color-text-primary, #111827);
  border: 1px solid var(--color-border, #e5e7eb);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.action-btn:hover:not(:disabled) {
  background-color: var(--color-surface, #ffffff);
  border-color: var(--color-primary, #3b82f6);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* IHK Calculation Practice Section */
.calc-practice-section {
  margin-top: 0.75rem;
}

.calc-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
  border: 2px solid #10b981;
  border-radius: 0.75rem;
  transition: all 0.2s;
  cursor: pointer;
}

.calc-btn:hover {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.calc-icon {
  font-size: 1.5rem;
}

.calc-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
}

.calc-text strong {
  font-size: 0.875rem;
  font-weight: 600;
  color: #059669;
}

.calc-text small {
  font-size: 0.7rem;
  color: var(--color-text-secondary, #6b7280);
}

.calc-badge {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  background-color: #10b981;
  color: white;
  border-radius: 9999px;
  text-transform: uppercase;
}

/* Methods Section */
.methods-section {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.empty-message {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary, #6b7280);
}

.empty-icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.5rem;
}

/* Method Card */
.method-card {
  padding: 1rem;
  margin-bottom: 0.75rem;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.75rem;
  background-color: var(--color-surface, #ffffff);
  transition: all 0.2s;
}

.method-card:hover {
  border-color: var(--color-primary, #3b82f6);
}

.method-card--disabled {
  opacity: 0.6;
}

.method-card--selected {
  border-color: var(--color-primary, #3b82f6);
  background-color: rgba(59, 130, 246, 0.05);
}

.method-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.method-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.method-icon {
  font-size: 1.25rem;
}

.method-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text-primary, #111827);
}

.method-badge {
  font-size: 0.625rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-basis { background-color: rgba(16, 185, 129, 0.15); color: #10b981; }
.badge-premium { background-color: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.badge-pro { background-color: rgba(139, 92, 246, 0.15); color: #8b5cf6; }
.method-badge--type { background-color: rgba(139, 92, 246, 0.2); color: #a78bfa; }
.badge-default { background-color: var(--color-surface-secondary, #f9fafb); color: var(--color-text-secondary, #6b7280); }

.method-desc {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  margin: 0 0 0.75rem;
  line-height: 1.4;
}

.method-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.method-meta {
  display: flex;
  gap: 0.5rem;
}

.meta-tag {
  font-size: 0.7rem;
  color: var(--color-text-secondary, #6b7280);
}

.meta-premium {
  color: #f59e0b;
}

.generate-btn {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 0.5rem;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.method-error {
  margin: 0.5rem 0 0;
  font-size: 0.75rem;
  color: #ef4444;
}

/* Spinner */
.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Recent Section */
.recent-section {
  padding: 1rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-surface-secondary, #f9fafb);
}

.recent-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
  margin: 0 0 0.5rem;
  text-transform: uppercase;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  font-size: 0.75rem;
  text-align: left;
  transition: all 0.2s;
}

.recent-item:hover {
  border-color: var(--color-primary, #3b82f6);
}

.recent-num {
  width: 22px;
  height: 22px;
  background-color: var(--color-primary, #3b82f6);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.7rem;
  flex-shrink: 0;
}

.recent-text {
  flex: 1;
  color: var(--color-text-primary, #111827);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-status {
  flex-shrink: 0;
}

/* Loading Overlay */
.loading-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

:root.dark .loading-overlay {
  background-color: rgba(17, 24, 39, 0.95);
}

.loading-box {
  text-align: center;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-border, #e5e7eb);
  border-top-color: var(--color-primary, #3b82f6);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

.loading-title {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0 0 0.25rem;
}

.loading-hint {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

/* Error Bar */
.error-bar {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  right: 1rem;
  padding: 0.75rem 1rem;
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: #ef4444;
  z-index: 20;
}

.error-close {
  padding: 0.25rem;
  color: #ef4444;
  opacity: 0.7;
  font-size: 1rem;
}

.error-close:hover {
  opacity: 1;
}

/* All Tasks Modal */
.overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.all-modal {
  background-color: var(--color-surface, #ffffff);
  border-radius: 1rem;
  max-width: 500px;
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.all-modal--large {
  max-width: 700px;
  max-height: 85vh;
}

.all-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.all-modal-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  color: var(--color-text-secondary, #6b7280);
  font-size: 1.25rem;
  transition: all 0.2s;
}

.modal-close:hover {
  background-color: var(--color-surface-secondary, #f9fafb);
}

.all-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.task-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  text-align: left;
  transition: all 0.2s;
  background-color: var(--color-surface, #ffffff);
}

.task-row:hover {
  border-color: var(--color-primary, #3b82f6);
}

.task-row--done {
  background-color: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.3);
}

.task-num {
  width: 28px;
  height: 28px;
  background-color: var(--color-primary, #3b82f6);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.task-text {
  flex: 1;
  font-size: 0.875rem;
  color: var(--color-text-primary, #111827);
}

.task-badge {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  flex-shrink: 0;
}

.all-modal-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
  display: flex;
  justify-content: flex-end;
}

.close-btn {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.5rem;
  background-color: var(--color-surface-secondary, #f9fafb);
  color: var(--color-text-primary, #111827);
  border: 1px solid var(--color-border, #e5e7eb);
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: var(--color-surface, #ffffff);
}

/* Transitions */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Enhanced Modal Toolbar */
.modal-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-surface-secondary, #f9fafb);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.toolbar-btn {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  border-radius: 0.375rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  color: var(--color-text-primary, #111827);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.toolbar-btn:hover {
  border-color: var(--color-primary, #3b82f6);
}

.toolbar-btn--active {
  background-color: var(--color-primary, #3b82f6);
  color: white;
  border-color: var(--color-primary, #3b82f6);
}

.toolbar-btn--primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border-color: transparent;
}

.toolbar-btn--danger {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
}

.toolbar-btn--danger:hover {
  background-color: #ef4444;
  color: white;
}

.selection-info {
  font-size: 0.75rem;
  color: var(--color-primary, #3b82f6);
  font-weight: 500;
}

/* Empty Tasks */
.empty-tasks {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary, #6b7280);
}

.empty-tasks .empty-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 0.75rem;
}

.empty-tasks p {
  margin: 0;
}

.empty-hint {
  font-size: 0.875rem;
  margin-top: 0.25rem !important;
}

/* Enhanced Task Row */
.task-row-enhanced {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  background-color: var(--color-surface, #ffffff);
  transition: all 0.2s;
}

.task-row-enhanced:hover {
  border-color: var(--color-primary, #3b82f6);
}

.task-row-enhanced.task-row--done {
  background-color: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.3);
}

.task-row-enhanced.task-row--selected {
  border-color: var(--color-primary, #3b82f6);
  background-color: rgba(59, 130, 246, 0.05);
}

/* Checkbox */
.task-checkbox {
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.task-checkbox input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border, #e5e7eb);
  border-radius: 4px;
  background-color: var(--color-surface, #ffffff);
  transition: all 0.2s;
}

.task-checkbox input:checked ~ .checkmark {
  background-color: var(--color-primary, #3b82f6);
  border-color: var(--color-primary, #3b82f6);
}

.task-checkbox input:checked ~ .checkmark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

/* Task Content */
.task-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  min-width: 0;
}

.task-details {
  flex: 1;
  min-width: 0;
}

.task-question {
  font-size: 0.875rem;
  color: var(--color-text-primary, #111827);
  margin: 0 0 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-meta {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.task-meta span {
  font-size: 0.7rem;
  color: var(--color-text-secondary, #6b7280);
}

.meta-method {
  background-color: var(--color-surface-secondary, #f9fafb);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

.task-status {
  flex-shrink: 0;
}

.task-delete {
  padding: 0.375rem;
  border-radius: 0.375rem;
  background: transparent;
  color: var(--color-text-secondary, #6b7280);
  transition: all 0.2s;
  flex-shrink: 0;
}

.task-delete:hover:not(:disabled) {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.task-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Footer Stats */
.footer-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
}

.all-modal-footer {
  justify-content: space-between;
}
</style>
