<!--
  Category Create/Edit Modal

  Modal for creating or editing categories
  Supports parent selection and all category fields
-->

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <!-- Header -->
      <div class="modal-header">
        <h2 class="text-xl font-bold text-[var(--color-text-primary)]">
          {{ isEditing ? $t('windows.categoryModal.titleEdit') : $t('windows.categoryModal.titleCreate') }}
        </h2>
        <button
          @click="$emit('close')"
          class="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] text-2xl leading-none"
        >
          ×
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="modal-body">
        <!-- Name -->
        <div class="form-group">
          <label class="form-label">
            {{ $t('windows.categoryModal.nameLabel') }}
            <span class="text-xs text-[var(--color-text-secondary)]">{{ $t('windows.categoryModal.nameHint') }}</span>
          </label>
          <input
            v-model="formData.name"
            type="text"
            required
            class="form-input"
            :placeholder="$t('windows.categoryModal.namePlaceholder')"
            maxlength="100"
          />
        </div>

        <!-- Slug -->
        <div class="form-group">
          <label class="form-label">
            {{ $t('windows.categoryModal.slugLabel') }}
            <span class="text-xs text-[var(--color-text-secondary)]">{{ $t('windows.categoryModal.slugHint') }}</span>
          </label>
          <input
            v-model="formData.slug"
            type="text"
            required
            class="form-input font-mono text-sm"
            :placeholder="$t('windows.categoryModal.slugPlaceholder')"
            pattern="[a-z0-9\-]+"
            maxlength="100"
          />
          <p class="text-xs text-[var(--color-text-secondary)] mt-1">
            {{ $t('windows.categoryModal.slugPattern') }}
          </p>
        </div>

        <!-- Description -->
        <div class="form-group">
          <label class="form-label">{{ $t('windows.categoryModal.descriptionLabel') }}</label>
          <textarea
            v-model="formData.description"
            rows="3"
            class="form-input"
            :placeholder="$t('windows.categoryModal.descriptionPlaceholder')"
            maxlength="500"
          ></textarea>
        </div>

        <!-- Parent Category -->
        <div class="form-group">
          <label class="form-label">
            {{ $t('windows.categoryModal.parentLabel') }}
            <span class="text-xs text-[var(--color-text-secondary)]">{{ $t('windows.categoryModal.parentHint') }}</span>
          </label>
          <select v-model="formData.parent_id" class="form-input">
            <option :value="null">{{ $t('windows.categoryModal.parentNone') }}</option>
            <option
              v-for="cat in selectableParents"
              :key="cat.category_id"
              :value="cat.category_id"
              :disabled="cat.level >= 20"
            >
              {{ '→'.repeat(Math.min(cat.level, 10)) }} {{ cat.name }}
              <span v-if="cat.path" class="text-[var(--color-text-secondary)]"> ({{ cat.path }})</span>
              <span v-if="cat.level >= 20">{{ $t('windows.categoryModal.parentMaxDepth') }}</span>
            </option>
          </select>
          <p class="text-xs text-[var(--color-text-secondary)] mt-1">
            {{ $t('windows.categoryModal.currentLevel', { level: currentLevel }) }}
          </p>
        </div>

        <!-- Icon & Color Row -->
        <div class="grid grid-cols-2 gap-4">
          <!-- Icon -->
          <div class="form-group">
            <label class="form-label">
              {{ $t('windows.categoryModal.iconLabel') }}
              <span class="text-xs text-[var(--color-text-secondary)]">{{ $t('windows.categoryModal.iconHint') }}</span>
            </label>
            <input
              v-model="formData.icon"
              type="text"
              class="form-input text-center text-2xl"
              placeholder="📚"
              maxlength="2"
            />
          </div>

          <!-- Color -->
          <div class="form-group">
            <label class="form-label">{{ $t('windows.categoryModal.colorLabel') }}</label>
            <input
              v-model="formData.color"
              type="color"
              class="form-input h-12 cursor-pointer"
            />
          </div>
        </div>

        <!-- Order Index -->
        <div class="form-group">
          <label class="form-label">
            {{ $t('windows.categoryModal.orderLabel') }}
            <span class="text-xs text-[var(--color-text-secondary)]">{{ $t('windows.categoryModal.orderHint') }}</span>
          </label>
          <input
            v-model.number="formData.order_index"
            type="number"
            min="0"
            step="1"
            class="form-input"
            placeholder="0"
          />
        </div>

        <!-- Active Status -->
        <div class="form-group">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="formData.is_active"
              type="checkbox"
              class="w-4 h-4 text-[var(--color-primary)] border-[var(--color-border)] rounded focus:ring-[var(--color-primary)]"
            />
            <span class="form-label mb-0">{{ $t('windows.categoryModal.isActive') }}</span>
          </label>
          <p class="text-xs text-[var(--color-text-secondary)] mt-1 ml-6">
            {{ $t('windows.categoryModal.inactiveHint') }}
          </p>
        </div>

        <!-- Actions -->
        <div class="modal-footer">
          <button
            type="button"
            @click="$emit('close')"
            class="btn-secondary"
          >
            {{ $t('windows.categoryModal.cancel') }}
          </button>
          <button
            type="submit"
            :disabled="!isValid"
            class="btn-primary"
          >
            {{ isEditing ? $t('windows.categoryModal.save') : $t('windows.categoryModal.create') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

interface Props {
  category?: any
  parentId?: number | null
  allCategories: any[]
}

const props = defineProps<Props>()

const emit = defineEmits(['close', 'save'])

// State
const formData = ref<{
  name: string
  slug: string
  description: string
  parent_id: number | null
  icon: string
  color: string
  order_index: number
  is_active: boolean
}>({
  name: '',
  slug: '',
  description: '',
  parent_id: null,
  icon: '',
  color: '#3B82F6',
  order_index: 0,
  is_active: true
})

// Computed
const isEditing = computed(() => !!props.category)

const selectableParents = computed(() => {
  // Exclude current category and its descendants when editing
  if (isEditing.value) {
    return props.allCategories.filter(cat => {
      return cat.category_id !== props.category.category_id &&
             !isDescendantOf(cat, props.category.category_id)
    })
  }
  return props.allCategories
})

const currentLevel = computed(() => {
  if (!formData.value.parent_id) return 1

  const parent = props.allCategories.find(cat => cat.category_id === formData.value.parent_id)
  return parent ? parent.level + 1 : 1
})

const isValid = computed(() => {
  return formData.value.name.length >= 2 &&
         formData.value.slug.length >= 2 &&
         /^[a-z0-9-]+$/.test(formData.value.slug) &&
         currentLevel.value <= 20
})

// Methods
const isDescendantOf = (category: any, ancestorId: number): boolean => {
  if (!category.parent_id) return false
  if (category.parent_id === ancestorId) return true

  const parent = props.allCategories.find(cat => cat.category_id === category.parent_id)
  return parent ? isDescendantOf(parent, ancestorId) : false
}

const handleSubmit = () => {
  if (!isValid.value) return

  const dataToSave: Record<string, any> = { ...formData.value }

  // Convert empty string to null for parent_id
  if (dataToSave.parent_id === '' || dataToSave.parent_id === 'null') {
    dataToSave.parent_id = null
  }

  // Calculate level based on parent_id
  if (dataToSave.parent_id === null) {
    dataToSave.level = 1 // Root category
  } else {
    const parent = props.allCategories.find(cat => cat.category_id === dataToSave.parent_id)
    dataToSave.level = parent ? parent.level + 1 : 1
  }

  emit('save', dataToSave)
}

// Auto-generate slug from name
watch(() => formData.value.name, (newName) => {
  if (!isEditing.value && newName) {
    formData.value.slug = newName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
  }
})

// Initialize form
onMounted(() => {
  if (props.category) {
    // Editing existing category
    formData.value = {
      name: props.category.name || '',
      slug: props.category.slug || '',
      description: props.category.description || '',
      parent_id: props.category.parent_id || null,
      icon: props.category.icon || '',
      color: props.category.color || '#3B82F6',
      order_index: props.category.order_index || 0,
      is_active: props.category.is_active !== false
    }
  } else if (props.parentId) {
    // Creating child category
    formData.value.parent_id = props.parentId
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background-color: var(--color-surface);
  border-radius: 0.75rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1.5rem;
  margin-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background-color: var(--color-background);
  color: var(--color-text-primary);
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  ring: 2px;
  ring-color: var(--color-primary);
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background-color: var(--color-primary);
  color: white;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: opacity 0.2s;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  border-radius: 0.5rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: var(--color-background);
}
</style>
