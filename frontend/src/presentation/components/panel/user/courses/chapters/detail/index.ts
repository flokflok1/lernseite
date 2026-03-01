// Chapter Detail Components (Barrel Export)

// Core layout
export { default as ChapterHero } from './ChapterHero.vue'
export { default as ChapterNavigation } from './ChapterNavigation.vue'
export { default as ChapterCompleteBanner } from './ChapterCompleteBanner.vue'

// Theory
export { default as TheoryAccordion } from './theory/TheoryAccordion.vue'
export { default as TheoryAccordionItem } from './theory/TheoryAccordionItem.vue'

// Lessons
export { default as LessonTimeline } from './timeline/LessonTimeline.vue'
export { default as LessonTimelineNode } from './timeline/LessonTimelineNode.vue'

// Shared
export { default as ProgressRing } from './timeline/ProgressRing.vue'

// Composables
export { useChapterDetail } from './composables/useChapterDetail'
