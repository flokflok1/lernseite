<template>
  <div class="schema-tab">
    <div class="schema-section">
      <h3 class="section-title">{{ $t('panel.plugins.schema') }}</h3>
      <pre class="schema-code">{{ JSON.stringify(plugin.config_schema, null, 2) }}</pre>
    </div>

    <div v-if="plugin.default_config" class="schema-section">
      <h3 class="section-title">{{ $t('common.defaultConfig') }}</h3>
      <pre class="schema-code">{{ JSON.stringify(plugin.default_config, null, 2) }}</pre>
    </div>

    <div v-if="plugin.agent_support" class="schema-section">
      <h3 class="section-title">{{ $t('common.agentSupport') }}</h3>
      <pre class="schema-code">{{ JSON.stringify(plugin.agent_support, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LMPluginMetadata } from '@/types/plugins'

interface Props {
  plugin: LMPluginMetadata
}

defineProps<Props>()
</script>

<style scoped>
.schema-tab {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.schema-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.section-title {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary, #6b7280);
}

.schema-code {
  background: #1e293b;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
}
</style>
