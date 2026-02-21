<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ArrayItemEditor from '../primitives/ArrayItemEditor.vue'

const props = defineProps<{ modelValue: Record<string, unknown> }>()
const emit = defineEmits<{ 'update:modelValue': [value: Record<string, unknown>] }>()
const { t } = useI18n()

type DragItem = { id: string; text: string }
type DragGroup = { label: string; correct_items: string[] }

const items = computed({
  get: () => (props.modelValue.items as DragItem[]) ?? [],
  set: (v) => emit('update:modelValue', { ...props.modelValue, items: v })
})

const groups = computed({
  get: () => (props.modelValue.groups as DragGroup[]) ?? [],
  set: (v) => emit('update:modelValue', { ...props.modelValue, groups: v })
})

const defaultItem = (): DragItem => ({ id: crypto.randomUUID(), text: '' })
const defaultGroup = (): DragGroup => ({ label: '', correct_items: [] })

const toggleItemInGroup = (group: DragGroup, itemId: string, groupIndex: number) => {
  const arr = [...groups.value]
  const current = group.correct_items ?? []
  const updated = current.includes(itemId)
    ? current.filter((id) => id !== itemId)
    : [...current, itemId]
  arr[groupIndex] = { ...group, correct_items: updated }
  groups.value = arr
}
</script>

<template>
  <div class="lm-form">
    <ArrayItemEditor
      v-model="items"
      :default-item="defaultItem"
      :label="t('panel.manualEditor.activityEditor.lm07.items')"
    >
      <template #default="{ item, update }">
        <input :value="item.text" @input="update({ ...item, text: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm07.itemText')" />
      </template>
    </ArrayItemEditor>

    <ArrayItemEditor
      v-model="groups"
      :default-item="defaultGroup"
      :label="t('panel.manualEditor.activityEditor.lm07.groups')"
    >
      <template #default="{ item: group, index: gIdx, update }">
        <input :value="group.label" @input="update({ ...group, label: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm07.groupLabel')" />
        <div v-if="items.length > 0" class="lm-field">
          <label>{{ t('panel.manualEditor.activityEditor.lm07.correctItems') }}</label>
          <div class="lm-checkbox-list">
            <label v-for="di in items" :key="di.id" class="lm-checkbox-item">
              <input
                type="checkbox"
                :checked="(group.correct_items ?? []).includes(di.id)"
                @change="toggleItemInGroup(group, di.id, gIdx)"
              />
              <span>{{ di.text || di.id.slice(0, 8) }}</span>
            </label>
          </div>
        </div>
      </template>
    </ArrayItemEditor>
  </div>
</template>

<style src="./lm-form.css" scoped />
