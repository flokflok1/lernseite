<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="$emit('close')"
    >
      <Card class="w-full max-w-md p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {{ mode === 'create' ? $t('panel.groups.create') : $t('panel.groups.edit') }}
        </h2>

        <div class="space-y-4">
          <!-- Group Name (GBA) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('panel.groups.roleName') }}
            </label>
            <Input v-model="form.name" :placeholder="$t('panel.groups.form.roleNamePlaceholder')" />
          </div>

          <!-- Slug (GBA) -->
          <div v-if="mode === 'create'">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('panel.groups.form.slug') }}
            </label>
            <Input v-model="form.slug" :placeholder="$t('panel.groups.form.slugPlaceholder')" />
            <p class="text-xs text-gray-500 mt-1">{{ $t('panel.groups.form.slugHelp') }}</p>
          </div>

          <!-- Group Type (GBA) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('panel.groups.form.groupType') }}
            </label>
            <select
              v-model="form.type"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="custom">{{ $t('panel.groups.typeCustom') }}</option>
              <option value="org_admin">{{ $t('panel.groups.typeOrg') }}</option>
              <option value="system_admin" :disabled="mode === 'create'">{{ $t('panel.groups.typeSystem') }}</option>
            </select>
          </div>

          <!-- Description (GBA) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('panel.groups.description') }}
            </label>
            <textarea
              v-model="form.description"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              rows="2"
              :placeholder="$t('panel.groups.form.descriptionPlaceholder')"
            />
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <Button variant="secondary" @click="$emit('close')">{{ $t('common.cancel') }}</Button>
          <Button @click="handleSave">
            {{ mode === 'create' ? $t('common.create') : $t('common.save') }}
          </Button>
        </div>
      </Card>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
/**
 * Group Edit Modal (GBA)
 * Modal for creating and editing groups.
 */
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from '@/presentation/components/shared/ui/Card.vue'
import Button from '@/presentation/components/shared/ui/Button.vue'
import Input from '@/presentation/components/shared/ui/Input.vue'
import type { Group } from '@/presentation/components/panel/groups/types/group.types'

const { t } = useI18n()

// GBA Form Data type
export interface GroupFormData {
  name: string
  slug: string
  type: 'system_admin' | 'org_admin' | 'custom'
  description?: string
}

interface Props {
  show: boolean
  mode: 'create' | 'edit'
  group?: Group | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  save: [data: GroupFormData]
}>()

const form = ref<GroupFormData>({
  name: '',
  slug: '',
  type: 'custom',
  description: ''
})

function resetForm() {
  if (props.mode === 'create') {
    form.value = {
      name: '',
      slug: '',
      type: 'custom',
      description: ''
    }
  } else if (props.group) {
    form.value = {
      name: props.group.name,
      slug: props.group.slug,
      type: props.group.type,
      description: props.group.description || ''
    }
  }
}

function handleSave() {
  emit('save', form.value)
}

// Reset form when modal opens or group changes
watch(() => props.show, (newVal) => {
  if (newVal) resetForm()
})

watch(() => props.group, () => {
  if (props.show) resetForm()
})
</script>
