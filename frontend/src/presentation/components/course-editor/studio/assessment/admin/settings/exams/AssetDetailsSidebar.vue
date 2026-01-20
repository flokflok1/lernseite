<!--
  AssetDetailsSidebar - Asset Details & Actions
  Sub-component of AssetsTab
-->

<template>
  <div
    v-if="asset"
    class="fixed top-0 right-0 w-80 h-full bg-[var(--color-surface)] border-l border-[var(--color-border)] p-4 shadow-xl z-50"
  >
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold text-[var(--color-text-primary)]">
        {{ $t('features.aiEditorAssets.details.title') }}
      </h3>
      <button
        @click="$emit('close')"
        class="p-1 hover:bg-[var(--color-surface-secondary)] rounded"
      >
        ✕
      </button>
    </div>

    <!-- Preview -->
    <div class="aspect-video bg-[var(--color-surface-secondary)] rounded-lg mb-4 flex items-center justify-center overflow-hidden">
      <img
        v-if="asset.type === 'image'"
        :src="asset.thumbnail"
        :alt="asset.name"
        class="max-w-full max-h-full object-contain"
      />
      <span v-else class="text-4xl">{{ asset.preview }}</span>
    </div>

    <!-- Info -->
    <div class="space-y-3 text-sm">
      <div>
        <label class="text-[var(--color-text-tertiary)]">
          {{ $t('features.aiEditorAssets.details.name') }}
        </label>
        <input
          :value="asset.name"
          @input="$emit('update:name', ($event.target as HTMLInputElement).value)"
          type="text"
          class="w-full mt-1 px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
        />
      </div>
      <div>
        <label class="text-[var(--color-text-tertiary)]">
          {{ $t('features.aiEditorAssets.details.type') }}
        </label>
        <p class="text-[var(--color-text-primary)]">{{ asset.type }}</p>
      </div>
      <div>
        <label class="text-[var(--color-text-tertiary)]">
          {{ $t('features.aiEditorAssets.details.size') }}
        </label>
        <p class="text-[var(--color-text-primary)]">{{ asset.size }}</p>
      </div>
      <div>
        <label class="text-[var(--color-text-tertiary)]">
          {{ $t('features.aiEditorAssets.details.created') }}
        </label>
        <p class="text-[var(--color-text-primary)]">{{ asset.createdAt }}</p>
      </div>
      <div>
        <label class="text-[var(--color-text-tertiary)]">
          {{ $t('features.aiEditorAssets.details.usedIn') }}
        </label>
        <p class="text-[var(--color-text-primary)]">
          {{ $t('features.aiEditorAssets.details.lessonsCount', { count: asset.usageCount }) }}
        </p>
      </div>
    </div>

    <!-- Actions -->
    <div class="mt-6 space-y-2">
      <button
        @click="$emit('insert', asset)"
        class="w-full py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors"
      >
        {{ $t('features.aiEditorAssets.insertIntoLesson') }}
      </button>
      <button
        @click="$emit('download', asset)"
        class="w-full py-2 bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-surface)] transition-colors"
      >
        {{ $t('features.aiEditorAssets.download') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Asset {
  id: string
  name: string
  type: 'image' | 'formula' | 'diagram' | 'icon'
  thumbnail?: string
  preview?: string
  size: string
  createdAt: string
  usageCount: number
}

defineProps<{
  asset: Asset | null
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'insert', asset: Asset): void
  (e: 'download', asset: Asset): void
  (e: 'update:name', name: string): void
}>()
</script>
