<template>
  <div class="ap2-stub">
    <h2 class="ap2-stub-title">{{ t(titleKey) }}</h2>
    <p class="ap2-stub-sub">{{ t(subtitleKey) }}</p>
    <div class="ap2-stub-status">
      <span class="ap2-stub-badge">{{ t('ap2Trainer.stub.inDevBadge') }}</span>
      {{ t(stubTextKey) }}
    </div>
    <RouterLink to="/ap2-training/dashboard" class="ap2-stub-back">
      {{ t('ap2Trainer.stub.back') }}
    </RouterLink>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

interface Props {
  titleKey: string
  subtitleKey: string
  stubTextKey: string
}
defineProps<Props>()
const { t } = useI18n()
</script>

<style scoped>
.ap2-stub { text-align: center; padding: 64px 24px; }
.ap2-stub-title { color: var(--color-text-primary, #fff); margin: 0 0 8px; }
.ap2-stub-sub { color: #94a3b8; margin: 0 0 24px; }
.ap2-stub-status {
  display: inline-block; padding: 16px 24px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid #d97706;
  border-radius: 10px;
  color: #fcd34d;
  max-width: 520px;
  margin-bottom: 24px;
}
.ap2-stub-badge { display: block; font-weight: 700; margin-bottom: 8px; }
.ap2-stub-back { color: #818cf8; text-decoration: none; font-weight: 600; }
.ap2-stub-back:hover { text-decoration: underline; }
</style>
