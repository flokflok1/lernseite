/**
 * ChatSession.model.ts
 *
 * Chat Session Domain Model - Entity
 *
 * Represents a conversation session with AI during course editing.
 */

export interface ChatMessageEntity {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export class ChatSession {
  constructor(
    public id: string,
    public projectId: string,
    public messages: ChatMessageEntity[],
    public createdAt: Date,
    public updatedAt: Date
  ) {}

  /**
   * Create new chat session
   */
  static create(id: string, projectId: string): ChatSession {
    return new ChatSession(
      id,
      projectId,
      [],
      new Date(),
      new Date()
    )
  }

  /**
   * Add message to session
   */
  addMessage(message: ChatMessageEntity): void {
    this.messages.push(message)
    this.updatedAt = new Date()
  }

  /**
   * Get last message
   */
  getLastMessage(): ChatMessageEntity | undefined {
    return this.messages[this.messages.length - 1]
  }

  /**
   * Get user message count
   */
  getUserMessageCount(): number {
    return this.messages.filter(m => m.role === 'user').length
  }
}
