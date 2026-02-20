<template>
  <div class="info-tab">
    <div class="info-section">
      <h3 class="section-title">{{ $t('panel.plugins.pluginCode') }}</h3>
      <p class="section-value code">{{ plugin.plugin_code }}</p>
    </div>

    <div class="info-section">
      <h3 class="section-title">{{ $t('panel.plugins.description') }}</h3>
      <p class="section-value">{{ plugin.description || $t('common.notSpecified') }}</p>
    </div>

    <div class="info-grid">
      <div class="info-section">
        <h3 class="section-title">{{ $t('panel.plugins.group') }}</h3>
        <span class="badge badge-group">{{ plugin.group_code }}</span>
      </div>

      <div class="info-section">
        <h3 class="section-title">{{ $t('panel.plugins.tier') }}</h3>
        <span class="badge badge-tier">{{ plugin.tier }}</span>
      </div>

      <div class="info-section">
        <h3 class="section-title">{{ $t('panel.plugins.kiUsage') }}</h3>
        <span class="badge badge-ki">{{ plugin.ki_usage }}</span>
      </div>
    </div>

    <div class="info-section">
      <h3 class="section-title">{{ $t('panel.plugins.filePath') }}</h3>
      <p class="section-value code">{{ plugin.file_path }}</p>
    </div>

    <div class="info-section">
      <h3 class="section-title">{{ $t('panel.plugins.fileHash') }}</h3>
      <p class="section-value code">{{ plugin.file_hash }}</p>
    </div>

    <div v-if="plugin.submitted_at" class="info-section">
      <h3 class="section-title">{{ $t('common.createdAt') }}</h3>
      <p class="section-value">{{ formatDate(plugin.submitted_at) }}</p>
    </div>

    <div v-if="plugin.reviewed_at" class="info-section">
      <h3 class="section-title">{{ $t('common.reviewedAt') }}</h3>
      <p class="section-value">{{ formatDate(plugin.reviewed_at) }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LMPluginMetadata } from '@/domain/models/learning/plugins.types'

interface Props {
  plugin: LMPluginMetadata
  formatDate: (dateString: string) => string
}

defineProps<Props>()
</script>

<style scoped>
.info-tab {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.section-title {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary, #6b7280);
}

.section-value {
  margin: 0;
  font-size: 0.95rem;
  color: var(--color-text-primary, #1f2937);
}

.section-value.code {
  font-family: monospace;
  font-size: 0.875rem;
  background: var(--color-bg-secondary, #f3f4f6);
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  word-break: break-all;
}

.badge {
  display: inline-block;
  padding: 0.375rem 0.875rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.badge-group {
  background: var(--color-bg-badge-group, #dbeafe);
  color: var(--color-text-badge-group, #1e40af);
}

.badge-tier {
  background: var(--color-bg-badge-tier, #fef3c7);
  color: var(--color-text-badge-tier, #92400e);
}

.badge-ki {
  background: var(--color-bg-badge-ki, #e0e7ff);
  color: var(--color-text-badge-ki, #3730a3);
}
</style>
