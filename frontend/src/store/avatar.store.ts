/**
 * Avatar Store - Advanced 3D Avatar System with VRM Support
 *
 * Features:
 * - VRM Avatar loading (Ready Player Me compatible)
 * - Lip-sync with audio analysis
 * - Multiple avatar modes (floating, classroom, whiteboard)
 * - Animation states (idle, talking, explaining, thinking)
 * - Customizable appearance
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// =====================================
// TYPES
// =====================================

export type AvatarMode = 'floating' | 'classroom' | 'whiteboard' | 'fullscreen'
export type AvatarState = 'idle' | 'talking' | 'thinking' | 'explaining' | 'waving' | 'nodding'
export type AvatarStyle = 'robot' | 'human' | 'anime' | 'custom'

export interface AvatarAppearance {
  style: AvatarStyle
  skinTone?: string
  hairColor?: string
  hairStyle?: string
  eyeColor?: string
  outfit?: string
  accessories?: string[]
  // For custom VRM
  vrmUrl?: string
}

export interface AvatarSettings {
  enabled: boolean
  mode: AvatarMode
  position: 'bottom-right' | 'bottom-left'
  scale: number
  appearance: AvatarAppearance
  lipSyncEnabled: boolean
  lipSyncSensitivity: number
  animationsEnabled: boolean
  showWhiteboardInCourse: boolean
  autoExpandOnSpeaking: boolean
}

export interface LipSyncData {
  mouthOpen: number      // 0-1 how open the mouth is
  mouthWide: number      // 0-1 how wide the mouth is
  viseme: string         // Current viseme (phoneme shape)
  volume: number         // Current audio volume
}

export interface AvatarAnimation {
  name: string
  duration: number
  loop: boolean
}

// =====================================
// PRESET AVATARS
// =====================================

export const PRESET_AVATARS = [
  {
    id: 'robot-lumi',
    name: 'Lumi (Robot)',
    style: 'robot' as AvatarStyle,
    description: 'Der klassische lilane Lernroboter',
    thumbnail: '/avatars/robot-lumi.png'
  },
  {
    id: 'human-teacher-m',
    name: 'Max (Lehrer)',
    style: 'human' as AvatarStyle,
    vrmUrl: '/avatars/teacher-male.vrm',
    description: 'Ein freundlicher Lehrer',
    thumbnail: '/avatars/teacher-male.png'
  },
  {
    id: 'human-teacher-f',
    name: 'Marie (Lehrerin)',
    style: 'human' as AvatarStyle,
    vrmUrl: '/avatars/teacher-female.vrm',
    description: 'Eine geduldige Lehrerin',
    thumbnail: '/avatars/teacher-female.png'
  },
  {
    id: 'anime-sensei',
    name: 'Sensei (Anime)',
    style: 'anime' as AvatarStyle,
    vrmUrl: '/avatars/anime-sensei.vrm',
    description: 'Ein cooler Anime-Tutor',
    thumbnail: '/avatars/anime-sensei.png'
  }
]

// =====================================
// VISEME MAPPING (for lip-sync)
// =====================================

// Maps phonemes to VRM blend shapes
export const VISEME_MAP: Record<string, { mouth: number; wide: number }> = {
  'sil': { mouth: 0, wide: 0 },      // Silence
  'aa': { mouth: 0.8, wide: 0.3 },   // "ah"
  'ae': { mouth: 0.6, wide: 0.5 },   // "cat"
  'ah': { mouth: 0.7, wide: 0.3 },   // "but"
  'ao': { mouth: 0.7, wide: 0.2 },   // "dog"
  'aw': { mouth: 0.6, wide: 0.2 },   // "cow"
  'ay': { mouth: 0.5, wide: 0.4 },   // "say"
  'b': { mouth: 0, wide: 0 },        // Closed
  'ch': { mouth: 0.3, wide: 0.5 },   // "chair"
  'd': { mouth: 0.2, wide: 0.3 },
  'dh': { mouth: 0.2, wide: 0.3 },   // "the"
  'eh': { mouth: 0.5, wide: 0.5 },   // "bed"
  'er': { mouth: 0.4, wide: 0.2 },   // "bird"
  'ey': { mouth: 0.4, wide: 0.5 },   // "say"
  'f': { mouth: 0.1, wide: 0.4 },
  'g': { mouth: 0.3, wide: 0.2 },
  'hh': { mouth: 0.3, wide: 0.3 },   // "hat"
  'ih': { mouth: 0.3, wide: 0.5 },   // "bit"
  'iy': { mouth: 0.2, wide: 0.6 },   // "beat"
  'jh': { mouth: 0.3, wide: 0.4 },   // "job"
  'k': { mouth: 0.2, wide: 0.2 },
  'l': { mouth: 0.3, wide: 0.3 },
  'm': { mouth: 0, wide: 0 },        // Closed
  'n': { mouth: 0.2, wide: 0.3 },
  'ng': { mouth: 0.2, wide: 0.2 },
  'ow': { mouth: 0.6, wide: 0.1 },   // "know"
  'oy': { mouth: 0.5, wide: 0.2 },   // "boy"
  'p': { mouth: 0, wide: 0 },        // Closed
  'r': { mouth: 0.3, wide: 0.2 },
  's': { mouth: 0.1, wide: 0.5 },
  'sh': { mouth: 0.2, wide: 0.4 },   // "she"
  't': { mouth: 0.1, wide: 0.3 },
  'th': { mouth: 0.2, wide: 0.4 },   // "think"
  'uh': { mouth: 0.4, wide: 0.2 },   // "book"
  'uw': { mouth: 0.3, wide: 0.1 },   // "boot"
  'v': { mouth: 0.1, wide: 0.4 },
  'w': { mouth: 0.2, wide: 0.1 },
  'y': { mouth: 0.2, wide: 0.5 },
  'z': { mouth: 0.1, wide: 0.5 },
  'zh': { mouth: 0.2, wide: 0.4 }    // "vision"
}

// =====================================
// STORE
// =====================================

export const useAvatarStore = defineStore('avatar', () => {
  // =====================================
  // STATE
  // =====================================

  const settings = ref<AvatarSettings>({
    enabled: true,
    mode: 'floating',
    position: 'bottom-right',
    scale: 1,
    appearance: {
      style: 'robot'  // Default to robot avatar
    },
    lipSyncEnabled: true,
    lipSyncSensitivity: 0.5,
    animationsEnabled: true,
    showWhiteboardInCourse: true,
    autoExpandOnSpeaking: true
  })

  const currentState = ref<AvatarState>('idle')
  const isLoaded = ref(false)
  const isLoading = ref(false)
  const loadError = ref<string | null>(null)

  // Lip-sync state
  const lipSyncData = ref<LipSyncData>({
    mouthOpen: 0,
    mouthWide: 0,
    viseme: 'sil',
    volume: 0
  })

  // Audio analyzer
  const audioContext = ref<AudioContext | null>(null)
  const analyser = ref<AnalyserNode | null>(null)
  const dataArray = ref<Uint8Array | null>(null)

  // Animation queue
  const animationQueue = ref<AvatarAnimation[]>([])
  const currentAnimation = ref<string>('idle')

  // Whiteboard content (for classroom mode)
  const whiteboardContent = ref<string>('')

  // =====================================
  // COMPUTED
  // =====================================

  const isRobotStyle = computed(() => settings.value.appearance.style === 'robot')
  const isVRMStyle = computed(() => ['human', 'anime', 'custom'].includes(settings.value.appearance.style))
  const hasVRM = computed(() => !!settings.value.appearance.vrmUrl)

  const effectiveMode = computed(() => {
    // Auto-switch to classroom when on course page and enabled
    if (settings.value.showWhiteboardInCourse && settings.value.mode === 'floating') {
      // This will be set by the course page
      return settings.value.mode
    }
    return settings.value.mode
  })

  // =====================================
  // ACTIONS
  // =====================================

  /**
   * Initialize audio context for lip-sync
   */
  const initAudioAnalyzer = async (): Promise<boolean> => {
    try {
      audioContext.value = new AudioContext()
      analyser.value = audioContext.value.createAnalyser()
      analyser.value.fftSize = 256
      dataArray.value = new Uint8Array(analyser.value.frequencyBinCount)
      return true
    } catch (error) {
      console.error('Failed to init audio analyzer:', error)
      return false
    }
  }

  /**
   * Connect audio element to analyzer for lip-sync
   */
  const connectAudioForLipSync = (audioElement: HTMLAudioElement): void => {
    if (!audioContext.value || !analyser.value) {
      initAudioAnalyzer()
    }

    try {
      const source = audioContext.value!.createMediaElementSource(audioElement)
      source.connect(analyser.value!)
      analyser.value!.connect(audioContext.value!.destination)
    } catch (error) {
      // Element might already be connected
      console.warn('Audio element connection warning:', error)
    }
  }

  /**
   * Update lip-sync data from audio analysis
   */
  const updateLipSync = (): void => {
    if (!analyser.value || !dataArray.value || !settings.value.lipSyncEnabled) {
      lipSyncData.value = { mouthOpen: 0, mouthWide: 0, viseme: 'sil', volume: 0 }
      return
    }

    analyser.value.getByteFrequencyData(dataArray.value)

    // Calculate average volume
    let sum = 0
    for (let i = 0; i < dataArray.value.length; i++) {
      sum += dataArray.value[i]
    }
    const avgVolume = sum / dataArray.value.length / 255

    // Apply sensitivity
    const adjustedVolume = Math.min(1, avgVolume * (1 + settings.value.lipSyncSensitivity))

    // Simple mouth movement based on volume
    // For more accurate lip-sync, we'd need phoneme detection
    lipSyncData.value = {
      mouthOpen: adjustedVolume * 0.8,
      mouthWide: adjustedVolume * 0.3,
      viseme: adjustedVolume > 0.1 ? 'aa' : 'sil',
      volume: adjustedVolume
    }
  }

  /**
   * Set avatar state (affects animations)
   */
  const setState = (state: AvatarState): void => {
    currentState.value = state
    currentAnimation.value = state
  }

  /**
   * Queue an animation
   */
  const queueAnimation = (animation: AvatarAnimation): void => {
    animationQueue.value.push(animation)
  }

  /**
   * Play next animation in queue
   */
  const playNextAnimation = (): AvatarAnimation | null => {
    if (animationQueue.value.length === 0) return null
    return animationQueue.value.shift()!
  }

  /**
   * Set avatar mode
   */
  const setMode = (mode: AvatarMode): void => {
    settings.value.mode = mode
  }

  /**
   * Set avatar appearance
   */
  const setAppearance = (appearance: Partial<AvatarAppearance>): void => {
    settings.value.appearance = { ...settings.value.appearance, ...appearance }
    saveSettings()
  }

  /**
   * Set custom VRM URL
   */
  const setCustomVRM = (url: string): void => {
    settings.value.appearance = {
      ...settings.value.appearance,
      style: 'custom',
      vrmUrl: url
    }
    saveSettings()
  }

  /**
   * Select preset avatar
   */
  const selectPreset = (presetId: string): void => {
    const preset = PRESET_AVATARS.find(p => p.id === presetId)
    if (preset) {
      settings.value.appearance = {
        style: preset.style,
        vrmUrl: preset.vrmUrl
      }
      saveSettings()
    }
  }

  /**
   * Set whiteboard content (for classroom mode)
   */
  const setWhiteboardContent = (content: string): void => {
    whiteboardContent.value = content
  }

  /**
   * Toggle lip-sync
   */
  const toggleLipSync = (enabled?: boolean): void => {
    settings.value.lipSyncEnabled = enabled ?? !settings.value.lipSyncEnabled
    saveSettings()
  }

  /**
   * Load settings from localStorage
   */
  const loadSettings = (): void => {
    const saved = localStorage.getItem('avatar-settings')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        settings.value = { ...settings.value, ...parsed }
      } catch (e) {
        console.warn('Failed to load avatar settings:', e)
      }
    }
  }

  /**
   * Save settings to localStorage
   */
  const saveSettings = (): void => {
    localStorage.setItem('avatar-settings', JSON.stringify(settings.value))
  }

  /**
   * Reset to default settings
   */
  const resetSettings = (): void => {
    settings.value = {
      enabled: true,
      mode: 'floating',
      position: 'bottom-right',
      scale: 1,
      appearance: { style: 'robot' },
      lipSyncEnabled: true,
      lipSyncSensitivity: 0.5,
      animationsEnabled: true,
      showWhiteboardInCourse: true,
      autoExpandOnSpeaking: true
    }
    localStorage.removeItem('avatar-settings')
  }

  /**
   * Cleanup audio resources
   */
  const cleanup = (): void => {
    if (audioContext.value) {
      audioContext.value.close()
      audioContext.value = null
    }
    analyser.value = null
    dataArray.value = null
  }

  // =====================================
  // RETURN
  // =====================================

  return {
    // State
    settings,
    currentState,
    isLoaded,
    isLoading,
    loadError,
    lipSyncData,
    animationQueue,
    currentAnimation,
    whiteboardContent,

    // Computed
    isRobotStyle,
    isVRMStyle,
    hasVRM,
    effectiveMode,

    // Actions
    initAudioAnalyzer,
    connectAudioForLipSync,
    updateLipSync,
    setState,
    queueAnimation,
    playNextAnimation,
    setMode,
    setAppearance,
    setCustomVRM,
    selectPreset,
    setWhiteboardContent,
    toggleLipSync,
    loadSettings,
    saveSettings,
    resetSettings,
    cleanup,

    // Constants
    PRESET_AVATARS,
    VISEME_MAP
  }
})
