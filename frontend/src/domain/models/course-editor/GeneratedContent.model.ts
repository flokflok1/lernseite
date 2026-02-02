/**
 * GeneratedContent.model.ts
 *
 * Generated Content Domain Model - Value Object
 *
 * Represents AI-generated content within a course.
 */

export interface GenerationMetadata {
  model: string
  temperature: number
  promptId: string
  generatedAt: Date
}

export class GeneratedContent {
  constructor(
    public id: string,
    public projectId: string,
    public chapterId: string | null,
    public lessonId: string | null,
    public content: string,
    public type: 'explanation' | 'example' | 'exercise' | 'quiz',
    public metadata: GenerationMetadata,
    public isApproved: boolean = false
  ) {}

  /**
   * Create generated content
   */
  static create(
    id: string,
    projectId: string,
    content: string,
    type: GeneratedContent['type'],
    metadata: GenerationMetadata
  ): GeneratedContent {
    return new GeneratedContent(
      id,
      projectId,
      null,
      null,
      content,
      type,
      metadata
    )
  }

  /**
   * Approve generated content
   */
  approve(): void {
    this.isApproved = true
  }

  /**
   * Get content preview
   */
  getPreview(maxLength: number = 100): string {
    return this.content.substring(0, maxLength) + (this.content.length > maxLength ? '...' : '')
  }
}
