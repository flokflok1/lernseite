/**
 * QuizEditorSection.vue
 *
 * Quiz lesson editor sub-component with question input,
 * multiple-choice answers, and correct answer selection.
 */

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  lessonId: number | undefined
}

defineProps<Props>()

const quizQuestion = ref('')
const quizAnswers = ref<Array<{ text: string; correct: boolean }>>([
  { text: '', correct: true },
  { text: '', correct: false },
])

function addAnswer(): void {
  quizAnswers.value.push({ text: '', correct: false })
}

function removeAnswer(index: number): void {
  if (quizAnswers.value.length > 2) {
    quizAnswers.value.splice(index, 1)
  }
}

function setCorrectAnswer(index: number): void {
  quizAnswers.value.forEach((a, i) => {
    a.correct = i === index
  })
}
</script>

<template>
  <div class="quiz-editor">
    <h3>{{ $t('panel.manualEditor.content.quizQuestion') }}</h3>
    <textarea
      v-model="quizQuestion"
      :placeholder="$t('panel.manualEditor.content.quizQuestion')"
      rows="3"
    />

    <h4>{{ $t('panel.manualEditor.content.quizAnswer') }}</h4>
    <div v-for="(answer, i) in quizAnswers" :key="i" class="quiz-answer">
      <input
        type="radio"
        :name="'correct-' + lessonId"
        :checked="answer.correct"
        @change="setCorrectAnswer(i)"
      />
      <input
        v-model="answer.text"
        type="text"
        :placeholder="$t('panel.manualEditor.content.quizAnswer') + ' ' + (i + 1)"
      />
      <button
        v-if="quizAnswers.length > 2"
        class="remove-answer"
        @click="removeAnswer(i)"
      >
        &times;
      </button>
    </div>
    <button class="add-answer-btn" @click="addAnswer">
      + {{ $t('panel.manualEditor.content.quizAddAnswer') }}
    </button>
  </div>
</template>

<style scoped>
.quiz-editor {
  padding: 16px;
}

.quiz-editor h3,
.quiz-editor h4 {
  font-size: 14px;
  margin: 0 0 8px;
}

.quiz-editor textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  resize: vertical;
}

.quiz-answer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.quiz-answer input[type="text"] {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.remove-answer {
  border: none;
  background: none;
  color: #e53935;
  cursor: pointer;
  font-size: 18px;
}

.add-answer-btn {
  margin-top: 4px;
  padding: 6px 12px;
  border: 1px dashed #2196f3;
  background: none;
  color: #2196f3;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
</style>
