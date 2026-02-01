// AI Domain Components
// AI Studio, authoring, management, and user AI features
//
// Migrated from:
// - admin/ai-operations/* → ai/admin/*
// - user/ai/* → ai/user/*
//
// IMPORTANT: Exam settings moved to assessment/admin/settings/exams/

// Admin Sub-Domain
export * from './panel/authoring'
export * from './panel/management'
export * from './panel/settings'
export * from './panel/studio'

// User Sub-Domain
export * from './user/chat'
export * from './user/quiz-generation'
export * from './user/tutor'
