/**
 * useBulkTranslate Composable
 *
 * Manages the step-based AI bulk translation workflow:
 * 1. Creates a translation job
 * 2. Repeatedly calls /run to process batches
 * 3. Polls progress until complete or failed
 */

import { ref, computed } from 'vue'
import { languagesApi, type BulkTranslateJob } from '@/infrastructure/api/clients/panel/admin'

export function useBulkTranslate() {
  const translating = ref(false)
  const jobId = ref<string | null>(null)
  const status = ref<BulkTranslateJob['status'] | null>(null)
  const progressPercent = ref(0)
  const translated = ref(0)
  const failed = ref(0)
  const total = ref(0)
  const error = ref<string | null>(null)

  const isActive = computed(() =>
    translating.value && (status.value === 'queued' || status.value === 'processing')
  )

  /**
   * Start bulk translation and drive it to completion.
   *
   * Calls POST /bulk-translate to create the job, then
   * repeatedly calls POST /bulk-translate/<id>/run until done.
   */
  async function startTranslation(
    sourceLanguage: string,
    targetLanguage: string
  ): Promise<void> {
    translating.value = true
    error.value = null
    progressPercent.value = 0
    translated.value = 0
    failed.value = 0
    total.value = 0

    try {
      // 1. Create job
      const job = await languagesApi.startBulkTranslate(sourceLanguage, targetLanguage)
      jobId.value = job.job_id
      status.value = job.status
      total.value = job.output_data?.total ?? 0

      if (total.value === 0) {
        status.value = 'completed'
        translating.value = false
        return
      }

      // 2. Run steps until done
      await driveToCompletion()
    } catch (err: any) {
      error.value = err.message || 'Translation failed'
      status.value = 'failed'
    } finally {
      translating.value = false
    }
  }

  async function driveToCompletion(): Promise<void> {
    if (!jobId.value) return

    let maxIterations = 200 // Safety limit
    while (maxIterations-- > 0) {
      try {
        const result = await languagesApi.runBulkTranslateStep(jobId.value)
        updateFromJob(result)

        if (result.status === 'completed' || result.status === 'failed') {
          if (result.status === 'failed') {
            error.value = result.output_data?.error || 'Translation failed'
          }
          break
        }

        // Brief pause between steps to avoid hammering the server
        await sleep(500)
      } catch (err: any) {
        error.value = err.message || 'Translation step failed'
        status.value = 'failed'
        break
      }
    }
  }

  function updateFromJob(job: BulkTranslateJob): void {
    status.value = job.status
    progressPercent.value = job.progress_percentage ?? 0
    if (job.output_data) {
      translated.value = job.output_data.translated ?? 0
      failed.value = job.output_data.failed ?? 0
      total.value = job.output_data.total ?? total.value
    }
  }

  function reset(): void {
    translating.value = false
    jobId.value = null
    status.value = null
    progressPercent.value = 0
    translated.value = 0
    failed.value = 0
    total.value = 0
    error.value = null
  }

  return {
    translating,
    status,
    progressPercent,
    translated,
    failed,
    total,
    error,
    isActive,
    startTranslation,
    reset
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}
