<template>
  <div class="er-builder">
    <!-- Toolbar -->
    <div class="er-toolbar">
      <div class="er-toolbar-group">
        <button class="er-btn" @click="addEntity" :disabled="submitted" title="Entität hinzufügen">
          <span class="er-btn-icon">&#9634;</span> Entität
        </button>
        <button
          class="er-btn"
          @click="startRelationship"
          :disabled="submitted || entities.length < 2"
          :class="{ 'er-btn-active': isConnecting }"
          title="Beziehung zeichnen"
        >
          <span class="er-btn-icon">&#8596;</span> Beziehung
        </button>
      </div>
      <div class="er-toolbar-group">
        <button class="er-btn er-btn-danger" @click="clearAll" :disabled="submitted" title="Alles löschen">
          &#128465; Leeren
        </button>
      </div>
      <div v-if="isConnecting" class="er-connect-hint">
        Klicke auf zwei Entitäten um sie zu verbinden
        <button class="er-btn-sm" @click="cancelConnect">Abbrechen</button>
      </div>
    </div>

    <!-- SVG Canvas -->
    <div class="er-canvas-wrap" ref="canvasWrap">
      <svg
        class="er-canvas"
        :viewBox="`0 0 ${canvasWidth} ${canvasHeight}`"
        @mousedown="onCanvasMouse"
        @mousemove="onCanvasMove"
        @mouseup="onCanvasUp"
        ref="svgCanvas"
      >
        <!-- Grid -->
        <defs>
          <pattern id="er-grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#er-grid)" />

        <!-- Beziehungslinien -->
        <g v-for="rel in relationships" :key="rel.id">
          <line
            :x1="getEntityCenter(rel.from).x"
            :y1="getEntityCenter(rel.from).y"
            :x2="getEntityCenter(rel.to).x"
            :y2="getEntityCenter(rel.to).y"
            class="er-rel-line"
            :class="{ 'er-rel-selected': selectedRelId === rel.id }"
            @click.stop="selectRelationship(rel.id)"
          />
          <!-- Raute in der Mitte -->
          <g :transform="getRelDiamondTransform(rel)">
            <rect
              width="80" height="36" x="-40" y="-18"
              rx="3"
              class="er-rel-diamond"
              :class="{ 'er-rel-diamond-selected': selectedRelId === rel.id }"
              transform="rotate(45)"
              @click.stop="selectRelationship(rel.id)"
            />
            <text
              text-anchor="middle" dominant-baseline="central"
              class="er-rel-label"
              @click.stop="selectRelationship(rel.id)"
            >
              {{ rel.label || '?' }}
            </text>
          </g>
          <!-- Kardinalitäten -->
          <text
            :x="getCardPos(rel, 'from').x"
            :y="getCardPos(rel, 'from').y"
            class="er-card-text"
            text-anchor="middle"
          >
            {{ getCardLabel(rel.cardinality, 'from') }}
          </text>
          <text
            :x="getCardPos(rel, 'to').x"
            :y="getCardPos(rel, 'to').y"
            class="er-card-text"
            text-anchor="middle"
          >
            {{ getCardLabel(rel.cardinality, 'to') }}
          </text>
        </g>

        <!-- Entitäten -->
        <g
          v-for="entity in entities"
          :key="entity.id"
          :transform="`translate(${entity._x || 100}, ${entity._y || 100})`"
          class="er-entity-group"
          :class="{
            'er-entity-selected': selectedEntityId === entity.id,
            'er-entity-connect-target': isConnecting && connectFrom && connectFrom !== entity.id
          }"
          @mousedown.stop="onEntityMouseDown(entity, $event)"
          @click.stop="onEntityClick(entity)"
        >
          <!-- Entity-Box -->
          <rect
            :width="entityWidth"
            :height="getEntityHeight(entity)"
            rx="6"
            class="er-entity-rect"
            :class="{ 'er-entity-rect-selected': selectedEntityId === entity.id }"
          />
          <!-- Name -->
          <text
            :x="entityWidth / 2"
            y="22"
            text-anchor="middle"
            class="er-entity-name"
          >
            {{ entity.name }}
          </text>
          <!-- Trennlinie -->
          <line x1="0" :x2="entityWidth" y1="32" y2="32" class="er-entity-divider" />
          <!-- Attribute -->
          <g v-for="(attr, ai) in entity.attributes" :key="ai">
            <text
              x="10"
              :y="50 + ai * 22"
              class="er-attr-text"
              :class="{
                'er-attr-pk': attr.isPK,
                'er-attr-fk': attr.isFK
              }"
            >
              <tspan v-if="attr.isPK" class="er-attr-marker">PK </tspan>
              <tspan v-if="attr.isFK" class="er-attr-marker">FK </tspan>
              {{ attr.name }}
              <tspan v-if="attr.dataType" class="er-attr-type"> : {{ attr.dataType }}</tspan>
            </text>
            <!-- PK-Unterstreichung -->
            <line
              v-if="attr.isPK"
              :x1="10"
              :x2="10 + (attr.name.length + (attr.dataType ? attr.dataType.length + 3 : 0) + 3) * 7"
              :y1="53 + ai * 22"
              :y2="53 + ai * 22"
              class="er-pk-underline"
            />
          </g>
        </g>

        <!-- Verbindungslinie beim Zeichnen -->
        <line
          v-if="isConnecting && connectFrom && mousePos"
          :x1="getEntityCenter(connectFrom).x"
          :y1="getEntityCenter(connectFrom).y"
          :x2="mousePos.x"
          :y2="mousePos.y"
          class="er-connect-preview"
        />
      </svg>
    </div>

    <!-- Eigenschafts-Panel -->
    <div v-if="selectedEntityId && !submitted" class="er-props">
      <div class="er-props-header">
        <span>Entität bearbeiten</span>
        <button class="er-btn-sm er-btn-danger" @click="deleteEntity(selectedEntityId)">Löschen</button>
      </div>
      <div class="er-prop-row">
        <label class="er-prop-label">Name:</label>
        <input
          :value="selectedEntity?.name"
          @input="updateEntityName(($event.target as HTMLInputElement).value)"
          class="er-prop-input"
          placeholder="Entitätsname"
        />
      </div>
      <div class="er-prop-divider"></div>
      <div class="er-attr-header">
        <span class="er-prop-label">Attribute:</span>
        <button class="er-btn-sm" @click="addAttribute">+ Attribut</button>
      </div>
      <div v-for="(attr, ai) in selectedEntity?.attributes" :key="ai" class="er-attr-row">
        <input
          :value="attr.name"
          @input="updateAttribute(ai, 'name', ($event.target as HTMLInputElement).value)"
          class="er-prop-input er-prop-input-sm"
          placeholder="Name"
        />
        <input
          :value="attr.dataType || ''"
          @input="updateAttribute(ai, 'dataType', ($event.target as HTMLInputElement).value)"
          class="er-prop-input er-prop-input-xs"
          placeholder="Typ"
        />
        <label class="er-checkbox" title="Primärschlüssel">
          <input type="checkbox" :checked="attr.isPK" @change="updateAttribute(ai, 'isPK', ($event.target as HTMLInputElement).checked)" />
          PK
        </label>
        <label class="er-checkbox" title="Fremdschlüssel">
          <input type="checkbox" :checked="attr.isFK" @change="updateAttribute(ai, 'isFK', ($event.target as HTMLInputElement).checked)" />
          FK
        </label>
        <button class="er-btn-icon-sm" @click="removeAttribute(ai)" title="Attribut entfernen">&#10005;</button>
      </div>
    </div>

    <!-- Beziehungs-Panel -->
    <div v-if="selectedRelId && !submitted" class="er-props">
      <div class="er-props-header">
        <span>Beziehung bearbeiten</span>
        <button class="er-btn-sm er-btn-danger" @click="deleteRelationship(selectedRelId)">Löschen</button>
      </div>
      <div class="er-prop-row">
        <label class="er-prop-label">Bezeichnung:</label>
        <input
          :value="selectedRelationship?.label"
          @input="updateRelLabel(($event.target as HTMLInputElement).value)"
          class="er-prop-input"
          placeholder="z.B. bestellt, gehört zu"
        />
      </div>
      <div class="er-prop-row">
        <label class="er-prop-label">Kardinalität:</label>
        <select
          :value="selectedRelationship?.cardinality"
          @change="updateRelCardinality(($event.target as HTMLSelectElement).value)"
          class="er-prop-select"
        >
          <option value="1:1">1:1</option>
          <option value="1:n">1:n</option>
          <option value="n:1">n:1</option>
          <option value="n:m">n:m</option>
        </select>
      </div>
      <div class="er-prop-info">
        {{ getEntityName(selectedRelationship?.from || '') }}
        &#8594;
        {{ getEntityName(selectedRelationship?.to || '') }}
      </div>
    </div>

    <!-- Ergebnis nach Abgabe -->
    <div v-if="submitted && gradingFeedback" class="er-result">
      <div class="er-result-score" :class="resultClass">
        {{ gradingFeedback.pct }}% — {{ gradingFeedback.feedback }}
      </div>
      <div v-if="gradingFeedback.details" class="er-result-details">
        <div v-if="gradingFeedback.details.entityScore !== undefined" class="er-result-row">
          <span>Entitäten:</span>
          <span class="er-result-val">{{ gradingFeedback.details.entityScore }}%</span>
        </div>
        <div v-if="gradingFeedback.details.attributeScore !== undefined" class="er-result-row">
          <span>Attribute & Schlüssel:</span>
          <span class="er-result-val">{{ gradingFeedback.details.attributeScore }}%</span>
        </div>
        <div v-if="gradingFeedback.details.relationshipScore !== undefined" class="er-result-row">
          <span>Beziehungen & Kardinalitäten:</span>
          <span class="er-result-val">{{ gradingFeedback.details.relationshipScore }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { EREntity, ERAttribute, ERRelationship, ERDiagramData, DiagramGradingResult } from '../../types'

interface PositionedEntity extends EREntity {
  _x: number
  _y: number
}

const props = defineProps<{
  /** Vorgabe-Daten (teilweise ausgefülltes ER-Modell) */
  template?: ERDiagramData
  /** Erwartete Lösung für Bewertung */
  solution?: ERDiagramData
  submitted: boolean
  instructions?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', data: ERDiagramData): void
  (e: 'graded', result: DiagramGradingResult): void
}>()

// ─── Constants ───
const entityWidth = 180
const canvasWidth = 900
const canvasHeight = 600

// ─── State ───
const entities = ref<PositionedEntity[]>([])
const relationships = ref<ERRelationship[]>([])
const selectedEntityId = ref<string | null>(null)
const selectedRelId = ref<string | null>(null)
const isConnecting = ref(false)
const connectFrom = ref<string | null>(null)
const mousePos = ref<{ x: number; y: number } | null>(null)
const isDragging = ref(false)
const dragEntity = ref<string | null>(null)
const dragOffsetX = ref(0)
const dragOffsetY = ref(0)
const svgCanvas = ref<SVGSVGElement | null>(null)
const canvasWrap = ref<HTMLElement | null>(null)
const gradingFeedback = ref<DiagramGradingResult | null>(null)
let nextEntityId = 1
let nextRelId = 1

// ─── Computed ───
const selectedEntity = computed(() =>
  entities.value.find(e => e.id === selectedEntityId.value)
)

const selectedRelationship = computed(() =>
  relationships.value.find(r => r.id === selectedRelId.value)
)

const resultClass = computed(() => {
  if (!gradingFeedback.value) return ''
  if (gradingFeedback.value.pct >= 80) return 'er-result-great'
  if (gradingFeedback.value.pct >= 50) return 'er-result-ok'
  return 'er-result-bad'
})

// ─── Entity Helpers ───
function getEntityHeight(entity: EREntity | PositionedEntity): number {
  return 38 + Math.max(entity.attributes.length, 1) * 22
}

function getEntityCenter(entityId: string): { x: number; y: number } {
  const e = entities.value.find(en => en.id === entityId)
  if (!e) return { x: 0, y: 0 }
  return {
    x: e._x + entityWidth / 2,
    y: e._y + getEntityHeight(e) / 2,
  }
}

function getEntityName(id: string): string {
  return entities.value.find(e => e.id === id)?.name || '?'
}

// ─── Relationship Helpers ───
function getRelDiamondTransform(rel: ERRelationship): string {
  const from = getEntityCenter(rel.from)
  const to = getEntityCenter(rel.to)
  const mx = (from.x + to.x) / 2
  const my = (from.y + to.y) / 2
  return `translate(${mx}, ${my})`
}

function getCardPos(rel: ERRelationship, side: 'from' | 'to'): { x: number; y: number } {
  const from = getEntityCenter(rel.from)
  const to = getEntityCenter(rel.to)
  const t = side === 'from' ? 0.2 : 0.8
  return {
    x: from.x + (to.x - from.x) * t,
    y: from.y + (to.y - from.y) * t - 12,
  }
}

function getCardLabel(cardinality: string, side: 'from' | 'to'): string {
  const parts = cardinality.split(':')
  return side === 'from' ? parts[0] : parts[1]
}

// ─── Actions ───
function addEntity() {
  const id = `e${nextEntityId++}`
  const offsetX = 80 + (entities.value.length % 3) * 220
  const offsetY = 60 + Math.floor(entities.value.length / 3) * 180
  entities.value.push({
    id,
    name: 'NeueEntität',
    attributes: [{ name: 'id', isPK: true, dataType: 'INT' }],
    _x: offsetX,
    _y: offsetY,
  })
  selectedEntityId.value = id
  selectedRelId.value = null
  emitUpdate()
}

function deleteEntity(id: string) {
  entities.value = entities.value.filter(e => e.id !== id)
  relationships.value = relationships.value.filter(r => r.from !== id && r.to !== id)
  selectedEntityId.value = null
  emitUpdate()
}

function updateEntityName(name: string) {
  const e = entities.value.find(en => en.id === selectedEntityId.value)
  if (e) e.name = name
  emitUpdate()
}

function addAttribute() {
  const e = entities.value.find(en => en.id === selectedEntityId.value)
  if (e) {
    e.attributes.push({ name: '', dataType: '' })
    emitUpdate()
  }
}

function updateAttribute(idx: number, field: keyof ERAttribute, value: any) {
  const e = entities.value.find(en => en.id === selectedEntityId.value)
  if (e && e.attributes[idx]) {
    (e.attributes[idx] as any)[field] = value
    emitUpdate()
  }
}

function removeAttribute(idx: number) {
  const e = entities.value.find(en => en.id === selectedEntityId.value)
  if (e) {
    e.attributes.splice(idx, 1)
    emitUpdate()
  }
}

// ─── Relationships ───
function startRelationship() {
  isConnecting.value = true
  connectFrom.value = null
  selectedEntityId.value = null
  selectedRelId.value = null
}

function cancelConnect() {
  isConnecting.value = false
  connectFrom.value = null
  mousePos.value = null
}

function selectRelationship(id: string) {
  if (isConnecting.value) return
  selectedRelId.value = id
  selectedEntityId.value = null
}

function deleteRelationship(id: string) {
  relationships.value = relationships.value.filter(r => r.id !== id)
  selectedRelId.value = null
  emitUpdate()
}

function updateRelLabel(label: string) {
  const r = relationships.value.find(rel => rel.id === selectedRelId.value)
  if (r) r.label = label
  emitUpdate()
}

function updateRelCardinality(card: string) {
  const r = relationships.value.find(rel => rel.id === selectedRelId.value)
  if (r) r.cardinality = card as ERRelationship['cardinality']
  emitUpdate()
}

// ─── Entity Interaction ───
function onEntityClick(entity: PositionedEntity) {
  if (isDragging.value) return

  if (isConnecting.value) {
    if (!connectFrom.value) {
      connectFrom.value = entity.id
    } else if (connectFrom.value !== entity.id) {
      // Beziehung erstellen
      const id = `r${nextRelId++}`
      relationships.value.push({
        id,
        from: connectFrom.value,
        to: entity.id,
        label: '',
        cardinality: '1:n',
      })
      isConnecting.value = false
      connectFrom.value = null
      mousePos.value = null
      selectedRelId.value = id
      emitUpdate()
    }
    return
  }

  selectedEntityId.value = entity.id
  selectedRelId.value = null
}

function onEntityMouseDown(entity: PositionedEntity, e: MouseEvent) {
  if (props.submitted || isConnecting.value) return
  isDragging.value = false
  dragEntity.value = entity.id

  const pt = svgPoint(e)
  dragOffsetX.value = pt.x - entity._x
  dragOffsetY.value = pt.y - entity._y
}

function onCanvasMouse(e: MouseEvent) {
  if (!isConnecting.value) {
    selectedEntityId.value = null
    selectedRelId.value = null
  }
}

function onCanvasMove(e: MouseEvent) {
  const pt = svgPoint(e)

  if (isConnecting.value && connectFrom.value) {
    mousePos.value = pt
  }

  if (dragEntity.value && !props.submitted) {
    isDragging.value = true
    const entity = entities.value.find(en => en.id === dragEntity.value)
    if (entity) {
      entity._x = Math.max(0, Math.min(canvasWidth - entityWidth, pt.x - dragOffsetX.value))
      entity._y = Math.max(0, Math.min(canvasHeight - 60, pt.y - dragOffsetY.value))
    }
  }
}

function onCanvasUp() {
  // Kleiner Timeout um Click-Handler nicht zu blockieren
  setTimeout(() => { isDragging.value = false }, 50)
  dragEntity.value = null
}

function svgPoint(e: MouseEvent): { x: number; y: number } {
  if (!svgCanvas.value) return { x: e.offsetX, y: e.offsetY }
  const svg = svgCanvas.value
  const pt = svg.createSVGPoint()
  pt.x = e.clientX
  pt.y = e.clientY
  const ctm = svg.getScreenCTM()?.inverse()
  if (ctm) {
    const transformed = pt.matrixTransform(ctm)
    return { x: transformed.x, y: transformed.y }
  }
  return { x: e.offsetX, y: e.offsetY }
}

function clearAll() {
  entities.value = []
  relationships.value = []
  selectedEntityId.value = null
  selectedRelId.value = null
  nextEntityId = 1
  nextRelId = 1
  emitUpdate()
}

// ─── Emit ───
function emitUpdate() {
  const data: ERDiagramData = {
    entities: entities.value.map(e => ({
      id: e.id,
      name: e.name,
      attributes: [...e.attributes],
    })),
    relationships: relationships.value.map(r => ({ ...r })),
  }
  emit('update:modelValue', data)
}

// ─── Grading ───
function gradeER(): DiagramGradingResult {
  if (!props.solution) {
    return { pct: 0, feedback: 'Keine Musterlösung vorhanden', details: {} }
  }

  const sol = props.solution as ERDiagramData
  const user: ERDiagramData = {
    entities: entities.value.map(e => ({ id: e.id, name: e.name, attributes: [...e.attributes] })),
    relationships: [...relationships.value],
  }

  // Entitäten-Score: Name-Match (case-insensitive)
  const solEntityNames = sol.entities.map(e => e.name.toLowerCase())
  const userEntityNames = user.entities.map(e => e.name.toLowerCase())
  const matchedEntities = solEntityNames.filter(n => userEntityNames.includes(n))
  const entityScore = solEntityNames.length > 0
    ? Math.round((matchedEntities.length / solEntityNames.length) * 100)
    : 100

  // Attribut-Score: Für gematchte Entitäten, Attribute + PK/FK prüfen
  let totalAttrs = 0
  let matchedAttrs = 0
  for (const solEntity of sol.entities) {
    const userEntity = user.entities.find(e => e.name.toLowerCase() === solEntity.name.toLowerCase())
    if (!userEntity) continue

    for (const solAttr of solEntity.attributes) {
      totalAttrs++
      const userAttr = userEntity.attributes.find(a => a.name.toLowerCase() === solAttr.name.toLowerCase())
      if (userAttr) {
        // Basisname korrekt
        matchedAttrs += 0.5
        // PK/FK korrekt
        if (!!userAttr.isPK === !!solAttr.isPK && !!userAttr.isFK === !!solAttr.isFK) {
          matchedAttrs += 0.5
        }
      }
    }
  }
  const attributeScore = totalAttrs > 0 ? Math.round((matchedAttrs / totalAttrs) * 100) : 100

  // Beziehungs-Score: Entity-Paare + Kardinalität
  let totalRels = sol.relationships.length
  let matchedRels = 0
  for (const solRel of sol.relationships) {
    const solFromName = sol.entities.find(e => e.id === solRel.from)?.name.toLowerCase() || ''
    const solToName = sol.entities.find(e => e.id === solRel.to)?.name.toLowerCase() || ''

    const userRel = user.relationships.find(r => {
      const uFrom = user.entities.find(e => e.id === r.from)?.name.toLowerCase() || ''
      const uTo = user.entities.find(e => e.id === r.to)?.name.toLowerCase() || ''
      return (uFrom === solFromName && uTo === solToName) || (uFrom === solToName && uTo === solFromName)
    })

    if (userRel) {
      matchedRels += 0.5 // Verbindung existiert
      // Kardinalität korrekt?
      const normalizedUser = normalizeCardinality(userRel, user.entities, solFromName, solToName)
      if (normalizedUser === solRel.cardinality) {
        matchedRels += 0.5
      }
    }
  }
  const relationshipScore = totalRels > 0 ? Math.round((matchedRels / totalRels) * 100) : 100

  // Gesamtscore: gewichtet
  const pct = Math.round(entityScore * 0.3 + attributeScore * 0.4 + relationshipScore * 0.3)

  let feedback = ''
  if (pct >= 90) feedback = 'Ausgezeichnet! Dein ER-Modell ist nahezu perfekt.'
  else if (pct >= 70) feedback = 'Gut gemacht! Einige Details fehlen oder sind nicht ganz korrekt.'
  else if (pct >= 50) feedback = 'Auf dem richtigen Weg, aber es fehlen wichtige Elemente.'
  else feedback = 'Es gibt noch viel zu verbessern. Überprüfe Entitäten, Attribute und Beziehungen.'

  return {
    pct,
    feedback,
    details: { entityScore, attributeScore, relationshipScore },
  }
}

function normalizeCardinality(
  rel: ERRelationship,
  userEntities: EREntity[],
  solFromName: string,
  solToName: string
): string {
  const uFrom = userEntities.find(e => e.id === rel.from)?.name.toLowerCase() || ''
  if (uFrom === solFromName) {
    return rel.cardinality
  }
  // Umgekehrte Richtung → Kardinalität spiegeln
  const parts = rel.cardinality.split(':')
  return `${parts[1]}:${parts[0]}` as ERRelationship['cardinality']
}

// ─── Lifecycle ───
onMounted(() => {
  if (props.template) {
    loadTemplate(props.template)
  }
})

function loadTemplate(data: ERDiagramData) {
  entities.value = data.entities.map((e, i) => ({
    ...e,
    attributes: [...e.attributes],
    _x: 80 + (i % 3) * 260,
    _y: 60 + Math.floor(i / 3) * 200,
  }))
  relationships.value = data.relationships.map(r => ({ ...r }))
  nextEntityId = data.entities.length + 1
  nextRelId = data.relationships.length + 1
}

watch(() => props.submitted, (isSubmitted) => {
  if (isSubmitted) {
    const result = gradeER()
    gradingFeedback.value = result
    emit('graded', result)
  }
})
</script>

<style scoped>
.er-builder {
  width: 100%;
  margin: 12px 0;
}

/* ─── Toolbar ─── */
.er-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px 8px 0 0;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-bottom: none;
  flex-wrap: wrap;
}
.er-toolbar-group {
  display: flex;
  gap: 6px;
}
.er-btn {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  color: #b0bec5;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}
.er-btn:hover:not(:disabled) {
  background: rgba(26, 115, 232, 0.12);
  border-color: rgba(26, 115, 232, 0.3);
  color: #e3f2fd;
}
.er-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.er-btn-active {
  background: rgba(26, 115, 232, 0.2) !important;
  border-color: #1a73e8 !important;
  color: #e3f2fd !important;
}
.er-btn-icon { font-size: 0.9rem; }
.er-btn-danger { color: #ef5350; }
.er-btn-danger:hover:not(:disabled) {
  background: rgba(239, 83, 80, 0.12);
  border-color: rgba(239, 83, 80, 0.3);
}
.er-btn-sm {
  padding: 3px 8px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: #90a4ae;
  font-size: 0.75rem;
  cursor: pointer;
}
.er-btn-sm:hover { color: #e3f2fd; }
.er-btn-icon-sm {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: #78909c;
  cursor: pointer;
  font-size: 0.75rem;
  border-radius: 3px;
}
.er-btn-icon-sm:hover {
  background: rgba(239, 83, 80, 0.15);
  color: #ef5350;
}

.er-connect-hint {
  flex: 1;
  text-align: right;
  font-size: 0.78rem;
  color: #64b5f6;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: flex-end;
}

/* ─── Canvas ─── */
.er-canvas-wrap {
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0 0 8px 8px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.25);
}
.er-canvas {
  width: 100%;
  height: 500px;
  display: block;
}

/* ─── Entity SVG ─── */
.er-entity-group {
  cursor: grab;
}
.er-entity-group:active {
  cursor: grabbing;
}
.er-entity-rect {
  fill: rgba(38, 50, 56, 0.85);
  stroke: #546e7a;
  stroke-width: 1.5;
  transition: stroke 0.15s ease;
}
.er-entity-rect-selected {
  stroke: #1a73e8;
  stroke-width: 2;
}
.er-entity-connect-target .er-entity-rect {
  stroke: #66bb6a;
  stroke-width: 2;
  stroke-dasharray: 4 2;
}
.er-entity-name {
  fill: #e3f2fd;
  font-size: 13px;
  font-weight: 600;
}
.er-entity-divider {
  stroke: rgba(255, 255, 255, 0.1);
  stroke-width: 1;
}
.er-attr-text {
  fill: #b0bec5;
  font-size: 11px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
.er-attr-pk { fill: #ffc107; }
.er-attr-fk { fill: #64b5f6; }
.er-attr-marker {
  font-weight: 700;
  font-size: 10px;
}
.er-attr-type {
  fill: #78909c;
  font-size: 10px;
}
.er-pk-underline {
  stroke: #ffc107;
  stroke-width: 1;
}

/* ─── Relationships SVG ─── */
.er-rel-line {
  stroke: #546e7a;
  stroke-width: 1.5;
  cursor: pointer;
}
.er-rel-line:hover {
  stroke: #90a4ae;
}
.er-rel-selected {
  stroke: #1a73e8;
  stroke-width: 2;
}
.er-rel-diamond {
  fill: rgba(38, 50, 56, 0.9);
  stroke: #546e7a;
  stroke-width: 1;
  cursor: pointer;
  width: 50px;
  height: 50px;
  x: -25;
  y: -25;
}
.er-rel-diamond-selected {
  stroke: #1a73e8;
  stroke-width: 2;
}
.er-rel-label {
  fill: #e0e0e0;
  font-size: 11px;
  pointer-events: none;
}
.er-card-text {
  fill: #ffc107;
  font-size: 12px;
  font-weight: 700;
}
.er-connect-preview {
  stroke: #1a73e8;
  stroke-width: 1.5;
  stroke-dasharray: 6 3;
  pointer-events: none;
}

/* ─── Props Panel ─── */
.er-props {
  margin-top: 10px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
}
.er-props-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #e3f2fd;
}
.er-prop-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.er-prop-label {
  font-size: 0.8rem;
  color: #90a4ae;
  min-width: 80px;
}
.er-prop-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 5px 8px;
  color: #e0e0e0;
  font-size: 0.82rem;
  outline: none;
}
.er-prop-input:focus {
  border-color: #1a73e8;
}
.er-prop-input-sm { flex: 2; }
.er-prop-input-xs { flex: 1; max-width: 90px; }
.er-prop-select {
  flex: 1;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 5px 8px;
  color: #e0e0e0;
  font-size: 0.82rem;
  outline: none;
}
.er-prop-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
  margin: 8px 0;
}
.er-attr-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.er-attr-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}
.er-checkbox {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 0.72rem;
  color: #90a4ae;
  cursor: pointer;
  white-space: nowrap;
}
.er-checkbox input[type="checkbox"] {
  width: 14px;
  height: 14px;
  accent-color: #1a73e8;
}
.er-prop-info {
  font-size: 0.78rem;
  color: #78909c;
  margin-top: 6px;
}

/* ─── Result ─── */
.er-result {
  margin-top: 12px;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}
.er-result-score {
  font-size: 0.9rem;
  font-weight: 600;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 8px;
}
.er-result-great { background: rgba(34, 197, 94, 0.12); color: #22c55e; }
.er-result-ok { background: rgba(245, 158, 11, 0.12); color: #f59e0b; }
.er-result-bad { background: rgba(239, 68, 68, 0.12); color: #ef4444; }
.er-result-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.er-result-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
  color: #90a4ae;
  padding: 4px 8px;
}
.er-result-val {
  font-weight: 600;
  color: #e0e0e0;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
</style>
