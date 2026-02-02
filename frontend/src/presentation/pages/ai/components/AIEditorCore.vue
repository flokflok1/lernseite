<!--
  AI Editor Core Component
  Shared features for all authenticated users
-->

<template>
  <div class="bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl p-8 text-white text-center">
    <div class="w-20 h-20 mx-auto mb-6 bg-white/20 rounded-2xl flex items-center justify-center">
      <span class="text-5xl">✨</span>
    </div>
    <h1 class="text-3xl font-bold mb-3">{{ $t('panel.aiEditor.title') }}</h1>
    <p class="text-white/80 mb-6 max-w-md mx-auto">
      {{ $t('panel.aiEditor.description') }}
    </p>

    <button
      @click="emit('open-editor')"
      class="px-8 py-4 bg-white text-violet-600 font-bold rounded-xl hover:bg-white/90 transition-colors text-lg"
    >
      {{ $t('panel.aiEditor.openStudio') }}
    </button>

    <!-- Features -->
    <div class="grid grid-cols-3 gap-4 mt-8 text-sm">
      <div class="bg-white/10 rounded-xl p-4">
        <span class="text-2xl mb-2 block">🎬</span>
        <span class="font-medium">{{ $t('panel.aiEditor.features.videos') }}</span>
        <p class="text-white/60 text-xs mt-1">{{ $t('panel.aiEditor.features.videosDesc') }}</p>
      </div>
      <div class="bg-white/10 rounded-xl p-4">
        <span class="text-2xl mb-2 block">📝</span>
        <span class="font-medium">{{ $t('panel.aiEditor.features.prompts') }}</span>
        <p class="text-white/60 text-xs mt-1">{{ $t('panel.aiEditor.features.promptsDesc') }}</p>
      </div>
      <div class="bg-white/10 rounded-xl p-4">
        <span class="text-2xl mb-2 block">⚙️</span>
        <span class="font-medium">{{ $t('panel.aiEditor.features.models') }}</span>
        <p class="text-white/60 text-xs mt-1">{{ $t('panel.aiEditor.features.modelsDesc') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

useI18n()

const emit = defineEmits<{
  'open-editor': []
}>()
</script>
