<!--
  TheoryTextContent - Displays the theory text blocks

  Renders overview, learning goals, concepts, terms, exam tips,
  and summary sections from generated chapter theory content.
-->

<template>
  <div class="text-section">
    <!-- Overview -->
    <div v-if="content.overview" class="theory-block overview">
      <h3><span class="block-icon">&#128161;</span> {{ $t('chapterTheory.blocks.overview') }}</h3>
      <p>{{ content.overview }}</p>
    </div>

    <!-- Learning Goals -->
    <div v-if="content.learningGoals?.length" class="theory-block goals">
      <h3><span class="block-icon">&#127919;</span> {{ $t('chapterTheory.blocks.learningGoals') }}</h3>
      <ul>
        <li v-for="(goal, i) in content.learningGoals" :key="i">
          {{ goal }}
        </li>
      </ul>
    </div>

    <!-- Concepts -->
    <div v-if="content.concepts?.length" class="theory-block concepts">
      <h3><span class="block-icon">&#128218;</span> {{ $t('chapterTheory.blocks.coreConcepts') }}</h3>
      <div class="concepts-grid">
        <div
          v-for="(concept, i) in content.concepts"
          :key="i"
          class="concept-card"
        >
          <div class="concept-header">
            <span v-if="concept.emoji" class="concept-emoji">{{ concept.emoji }}</span>
            <span class="concept-title">{{ concept.title }}</span>
          </div>
          <p class="concept-desc">
            {{ concept.description || concept.oneLiner }}
          </p>
          <p v-if="concept.example" class="concept-example">
            <strong>{{ $t('chapterTheory.blocks.example') }}</strong> {{ concept.example }}
          </p>
          <p v-if="concept.tip" class="concept-tip">
            <span>&#128161;</span> {{ concept.tip }}
          </p>
        </div>
      </div>
    </div>

    <!-- Terms -->
    <div v-if="content.terms?.length" class="theory-block terms">
      <h3><span class="block-icon">&#128214;</span> {{ $t('chapterTheory.blocks.importantTerms') }}</h3>
      <div class="terms-list">
        <div v-for="(term, i) in content.terms" :key="i" class="term-item">
          <span class="term-name">{{ term.term }}</span>
          <span class="term-def">{{ term.definition || term.simple }}</span>
        </div>
      </div>
    </div>

    <!-- Exam Tips -->
    <div v-if="content.examTips?.length" class="theory-block exam-tips">
      <h3><span class="block-icon">&#128293;</span> {{ $t('chapterTheory.blocks.examTips') }}</h3>
      <ul class="tips-list">
        <li v-for="(tip, i) in content.examTips" :key="i">
          {{ tip }}
        </li>
      </ul>
    </div>

    <!-- Summary -->
    <div v-if="content.summary" class="theory-block summary">
      <h3><span class="block-icon">&#128221;</span> {{ $t('chapterTheory.blocks.summary') }}</h3>
      <p>{{ content.summary }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Concept {
  emoji?: string
  title: string
  description?: string
  oneLiner?: string
  example?: string
  tip?: string
}

interface Term {
  term: string
  definition?: string
  simple?: string
}

interface TheoryContent {
  overview?: string
  learningGoals?: string[]
  concepts?: Concept[]
  terms?: Term[]
  examTips?: string[]
  summary?: string
}

interface Props {
  content: TheoryContent
}

defineProps<Props>()
</script>

<style scoped>
.text-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.text-section::-webkit-scrollbar {
  width: 6px;
}

.text-section::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.text-section::-webkit-scrollbar-thumb {
  background: rgba(99, 102, 241, 0.3);
  border-radius: 3px;
}

/* Theory Blocks */
.theory-block {
  padding: 1rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.theory-block h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.75rem;
  color: var(--color-text-primary, #f1f5f9);
}

.block-icon {
  font-size: 1.1rem;
}

.theory-block p {
  margin: 0;
  color: var(--color-text-secondary, #94a3b8);
  line-height: 1.6;
}

.theory-block ul {
  margin: 0;
  padding-left: 1.5rem;
  color: var(--color-text-secondary, #94a3b8);
}

.theory-block li {
  margin-bottom: 0.25rem;
}

/* Concepts Grid */
.concepts-grid {
  display: grid;
  gap: 1rem;
}

.concept-card {
  padding: 1rem;
  background: rgba(99, 102, 241, 0.05);
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: 0.5rem;
}

.concept-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.concept-emoji {
  font-size: 1.25rem;
}

.concept-title {
  font-weight: 600;
  color: var(--color-text-primary, #f1f5f9);
}

.concept-desc {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
  margin: 0 0 0.5rem;
}

.concept-example {
  font-size: 0.8rem;
  color: var(--color-text-tertiary, #64748b);
  margin: 0 0 0.25rem;
}

.concept-tip {
  display: flex;
  align-items: flex-start;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #f59e0b;
  margin: 0;
  padding-top: 0.5rem;
  border-top: 1px dashed rgba(245, 158, 11, 0.3);
}

/* Terms List */
.terms-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.term-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.term-item:last-child {
  border-bottom: none;
}

.term-name {
  font-weight: 600;
  color: #818cf8;
  min-width: 120px;
}

.term-def {
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.875rem;
}

/* Tips List */
.tips-list li {
  position: relative;
  padding-left: 0.25rem;
}

.tips-list li::marker {
  color: #f59e0b;
}

/* Summary Block */
.summary {
  background: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.1);
}

.summary h3 {
  color: #10b981;
}
</style>
