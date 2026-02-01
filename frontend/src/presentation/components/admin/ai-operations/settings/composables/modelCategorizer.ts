/**
 * Model Categorizer
 *
 * Automatically categorizes AI models based on their names and properties.
 * Uses pattern matching and heuristics to assign categories like:
 * - Audio (TTS, Speech, Voice)
 * - Realtime (Streaming, Live, WebRTC)
 * - Vision (Image, Multimodal)
 * - Large Context (200k+ tokens)
 * - Fast (Mini, Lightweight, Small)
 * - General (Default)
 */

export interface AIModelInfo {
  id: string
  name: string
  provider: string
  description?: string
  inputTokens?: number
  outputTokens?: number
}

export interface CategorizedModel extends AIModelInfo {
  category: string
}

/**
 * Categorize a single model
 */
export function categorizeModel(model: AIModelInfo): string {
  const name = model.name.toLowerCase()
  const description = (model.description || '').toLowerCase()
  const inputTokens = model.inputTokens || 0

  // ============================================
  // AUDIO MODELS
  // ============================================
  if (
    name.includes('whisper') ||
    name.includes('audio') ||
    name.includes('tts') ||
    name.includes('speech') ||
    name.includes('voice') ||
    description.includes('speech') ||
    description.includes('audio') ||
    description.includes('voice')
  ) {
    return 'Audio'
  }

  // ============================================
  // REALTIME / STREAMING MODELS
  // ============================================
  if (
    name.includes('realtime') ||
    name.includes('streaming') ||
    name.includes('live') ||
    name.includes('turbo') ||
    name.includes('-o') || // GPT-4o pattern
    name.includes('flash') ||
    description.includes('realtime') ||
    description.includes('streaming') ||
    description.includes('live')
  ) {
    return 'Realtime'
  }

  // ============================================
  // VISION / MULTIMODAL MODELS
  // ============================================
  if (
    name.includes('vision') ||
    name.includes('multimodal') ||
    name.includes('image') ||
    name.includes('visual') ||
    description.includes('vision') ||
    description.includes('multimodal') ||
    description.includes('image')
  ) {
    return 'Vision'
  }

  // ============================================
  // LARGE CONTEXT MODELS
  // ============================================
  if (
    inputTokens >= 200000 ||
    name.includes('200k') ||
    name.includes('large-context') ||
    description.includes('200k') ||
    description.includes('context window')
  ) {
    return 'Large Context'
  }

  // ============================================
  // FAST / LIGHTWEIGHT MODELS
  // ============================================
  if (
    name.includes('mini') ||
    name.includes('small') ||
    name.includes('lite') ||
    name.includes('lightweight') ||
    name.includes('fast') ||
    name.includes('-3.5') ||
    name.includes('haiku') ||
    description.includes('fast') ||
    description.includes('lightweight') ||
    description.includes('mini')
  ) {
    return 'Fast'
  }

  // ============================================
  // ADVANCED / REASONING MODELS
  // ============================================
  if (
    name.includes('advanced') ||
    name.includes('reasoning') ||
    name.includes('opus') ||
    name.includes('sonnet') ||
    name.includes('pro') ||
    name.includes('gpt-4') ||
    description.includes('reasoning') ||
    description.includes('advanced')
  ) {
    return 'Advanced'
  }

  // ============================================
  // DEFAULT
  // ============================================
  return 'General'
}

/**
 * Categorize multiple models
 */
export function categorizeModels(models: AIModelInfo[]): CategorizedModel[] {
  return models.map(model => ({
    ...model,
    category: categorizeModel(model)
  }))
}

/**
 * Get all unique categories from models
 */
export function getCategories(models: CategorizedModel[]): string[] {
  const categories = new Set<string>()
  models.forEach(model => {
    if (model.category) categories.add(model.category)
  })
  return Array.from(categories).sort()
}

/**
 * Get models by category
 */
export function getModelsByCategory(models: CategorizedModel[], category: string): CategorizedModel[] {
  return models.filter(m => m.category === category)
}

/**
 * Debug: Show categorization for all models
 */
export function debugCategorization(models: AIModelInfo[]): void {
  console.group('🏷️ Model Categorization Debug')
  categorizeModels(models).forEach(model => {
    console.log(`${model.name} → ${model.category}`)
  })
  console.groupEnd()
}
