<template>
  <div class="divide-y divide-[var(--color-border)]">
    <div
      v-for="item in items"
      :key="item.key_path"
      class="p-3 hover:bg-[var(--color-surface-secondary)] transition-colors"
    >
      <!-- Key (short) -->
      <div class="text-xs text-[var(--color-text-secondary)] mb-1 font-mono">
        {{ getShortKey(item.key_path, item.namespace) }}
      </div>

      <!-- Values Row -->
      <div class="flex gap-4 items-start">
        <!-- German (Source) -->
        <div class="flex-1 min-w-0">
          <div class="text-sm text-[var(--color-text-primary)] truncate" :title="item.de_value">
            {{ item.de_value || '---' }}
          </div>
        </div>

        <!-- Arrow -->
        <div class="text-[var(--color-text-secondary)]">&#8594;</div>

        <!-- Selected Language -->
        <div class="flex-1 min-w-0">
          <!-- Edit Mode -->
          <div v-if="editingKey === item.key_path" class="flex gap-2">
            <input
              :value="editValue"
              @input="$emit('update:editValue', ($event.target as HTMLInputElement).value)"
              type="text"
              class="flex-1 px-2 py-1 text-sm border border-primary-500 bg-[var(--color-bg)] text-[var(--color-text-primary)] rounded"
              @keyup.enter="$emit('save', item)"
              @keyup.escape="$emit('cancelEdit')"
              ref="editInput"
            />
            <button @click="$emit('save', item)" class="px-2 py-1 bg-green-600 text-white rounded text-sm">&#10003;</button>
            <button @click="$emit('cancelEdit')" class="px-2 py-1 bg-gray-500 text-white rounded text-sm">&#10005;</button>
          </div>

          <!-- Display Mode -->
          <div v-else class="flex items-center gap-2 group cursor-pointer" @click="$emit('startEdit', item)">
            <span
              class="text-sm truncate"
              :class="item.translated_value ? 'text-[var(--color-text-primary)]' : 'text-red-500 italic'"
              :title="item.translated_value || $t('panel.translations.notTranslated')"
            >
              {{ item.translated_value || $t('panel.translations.notTranslated') }}
            </span>
            <svg class="w-3 h-3 opacity-0 group-hover:opacity-100 text-primary-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface TranslationItem {
  key_id: string | null
  key_path: string
  namespace: string
  de_value: string
  translated_value: string
}

interface Props {
  items: TranslationItem[]
  editingKey: string | null
  editValue: string
}

defineProps<Props>()

defineEmits<{
  startEdit: [item: TranslationItem]
  save: [item: TranslationItem]
  cancelEdit: []
  'update:editValue': [value: string]
}>()

function getShortKey(keyPath: string, namespace: string): string {
  if (keyPath.startsWith(namespace + '.')) {
    return keyPath.slice(namespace.length + 1)
  }
  return keyPath
}
</script>
