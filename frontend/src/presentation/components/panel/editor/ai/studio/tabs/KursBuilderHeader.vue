<!--
  KursBuilderHeader.vue

  Header for the KursBuilder tab showing session status
  and action buttons (create/finalize session).
-->

<template>
  <div class="kurs-builder-header">
    <div class="header-left">
      <h3 class="header-title">
        {{ course?.title || $t('kursBuilder.title') }}
      </h3>
      <span v-if="session" class="session-badge">
        {{ $t('kursBuilder.sessionActive') }}
      </span>
    </div>

    <div class="header-right">
      <span v-if="hasChanges && draftStats" class="draft-stats">
        {{ draftStats.chapters }} {{ $t('kursBuilder.chapters') }},
        {{ draftStats.lessons }} {{ $t('kursBuilder.lessons') }}
      </span>

      <button
        v-if="!session"
        class="btn btn-primary btn-sm"
        :disabled="!course || creatingSession"
        @click="$emit('create-session')"
      >
        <span v-if="creatingSession" class="spinner-sm" />
        {{ $t('kursBuilder.createSession') }}
      </button>

      <button
        v-if="session && hasChanges"
        class="btn btn-success btn-sm"
        :disabled="finalizing"
        @click="$emit('finalize-session')"
      >
        <span v-if="finalizing" class="spinner-sm" />
        {{ $t('kursBuilder.finalizeSession') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface DraftStats {
  chapters: number
  lessons: number
}

defineProps<{
  course: { title: string } | null
  session: unknown | null
  creatingSession: boolean
  finalizing: boolean
  hasChanges: boolean
  draftStats: DraftStats | null
}>()

defineEmits<{
  'create-session': []
  'finalize-session': []
}>()
</script>

<style scoped>
.kurs-builder-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.session-badge {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border-radius: 9999px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.draft-stats {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

.spinner-sm {
  display: inline-block;
  width: 0.875rem;
  height: 0.875rem;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 0.25rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
