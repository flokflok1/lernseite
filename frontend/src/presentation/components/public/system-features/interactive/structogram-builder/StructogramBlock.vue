<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { StructogramBlock as Block } from './types/structogram.types'

interface Props {
  block: Block
  selectedId: string | null
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), { readonly: false })

const emit = defineEmits<{
  select: [id: string]
  update: [id: string, field: string, value: string]
  delete: [id: string]
  'add-to': [targetBlocks: Block[], type: string]
}>()

const { t } = useI18n()

function onInput(event: Event, field: string) {
  const text = (event.target as HTMLElement).textContent || ''
  emit('update', props.block.id, field, text)
}
</script>

<template>
  <div class="structogram-block" :class="{ 'ring-1 ring-blue-500': selectedId === block.id }">
    <!-- SEQUENCE -->
    <div v-if="block.type === 'sequence'" class="block-sequence" @click.stop="emit('select', block.id)">
      <div class="block-indicator bg-emerald-500" />
      <div
        class="block-content"
        :contenteditable="!readonly"
        @blur="onInput($event, 'text')"
        @keydown.enter.prevent="($event.target as HTMLElement).blur()"
        v-text="block.text || t('structogramBuilder.placeholderSequence')"
      />
      <button v-if="!readonly && selectedId === block.id" class="block-delete" @click.stop="emit('delete', block.id)">×</button>
    </div>

    <!-- IF/ELSE -->
    <div v-else-if="block.type === 'if'" class="block-if">
      <div class="block-condition" @click.stop="emit('select', block.id)">
        <div class="block-indicator bg-amber-500" />
        <div
          class="condition-text"
          :contenteditable="!readonly"
          @blur="onInput($event, 'condition')"
          @keydown.enter.prevent="($event.target as HTMLElement).blur()"
          v-text="block.condition || t('structogramBuilder.placeholderCondition')"
        />
        <button v-if="!readonly && selectedId === block.id" class="block-delete" @click.stop="emit('delete', block.id)">×</button>
      </div>
      <div class="block-branches">
        <div class="branch">
          <div class="branch-label yes">{{ t('structogramBuilder.yes') }}</div>
          <div class="branch-body">
            <StructogramBlock
              v-for="child in block.yes"
              :key="child.id"
              :block="child"
              :selected-id="selectedId"
              :readonly="readonly"
              @select="emit('select', $event)"
              @update="emit('update', $event, arguments[1], arguments[2])"
              @delete="emit('delete', $event)"
              @add-to="emit('add-to', $event, arguments[1])"
            />
            <button
              v-if="!readonly"
              class="add-nested"
              @click.stop="emit('add-to', block.yes as Block[], 'sequence')"
            >+</button>
          </div>
        </div>
        <div class="branch">
          <div class="branch-label no">{{ t('structogramBuilder.no') }}</div>
          <div class="branch-body">
            <StructogramBlock
              v-for="child in block.no"
              :key="child.id"
              :block="child"
              :selected-id="selectedId"
              :readonly="readonly"
              @select="emit('select', $event)"
              @update="emit('update', $event, arguments[1], arguments[2])"
              @delete="emit('delete', $event)"
              @add-to="emit('add-to', $event, arguments[1])"
            />
            <button
              v-if="!readonly"
              class="add-nested"
              @click.stop="emit('add-to', block.no as Block[], 'sequence')"
            >+</button>
          </div>
        </div>
      </div>
    </div>

    <!-- WHILE -->
    <div v-else-if="block.type === 'while'" class="block-while">
      <div class="block-condition" @click.stop="emit('select', block.id)">
        <div class="block-indicator bg-violet-500" />
        <div
          class="condition-text"
          :contenteditable="!readonly"
          @blur="onInput($event, 'condition')"
          @keydown.enter.prevent="($event.target as HTMLElement).blur()"
          v-text="block.condition || t('structogramBuilder.placeholderWhile')"
        />
        <button v-if="!readonly && selectedId === block.id" class="block-delete" @click.stop="emit('delete', block.id)">×</button>
      </div>
      <div class="while-body">
        <StructogramBlock
          v-for="child in block.body"
          :key="child.id"
          :block="child"
          :selected-id="selectedId"
          :readonly="readonly"
          @select="emit('select', $event)"
          @update="emit('update', $event, arguments[1], arguments[2])"
          @delete="emit('delete', $event)"
          @add-to="emit('add-to', $event, arguments[1])"
        />
        <button
          v-if="!readonly"
          class="add-nested"
          @click.stop="emit('add-to', block.body as Block[], 'sequence')"
        >+</button>
      </div>
    </div>

    <!-- SWITCH -->
    <div v-else-if="block.type === 'switch'" class="block-switch">
      <div class="block-condition" @click.stop="emit('select', block.id)">
        <div class="block-indicator bg-pink-500" />
        <div
          class="condition-text"
          :contenteditable="!readonly"
          @blur="onInput($event, 'expression')"
          @keydown.enter.prevent="($event.target as HTMLElement).blur()"
          v-text="block.expression || t('structogramBuilder.placeholderSwitch')"
        />
        <button v-if="!readonly && selectedId === block.id" class="block-delete" @click.stop="emit('delete', block.id)">×</button>
      </div>
      <div class="block-branches">
        <div v-for="(c, ci) in block.cases" :key="ci" class="branch">
          <div class="branch-label case">{{ c.label }}</div>
          <div class="branch-body">
            <StructogramBlock
              v-for="child in c.blocks"
              :key="child.id"
              :block="child"
              :selected-id="selectedId"
              :readonly="readonly"
              @select="emit('select', $event)"
              @update="emit('update', $event, arguments[1], arguments[2])"
              @delete="emit('delete', $event)"
              @add-to="emit('add-to', $event, arguments[1])"
            />
            <button
              v-if="!readonly"
              class="add-nested"
              @click.stop="emit('add-to', c.blocks as Block[], 'sequence')"
            >+</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.structogram-block { border-bottom: 1px solid var(--color-border); }
.structogram-block:last-child { border-bottom: none; }

.block-sequence { display: flex; align-items: stretch; position: relative; cursor: pointer; }
.block-sequence:hover { background: rgba(59,130,246,0.05); }
.block-indicator { width: 3px; flex-shrink: 0; }
.block-content { padding: 10px 14px; flex: 1; font-size: 0.875rem; color: var(--color-text); outline: none; min-height: 38px; }

.block-condition { display: flex; align-items: stretch; background: var(--color-surface-elevated, #1e2540); cursor: pointer; }
.block-condition:hover { background: rgba(59,130,246,0.08); }
.condition-text { padding: 10px 14px; flex: 1; font-weight: 600; font-size: 0.875rem; color: var(--color-text); text-align: center; outline: none; }

.block-branches { display: flex; }
.branch { flex: 1; border-right: 1px solid var(--color-border); }
.branch:last-child { border-right: none; }
.branch-label { padding: 3px 10px; font-size: 0.7rem; text-align: center; background: var(--color-background); border-bottom: 1px solid var(--color-border); font-weight: 600; }
.branch-label.yes { color: #22c55e; }
.branch-label.no { color: #ef4444; }
.branch-label.case { color: #ec4899; }
.branch-body { min-height: 38px; }

.while-body { margin-left: 16px; border-left: 2px solid #8b5cf6; min-height: 38px; }

.block-delete { position: absolute; right: 4px; top: 50%; transform: translateY(-50%); width: 20px; height: 20px; border-radius: 50%; border: none; background: #ef4444; color: white; font-size: 14px; line-height: 1; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.block-if .block-delete, .block-while .block-delete, .block-switch .block-delete { position: static; margin: 0 8px; transform: none; flex-shrink: 0; align-self: center; }

.add-nested { width: 100%; padding: 4px; border: 1px dashed var(--color-border); background: transparent; color: var(--color-text-secondary); font-size: 0.8rem; cursor: pointer; opacity: 0.4; transition: opacity 0.15s; }
.add-nested:hover { opacity: 1; border-color: #3b82f6; color: #3b82f6; }
</style>
