<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Error Alert (if any) -->
    <div
      v-if="error"
      class="p-4 bg-red-50 border border-red-200 rounded-lg"
    >
      <p class="text-sm text-red-700">{{ error }}</p>
    </div>

    <!-- Form Sections -->
    <div v-for="section in resolvedSections" :key="section.name">
      <!-- Section Header (if available) -->
      <div v-if="section.label" class="mb-4">
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
          {{ section.label }}
        </h3>
      </div>

      <!-- Fields in this section -->
      <div class="space-y-4">
        <div
          v-for="field in getSectionFields(section.name)"
          :key="field.name"
          class="form-group"
        >
          <!-- Label -->
          <label
            :for="`field-${field.name}`"
            class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2"
          >
            {{ field.label || field.name }}
            <span v-if="isFieldRequired(field)" class="text-red-500">*</span>
          </label>

          <!-- Text Input -->
          <input
            v-if="field.type === 'text' || field.type === 'email' || field.type === 'number'"
            :id="`field-${field.name}`"
            :key="`${field.name}-text`"
            :value="getFieldValue(field.name)"
            :type="field.type"
            :placeholder="field.placeholder"
            :required="isFieldRequired(field)"
            :disabled="isSubmitting"
            @input="updateField(field.name, ($event.target as HTMLInputElement).value)"
            class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent disabled:opacity-50"
          />

          <!-- Textarea -->
          <textarea
            v-else-if="field.type === 'textarea'"
            :id="`field-${field.name}`"
            :key="`${field.name}-textarea`"
            :value="getFieldValue(field.name)"
            :placeholder="field.placeholder"
            :required="isFieldRequired(field)"
            :disabled="isSubmitting"
            @input="updateField(field.name, ($event.target as HTMLTextAreaElement).value)"
            class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent disabled:opacity-50"
            rows="4"
          ></textarea>

          <!-- Select Dropdown -->
          <select
            v-else-if="field.type === 'select'"
            :id="`field-${field.name}`"
            :key="`${field.name}-select`"
            :value="getFieldValue(field.name)"
            :required="isFieldRequired(field)"
            :disabled="isSubmitting"
            @change="updateField(field.name, ($event.target as HTMLSelectElement).value)"
            class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent disabled:opacity-50"
          >
            <option value="">{{ field.placeholder || $t('common.selectOption') }}</option>
            <option
              v-for="option in field.options"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label || option.value }}
            </option>
          </select>

          <!-- Checkbox -->
          <div
            v-else-if="field.type === 'checkbox'"
            :key="`${field.name}-checkbox`"
            class="flex items-center"
          >
            <input
              :id="`field-${field.name}`"
              :checked="getFieldValue(field.name) === true || getFieldValue(field.name) === 'true'"
              type="checkbox"
              :disabled="isSubmitting"
              @change="updateField(field.name, ($event.target as HTMLInputElement).checked)"
              class="w-4 h-4 text-[var(--color-primary)] border-[var(--color-border)] rounded focus:ring-[var(--color-primary)] disabled:opacity-50"
            />
            <label
              :for="`field-${field.name}`"
              class="ml-2 text-sm text-[var(--color-text-secondary)] cursor-pointer"
            >
              {{ field.placeholder || field.label }}
            </label>
          </div>

          <!-- Radio Buttons -->
          <div
            v-else-if="field.type === 'radio'"
            :key="`${field.name}-radio`"
            class="space-y-2"
          >
            <label
              v-for="option in field.options"
              :key="option.value"
              class="flex items-center"
            >
              <input
                :value="option.value"
                :checked="getFieldValue(field.name) === option.value"
                type="radio"
                :name="field.name"
                :disabled="isSubmitting"
                @change="updateField(field.name, ($event.target as HTMLInputElement).value)"
                class="w-4 h-4 text-[var(--color-primary)] border-[var(--color-border)] focus:ring-[var(--color-primary)] disabled:opacity-50"
              />
              <span class="ml-2 text-sm text-[var(--color-text-secondary)]">
                {{ option.label || option.value }}
              </span>
            </label>
          </div>

          <!-- Hint Text (if available) -->
          <p v-if="field.hint" class="mt-1 text-xs text-[var(--color-text-secondary)]">
            {{ field.hint }}
          </p>
        </div>
      </div>
    </div>

    <!-- Submit Button -->
    <div class="flex gap-2">
      <button
        type="submit"
        :disabled="isSubmitting"
        class="px-6 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 font-medium transition-opacity"
      >
        {{ isSubmitting ? $t('common.submitting') : submitLabel }}
      </button>

      <button
        v-if="showCancelButton"
        type="button"
        :disabled="isSubmitting"
        @click="$emit('cancel')"
        class="px-6 py-2 border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-background)] disabled:opacity-50 font-medium transition-colors"
      >
        {{ $t('common.cancel') }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSchemaI18n } from '@/application/composables/i18n/useSchemaI18n'
import type { UISchema, ResolvedField } from '@/infrastructure/utils/i18nResolver'

interface Props {
  /**
   * UI Schema defining the form structure
   * Should already be resolved with i18n keys if using dynamic schemas
   */
  schema: UISchema

  /**
   * Form data to bind to fields
   * Should match the schema field structure
   */
  modelValue: Record<string, any>

  /**
   * Show cancel button
   */
  showCancelButton?: boolean

  /**
   * Label for submit button
   */
  submitLabel?: string

  /**
   * Disable form submission
   */
  isSubmitting?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: Record<string, any>): void
  (e: 'submit', data: Record<string, any>): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  showCancelButton: false,
  submitLabel: 'common.submit',
  isSubmitting: false
})

const emit = defineEmits<Emits>()
const { resolveSchema } = useSchemaI18n()
const error = ref<string | null>(null)

// Resolve schema with i18n translations
const resolvedSchema = computed(() => {
  try {
    return resolveSchema(props.schema)
  } catch (err) {
    error.value = `Failed to resolve schema: ${err instanceof Error ? err.message : 'Unknown error'}`
    console.error('Schema resolution error:', err)
    // Return original schema as fallback
    return props.schema as any
  }
})

// Group fields by section (if ui_config.sections exists)
const resolvedSections = computed(() => {
  const sections = resolvedSchema.value.ui_config?.sections || []

  if (sections.length === 0) {
    // If no sections defined, create default section
    return [{ name: 'default', label: null }]
  }

  return sections
})

// Get fields for a specific section
const getSectionFields = (sectionName: string): ResolvedField[] => {
  if (sectionName === 'default') {
    // Return all fields if no sections are defined
    if (!resolvedSchema.value.ui_config?.sections || resolvedSchema.value.ui_config.sections.length === 0) {
      return resolvedSchema.value.fields || []
    }
    return []
  }

  // Return fields associated with this section
  // Note: This assumes fields have a section property; adjust based on actual schema structure
  return (resolvedSchema.value.fields || []).filter(
    (field: any) => field.section === sectionName || (!field.section && sectionName === 'default')
  )
}

// Get current value of a field
const getFieldValue = (fieldName: string): any => {
  return props.modelValue[fieldName] ?? ''
}

// Update a single field
const updateField = (fieldName: string, value: any) => {
  emit('update:modelValue', {
    ...props.modelValue,
    [fieldName]: value
  })
}

// Check if a field is required
const isFieldRequired = (field: ResolvedField): boolean => {
  return (field as any).required === true
}

// Handle form submission
const handleSubmit = () => {
  error.value = null

  // Validate required fields
  const missingRequired = resolvedSchema.value.fields.filter(
    (field: ResolvedField) =>
      isFieldRequired(field) &&
      (!props.modelValue[field.name] || props.modelValue[field.name] === '')
  )

  if (missingRequired.length > 0) {
    error.value = `Missing required fields: ${missingRequired.map((f: ResolvedField) => f.label || f.name).join(', ')}`
    return
  }

  // Emit submit event with form data
  emit('submit', { ...props.modelValue })
}

// Initialize component
onMounted(() => {
  // Verify schema is valid
  if (!props.schema || !props.schema.fields) {
    error.value = 'Invalid schema: missing fields array'
  }
})
</script>

<style scoped>
.form-group {
  @apply space-y-1;
}
</style>
