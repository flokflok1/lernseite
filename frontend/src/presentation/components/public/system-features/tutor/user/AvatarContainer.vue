<script setup lang="ts">
/**
 * AvatarContainer - Main container for the 3D Avatar System
 *
 * Features:
 * - Floating avatar with chat
 * - Classroom/Whiteboard mode for courses
 * - Feedback button (separate window)
 * - Avatar settings panel
 * - Lip-sync integration
 *
 * Sub-components: AvatarChatWindow, AvatarSettingsPanel, Avatar3D, FeedbackWindow
 */

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import Avatar3D from './Avatar3D.vue'
import AvatarChatWindow from './AvatarChatWindow.vue'
import AvatarSettingsPanel from './AvatarSettingsPanel.vue'
import FeedbackWindow from './FeedbackWindow.vue'
import { useAvatarStore, type AvatarMode } from '@/application/stores/modules/ui/avatar.store'
import { useTutorStore } from '@/application/stores/modules/learning/tutor.store'

const avatarStore = useAvatarStore()
const tutorStore = useTutorStore()

const props = defineProps<{
  courseId?: string
  lessonId?: string
  courseName?: string
}>()

const showChat = ref(false)
const showSettings = ref(false)
const showFeedback = ref(false)
const isExpanded = ref(false)

const currentMode = computed<AvatarMode>(() => {
  if (props.courseId && avatarStore.settings.showWhiteboardInCourse) {
    return 'classroom'
  }
  return avatarStore.settings.mode
})

const positionClasses = computed(() => {
  const base = 'fixed z-40 transition-all duration-500'
  if (avatarStore.settings.position === 'bottom-right') {
    return `${base} right-6 bottom-6`
  }
  return `${base} left-6 bottom-6`
})

const avatarSize = computed(() => {
  if (isExpanded.value || currentMode.value === 'classroom') {
    return 'w-[300px] h-[300px]'
  }
  return 'w-[120px] h-[120px]'
})

function toggleChat(): void {
  showChat.value = !showChat.value
  if (showChat.value) {
    showSettings.value = false
  }
}

function toggleExpand(): void {
  isExpanded.value = !isExpanded.value
}

function onFeedbackSubmitted(feedbackId: string): void {
  console.log('Feedback submitted:', feedbackId)
}

watch(() => tutorStore.isSpeaking, (speaking) => {
  if (speaking && avatarStore.settings.autoExpandOnSpeaking) {
    isExpanded.value = true
  }
})

watch([() => props.courseId, () => props.lessonId, () => props.courseName], () => {
  tutorStore.updateContext({
    courseId: props.courseId || null,
    lessonId: props.lessonId || null,
    courseName: props.courseName || null
  })
})

onMounted(() => {
  tutorStore.loadSettings()
  avatarStore.loadSettings()
  avatarStore.initAudioAnalyzer()
})

onUnmounted(() => {
  avatarStore.cleanup()
})
</script>

<template>
  <div v-if="tutorStore.settings.enabled">
    <!-- FLOATING AVATAR -->
    <div :class="positionClasses" class="group">
      <div class="relative">
        <!-- Glow effects -->
        <div
          v-if="tutorStore.isSpeaking"
          class="absolute inset-0 rounded-full bg-green-400/30 animate-ping pointer-events-none"
          :style="{ width: isExpanded ? '320px' : '140px', height: isExpanded ? '320px' : '140px', margin: '-10px' }"
        ></div>

        <div
          v-if="tutorStore.isTyping"
          class="absolute inset-0 rounded-full border-4 border-yellow-400/50 animate-spin pointer-events-none"
          :style="{ width: isExpanded ? '320px' : '140px', height: isExpanded ? '320px' : '140px', margin: '-10px', borderTopColor: 'transparent' }"
        ></div>

        <!-- 3D Avatar -->
        <div
          :class="[
            avatarSize,
            'rounded-full overflow-hidden cursor-pointer',
            'bg-gradient-to-br from-indigo-500/20 to-purple-600/20',
            'backdrop-blur-sm border-2 border-white/20 shadow-2xl',
            'transition-all duration-300 group-hover:scale-105'
          ]"
          @click="toggleChat"
        >
          <Avatar3D
            :mode="currentMode"
            :show-whiteboard="currentMode === 'classroom'"
            :whiteboard-content="avatarStore.whiteboardContent"
          />
        </div>

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
              <path d="M3 9v6h4l5 5V4L7 9H3z"/>
            </svg>
          </span>
          <span v-else-if="tutorStore.isTyping" class="text-white text-xs">...</span>
        </div>

        <!-- Action Buttons -->
        <div
          class="absolute -right-12 top-1/2 -translate-y-1/2 flex flex-col gap-2"
          :class="avatarStore.settings.position === 'bottom-left' ? '-right-12' : '-left-12'"
        >
          <!-- Feedback Button -->
          <button
            @click.stop="showFeedback = true"
            class="w-9 h-9 rounded-full bg-white dark:bg-gray-800 shadow-lg flex items-center justify-center hover:scale-110 transition-transform border border-gray-200 dark:border-gray-700"
            title="Feedback geben"
          >
            <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
            </svg>
          </button>

          <!-- Expand/Collapse Button -->
          <button
            @click.stop="toggleExpand"
            class="w-9 h-9 rounded-full bg-white dark:bg-gray-800 shadow-lg flex items-center justify-center hover:scale-110 transition-transform border border-gray-200 dark:border-gray-700"
            :title="isExpanded ? 'Verkleinern' : 'Vergrößern'"
          >
            <svg v-if="isExpanded" class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/>
            </svg>
            <svg v-else class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/>
            </svg>
          </button>

          <!-- Settings Button -->
          <button
            @click.stop="showSettings = !showSettings"
            class="w-9 h-9 rounded-full bg-white dark:bg-gray-800 shadow-lg flex items-center justify-center hover:scale-110 transition-transform border border-gray-200 dark:border-gray-700"
            title="Einstellungen"
          >
            <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </button>
        </div>

        <!-- Hint bubble -->
        <div
          v-if="!showChat && tutorStore.messages.length === 0"
          class="absolute -top-12 left-1/2 -translate-x-1/2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity shadow-lg pointer-events-none"
        >
          Klick mich an!
          <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-3 h-3 bg-gray-900 rotate-45"></div>
        </div>
      </div>
    </div>

    <!-- SETTINGS PANEL -->
    <AvatarSettingsPanel
      :show="showSettings"
      @close="showSettings = false"
    />

    <!-- CHAT WINDOW -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-4 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-4 scale-95"
    >
      <AvatarChatWindow
        v-if="showChat"
        :is-expanded="isExpanded"
        @close="showChat = false"
      />
    </Transition>

    <!-- FEEDBACK WINDOW -->
    <FeedbackWindow
      v-if="showFeedback"
      :course-id="courseId"
      :lesson-id="lessonId"
      :context="courseName"
      @close="showFeedback = false"
      @submitted="onFeedbackSubmitted"
    />
  </div>
</template>
