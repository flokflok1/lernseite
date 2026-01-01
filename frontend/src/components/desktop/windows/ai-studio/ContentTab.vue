<!--
  Content Tab - Lesson Content Editor

  Layout: Drei-Spalten wie ExamsTab
  - Links: Content-Typen & Versionen
  - Mitte: Editor
  - Rechts: Teaching Steps & Aktionen
-->

<template>
  <div class="content-tab">
    <!-- No Lesson Selected -->
    <div v-if="!lesson" class="empty-state">
      <div class="empty-icon">📝</div>
      <h3>Content-Editor</h3>
      <p>Wähle links eine Lektion aus, um den Inhalt zu bearbeiten oder mit KI zu generieren.</p>
    </div>

    <!-- Main Content -->
    <div v-else class="content-main">
      <!-- Header (wie ExamsTab) -->
      <div class="content-header">
        <div class="header-icon">📝</div>
        <div class="header-info">
          <h2>Lektions-Editor</h2>
          <p>{{ lesson.title }} • {{ chapter?.title }}</p>
        </div>
        <div class="header-stats">
          <div class="stat">
            <span class="stat-value">{{ wordCount }}</span>
            <span class="stat-label">Wörter</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ teachingSteps.length }}</span>
            <span class="stat-label">Steps</span>
          </div>
        </div>
      </div>

      <!-- Three-Column Layout -->
      <div class="main-layout">
        <!-- Left: Content Types -->
        <div class="types-panel">
          <div class="panel-header">
            <span class="panel-icon">📚</span>
            <span class="panel-title">Inhaltstypen</span>
          </div>

          <div class="type-list">
            <div
              v-for="type in contentTypes"
              :key="type.id"
              class="type-item"
              :class="{ active: selectedContentType === type.id }"
              @click="selectedContentType = type.id"
            >
              <span class="type-emoji">{{ type.emoji }}</span>
              <span class="type-name">{{ type.name }}</span>
            </div>
          </div>

          <div class="panel-divider"></div>

          <!-- Lesson Info -->
          <div class="info-section">
            <h4>Lektion</h4>
            <div class="info-item">
              <span class="info-label">Typ:</span>
              <span class="info-value">{{ lesson.lm_type || 'LM00' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Status:</span>
              <span class="info-value status-badge" :class="hasContent ? 'saved' : 'draft'">
                {{ hasContent ? 'Gespeichert' : 'Entwurf' }}
              </span>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="quick-actions">
            <button @click="$emit('back-to-chapter')" class="action-btn">
              ← Zurück zum Kapitel
            </button>
          </div>
        </div>

        <!-- Middle: Editor -->
        <div class="editor-panel">
          <div class="panel-header">
            <span class="panel-icon">✏️</span>
            <span class="panel-title">{{ getContentTypeName(selectedContentType) }}</span>
            <button @click="generateContent" class="generate-btn-small" :disabled="isGenerating">
              {{ isGenerating ? '⏳' : '✨' }} KI
            </button>
          </div>

          <!-- Toolbar -->
          <div class="editor-toolbar">
            <button class="toolbar-btn" title="Fett"><strong>B</strong></button>
            <button class="toolbar-btn" title="Kursiv"><em>I</em></button>
            <button class="toolbar-btn" title="Unterstrichen"><u>U</u></button>
            <div class="toolbar-divider"></div>
            <button class="toolbar-btn" title="Liste">📋</button>
            <button class="toolbar-btn" title="Nummerierte Liste">🔢</button>
            <div class="toolbar-divider"></div>
            <button class="toolbar-btn" title="Formel">ƒx</button>
            <button class="toolbar-btn" title="Code">&lt;/&gt;</button>
            <button class="toolbar-btn" title="Bild">🖼️</button>
          </div>

          <!-- Editor Area -->
          <div class="editor-area">
            <textarea
              v-model="contentText"
              class="editor-textarea"
              placeholder="Lektions-Inhalt hier eingeben oder mit KI generieren..."
            ></textarea>
          </div>

          <!-- Editor Footer -->
          <div class="editor-footer">
            <div class="word-count">
              <span>{{ wordCount }} Wörter</span>
              <span>{{ characterCount }} Zeichen</span>
            </div>
            <div class="editor-actions">
              <button @click="resetContent" class="btn-secondary">Zurücksetzen</button>
              <button @click="saveContent" class="btn-primary" :disabled="isSaving">
                {{ isSaving ? 'Speichert...' : 'Speichern' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Right: Teaching Steps -->
        <div class="steps-panel">
          <div class="panel-header">
            <span class="panel-icon">🎯</span>
            <span class="panel-title">Teaching Steps</span>
            <button @click="addTeachingStep" class="add-btn">+</button>
          </div>

          <!-- Steps List -->
          <div class="steps-list">
            <div v-if="teachingSteps.length === 0" class="steps-empty">
              <span class="empty-icon-small">📝</span>
              <p>Keine Steps vorhanden</p>
              <button @click="generateTeachingSteps" class="generate-link">
                ✨ Mit KI generieren
              </button>
            </div>

            <div
              v-for="(step, index) in teachingSteps"
              :key="index"
              class="step-item"
            >
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-content">
                <input
                  v-model="step.title"
                  type="text"
                  class="step-title-input"
                  placeholder="Titel..."
                />
                <textarea
                  v-model="step.speech"
                  class="step-speech-input"
                  rows="2"
                  placeholder="Was der Tutor sagt..."
                ></textarea>
              </div>
              <button @click="removeTeachingStep(index)" class="step-delete">🗑️</button>
            </div>
          </div>

          <!-- Generate Button -->
          <div class="steps-footer">
            <button @click="generateTeachingSteps" class="generate-steps-btn" :disabled="isGenerating">
              ✨ Steps generieren
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Lesson {
  lesson_id: string
  title: string
  lm_type?: string
  content?: Record<string, unknown>
}

interface Chapter {
  chapter_id: string
  title: string
}

interface Course {
  course_id: string
  title: string
}

interface TeachingStep {
  title: string
  speech: string
  animation: string
  duration: string
  whiteboard?: unknown[]
}

interface Props {
  lesson?: Lesson | null
  chapter?: Chapter | null
  course?: Course | null
}

const props = withDefaults(defineProps<Props>(), {
  lesson: null,
  chapter: null,
  course: null
})
const emit = defineEmits<{
  (e: 'save', data: { content: string; teachingSteps: TeachingStep[] }): void
  (e: 'back-to-chapter'): void
}>()

// State
const contentText = ref('')
const selectedContentType = ref('theory')
const teachingSteps = ref<TeachingStep[]>([])
const isGenerating = ref(false)
const isSaving = ref(false)
const lastSaved = ref<string | null>(null)

// Content Types
const contentTypes = [
  { id: 'theory', name: 'Theorie', emoji: '📚' },
  { id: 'example', name: 'Beispiel', emoji: '💡' },
  { id: 'exercise', name: 'Übung', emoji: '✏️' },
  { id: 'summary', name: 'Zusammenfassung', emoji: '📋' }
]

// Computed
const wordCount = computed(() => {
  return contentText.value.trim().split(/\s+/).filter(w => w).length
})

const characterCount = computed(() => {
  return contentText.value.length
})

const hasContent = computed(() => {
  return contentText.value.trim().length > 0 || teachingSteps.value.length > 0
})

// Get content type name
function getContentTypeName(typeId: string): string {
  const type = contentTypes.find(t => t.id === typeId)
  return type ? type.name : 'Inhalt'
}

// Methods
function addTeachingStep() {
  teachingSteps.value.push({
    title: `Schritt ${teachingSteps.value.length + 1}`,
    speech: '',
    animation: 'talking',
    duration: '0:30'
  })
}

function removeTeachingStep(index: number) {
  teachingSteps.value.splice(index, 1)
}

async function generateContent() {
  if (!props.lesson) return

  isGenerating.value = true

  try {
    // TODO: API call to generate content
    await new Promise(resolve => setTimeout(resolve, 2000))

    contentText.value = `# ${props.lesson.title}\n\n## Einführung\n\nHier kommt der generierte Inhalt für die Lektion...\n\n## Hauptteil\n\n...\n\n## Zusammenfassung\n\n...`
  } catch (error) {
    console.error('Content generation failed:', error)
  } finally {
    isGenerating.value = false
  }
}

async function generateTeachingSteps() {
  isGenerating.value = true

  try {
    // TODO: API call to generate teaching steps
    await new Promise(resolve => setTimeout(resolve, 1500))

    teachingSteps.value = [
      { title: 'Einführung', speech: 'Willkommen zu dieser Lektion...', animation: 'talking', duration: '0:30' },
      { title: 'Hauptkonzept', speech: 'Das wichtigste Konzept ist...', animation: 'pointing', duration: '1:00' },
      { title: 'Beispiel', speech: 'Schauen wir uns ein Beispiel an...', animation: 'gesture', duration: '1:30' },
      { title: 'Zusammenfassung', speech: 'Fassen wir zusammen...', animation: 'talking', duration: '0:30' }
    ]
  } catch (error) {
    console.error('Teaching steps generation failed:', error)
  } finally {
    isGenerating.value = false
  }
}

async function saveContent() {
  isSaving.value = true

  try {
    // TODO: API call to save content
    await new Promise(resolve => setTimeout(resolve, 500))

    emit('save', {
      content: contentText.value,
      teachingSteps: teachingSteps.value
    })

    lastSaved.value = new Date().toLocaleTimeString('de-DE')
  } catch (error) {
    console.error('Save failed:', error)
  } finally {
    isSaving.value = false
  }
}

function resetContent() {
  if (confirm('Änderungen verwerfen?')) {
    contentText.value = ''
    teachingSteps.value = []
    lastSaved.value = null
  }
}

// Watch for lesson changes
watch(() => props.lesson, (newLesson) => {
  if (newLesson) {
    // Load lesson content
    contentText.value = ''
    teachingSteps.value = []
    lastSaved.value = null
  }
}, { immediate: true })
</script>

<style scoped>
.content-tab {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-text-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: var(--color-text-primary);
  margin: 0 0 0.5rem;
}

.empty-state p {
  margin: 0;
}

/* Main Content */
.content-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  overflow: hidden;
}

/* Header (wie ExamsTab) */
.content-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  margin-bottom: 1rem;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.header-info {
  flex: 1;
}

.header-info h2 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.header-info p {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin: 0.25rem 0 0;
}

.header-stats {
  display: flex;
  gap: 1.5rem;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-label {
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Three-Column Layout */
.main-layout {
  display: grid;
  grid-template-columns: 240px 1fr 280px;
  gap: 1rem;
  flex: 1;
  min-height: 0;
}

/* Panel Base Styles */
.types-panel, .editor-panel, .steps-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.panel-icon {
  font-size: 1rem;
}

.panel-title {
  flex: 1;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.panel-divider {
  height: 1px;
  background: var(--color-border);
  margin: 0.5rem 0;
}

/* Types Panel */
.type-list {
  padding: 0.5rem;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.15s;
}

.type-item:hover {
  background: var(--color-surface-secondary);
}

.type-item.active {
  background: rgba(var(--color-primary-rgb, 59, 130, 246), 0.1);
  border: 1px solid var(--color-primary);
}

.type-emoji {
  font-size: 1.125rem;
}

.type-name {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.info-section {
  padding: 1rem;
}

.info-section h4 {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.info-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.info-value {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.status-badge {
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
}

.status-badge.saved {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.draft {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.quick-actions {
  padding: 0.75rem;
  margin-top: auto;
  border-top: 1px solid var(--color-border);
}

.action-btn {
  width: 100%;
  padding: 0.5rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

/* Editor Panel */
.generate-btn-small {
  padding: 0.25rem 0.5rem;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: opacity 0.15s;
}

.generate-btn-small:hover:not(:disabled) {
  opacity: 0.9;
}

.generate-btn-small:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.toolbar-btn {
  padding: 0.375rem 0.5rem;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 0.8125rem;
  transition: background 0.15s;
}

.toolbar-btn:hover {
  background: var(--color-surface-secondary);
}

.toolbar-divider {
  width: 1px;
  height: 1rem;
  background: var(--color-border);
  margin: 0 0.25rem;
}

.editor-area {
  flex: 1;
  overflow: hidden;
}

.editor-textarea {
  width: 100%;
  height: 100%;
  padding: 1rem;
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  font-size: 0.875rem;
  line-height: 1.6;
  resize: none;
}

.editor-textarea:focus {
  outline: none;
}

.editor-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.word-count {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.editor-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.btn-secondary:hover {
  background: var(--color-surface-secondary);
}

.btn-primary {
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark, #2563eb);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Steps Panel */
.add-btn {
  padding: 0.25rem 0.5rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  cursor: pointer;
  line-height: 1;
}

.steps-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.steps-empty {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--color-text-secondary);
}

.empty-icon-small {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.5rem;
}

.generate-link {
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: 0.8125rem;
  cursor: pointer;
  margin-top: 0.5rem;
}

.generate-link:hover {
  text-decoration: underline;
}

.step-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
}

.step-number {
  width: 1.75rem;
  height: 1.75rem;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
  min-width: 0;
}

.step-title-input {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  font-size: 0.8125rem;
  font-weight: 500;
  margin-bottom: 0.375rem;
}

.step-title-input:focus {
  outline: none;
}

.step-speech-input {
  width: 100%;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  padding: 0.5rem;
  color: var(--color-text-secondary);
  font-size: 0.75rem;
  resize: none;
}

.step-speech-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.step-delete {
  padding: 0.25rem;
  background: transparent;
  border: none;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.15s;
}

.step-delete:hover {
  opacity: 1;
}

.steps-footer {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.generate-steps-btn {
  width: 100%;
  padding: 0.625rem;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s;
}

.generate-steps-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.generate-steps-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 1200px) {
  .main-layout {
    grid-template-columns: 1fr;
  }

  .types-panel { order: 1; }
  .editor-panel { order: 2; min-height: 300px; }
  .steps-panel { order: 3; max-height: 300px; }
}
</style>
