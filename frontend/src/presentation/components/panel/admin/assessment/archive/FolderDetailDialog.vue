<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

interface Props {
  visible: boolean
  folderName: string
  folderIcon: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  save: [name: string, icon: string]
  close: []
}>()

const { t } = useI18n()

const editName = ref('')
const editIcon = ref('')

watch(() => props.visible, (v) => {
  if (v) {
    editName.value = props.folderName
    editIcon.value = props.folderIcon
  }
})

function handleSave() {
  if (editName.value.trim()) {
    emit('save', editName.value.trim(), editIcon.value)
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="fixed inset-0 bg-black/60 flex items-center justify-center z-[10001]"
      @click.self="emit('close')"
    >
      <div class="bg-gray-800 border border-gray-600/50 rounded-xl p-6 w-[380px] shadow-2xl">
        <h3 class="text-lg font-semibold mb-4">
          {{ t('panel.examArchive.folderDialog.editTitle') }}
        </h3>

        <div class="space-y-4">
          <div>
            <label class="block text-sm text-gray-400 mb-1">
              {{ t('panel.examArchive.folderDialog.name') }}
            </label>
            <input
              v-model="editName"
              class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2
                     text-white outline-none focus:border-indigo-500"
              @keydown.enter="handleSave"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">
              {{ t('panel.examArchive.folderDialog.icon') }}
            </label>
            <input
              v-model="editIcon"
              class="w-20 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2
                     text-white text-center text-xl outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-6">
          <button
            class="px-4 py-2 rounded-lg text-sm text-gray-300 hover:bg-gray-700"
            @click="emit('close')"
          >
            {{ t('panel.examArchive.folderDialog.cancel') }}
          </button>
          <button
            class="px-4 py-2 rounded-lg text-sm bg-indigo-600 text-white hover:bg-indigo-500"
            @click="handleSave"
          >
            {{ t('panel.examArchive.folderDialog.save') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
