/**
 * LernsystemX - Panel AI Jobs Sub-Store (Pinia)
 *
 * Manages AI job lifecycle:
 * - Starting, polling, and cancelling AI jobs
 * - Job status tracking with automatic polling
 * - Finalizing jobs into course content
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as adminApi from '@/application/services/api/panel-admin'

export const usePanelAIJobsStore = defineStore('panel-ai-jobs', () => {
  // State
  const aiJobs = ref<Map<string, adminApi.AIJob>>(new Map())
  const currentAIJob = ref<adminApi.AIJob | null>(null)
  const aiJobPollingInterval = ref<number | null>(null)
  const aiJobLoading = ref(false)
  const aiJobError = ref<string | null>(null)

  // Actions

  /**
   * Start AI Job
   * @param file - Optional file to process (PDF, DOCX, PPTX, TXT)
   * @param prompt - Optional custom prompt text
   * @param promptId - Optional prompt template ID from prompt registry
   * @param model - Optional AI model override
   */
  const startAIJob = async (
    file?: File,
    prompt?: string,
    promptId?: string,
    model?: string
  ): Promise<adminApi.AIJob> => {
    aiJobLoading.value = true
    aiJobError.value = null

    try {
      const formData = new FormData()
      formData.append('type', 'course_from_pdf')
      if (file) {
        formData.append('file', file)
      }
      if (prompt) {
        formData.append('prompt', prompt)
      }
      if (promptId) {
        formData.append('prompt_id', promptId)
      }
      if (model) {
        formData.append('model', model)
      }

      const job = await adminApi.adminStartAIJob(formData)

      aiJobs.value.set(job.id, job)
      currentAIJob.value = job

      if (job.status === 'pending' || job.status === 'processing') {
        startAIJobPolling(job.id)
      }

      return job
    } catch (err: any) {
      aiJobError.value = err.response?.data?.message || 'Fehler beim Starten des AI-Jobs'
      console.error('Failed to start AI job:', err)
      throw err
    } finally {
      aiJobLoading.value = false
    }
  }

  /**
   * Poll AI Job Status
   */
  const pollAIJob = async (jobId: string): Promise<adminApi.AIJob> => {
    try {
      const job = await adminApi.adminGetAIJob(jobId)

      aiJobs.value.set(jobId, job)

      if (currentAIJob.value?.id === jobId) {
        currentAIJob.value = job
      }

      if (['completed', 'failed', 'cancelled'].includes(job.status)) {
        stopAIJobPolling()
      }

      return job
    } catch (err: any) {
      aiJobError.value = err.response?.data?.message || 'Fehler beim Abrufen des Job-Status'
      console.error('Failed to poll AI job:', err)
      throw err
    }
  }

  /**
   * Start polling for AI job updates (every 1500ms)
   */
  const startAIJobPolling = (jobId: string): void => {
    stopAIJobPolling()

    aiJobPollingInterval.value = window.setInterval(async () => {
      try {
        await pollAIJob(jobId)
      } catch (err) {
        console.error('Polling error:', err)
        stopAIJobPolling()
      }
    }, 1500)
  }

  /**
   * Stop polling for AI job updates
   */
  const stopAIJobPolling = (): void => {
    if (aiJobPollingInterval.value !== null) {
      clearInterval(aiJobPollingInterval.value)
      aiJobPollingInterval.value = null
    }
  }

  /**
   * Get AI Job by ID
   */
  const getAIJob = async (jobId: string): Promise<adminApi.AIJob> => {
    aiJobLoading.value = true
    aiJobError.value = null

    try {
      const job = await adminApi.adminGetAIJob(jobId)

      aiJobs.value.set(jobId, job)
      currentAIJob.value = job

      if (job.status === 'pending' || job.status === 'processing') {
        startAIJobPolling(job.id)
      }

      return job
    } catch (err: any) {
      aiJobError.value = err.response?.data?.message || 'Fehler beim Laden des AI-Jobs'
      console.error('Failed to get AI job:', err)
      throw err
    } finally {
      aiJobLoading.value = false
    }
  }

  /**
   * Cancel AI Job
   */
  const cancelAIJob = async (jobId: string): Promise<void> => {
    try {
      await adminApi.adminCancelAIJob(jobId)

      stopAIJobPolling()

      const job = aiJobs.value.get(jobId)
      if (job) {
        job.status = 'cancelled'
        aiJobs.value.set(jobId, job)

        if (currentAIJob.value?.id === jobId) {
          currentAIJob.value = job
        }
      }
    } catch (err: any) {
      aiJobError.value = err.response?.data?.message || 'Fehler beim Abbrechen des Jobs'
      console.error('Failed to cancel AI job:', err)
      throw err
    }
  }

  /**
   * Finalize AI Job - creates course content from AI output
   * Returns the created course ID for navigation
   */
  const finalizeAIJob = async (
    jobId: string,
    options?: adminApi.AIJobFinalizeRequest
  ): Promise<number> => {
    aiJobLoading.value = true
    aiJobError.value = null

    try {
      const response = await adminApi.adminFinalizeAIJob(jobId, options)

      stopAIJobPolling()

      const job = aiJobs.value.get(jobId)
      if (job) {
        job.course_id = response.course_id.toString()
        aiJobs.value.set(jobId, job)

        if (currentAIJob.value?.id === jobId) {
          currentAIJob.value = job
        }
      }

      return response.course_id
    } catch (err: any) {
      aiJobError.value = err.response?.data?.message || 'Fehler beim Finalisieren des Jobs'
      console.error('Failed to finalize AI job:', err)
      throw err
    } finally {
      aiJobLoading.value = false
    }
  }

  /**
   * Clear current AI job state and stop polling
   */
  const clearCurrentAIJob = (): void => {
    stopAIJobPolling()
    currentAIJob.value = null
    aiJobError.value = null
  }

  return {
    // State
    aiJobs,
    currentAIJob,
    aiJobLoading,
    aiJobError,

    // Actions
    startAIJob,
    pollAIJob,
    getAIJob,
    cancelAIJob,
    finalizeAIJob,
    clearCurrentAIJob,
    startAIJobPolling,
    stopAIJobPolling
  }
})
