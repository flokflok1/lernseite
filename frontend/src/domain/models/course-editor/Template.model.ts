/**
 * Template.model.ts
 *
 * Template Domain Model - Entity
 *
 * Represents reusable AI content generation templates.
 */

export class Template {
  constructor(
    public id: string,
    public name: string,
    public description: string,
    public category: string,
    public prompt: string,
    public contentType: 'explanation' | 'example' | 'exercise' | 'quiz',
    public isPublic: boolean = false,
    public createdAt: Date = new Date()
  ) {}

  /**
   * Create new template
   */
  static create(
    id: string,
    name: string,
    description: string,
    category: string,
    prompt: string,
    contentType: Template['contentType']
  ): Template {
    return new Template(
      id,
      name,
      description,
      category,
      prompt,
      contentType
    )
  }

  /**
   * Get template preview
   */
  getPreview(): string {
    return {
      name: this.name,
      category: this.category,
      contentType: this.contentType,
      promptLength: this.prompt.length
    } as any
  }
}
