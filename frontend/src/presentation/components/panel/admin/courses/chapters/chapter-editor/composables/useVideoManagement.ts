/**
 * useVideoManagement Composable
 * Handles video management (add, remove, list)
 */

import { ref } from 'vue'
import type { VideoItem } from '../types'

export function useVideoManagement() {
  // State
  const videos = ref<VideoItem[]>([])

  /**
   * Add new video to list
   */
  const addVideo = () => {
    videos.value.push({ title: '', url: '' })
  }

  /**
   * Remove video from list by index
   */
  const removeVideo = (index: number) => {
    videos.value.splice(index, 1)
  }

  /**
   * Update video at index
   */
  const updateVideo = (index: number, video: VideoItem) => {
    if (index >= 0 && index < videos.value.length) {
      videos.value[index] = video
    }
  }

  /**
   * Validate video URL
   */
  const isValidVideoUrl = (url: string): boolean => {
    try {
      new URL(url)
      return /\.(mp4|webm|ogg|mkv)$|youtube\.com|vimeo\.com/.test(url)
    } catch {
      return false
    }
  }

  /**
   * Clear all videos
   */
  const clearVideos = () => {
    videos.value = []
  }

  return {
    // State
    videos,

    // Methods
    addVideo,
    removeVideo,
    updateVideo,
    isValidVideoUrl,
    clearVideos
  }
}
