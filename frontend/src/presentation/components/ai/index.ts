// AI Domain Components
// AI Studio, authoring, management, and user AI features
//
// Migrated from:
// - admin/ai-operations/* → ai/admin/*
// - user/ai/* → ai/user/*
//
// IMPORTANT: Exam settings moved to assessment/admin/settings/exams/

// Admin Sub-Domain
export * from './admin/authoring'
export * from './admin/management'
export * from './admin/settings'
export * from './admin/studio'

// User Sub-Domain
export * from './user/chat'
export * from './user/quiz-generation'
export * from './user/tutor'
