<template>
  <div class="renderer">
    <p v-if="taskText" class="task-text">{{ taskText }}</p>

    <!-- Task Checklist -->
    <div v-if="tasks.length" class="task-checklist">
      <h4 class="section-label">{{ t('lesson.methodExecution.renderer.handsOnLab.tasks') }}</h4>
      <div v-for="(task, i) in tasks" :key="i" class="task-item" :class="{ 'task-item--done': taskChecks[i] }">
        <input v-model="taskChecks[i]" type="checkbox" class="task-check" />
        <div class="task-info">
          <span class="task-name">{{ task.title || task }}</span>
          <span v-if="task.hint" class="task-hint">{{ task.hint }}</span>
        </div>
      </div>
    </div>

    <!-- Code Editor -->
    <div class="editor-section">
      <div class="editor-header">
        <h4 class="section-label">{{ t('lesson.methodExecution.renderer.handsOnLab.codeEditor') }}</h4>
        <span class="editor-lang">{{ language }}</span>
      </div>
      <textarea v-model="userCode" class="code-editor" :rows="editorRows" :placeholder="placeholder" />
    </div>

    <!-- Output Console -->
    <div class="console-section">
      <div class="console-header">
        <h4 class="section-label">{{ t('lesson.methodExecution.renderer.handsOnLab.output') }}</h4>
        <button class="run-btn" @click="runCode">
          <span class="run-icon">&#9654;</span> {{ t('lesson.methodExecution.renderer.handsOnLab.run') }}
        </button>
      </div>
      <pre class="console-output" :class="{ 'console--has-output': output }">{{ output || t('lesson.methodExecution.renderer.handsOnLab.noOutput') }}</pre>
    </div>

    <!-- Progress -->
    <div v-if="tasks.length" class="progress-bar-section">
      <div class="progress-track"><div class="progress-fill" :style="{ width: `${progressPercent}%` }" /></div>
      <span class="progress-text">{{ completedTasks }}/{{ tasks.length }} {{ t('lesson.methodExecution.renderer.handsOnLab.tasksCompleted') }}</span>
    </div>

    <!-- Solution -->
    <button v-if="solution" class="solution-btn" @click="showSolution = !showSolution">
      {{ showSolution ? t('lesson.methodExecution.renderer.common.hideSolution') : t('lesson.methodExecution.renderer.common.sampleSolution') }}
    </button>
    <Transition name="fade">
      <div v-if="showSolution && solution" class="solution-box">
        <pre v-if="solution.code" class="sol-code">{{ solution.code }}</pre>
        <p v-if="solution.explanation" class="sol-explanation">{{ solution.explanation }}</p>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { HandsOnLabData, HandsOnLabSolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: HandsOnLabData | null; solution: HandsOnLabSolution | null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const showSolution = ref(false)
const output = ref('')

watch(() => props.data, () => {
  showSolution.value = false
  output.value = ''
  userCode.value = props.data?.starterCode || ''
  taskChecks.value = tasks.value.map(() => false)
}, { deep: true })

const taskText = computed(() => props.data?.task || props.data?.description || '')
const tasks = computed(() => props.data?.tasks || props.data?.checklist || [])
const language = computed(() => props.data?.language || 'code')
const placeholder = computed(() => props.data?.starterCode || '// ' + t('lesson.methodExecution.renderer.handsOnLab.codePlaceholder'))
const editorRows = computed(() => props.data?.editorRows || 12)
const userCode = ref(props.data?.starterCode || '')
const taskChecks = ref<boolean[]>(tasks.value.map(() => false))

const completedTasks = computed(() => taskChecks.value.filter(Boolean).length)
const progressPercent = computed(() => tasks.value.length ? (completedTasks.value / tasks.value.length) * 100 : 0)

// Emit when all tasks are checked off
watch(completedTasks, (count) => {
  if (count === tasks.value.length && count > 0) {
    emit('complete', count, tasks.value.length)
  }
})

function runCode() {
  output.value = t('lesson.methodExecution.renderer.handsOnLab.simulatedOutput') + '\n> ' + (userCode.value.trim().split('\n')[0] || '...')
}
</script>

<style scoped>
.task-text { font-size: 0.9375rem; line-height: 1.75; margin-bottom: 1.25rem; color: var(--color-text-primary); }

.section-label {
  font-size: 0.6875rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--color-accent-light); margin: 0 0 0.5rem;
}

.task-checklist { margin-bottom: 1.25rem; }
.task-item {
  display: flex; align-items: flex-start; gap: 0.625rem; padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0.5rem; margin-bottom: 0.375rem; transition: all 0.2s;
}
.task-item--done { border-color: rgba(16, 185, 129, 0.2); background: rgba(16, 185, 129, 0.04); }
.task-check { width: 1.125rem; height: 1.125rem; accent-color: var(--color-success); flex-shrink: 0; margin-top: 0.125rem; }
.task-name { font-size: 0.875rem; color: var(--color-text-primary); }
.task-item--done .task-name { text-decoration: line-through; opacity: 0.5; }
.task-hint { display: block; font-size: 0.75rem; color: var(--color-text-tertiary); margin-top: 0.125rem; }

.editor-section { margin-bottom: 1rem; }
.editor-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.375rem; }
.editor-lang {
  font-size: 0.625rem; font-weight: 600; padding: 0.125rem 0.5rem;
  background: rgba(99, 102, 241, 0.1); color: var(--color-accent-light);
  border-radius: 1rem; text-transform: uppercase;
}

.code-editor {
  width: 100%; padding: 0.875rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 0.8125rem; line-height: 1.7;
  border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.625rem;
  background: var(--color-code-bg); color: var(--color-code-text); resize: vertical;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.code-editor:focus { outline: none; border-color: rgba(99, 102, 241, 0.4); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1); }

.console-section { margin-bottom: 1.25rem; }
.console-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.375rem; }

.run-btn {
  display: flex; align-items: center; gap: 0.375rem;
  padding: 0.375rem 0.875rem; background: linear-gradient(135deg, #10b981, #059669);
  color: #fff; border: none; border-radius: 0.5rem;
  font-size: 0.75rem; font-weight: 600; cursor: pointer;
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.25); transition: all 0.15s;
}
.run-btn:hover { box-shadow: 0 4px 10px rgba(16, 185, 129, 0.35); transform: translateY(-1px); }
.run-icon { font-size: 0.625rem; }

.console-output {
  margin: 0; padding: 0.875rem;
  background: var(--color-code-bg); color: var(--color-text-tertiary); border-radius: 0.625rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 0.8125rem; line-height: 1.6; min-height: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.04);
  white-space: pre-wrap;
}
.console--has-output { color: #4ade80; }

.progress-bar-section { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; }
.progress-track { flex: 1; height: 3px; background: rgba(255, 255, 255, 0.06); border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #10b981, #34d399); border-radius: 2px; transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
.progress-text { font-size: 0.75rem; color: var(--color-text-tertiary); white-space: nowrap; }

.solution-btn {
  padding: 0.5rem 1.25rem; background: rgba(16, 185, 129, 0.06); color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 0.5rem;
  font-size: 0.8125rem; font-weight: 500; cursor: pointer; transition: all 0.15s;
}
.solution-btn:hover { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3); }

.solution-box {
  margin-top: 1rem; padding: 1rem 1.125rem; background: rgba(16, 185, 129, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.15); border-radius: 0.625rem;
}
.sol-code {
  margin: 0; padding: 0.875rem; background: var(--color-code-bg); color: var(--color-code-text); border-radius: 0.5rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace; font-size: 0.8125rem;
  line-height: 1.7; white-space: pre-wrap; border: 1px solid rgba(255, 255, 255, 0.06);
}
.sol-explanation { margin: 0.75rem 0 0; font-size: 0.8125rem; color: var(--color-text-secondary); font-style: italic; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
