/**
 * Project.model.ts
 *
 * Project Domain Model - Aggregate Root
 *
 * Represents a course editing project.
 * This is the main aggregate root for course-editor domain.
 */

export interface ProjectMetadata {
  createdAt: Date
  updatedAt: Date
  createdBy: string
  version: number
}

export class Project {
  constructor(
    public id: string,
    public title: string,
    public description: string,
    public status: 'draft' | 'published' | 'archived',
    public chapters: string[], // Array of chapter IDs
    public metadata: ProjectMetadata
  ) {}

  /**
   * Create a new project
   */
  static create(
    id: string,
    title: string,
    description: string,
    createdBy: string
  ): Project {
    return new Project(
      id,
      title,
      description,
      'draft',
      [],
      {
        createdAt: new Date(),
        updatedAt: new Date(),
        createdBy,
        version: 1
      }
    )
  }

  /**
   * Mark project as published
   */
  publish(): void {
    if (this.status !== 'draft') {
      throw new Error('Only draft projects can be published')
    }
    this.status = 'published'
    this.metadata.updatedAt = new Date()
  }

  /**
   * Archive project
   */
  archive(): void {
    if (this.status === 'archived') {
      throw new Error('Project is already archived')
    }
    this.status = 'archived'
    this.metadata.updatedAt = new Date()
  }

  /**
   * Check if project can be edited
   */
  canEdit(): boolean {
    return this.status !== 'archived'
  }
}
