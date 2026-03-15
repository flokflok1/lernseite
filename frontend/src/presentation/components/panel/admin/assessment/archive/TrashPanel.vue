<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  fetchTrash, restoreFromTrash, purgeFromTrash,
  type TrashItem
} from '@/infrastructure/api/clients/panel/admin/exams/folders.api'

interface Props {
  visible: boolean
}

defineProps<Props>()
const emit = defineEmits<{ close: []; restored: [] }>()
const { t, locale } = useI18n()

const programs = ref<TrashItem[]>([])
const folders = ref<TrashItem[]>([])
const loading = ref(false)

const allItems = computed(() => [
  ...programs.value.map(p => ({
    ...p,
    id: String(p.program_id),
    label: p.display_name?.[locale.value] || p.display_name?.de || 'Programm',
    icon: p.icon || '🎓',
  })),
  ...folders.value.map(f => ({
    ...f,
    id: String(f.folder_id),
    label: f.name || 'Ordner',
    icon: f.icon || '📁',
  })),
])

const isEmpty = computed(() => allItems.value.length === 0)

async function load() {
  loading.value = true
  try {
    const res = await fetchTrash()
    programs.value = res.data.programs || []
    folders.value = res.data.folders || []
  } catch {
    programs.value = []
    folders.value = []
  } finally {
    loading.value = false
  }
}

async function restore(item: TrashItem & { id: string }) {
  await restoreFromTrash(item.type, item.id)
  await load()
  emit('restored')
}

async function purge(item: TrashItem & { id: string }) {
  await purgeFromTrash(item.type, item.id)
  await load()
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(locale.value, {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

onMounted(load)
</script>

<template>
  <Teleport to="body">
    <Transition name="slide">
      <div
        v-if="visible"
        class="fixed inset-0 z-[10001] flex justify-end"
        @click.self="emit('close')"
      >
        <div class="w-[400px] h-full bg-gray-800 border-l border-gray-600/50 shadow-2xl flex flex-col">
          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/50">
            <div class="flex items-center gap-2">
              <span class="text-xl">🗑</span>
              <h3 class="text-lg font-semibold text-white">Papierkorb</h3>
              <span class="text-xs text-gray-400 bg-gray-700 px-2 py-0.5 rounded-full">
                {{ allItems.length }}
              </span>
            </div>
            <button
              class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400
                     hover:text-white hover:bg-gray-700 transition-colors"
              @click="emit('close')"
            >&times;</button>
          </div>

          <!-- Content -->
          <div class="flex-1 overflow-y-auto p-4">
            <div v-if="loading" class="flex justify-center py-8">
              <div class="animate-spin w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full" />
            </div>

            <div v-else-if="isEmpty" class="flex flex-col items-center justify-center py-12 text-gray-500">
              <span class="text-4xl mb-3">✨</span>
              <span class="text-sm">Papierkorb ist leer</span>
            </div>

            <div v-else class="space-y-2">
              <div
                v-for="item in allItems"
                :key="`${item.type}-${item.id}`"
                class="flex items-center gap-3 p-3 bg-gray-900/60 border border-gray-700/40
                       rounded-xl hover:border-gray-600 transition-colors"
              >
                <span class="text-2xl shrink-0">{{ item.icon }}</span>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-white truncate">{{ item.label }}</div>
                  <div class="text-[11px] text-gray-400">
                    {{ item.type === 'program' ? 'Programm' : 'Ordner' }}
                    · {{ formatDate(item.trashed_at) }}
                  </div>
                </div>
                <div class="flex gap-1 shrink-0">
                  <button
                    class="px-2.5 py-1.5 text-xs rounded-lg bg-green-600/20 text-green-400
                           hover:bg-green-600/30 transition-colors"
                    title="Wiederherstellen"
                    @click="restore(item as any)"
                  >↩</button>
                  <button
                    class="px-2.5 py-1.5 text-xs rounded-lg bg-red-600/20 text-red-400
                           hover:bg-red-600/30 transition-colors"
                    title="Endgültig löschen"
                    @click="purge(item as any)"
                  >✕</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.slide-enter-active { transition: transform 0.2s ease-out; }
.slide-leave-active { transition: transform 0.15s ease-in; }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }
</style>
