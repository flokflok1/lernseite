/**
 * ActivityFormSwitch.vue
 *
 * Dynamic component loader that maps methodType to the correct LM form.
 * Uses defineAsyncComponent for code-splitting.
 */
<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  methodType: number
  modelValue: Record<string, unknown>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, unknown>]
}>()

const { t } = useI18n()

const formComponents: Record<number, ReturnType<typeof defineAsyncComponent>> = {
  0: defineAsyncComponent(() => import('./forms/LM00DeepExplanationForm.vue')),
  1: defineAsyncComponent(() => import('./forms/LM01StepByStepForm.vue')),
  2: defineAsyncComponent(() => import('./forms/LM02InteractiveTheoryForm.vue')),
  3: defineAsyncComponent(() => import('./forms/LM03DiagramForm.vue')),
  4: defineAsyncComponent(() => import('./forms/LM04ExampleScenarioForm.vue')),
  5: defineAsyncComponent(() => import('./forms/LM05MathInteractiveForm.vue')),
  6: defineAsyncComponent(() => import('./forms/LM06FlashcardsForm.vue')),
  7: defineAsyncComponent(() => import('./forms/LM07DragAndDropForm.vue')),
  8: defineAsyncComponent(() => import('./forms/LM08ClozeTestForm.vue')),
  9: defineAsyncComponent(() => import('./forms/LM09FreeTextForm.vue')),
  10: defineAsyncComponent(() => import('./forms/LM10IHKStyleForm.vue')),
  11: defineAsyncComponent(() => import('./forms/LM11MultiStepForm.vue')),
}

const currentForm = computed(() => formComponents[props.methodType] ?? null)
</script>

<template>
  <component
    v-if="currentForm"
    :is="currentForm"
    :modelValue="modelValue"
    @update:modelValue="emit('update:modelValue', $event)"
  />
  <div v-else class="unsupported-form">
    {{ t('panel.manualEditor.activityEditor.unsupported') }}
  </div>
</template>

<style scoped>
.unsupported-form {
  padding: 12px;
  text-align: center;
  font-size: 12px;
  color: var(--color-text-tertiary);
  background: var(--color-surface);
  border: 1px dashed var(--color-border);
  border-radius: 4px;
}
</style>
