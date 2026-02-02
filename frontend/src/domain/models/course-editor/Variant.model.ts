/**
 * Variant.model.ts
 *
 * Variant Domain Model - Entity
 *
 * Represents alternate versions of AI-generated content.
 */

export class Variant {
  constructor(
    public id: string,
    public generatedContentId: string,
    public content: string,
    public style: 'formal' | 'casual' | 'academic' | 'simplified',
    public score: number = 0,
    public isSelected: boolean = false,
    public createdAt: Date = new Date()
  ) {}

  /**
   * Create new variant
   */
  static create(
    id: string,
    generatedContentId: string,
    content: string,
    style: Variant['style']
  ): Variant {
    return new Variant(
      id,
      generatedContentId,
      content,
      style
    )
  }

  /**
   * Select this variant
   */
  select(): void {
    this.isSelected = true
  }

  /**
   * Update score
   */
  updateScore(score: number): void {
    this.score = Math.max(0, Math.min(100, score))
  }
}
