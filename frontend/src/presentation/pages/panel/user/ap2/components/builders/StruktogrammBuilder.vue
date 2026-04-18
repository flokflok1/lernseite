<script setup lang="ts">
import { ref } from 'vue'

type BlockType = 'statement' | 'ifStart' | 'ifBranch' | 'ifEnd' | 'loopStart' | 'loopEnd' | 'caseStart' | 'caseBranch' | 'caseEnd'

interface Block {
  id: string
  type: BlockType
  label: string
  depth: number
}

interface Props {
  submitted?: boolean
  initialBlocks?: Block[]
}

const props = withDefaults(defineProps<Props>(), {
  submitted: false,
  initialBlocks: () => [],
})

const emit = defineEmits<{
  change: [blocks: Block[]]
}>()

const blocks = ref<Block[]>([...props.initialBlocks])

let idCounter = 1
function nextId() { return `b-${idCounter++}-${Date.now()}` }

function currentDepth(): number {
  if (blocks.value.length === 0) return 0
  return blocks.value[blocks.value.length - 1].depth
}

function addStatement() {
  if (props.submitted) return
  const label = window.prompt('Anweisung:')
  if (!label) return
  blocks.value.push({ id: nextId(), type: 'statement', label, depth: currentDepth() })
  emitChange()
}

function addIfElse() {
  if (props.submitted) return
  const cond = window.prompt('Bedingung?')
  if (!cond) return
  const d = currentDepth()
  blocks.value.push({ id: nextId(), type: 'ifStart', label: cond, depth: d })
  blocks.value.push({ id: nextId(), type: 'ifBranch', label: 'wahr (ja)', depth: d + 1 })
  blocks.value.push({ id: nextId(), type: 'ifBranch', label: 'falsch (nein)', depth: d + 1 })
  blocks.value.push({ id: nextId(), type: 'ifEnd', label: '', depth: d })
  emitChange()
}

function addLoop() {
  if (props.submitted) return
  const cond = window.prompt('Schleifen-Kopf (z.B. „solange i < n" oder „für i = 1 bis n"):')
  if (!cond) return
  const d = currentDepth()
  blocks.value.push({ id: nextId(), type: 'loopStart', label: cond, depth: d })
  blocks.value.push({ id: nextId(), type: 'loopEnd', label: '', depth: d })
  emitChange()
}

function addCase() {
  if (props.submitted) return
  const label = window.prompt('Fallauswahl (z.B. „Statuscode"):')
  if (!label) return
  const d = currentDepth()
  blocks.value.push({ id: nextId(), type: 'caseStart', label, depth: d })
  blocks.value.push({ id: nextId(), type: 'caseBranch', label: 'Fall 1', depth: d + 1 })
  blocks.value.push({ id: nextId(), type: 'caseBranch', label: 'Fall 2', depth: d + 1 })
  blocks.value.push({ id: nextId(), type: 'caseEnd', label: '', depth: d })
  emitChange()
}

function editBlock(block: Block) {
  if (props.submitted) return
  const next = window.prompt('Label:', block.label)
  if (next !== null) {
    block.label = next
    emitChange()
  }
}

function removeBlock(id: string) {
  if (props.submitted) return
  blocks.value = blocks.value.filter(b => b.id !== id)
  emitChange()
}

function clearAll() {
  if (props.submitted) return
  if (!window.confirm('Alles löschen?')) return
  blocks.value = []
  emitChange()
}

function emitChange() {
  emit('change', JSON.parse(JSON.stringify(blocks.value)))
}
</script>

<template>
  <div class="strukt-builder">
    <div class="strukt-toolbar">
      <span class="strukt-tool-label">Nassi-Shneiderman:</span>
      <button class="strukt-btn" :disabled="submitted" @click="addStatement">▭ Anweisung</button>
      <button class="strukt-btn" :disabled="submitted" @click="addIfElse">⬡ if/else</button>
      <button class="strukt-btn" :disabled="submitted" @click="addLoop">⟳ Schleife</button>
      <button class="strukt-btn" :disabled="submitted" @click="addCase">⬒ Fallauswahl</button>
      <button class="strukt-btn strukt-btn-danger" :disabled="submitted" @click="clearAll">🗑 Leeren</button>
    </div>

    <p class="strukt-hint">
      <strong>DIN 66261:</strong> Füge sequenziell Blöcke hinzu — Anweisungen, Bedingungen, Schleifen.
      Klick auf Label: Bearbeiten. Ineinander verschachtelte Strukturen werden automatisch eingerückt.
    </p>

    <div class="strukt-canvas">
      <div v-if="blocks.length === 0" class="strukt-empty">
        Noch kein Struktogramm. Füge oben einen Block hinzu.
      </div>

      <div v-else class="strukt-frame">
        <div
          v-for="b in blocks"
          :key="b.id"
          class="strukt-block"
          :class="`strukt-${b.type}`"
          :style="{ marginLeft: (b.depth * 20) + 'px' }"
        >
          <span v-if="b.type === 'ifStart'" class="strukt-prefix">wenn</span>
          <span v-if="b.type === 'loopStart'" class="strukt-prefix">⟳</span>
          <span v-if="b.type === 'caseStart'" class="strukt-prefix">fall</span>

          <span v-if="b.type !== 'ifEnd' && b.type !== 'loopEnd' && b.type !== 'caseEnd'" class="strukt-label">
            {{ b.label }}
          </span>
          <span v-else class="strukt-label strukt-end-marker">— Ende —</span>

          <div class="strukt-block-actions">
            <button
              v-if="b.type !== 'ifEnd' && b.type !== 'loopEnd' && b.type !== 'caseEnd'"
              class="strukt-mini"
              :disabled="submitted"
              @click="editBlock(b)"
            >✎</button>
            <button class="strukt-mini strukt-mini-danger" :disabled="submitted" @click="removeBlock(b.id)">🗑</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.strukt-builder {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 8px;
}

.strukt-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  align-items: center;
  padding: 0.5rem;
  background: #fff;
  border-radius: 6px;
}

.strukt-tool-label {
  font-weight: 600;
  font-size: 0.85rem;
  color: #374151;
  margin-right: 0.4rem;
}

.strukt-btn {
  padding: 0.4rem 0.7rem;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
}
.strukt-btn:hover:not(:disabled) { background: #f3f4f6; }
.strukt-btn-danger:hover:not(:disabled) { background: #fee2e2; color: #dc2626; }
.strukt-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.strukt-hint {
  margin: 0;
  font-size: 0.8rem;
  color: #6b7280;
  padding: 0.4rem 0.6rem;
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
  border-radius: 3px;
}

.strukt-canvas {
  min-height: 300px;
  padding: 0;
  background: #fff;
  border: 2px solid #1f2937;
  border-radius: 4px;
  font-family: 'Liberation Sans', sans-serif;
  overflow: hidden;
}

.strukt-frame { padding: 0.5rem; }

.strukt-empty {
  color: #9ca3af;
  text-align: center;
  padding: 2rem;
  font-style: italic;
}

.strukt-block {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.7rem;
  background: #fff;
  border: 1px solid #1f2937;
  margin-top: -1px;
  min-height: 36px;
}

.strukt-block:first-child { margin-top: 0; }

.strukt-statement { background: #fff; }
.strukt-ifStart    { background: #fef3c7; font-weight: 600; }
.strukt-ifBranch   { background: #fffbeb; font-weight: 500; font-size: 0.85rem; border-top: 1px dashed #f59e0b; }
.strukt-ifEnd      { background: #f3f4f6; font-size: 0.8rem; }
.strukt-loopStart  { background: #dbeafe; font-weight: 600; border-left: 4px solid #2563eb; }
.strukt-loopEnd    { background: #f3f4f6; font-size: 0.8rem; border-left: 4px solid #2563eb; }
.strukt-caseStart  { background: #ede9fe; font-weight: 600; }
.strukt-caseBranch { background: #f5f3ff; font-weight: 500; font-size: 0.85rem; }
.strukt-caseEnd    { background: #f3f4f6; font-size: 0.8rem; }

.strukt-prefix {
  display: inline-block;
  padding: 1px 6px;
  background: #1f2937;
  color: #fff;
  border-radius: 3px;
  font-size: 0.75rem;
  font-weight: 600;
}

.strukt-label { flex: 1; font-size: 0.9rem; color: #111827; }

.strukt-end-marker { color: #9ca3af; font-style: italic; }

.strukt-block-actions { display: flex; gap: 0.2rem; opacity: 0.3; transition: opacity 0.15s; }
.strukt-block:hover .strukt-block-actions { opacity: 1; }

.strukt-mini {
  padding: 2px 6px;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 3px;
  font-size: 0.75rem;
  cursor: pointer;
}
.strukt-mini:hover:not(:disabled) { background: #e5e7eb; }
.strukt-mini-danger:hover:not(:disabled) { background: #fee2e2; color: #dc2626; }
.strukt-mini:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
