<script setup lang="ts">
/**
 * TutorCompanion - Global 3D AI Tutor Widget
 *
 * A floating 3D avatar tutor that accompanies users throughout the app.
 * Avatar and Chat window are SEPARATE - Avatar floats freely, chat opens separately.
 */

import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import * as THREE from 'three'
import { useTutorStore, DEFAULT_PERSONALITIES } from '@/application/stores/tutor.store'
import { tutorChat, tutorTTS } from '@/infrastructure/api/tutor.api'

const { t } = useI18n()

const tutorStore = useTutorStore()

// Check if tutor has context (course/chapter/lesson loaded)
const hasContext = computed(() => {
  const ctx = tutorStore.contextIds
  return !!(ctx.courseId || ctx.chapterId || ctx.lessonId || ctx.methodId)
})

// Refs
const avatarContainer = ref<HTMLDivElement | null>(null)
const chatContainer = ref<HTMLDivElement | null>(null)
const userInput = ref('')
const showSettings = ref(false)
const showChat = ref(false)

// Three.js refs
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let avatar: THREE.Group
let animationId: number
let clock: THREE.Clock

// Initialize Three.js scene
const initThreeJS = () => {
  if (!avatarContainer.value) return

  const container = avatarContainer.value
  const width = container.clientWidth
  const height = container.clientHeight

  // Scene
  scene = new THREE.Scene()
  scene.background = null  // Transparent background

  // Camera
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
  camera.position.set(0, 0.3, 2)
  camera.lookAt(0, 0.2, 0)

  // Renderer with transparency and WebGL fallback
  try {
    renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'default',
      failIfMajorPerformanceCaveat: false
    })
  } catch (e) {
    console.warn('WebGL not available, using fallback')
    // Fallback: show static avatar image instead
    container.innerHTML = '<div class="w-full h-full flex items-center justify-center text-4xl">🤖</div>'
    return
  }
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.setClearColor(0x000000, 0)  // Explicit transparent clear
  container.appendChild(renderer.domElement)

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(2, 3, 2)
  scene.add(directionalLight)

  const fillLight = new THREE.DirectionalLight(0x8888ff, 0.3)
  fillLight.position.set(-2, 1, -1)
  scene.add(fillLight)

  // Create placeholder avatar (stylized robot/character)
  createPlaceholderAvatar()

  // Clock for animations
  clock = new THREE.Clock()

  // Start animation loop
  animate()
}

// Create a stylized placeholder avatar
const createPlaceholderAvatar = () => {
  avatar = new THREE.Group()

  // Body - Rounded cylinder
  const bodyGeometry = new THREE.CapsuleGeometry(0.25, 0.4, 8, 16)
  const bodyMaterial = new THREE.MeshStandardMaterial({
    color: 0x6366f1,  // Indigo
    metalness: 0.3,
    roughness: 0.7
  })
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
  body.position.y = 0
  avatar.add(body)

  // Head - Sphere
  const headGeometry = new THREE.SphereGeometry(0.22, 32, 32)
  const headMaterial = new THREE.MeshStandardMaterial({
    color: 0x818cf8,  // Lighter indigo
    metalness: 0.2,
    roughness: 0.6
  })
  const head = new THREE.Mesh(headGeometry, headMaterial)
  head.position.y = 0.55
  head.name = 'head'
  avatar.add(head)

  // Eyes - Two small spheres
  const eyeGeometry = new THREE.SphereGeometry(0.04, 16, 16)
  const eyeMaterial = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    emissive: 0x88ffff,
    emissiveIntensity: 0.5
  })

  const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
  leftEye.position.set(-0.08, 0.58, 0.18)
  avatar.add(leftEye)

  const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
  rightEye.position.set(0.08, 0.58, 0.18)
  avatar.add(rightEye)

  // Pupils
  const pupilGeometry = new THREE.SphereGeometry(0.02, 8, 8)
  const pupilMaterial = new THREE.MeshStandardMaterial({ color: 0x1e1b4b })

  const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
  leftPupil.position.set(-0.08, 0.58, 0.21)
  leftPupil.name = 'leftPupil'
  avatar.add(leftPupil)

  const rightPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
  rightPupil.position.set(0.08, 0.58, 0.21)
  rightPupil.name = 'rightPupil'
  avatar.add(rightPupil)

  // Mouth - Curved line (torus segment)
  const mouthGeometry = new THREE.TorusGeometry(0.06, 0.015, 8, 16, Math.PI)
  const mouthMaterial = new THREE.MeshStandardMaterial({ color: 0x312e81 })
  const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial)
  mouth.position.set(0, 0.48, 0.18)
  mouth.rotation.x = Math.PI
  mouth.rotation.z = Math.PI
  mouth.name = 'mouth'
  avatar.add(mouth)

  // Antenna/Hair - Small cone on top
  const antennaGeometry = new THREE.ConeGeometry(0.03, 0.15, 8)
  const antennaMaterial = new THREE.MeshStandardMaterial({
    color: 0xa5b4fc,
    emissive: 0x6366f1,
    emissiveIntensity: 0.3
  })
  const antenna = new THREE.Mesh(antennaGeometry, antennaMaterial)
  antenna.position.y = 0.82
  antenna.name = 'antenna'
  avatar.add(antenna)

  // Glow ball on antenna
  const glowGeometry = new THREE.SphereGeometry(0.04, 16, 16)
  const glowMaterial = new THREE.MeshStandardMaterial({
    color: 0x22d3ee,
    emissive: 0x22d3ee,
    emissiveIntensity: 1
  })
  const glow = new THREE.Mesh(glowGeometry, glowMaterial)
  glow.position.y = 0.92
  glow.name = 'glow'
  avatar.add(glow)

  scene.add(avatar)
}

// Animation loop
const animate = () => {
  animationId = requestAnimationFrame(animate)

  const time = clock.getElapsedTime()

  if (avatar) {
    // Floating animation - more pronounced
    avatar.position.y = Math.sin(time * 1.5) * 0.05

    // Gentle rotation
    avatar.rotation.y = Math.sin(time * 0.5) * 0.15

    // Find components
    const head = avatar.getObjectByName('head') as THREE.Mesh
    const antenna = avatar.getObjectByName('antenna') as THREE.Mesh
    const glow = avatar.getObjectByName('glow') as THREE.Mesh
    const mouth = avatar.getObjectByName('mouth') as THREE.Mesh

    if (head) {
      // Head bob
      head.rotation.z = Math.sin(time * 1.5) * 0.08
      head.rotation.x = Math.sin(time * 1.2) * 0.03
    }

    if (antenna) {
      // Antenna sway
      antenna.rotation.z = Math.sin(time * 3) * 0.15
    }

    if (glow) {
      // Pulsing glow
      const scale = 1 + Math.sin(time * 4) * 0.3
      glow.scale.set(scale, scale, scale)

      // Color shift based on state
      const mat = glow.material as THREE.MeshStandardMaterial
      if (tutorStore.isTyping || tutorStore.isLoading) {
        mat.emissive.setHex(0xfbbf24)  // Yellow when thinking
      } else if (tutorStore.isSpeaking) {
        mat.emissive.setHex(0x22c55e)  // Green when speaking
      } else {
        mat.emissive.setHex(0x22d3ee)  // Cyan idle
      }
    }

    if (mouth) {
      // Mouth animation when speaking
      if (tutorStore.isSpeaking) {
        mouth.scale.y = 1 + Math.sin(time * 20) * 0.6
        mouth.scale.x = 1 + Math.sin(time * 15) * 0.3
      } else {
        mouth.scale.y = 1
        mouth.scale.x = 1
      }
    }
  }

  renderer.render(scene, camera)
}

// Handle resize
const handleResize = () => {
  if (!avatarContainer.value || !renderer || !camera) return

  const width = avatarContainer.value.clientWidth
  const height = avatarContainer.value.clientHeight

  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

// Toggle chat window
const toggleChat = () => {
  showChat.value = !showChat.value
}

// Send message to tutor
const sendMessage = async () => {
  const message = userInput.value.trim()
  if (!message || tutorStore.isLoading) return

  userInput.value = ''

  // Add user message
  tutorStore.addMessage('user', message)

  // Scroll to bottom
  await nextTick()
  scrollToBottom()

  // Set loading state
  tutorStore.isLoading = true
  tutorStore.isTyping = true

  try {
    // Call API with context IDs for knowledge-aware responses
    const contextIds = tutorStore.contextIds
    const response = await tutorChat({
      message,
      context: tutorStore.contextDescription,
      systemPrompt: tutorStore.effectiveSystemPrompt,
      history: tutorStore.messages.slice(-10).map(m => ({
        role: m.role === 'user' ? 'user' : 'assistant',
        content: m.content
      })),
      // Pass context IDs for DB-based knowledge loading
      courseId: contextIds.courseId || undefined,
      chapterId: contextIds.chapterId || undefined,
      lessonId: contextIds.lessonId || undefined,
      methodId: contextIds.methodId || undefined
    })

    tutorStore.isTyping = false

    // Add tutor response
    tutorStore.addMessage('tutor', response.message)

    // Scroll to bottom
    await nextTick()
    scrollToBottom()

    // Auto-play TTS if enabled
    if (tutorStore.settings.ttsEnabled && tutorStore.settings.ttsAutoPlay) {
      await playTTS(response.message)
    }

  } catch (error) {
    console.error('Tutor chat error:', error)
    tutorStore.addMessage('tutor', t('tutor.errorMessage'))
  } finally {
    tutorStore.isLoading = false
    tutorStore.isTyping = false
  }
}

// Play TTS
const playTTS = async (text: string) => {
  if (!tutorStore.settings.ttsEnabled) return

  try {
    const audioUrl = await tutorTTS({
      text,
      voice: tutorStore.settings.personality.voiceId || 'alloy'
    })

    const audio = new Audio(audioUrl)
    tutorStore.setSpeaking(true, audio)

    audio.onended = () => {
      tutorStore.setSpeaking(false)
    }

    audio.onerror = () => {
      tutorStore.setSpeaking(false)
    }

    await audio.play()

  } catch (error) {
    console.error('TTS error:', error)
    tutorStore.setSpeaking(false)
  }
}

// Scroll chat to bottom
const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// Lifecycle
onMounted(() => {
  tutorStore.loadSettings()
  nextTick(() => initThreeJS())
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  if (renderer) {
    renderer.dispose()
  }
  window.removeEventListener('resize', handleResize)
})

// Format time
const formatTime = (date: Date) => {
  return new Date(date).toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div v-if="tutorStore.settings.enabled">
    <!-- ============================================== -->
    <!-- FLOATING 3D AVATAR (separate from chat) -->
    <!-- ============================================== -->
    <div
      class="fixed z-40 transition-all duration-500 cursor-pointer group"
      :class="[
        tutorStore.settings.position === 'bottom-right' ? 'right-6 bottom-6' : 'left-6 bottom-6'
      ]"
      @click="toggleChat"
    >
      <!-- Avatar Container with glow effect -->
      <div class="relative">
        <!-- Glow ring when speaking -->
        <div
          v-if="tutorStore.isSpeaking"
          class="absolute inset-0 rounded-full bg-green-400/30 animate-ping"
          style="width: 140px; height: 140px; margin: -10px;"
        ></div>

        <!-- Thinking ring -->
        <div
          v-if="tutorStore.isTyping"
          class="absolute inset-0 rounded-full border-4 border-yellow-400/50 animate-spin"
          style="width: 140px; height: 140px; margin: -10px; border-top-color: transparent;"
        ></div>

        <!-- 3D Avatar Canvas -->
        <div
          ref="avatarContainer"
          class="w-[120px] h-[120px] rounded-full overflow-hidden bg-gradient-to-br from-indigo-500/20 to-purple-600/20 backdrop-blur-sm border-2 border-white/20 shadow-2xl group-hover:scale-110 transition-transform duration-300"
        ></div>

        <!-- Status Badge -->
        <div
          class="absolute -top-1 -right-1 w-5 h-5 rounded-full border-2 border-white shadow-lg flex items-center justify-center"
          :class="[
            tutorStore.isSpeaking ? 'bg-green-500' :
            tutorStore.isTyping ? 'bg-yellow-500' :
            'bg-indigo-500'
          ]"
        >
          <span v-if="tutorStore.isSpeaking" class="text-white text-xs">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
              <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
            </svg>
          </span>
          <span v-else-if="tutorStore.isTyping" class="text-white text-xs">...</span>
        </div>

        <!-- Chat bubble hint -->
        <div
          v-if="!showChat && tutorStore.messages.length === 0"
          class="absolute -top-12 left-1/2 -translate-x-1/2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
        >
          {{ $t('tutor.clickMe') }}
          <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-3 h-3 bg-gray-900 rotate-45"></div>
        </div>
      </div>
    </div>

    <!-- ============================================== -->
    <!-- CHAT WINDOW (separate, floating) -->
    <!-- ============================================== -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-4 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-4 scale-95"
    >
      <div
        v-if="showChat"
        class="fixed z-50 w-96 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
        :class="[
          tutorStore.settings.position === 'bottom-right' ? 'right-6 bottom-36' : 'left-6 bottom-36'
        ]"
        style="max-height: 500px; height: 60vh;"
      >
        <!-- Header -->
        <div class="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>

          <div class="flex-1 min-w-0">
            <h3 class="text-white font-semibold truncate">
              {{ tutorStore.settings.customPersonalityText ? $t('tutor.myTutor') : tutorStore.settings.personality.name }}
            </h3>
            <p class="text-indigo-200 text-sm truncate">
              {{ tutorStore.isTyping ? $t('tutor.statusTyping') : tutorStore.isSpeaking ? $t('tutor.statusSpeaking') : hasContext ? $t('tutor.statusContext') : $t('tutor.statusIdle') }}
            </p>
          </div>

          <!-- Context indicator -->
          <div
            v-if="hasContext"
            class="px-2 py-0.5 rounded-full bg-green-500/30 text-green-100 text-xs flex items-center gap-1"
            :title="tutorStore.contextDescription"
          >
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            {{ $t('tutor.context') }}
          </div>

          <div class="flex items-center gap-1">
            <!-- Settings -->
            <button
              @click="showSettings = !showSettings"
              class="p-2 rounded-lg hover:bg-white/20 transition-colors"
              :title="$t('tutor.settings')"
            >
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>

            <!-- Close -->
            <button
              @click="showChat = false"
              class="p-2 rounded-lg hover:bg-white/20 transition-colors"
              :title="$t('tutor.close')"
            >
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Settings Panel -->
        <div v-if="showSettings" class="p-4 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-600 max-h-48 overflow-y-auto">
          <h4 class="font-medium text-gray-900 dark:text-white mb-3">{{ $t('tutor.settingsTitle') }}</h4>

          <!-- Personality Selection -->
          <div class="mb-4">
            <label class="block text-sm text-gray-600 dark:text-gray-300 mb-2">{{ $t('tutor.personality') }}</label>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="personality in DEFAULT_PERSONALITIES"
                :key="personality.id"
                @click="tutorStore.setPersonality(personality); tutorStore.saveSettings()"
                class="p-2 text-left rounded-lg border transition-colors"
                :class="[
                  tutorStore.settings.personality.id === personality.id && !tutorStore.settings.customPersonalityText
                    ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
                    : 'border-gray-200 dark:border-gray-600 hover:border-indigo-300'
                ]"
              >
                <div class="font-medium text-sm text-gray-900 dark:text-white">{{ personality.name }}</div>
              </button>
            </div>
          </div>

          <!-- Custom Personality -->
          <div class="mb-4">
            <label class="block text-sm text-gray-600 dark:text-gray-300 mb-2">{{ $t('tutor.customDescription') }}</label>
            <textarea
              v-model="tutorStore.settings.customPersonalityText"
              @change="tutorStore.saveSettings()"
              :placeholder="$t('tutor.customPlaceholder')"
              class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm resize-none"
              rows="2"
            ></textarea>
          </div>

          <!-- TTS Toggle -->
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-600 dark:text-gray-300">{{ $t('tutor.tts') }}</span>
            <button
              @click="tutorStore.setTTSEnabled(!tutorStore.settings.ttsEnabled); tutorStore.saveSettings()"
              class="relative w-12 h-6 rounded-full transition-colors"
              :class="tutorStore.settings.ttsEnabled ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600'"
            >
              <span
                class="absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform"
                :class="tutorStore.settings.ttsEnabled ? 'translate-x-6' : ''"
              ></span>
            </button>
          </div>

          <!-- Auto-play TTS -->
          <div v-if="tutorStore.settings.ttsEnabled" class="flex items-center justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-300">{{ $t('tutor.ttsAutoPlay') }}</span>
            <button
              @click="tutorStore.setTTSAutoPlay(!tutorStore.settings.ttsAutoPlay); tutorStore.saveSettings()"
              class="relative w-12 h-6 rounded-full transition-colors"
              :class="tutorStore.settings.ttsAutoPlay ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600'"
            >
              <span
                class="absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform"
                :class="tutorStore.settings.ttsAutoPlay ? 'translate-x-6' : ''"
              ></span>
            </button>
          </div>
        </div>

        <!-- Chat Messages -->
        <div
          ref="chatContainer"
          class="flex-1 overflow-y-auto p-4 space-y-3"
        >
          <!-- Welcome message if empty -->
          <div v-if="tutorStore.messages.length === 0" class="text-center py-6">
            <div class="w-12 h-12 mx-auto mb-3 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/30 dark:to-purple-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
            </div>
            <h4 class="font-medium text-gray-900 dark:text-white mb-1">
              {{ $t('tutor.welcomeTitle') }}
            </h4>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ $t('tutor.welcomeHint') }}
            </p>
          </div>

          <!-- Messages -->
          <div
            v-for="message in tutorStore.messages"
            :key="message.id"
            class="flex"
            :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[85%] rounded-2xl px-4 py-2"
              :class="[
                message.role === 'user'
                  ? 'bg-indigo-600 text-white rounded-br-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-md'
              ]"
            >
              <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
              <div
                class="text-xs mt-1 flex items-center gap-2"
                :class="message.role === 'user' ? 'text-indigo-200' : 'text-gray-400'"
              >
                <span>{{ formatTime(message.timestamp) }}</span>
                <!-- TTS button for tutor messages -->
                <button
                  v-if="message.role === 'tutor' && tutorStore.settings.ttsEnabled"
                  @click="playTTS(message.content)"
                  class="hover:text-indigo-400 transition-colors"
                  :title="$t('tutor.readAloud')"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Typing indicator -->
          <div v-if="tutorStore.isTyping" class="flex justify-start">
            <div class="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-md px-4 py-3">
              <div class="flex gap-1">
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="p-3 border-t border-gray-200 dark:border-gray-700">
          <form @submit.prevent="sendMessage" class="flex gap-2">
            <input
              v-model="userInput"
              type="text"
              :placeholder="$t('tutor.inputPlaceholder')"
              class="flex-1 px-4 py-2 rounded-full border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              :disabled="tutorStore.isLoading"
            />
            <button
              type="submit"
              :disabled="!userInput.trim() || tutorStore.isLoading"
              class="p-2 rounded-full bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>

          <!-- Stop speaking button -->
          <button
            v-if="tutorStore.isSpeaking"
            @click="tutorStore.stopSpeaking()"
            class="mt-2 w-full py-1.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
          >
            {{ $t('tutor.stopSpeaking') }}
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>
