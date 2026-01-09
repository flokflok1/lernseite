<template>
  <div :class="cardClasses">
    <div v-if="$slots.header || title" class="card-header">
      <slot name="header">
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">{{ title }}</h3>
      </slot>
    </div>
    <div class="card-body">
      <slot />
    </div>
    <div v-if="$slots.footer" class="card-footer border-t border-[var(--color-border)] pt-4 mt-4">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  padding?: boolean
  shadow?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  padding: true,
  shadow: true,
})

const cardClasses = computed(() => {
  return [
    'card',
    {
      'p-0': !props.padding,
      'shadow-none': !props.shadow,
    },
  ]
})
</script>
