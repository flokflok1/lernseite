<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="$emit('close')"
    >
      <Card class="w-full max-w-md p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {{ mode === 'create' ? $t('admin.roles.createRole') : $t('admin.roles.editRole') }}
        </h2>

        <div class="space-y-4">
          <div v-if="mode === 'create'">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('admin.roles.technicalName') }}
            </label>
            <Input v-model="form.role_name" :placeholder="$t('admin.roles.technicalNamePlaceholder')" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('admin.roles.displayName') }}
            </label>
            <Input v-model="form.display_name" :placeholder="$t('admin.roles.displayNamePlaceholder')" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('admin.roles.description') }}
            </label>
            <textarea
              v-model="form.description"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              rows="2"
              :placeholder="$t('admin.roles.descriptionPlaceholder')"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('admin.roles.hierarchyLevel') }}
            </label>
            <Input v-model.number="form.hierarchy_level" type="number" min="1" max="9" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('admin.roles.color') }}
            </label>
            <div class="flex gap-2 flex-wrap">
              <button
                v-for="color in roleColors"
                :key="color"
                @click="form.color = color"
                :class="[
                  'w-8 h-8 rounded-full border-2 transition-all',
                  form.color === color ? 'border-gray-900 dark:border-white scale-110' : 'border-transparent'
                ]"
                :style="{ backgroundColor: color }"
              />
            </div>
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
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from '@/components/base/Card.vue'
import Button from '@/components/base/Button.vue'
import Input from '@/components/base/Input.vue'
import type { Role } from '@/api/admin/roles.api'

const { t } = useI18n()

interface Props {
  show: boolean
  mode: 'create' | 'edit'
  role?: Role | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  save: [data: RoleFormData]
}>()

export interface RoleFormData {
  role_name: string
  display_name: string
  description: string
  hierarchy_level: number
  color: string
  icon: string
}

const roleColors = [
  '#6b7280', '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#6366f1'
]

const form = ref<RoleFormData>({
  role_name: '',
  display_name: '',
  description: '',
  hierarchy_level: 1,
  color: '#6b7280',
  icon: 'user'
})

function resetForm() {
  if (props.mode === 'create') {
    form.value = {
      role_name: '',
      display_name: '',
      description: '',
      hierarchy_level: 1,
      color: '#6b7280',
      icon: 'user'
    }
  } else if (props.role) {
    form.value = {
      role_name: props.role.role_name,
      display_name: props.role.display_name,
      description: props.role.description || '',
      hierarchy_level: props.role.hierarchy_level,
      color: props.role.color,
      icon: props.role.icon
    }
  }
}

function handleSave() {
  emit('save', form.value)
}

// Reset form when modal opens or role changes
watch(() => props.show, (newVal) => {
  if (newVal) resetForm()
})

watch(() => props.role, () => {
  if (props.show) resetForm()
})
</script>
