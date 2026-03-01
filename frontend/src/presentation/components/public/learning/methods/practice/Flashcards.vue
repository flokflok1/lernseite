<template>
  <div class="flashcards-learning-method">
    <h2>{{ $t('learningMethods.flashcards.title') }}</h2>
    <p>{{ $t('learningMethods.flashcards.description') }}</p>

    <div class="stub-notice">
      ⚠️ Learning Method Stub - LM00 - Implementation Coming Soon
    </div>

    <!-- TODO: Implement flashcards learning method -->
    <!-- Features: Card flip animation, spaced repetition, progress tracking -->
  </div>
</template>

<script setup lang="ts">
// TODO: Implement Flashcards Learning Method (LM00)
// Group A: Erklärend (Explanation/Theory)
//
// Features to implement:
// - Card creation and editing
// - Front/back flip animation
// - Spaced repetition algorithm
// - Progress tracking
// - Mark as known/unknown
// - Shuffle mode
// - Study sessions
</script>

<style scoped>
.flashcards-learning-method {
  padding: 2rem;
}

.stub-notice {
  background-color: #fff3cd;
  border: 1px solid #ffc107;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
  color: #856404;
  font-weight: 500;
}
</style>
