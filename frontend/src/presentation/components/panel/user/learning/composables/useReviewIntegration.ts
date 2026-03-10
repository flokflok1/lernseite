/**
 * Composable for integrating SRS review tracking into LM execution.
 *
 * Call `recordReview()` after any LM completion with a score.
 * Silently fails if SRS is not initialized (non-exam courses).
 */
import { useReviewStore } from '@/application/stores/modules/learning/review.store'

export function useReviewIntegration() {
  const reviewStore = useReviewStore()

  /**
   * Record a review result for SRS scheduling.
   * Safe to call even if SRS is not initialized — will silently skip.
   */
  async function recordReview(
    methodId: string,
    score: number,
    timeSeconds: number = 0,
  ): Promise<void> {
    try {
      await reviewStore.processReview(methodId, score, timeSeconds)
    } catch {
      // SRS not initialized for this course — expected for non-exam courses
    }
  }

  /**
   * Initialize SRS for a course (call on course enrollment/start).
   */
  async function initializeSrs(courseId: string): Promise<void> {
    try {
      const { initializeReviews } = await import(
        '@/infrastructure/api/clients/panel/user/learning/reviews.api'
      )
      await initializeReviews(courseId)
    } catch {
      // SRS init failed — non-blocking
    }
  }

  return {
    recordReview,
    initializeSrs,
    hasDueReviews: reviewStore.hasDueReviews,
    dueCount: reviewStore.dueCount,
  }
}
