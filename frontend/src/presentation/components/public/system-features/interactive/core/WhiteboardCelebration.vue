<!--
  WhiteboardCelebration - Lesson completion celebration overlay
  Extracted from WhiteboardTutorLesson for quality gate G01 compliance.
-->

<template>
  <Transition name="fade">
    <div v-if="visible" class="celebration">
      <div class="celebration-content">
        <div class="confetti">&#127881;</div>
        <h2>{{ $t('lesson.whiteboard.celebration.title') }}</h2>
        <p>{{ $t('lesson.whiteboard.celebration.message') }}</p>
        <button @click="$emit('complete')" class="btn-complete">
          {{ $t('common.continue') }}
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
}>()

defineEmits<{
  (e: 'complete'): void
}>()
</script>

<style scoped>
.celebration {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.celebration-content {
  text-align: center;
  padding: 2rem;
}

.confetti {
  font-size: 4rem;
  animation: pop 0.5s ease-out;
}

@keyframes pop {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.celebration h2 {
  color: #f1f5f9;
  font-size: 1.75rem;
  margin: 1rem 0 0.5rem;
}

.celebration p {
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.btn-complete {
  padding: 0.875rem 2.5rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-complete:hover {
  transform: translateY(-2px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
