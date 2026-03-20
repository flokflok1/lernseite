<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useStructogram } from './composables/useStructogram'
import StructogramToolbar from './StructogramToolbar.vue'
import StructogramBlock from './StructogramBlock.vue'
import type { BlockType, StructogramBlock as Block, StructogramData } from './types/structogram.types'

interface Props {
  modelValue?: StructogramData
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
})

const emit = defineEmits<{
  'update:modelValue': [data: StructogramData]
}>()

const { t } = useI18n()

const {
  blocks, selectedId,
  addBlock, removeBlock, updateText, clearAll,
  toJSON, isEmpty,
} = useStructogram(props.modelValue)

function handleAdd(type: BlockType) {
  addBlock(type)
  emitUpdate()
}

function handleAddTo(targetList: Block[], type: string) {
  addBlock(type as BlockType, targetList)
  emitUpdate()
}

function handleDelete(id: string) {
  removeBlock(id)
  emitUpdate()
}

function handleUpdate(id: string, field: string, value: string) {
  updateText(id, field, value)
  emitUpdate()
}

function handleClear() {
  clearAll()
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', toJSON.value)
}
</script>

<template>
  <div class="structogram-builder" :class="{ 'structogram-readonly': readonly }">
    <div class="builder-layout">
      <!-- Toolbar (hidden in readonly) -->
      <div v-if="!readonly" class="builder-sidebar">
        <StructogramToolbar
          @add="handleAdd"
          @clear="handleClear"
        />
      </div>

      <!-- Canvas -->
      <div class="builder-canvas">
        <div
          class="structogram-canvas"
          :class="{ 'empty': isEmpty }"
        >
          <div v-if="isEmpty" class="empty-state">
            <p class="text-[var(--color-text-secondary)] text-sm">
              {{ readonly ? t('structogramBuilder.emptyReadonly') : t('structogramBuilder.empty') }}
            </p>
          </div>
          <StructogramBlock
            v-for="block in blocks"
            :key="block.id"
            :block="block"
            :selected-id="selectedId"
            :readonly="readonly"
            @select="selectedId = $event"
            @update="handleUpdate"
            @delete="handleDelete"
            @add-to="handleAddTo"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.builder-layout { display: flex; gap: 16px; }
.builder-sidebar { width: 180px; flex-shrink: 0; }
.builder-canvas { flex: 1; min-width: 0; }

.structogram-canvas {
  border: 2px solid var(--color-border);
  border-radius: 6px;
  overflow: hidden;
  background: var(--color-surface);
  min-height: 120px;
}

.structogram-canvas.empty {
  display: flex;
  align-items: center;
  justify-content: center;
  border-style: dashed;
}

.empty-state { padding: 24px; text-align: center; }

.structogram-readonly .structogram-canvas { border-color: var(--color-border); }
</style>
