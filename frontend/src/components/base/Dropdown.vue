<template>
  <div class="dropdown-wrapper" ref="dropdownRef">
    <select
      v-if="native"
      :id="id"
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      :class="selectClasses"
      @change="handleChange"
    >
      <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
      <option
        v-for="option in options"
        :key="getOptionValue(option)"
        :value="getOptionValue(option)"
      >
        {{ getOptionLabel(option) }}
      </option>
    </select>

    <div v-else class="custom-dropdown">
      <label v-if="label" :for="id" class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
        {{ label }}
        <span v-if="required" class="text-red-500">*</span>
      </label>

      <button
        type="button"
        :class="selectClasses"
        @click="toggleDropdown"
        :disabled="disabled"
      >
        <span class="selected-text">
          {{ selectedLabel || placeholder || 'Select option' }}
        </span>
        <svg class="dropdown-icon" :class="{ 'rotate-180': isOpen }" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>

      <Transition name="dropdown">
        <div v-if="isOpen" class="dropdown-menu">
          <div
            v-for="option in options"
            :key="getOptionValue(option)"
            :class="optionClasses(option)"
            @click="selectOption(option)"
          >
            {{ getOptionLabel(option) }}
          </div>
        </div>
      </Transition>

      <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
      <p v-else-if="hint" class="mt-1 text-sm text-[var(--color-text-secondary)]">{{ hint }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  id?: string
  label?: string
  modelValue?: string | number | null
  options: Array<any>
  valueKey?: string
  labelKey?: string
  placeholder?: string
  disabled?: boolean
  required?: boolean
  native?: boolean
  error?: string
  hint?: string
}

const props = withDefaults(defineProps<Props>(), {
  valueKey: 'value',
  labelKey: 'label',
  native: false,
  disabled: false,
  required: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number | null]
  change: [value: string | number | null]
}>()

const dropdownRef = ref<HTMLElement>()
const isOpen = ref(false)

const getOptionValue = (option: any) => {
  return typeof option === 'object' ? option[props.valueKey] : option
}

const getOptionLabel = (option: any) => {
  return typeof option === 'object' ? option[props.labelKey] : option
}

const selectedLabel = computed(() => {
  if (!props.modelValue) return ''
  const selected = props.options.find(opt => getOptionValue(opt) === props.modelValue)
  return selected ? getOptionLabel(selected) : ''
})

const selectClasses = computed(() => {
  return [
    'dropdown-select',
    {
      'dropdown-error': props.error,
      'opacity-50 cursor-not-allowed': props.disabled,
    },
  ]
})

const optionClasses = (option: any) => {
  return [
    'dropdown-option',
    {
      'dropdown-option-selected': getOptionValue(option) === props.modelValue,
    },
  ]
}

const toggleDropdown = () => {
  if (!props.disabled) {
    isOpen.value = !isOpen.value
  }
}

const selectOption = (option: any) => {
  const value = getOptionValue(option)
  emit('update:modelValue', value)
  emit('change', value)
  isOpen.value = false
}

const handleChange = (event: Event) => {
  const value = (event.target as HTMLSelectElement).value
  emit('update:modelValue', value || null)
  emit('change', value || null)
}

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.dropdown-wrapper {
  position: relative;
  width: 100%;
}

.dropdown-select {
  @apply w-full px-3 py-2 border border-[var(--color-border)] rounded-md;
  @apply focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent;
  @apply transition-colors;
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

.dropdown-error {
  @apply border-red-500 focus:ring-red-500;
}

.custom-dropdown .dropdown-select {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.selected-text {
  flex: 1;
  text-align: left;
}

.dropdown-icon {
  width: 1.25rem;
  height: 1.25rem;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.25rem;
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  max-height: 15rem;
  overflow-y: auto;
  z-index: 50;
}

.dropdown-option {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.15s;
}

.dropdown-option:hover {
  background-color: var(--color-background-secondary);
}

.dropdown-option-selected {
  background-color: var(--color-primary);
  color: white;
}

.dropdown-option-selected:hover {
  background-color: var(--color-primary-dark);
}

/* Transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-0.5rem);
}
</style>
