/**
 * API Response Transformers
 *
 * Utilities to transform backend DDD API responses to frontend domain models.
 * These transformers handle the field naming convention changes from the backend refactoring.
 *
 * Usage:
 *   const userDto = { user_id: '1', email: '...', first_name: 'John' }
 *   const user = transformUserFromAPI(userDto)
 */

/**
 * Transform backend user object (snake_case) to frontend format (camelCase)
 *
 * Handles multiple possible backend response formats:
 * - Standard snake_case: { user_id, email, first_name, last_name, role_type }
 * - Alternative formats with nested objects or different naming
 *
 * @param backendUser - Raw backend user object
 * @returns Transformed user object ready for User.fromAPI()
 *
 * @example
 * const backendUser = { user_id: '123', email: 'test@example.com', first_name: 'John', ... }
 * const transformed = transformUserFromAPI(backendUser)
 * const user = User.fromAPI(transformed)
 */
export function transformUserFromAPI(backendUser: any) {
  if (!backendUser || typeof backendUser !== 'object') {
    throw new Error('Invalid backend user object')
  }

  // Handle both possible field name patterns
  return {
    id: backendUser.user_id || backendUser.id,
    email: extractEmailValue(backendUser.email),
    username: backendUser.user_name || backendUser.username || backendUser.email,
    firstName: backendUser.first_name || backendUser.firstName,
    lastName: backendUser.last_name || backendUser.lastName,
    role: backendUser.role_type || backendUser.role,
    isActive: backendUser.is_active ?? backendUser.isActive ?? true,
    createdAt: backendUser.created_at || backendUser.createdAt,
    updatedAt: backendUser.updated_at || backendUser.updatedAt,
    lastLogin: backendUser.last_login || backendUser.lastLogin
  }
}

/**
 * Extract email value from various possible backend formats
 *
 * Handles:
 * - Simple string: "test@example.com"
 * - Nested object: { value: "test@example.com" }
 * - Alternative nested: { email: "test@example.com" }
 *
 * @param emailField - Email field from backend response
 * @returns Email string or undefined
 */
function extractEmailValue(emailField: any): string | undefined {
  if (typeof emailField === 'string') {
    return emailField
  }

  if (typeof emailField === 'object' && emailField !== null) {
    // Handle nested object patterns
    if (typeof emailField.value === 'string') {
      return emailField.value
    }
    if (typeof emailField.email === 'string') {
      return emailField.email
    }
  }

  return undefined
}

/**
 * Transform backend course object to frontend format
 *
 * Handles the modules → chapters refactoring (2025-11-27)
 *
 * @param backendCourse - Raw backend course object
 * @returns Transformed course object
 *
 * @example
 * const backendCourse = {
 *   course_id: 1,
 *   total_chapters: 5,  // Changed from total_modules
 *   chapter_ids: [...],  // Changed from module_ids
 *   ...
 * }
 * const course = transformCourseFromAPI(backendCourse)
 */
export function transformCourseFromAPI(backendCourse: any) {
  if (!backendCourse || typeof backendCourse !== 'object') {
    throw new Error('Invalid backend course object')
  }

  return {
    courseId: backendCourse.course_id || backendCourse.courseId,
    title: backendCourse.title,
    description: backendCourse.description,
    categoryId: backendCourse.category_id || backendCourse.categoryId,
    category: backendCourse.category,
    level: backendCourse.level,
    language: backendCourse.language,
    price: backendCourse.price,
    isPublic: backendCourse.is_public ?? backendCourse.isPublic,
    isPublished: backendCourse.is_published ?? backendCourse.isPublished,
    thumbnailUrl: backendCourse.thumbnail_url || backendCourse.thumbnailUrl,
    creatorId: backendCourse.creator_id || backendCourse.creatorId,
    creatorName: backendCourse.creator_name || backendCourse.creatorName,
    organisationId: backendCourse.organisation_id || backendCourse.organisationId,
    organisationName: backendCourse.organisation_name || backendCourse.organisationName,
    createdAt: backendCourse.created_at || backendCourse.createdAt,
    updatedAt: backendCourse.updated_at || backendCourse.updatedAt,
    tags: backendCourse.tags,

    // Modules → Chapters refactoring (2025-11-27)
    totalChapters: backendCourse.total_chapters || backendCourse.totalChapters || backendCourse.total_modules,
    totalLessons: backendCourse.total_lessons || backendCourse.totalLessons,
    totalDurationMinutes: backendCourse.total_duration_minutes || backendCourse.totalDurationMinutes,
    enrollmentCount: backendCourse.enrollment_count || backendCourse.enrollmentCount,
    averageRating: backendCourse.average_rating || backendCourse.averageRating
  }
}

/**
 * Transform backend chapter object to frontend format
 *
 * @param backendChapter - Raw backend chapter object
 * @returns Transformed chapter object
 */
export function transformChapterFromAPI(backendChapter: any) {
  if (!backendChapter || typeof backendChapter !== 'object') {
    throw new Error('Invalid backend chapter object')
  }

  return {
    chapterId: backendChapter.chapter_id || backendChapter.chapterId,
    chapterTitle: backendChapter.chapter_title || backendChapter.chapterTitle,
    courseId: backendChapter.course_id || backendChapter.courseId,
    courseTitle: backendChapter.course_title || backendChapter.courseTitle,
    description: backendChapter.description,
    orderIndex: backendChapter.order_index || backendChapter.orderIndex,
    totalLessons: backendChapter.total_lessons || backendChapter.totalLessons,
    totalDurationMinutes: backendChapter.total_duration_minutes || backendChapter.totalDurationMinutes,
    isPublished: backendChapter.is_published ?? backendChapter.isPublished,
    createdAt: backendChapter.created_at || backendChapter.createdAt,
    updatedAt: backendChapter.updated_at || backendChapter.updatedAt
  }
}

/**
 * Transform backend lesson object to frontend format
 *
 * @param backendLesson - Raw backend lesson object
 * @returns Transformed lesson object
 */
export function transformLessonFromAPI(backendLesson: any) {
  if (!backendLesson || typeof backendLesson !== 'object') {
    throw new Error('Invalid backend lesson object')
  }

  return {
    lessonId: backendLesson.lesson_id || backendLesson.lessonId,
    lessonTitle: backendLesson.lesson_title || backendLesson.lessonTitle,
    chapterId: backendLesson.chapter_id || backendLesson.chapterId,
    chapterTitle: backendLesson.chapter_title || backendLesson.chapterTitle,
    courseId: backendLesson.course_id || backendLesson.courseId,
    description: backendLesson.description,
    orderIndex: backendLesson.order_index || backendLesson.orderIndex,
    durationMinutes: backendLesson.duration_minutes || backendLesson.durationMinutes,
    learningMethodType: backendLesson.learning_method_type || backendLesson.learningMethodType,
    content: backendLesson.content,
    isPublished: backendLesson.is_published ?? backendLesson.isPublished,
    createdAt: backendLesson.created_at || backendLesson.createdAt,
    updatedAt: backendLesson.updated_at || backendLesson.updatedAt
  }
}

/**
 * Transform backend organization object to frontend format
 *
 * @param backendOrg - Raw backend organization object
 * @returns Transformed organization object
 */
export function transformOrganisationFromAPI(backendOrg: any) {
  if (!backendOrg || typeof backendOrg !== 'object') {
    throw new Error('Invalid backend organisation object')
  }

  return {
    organisationId: backendOrg.organisation_id || backendOrg.organisationId,
    name: backendOrg.name,
    type: backendOrg.type,
    planId: backendOrg.plan_id || backendOrg.planId,
    planName: backendOrg.plan_name || backendOrg.planName,
    tokenPool: backendOrg.token_pool || backendOrg.tokenPool,
    tokenUsed: backendOrg.token_used || backendOrg.tokenUsed,
    tokenAvailable: backendOrg.token_available || backendOrg.tokenAvailable,
    totalUsers: backendOrg.total_users || backendOrg.totalUsers,
    activeUsers: backendOrg.active_users || backendOrg.activeUsers,
    isActive: backendOrg.is_active ?? backendOrg.isActive ?? true,
    createdAt: backendOrg.created_at || backendOrg.createdAt,
    domain: backendOrg.domain,
    branding: backendOrg.branding
  }
}

/**
 * Transform backend category DTO to domain model
 *
 * Converts snake_case fields to camelCase format
 * Handles recursive transformation for nested Category children
 *
 * @param backendCategory - Backend category DTO (snake_case)
 * @returns Transformed category object (camelCase)
 */
export function transformCategoryFromAPI(backendCategory: any) {
  if (!backendCategory || typeof backendCategory !== 'object') {
    throw new Error('Invalid backend category object')
  }

  return {
    categoryId: backendCategory.category_id || backendCategory.categoryId,
    name: backendCategory.name,
    slug: backendCategory.slug,
    description: backendCategory.description,
    parentId: backendCategory.parent_id || backendCategory.parentId,
    level: backendCategory.level,
    path: backendCategory.path,
    icon: backendCategory.icon,
    color: backendCategory.color,
    orderIndex: backendCategory.order_index || backendCategory.orderIndex,
    isActive: backendCategory.is_active ?? backendCategory.isActive,
    courseCount: backendCategory.course_count || backendCategory.courseCount,
    totalCourseCount: backendCategory.total_course_count || backendCategory.totalCourseCount,
    children: backendCategory.children
      ? backendCategory.children.map(transformCategoryFromAPI)
      : undefined,
    createdAt: backendCategory.created_at || backendCategory.createdAt,
    updatedAt: backendCategory.updated_at || backendCategory.updatedAt
  }
}

/**
 * Generic transformer for handling pagination responses
 *
 * @param response - Backend pagination response
 * @param itemTransformer - Function to transform individual items
 * @returns Transformed pagination response
 *
 * @example
 * const response = await http.get('/courses')
 * const transformed = transformPaginationFromAPI(response.data, transformCourseFromAPI)
 */
export function transformPaginationFromAPI<T>(
  response: any,
  itemTransformer: (item: any) => T
) {
  if (!response || typeof response !== 'object') {
    throw new Error('Invalid pagination response')
  }

  const items = (response.items || response.data || response.courses || []).map(itemTransformer)
  const pagination = response.pagination || {}

  return {
    items,
    pagination: {
      page: pagination.page || response.page || 1,
      perPage: pagination.per_page || pagination.perPage || pagination.limit || 20,
      total: pagination.total || response.total || 0,
      totalPages: pagination.total_pages || pagination.totalPages || 0
    }
  }
}

/**
 * Transform backend course progress object to frontend format
 *
 * @param backendProgress - Raw backend course progress object
 * @returns Transformed course progress object
 */
export function transformCourseProgressFromAPI(backendProgress: any) {
  if (!backendProgress || typeof backendProgress !== 'object') {
    throw new Error('Invalid backend course progress object')
  }

  return {
    courseId: backendProgress.course_id || backendProgress.courseId,
    userId: backendProgress.user_id || backendProgress.userId,
    enrollmentId: backendProgress.enrollment_id || backendProgress.enrollmentId,
    status: backendProgress.status,
    progressPercentage: backendProgress.progress_percentage ?? backendProgress.progressPercentage,
    chaptersCompleted: backendProgress.chapters_completed || backendProgress.chaptersCompleted,
    totalChapters: backendProgress.total_chapters || backendProgress.totalChapters,
    lessonsCompleted: backendProgress.lessons_completed || backendProgress.lessonsCompleted,
    totalLessons: backendProgress.total_lessons || backendProgress.totalLessons,
    lastAccessedAt: backendProgress.last_accessed_at || backendProgress.lastAccessedAt,
    enrolledAt: backendProgress.enrolled_at || backendProgress.enrolledAt,
    completedAt: backendProgress.completed_at || backendProgress.completedAt
  }
}

/**
 * Transform backend chapter progress object to frontend format
 *
 * @param backendProgress - Raw backend chapter progress object
 * @returns Transformed chapter progress object
 */
export function transformChapterProgressFromAPI(backendProgress: any) {
  if (!backendProgress || typeof backendProgress !== 'object') {
    throw new Error('Invalid backend chapter progress object')
  }

  return {
    chapterId: backendProgress.chapter_id || backendProgress.chapterId,
    userId: backendProgress.user_id || backendProgress.userId,
    status: backendProgress.status,
    progressPercentage: backendProgress.progress_percentage ?? backendProgress.progressPercentage,
    lessonsCompleted: backendProgress.lessons_completed || backendProgress.lessonsCompleted,
    totalLessons: backendProgress.total_lessons || backendProgress.totalLessons,
    startedAt: backendProgress.started_at || backendProgress.startedAt,
    completedAt: backendProgress.completed_at || backendProgress.completedAt
  }
}

/**
 * Transform backend lesson progress object to frontend format
 *
 * @param backendProgress - Raw backend lesson progress object
 * @returns Transformed lesson progress object
 */
export function transformLessonProgressFromAPI(backendProgress: any) {
  if (!backendProgress || typeof backendProgress !== 'object') {
    throw new Error('Invalid backend lesson progress object')
  }

  return {
    lessonId: backendProgress.lesson_id || backendProgress.lessonId,
    userId: backendProgress.user_id || backendProgress.userId,
    status: backendProgress.status,
    progressPercentage: backendProgress.progress_percentage ?? backendProgress.progressPercentage,
    timeSpentMinutes: backendProgress.time_spent_minutes || backendProgress.timeSpentMinutes,
    startedAt: backendProgress.started_at || backendProgress.startedAt,
    completedAt: backendProgress.completed_at || backendProgress.completedAt,
    lastAccessedAt: backendProgress.last_accessed_at || backendProgress.lastAccessedAt
  }
}

/**
 * Transform backend saved task execution object to frontend format
 *
 * @param backendExecution - Raw backend execution object
 * @returns Transformed execution object
 */
export function transformSavedTaskExecutionFromAPI(backendExecution: any) {
  if (!backendExecution || typeof backendExecution !== 'object') {
    throw new Error('Invalid backend execution object')
  }

  return {
    executionId: backendExecution.execution_id || backendExecution.executionId,
    methodId: backendExecution.method_id || backendExecution.methodId,
    methodName: backendExecution.method_name || backendExecution.methodName,
    methodDescription: backendExecution.method_description || backendExecution.methodDescription,
    userInput: backendExecution.user_input || backendExecution.userInput,
    aiResponse: backendExecution.ai_response || backendExecution.aiResponse,
    inputTokens: backendExecution.input_tokens || backendExecution.inputTokens,
    outputTokens: backendExecution.output_tokens || backendExecution.outputTokens,
    totalTokens: backendExecution.total_tokens || backendExecution.totalTokens,
    model: backendExecution.model,
    provider: backendExecution.provider,
    executedAt: backendExecution.executed_at || backendExecution.executedAt
  }
}

/**
 * Transform backend quiz question object to frontend format
 *
 * @param backendQuestion - Raw backend question object
 * @returns Transformed question object
 */
export function transformQuizQuestionFromAPI(backendQuestion: any) {
  if (!backendQuestion || typeof backendQuestion !== 'object') {
    throw new Error('Invalid backend quiz question object')
  }

  return {
    questionId: backendQuestion.question_id || backendQuestion.questionId,
    type: backendQuestion.type,
    questionText: backendQuestion.question_text || backendQuestion.questionText,
    points: backendQuestion.points,
    options: backendQuestion.options,
    correctAnswer: backendQuestion.correct_answer || backendQuestion.correctAnswer,
    explanation: backendQuestion.explanation,
    order: backendQuestion.order
  }
}

/**
 * Transform backend quiz question result object to frontend format
 *
 * @param backendResult - Raw backend question result object
 * @returns Transformed question result object
 */
export function transformQuizQuestionResultFromAPI(backendResult: any) {
  if (!backendResult || typeof backendResult !== 'object') {
    throw new Error('Invalid backend quiz question result object')
  }

  return {
    questionId: backendResult.question_id || backendResult.questionId,
    isCorrect: backendResult.is_correct ?? backendResult.isCorrect,
    earnedPoints: backendResult.earned_points || backendResult.earnedPoints,
    maxPoints: backendResult.max_points || backendResult.maxPoints,
    userAnswer: backendResult.user_answer || backendResult.userAnswer,
    correctAnswer: backendResult.correct_answer || backendResult.correctAnswer,
    explanation: backendResult.explanation
  }
}

/**
 * Transform backend quiz data object to frontend format
 *
 * @param backendQuiz - Raw backend quiz data object
 * @returns Transformed quiz data object
 */
export function transformQuizDataFromAPI(backendQuiz: any) {
  if (!backendQuiz || typeof backendQuiz !== 'object') {
    throw new Error('Invalid backend quiz data object')
  }

  return {
    quizId: backendQuiz.quiz_id || backendQuiz.quizId,
    lessonId: backendQuiz.lesson_id || backendQuiz.lessonId,
    title: backendQuiz.title,
    description: backendQuiz.description,
    questions: backendQuiz.questions
      ? backendQuiz.questions.map(transformQuizQuestionFromAPI)
      : [],
    timeLimitSeconds: backendQuiz.time_limit_seconds ?? backendQuiz.timeLimitSeconds,
    passingScorePercentage: backendQuiz.passing_score_percentage || backendQuiz.passingScorePercentage,
    isExam: backendQuiz.is_exam ?? backendQuiz.isExam,
    allowRetry: backendQuiz.allow_retry ?? backendQuiz.allowRetry,
    showCorrectAnswers: backendQuiz.show_correct_answers ?? backendQuiz.showCorrectAnswers,
    shuffleQuestions: backendQuiz.shuffle_questions ?? backendQuiz.shuffleQuestions,
    shuffleOptions: backendQuiz.shuffle_options ?? backendQuiz.shuffleOptions
  }
}

/**
 * Transform backend quiz result object to frontend format
 *
 * @param backendResult - Raw backend quiz result object
 * @returns Transformed quiz result object
 */
export function transformQuizResultFromAPI(backendResult: any) {
  if (!backendResult || typeof backendResult !== 'object') {
    throw new Error('Invalid backend quiz result object')
  }

  return {
    quizAttemptId: backendResult.quiz_attempt_id || backendResult.quizAttemptId,
    quizId: backendResult.quiz_id || backendResult.quizId,
    lessonId: backendResult.lesson_id || backendResult.lessonId,
    userId: backendResult.user_id || backendResult.userId,
    totalPoints: backendResult.total_points || backendResult.totalPoints,
    maxPoints: backendResult.max_points || backendResult.maxPoints,
    scorePercentage: backendResult.score_percentage || backendResult.scorePercentage,
    passed: backendResult.passed,
    timeSpentSeconds: backendResult.time_spent_seconds || backendResult.timeSpentSeconds,
    questionResults: backendResult.question_results
      ? backendResult.question_results.map(transformQuizQuestionResultFromAPI)
      : [],
    submittedAt: backendResult.submitted_at || backendResult.submittedAt,
    isExam: backendResult.is_exam ?? backendResult.isExam
  }
}

/**
 * Log backend response structure for debugging
 *
 * Useful for identifying new field naming patterns in backend responses
 *
 * @param label - Label for the log
 * @param response - Response to log
 */
export function logBackendResponse(label: string, response: any) {
  console.log(`[API Transformer] ${label}:`, {
    keys: Object.keys(response || {}),
    data: response
  })
}
