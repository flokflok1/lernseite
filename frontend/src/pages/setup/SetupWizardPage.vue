<template>
  <SetupLayout>
    <div class="bg-[#1a1f35] rounded-lg shadow-lg p-6">
      <!-- Progress Stepper -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <template v-for="(step, index) in steps" :key="step.id">
            <!-- Step Circle and Label -->
            <div class="flex flex-col items-center" style="flex: 0 0 11%;">
              <!-- Circle -->
              <div
                :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all duration-300 mb-1.5',
                  currentStepIndex >= index
                    ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/50'
                    : currentStepIndex === index - 1
                    ? 'bg-[#3a4570] text-gray-300'
                    : 'bg-[#2a3350] text-gray-500'
                ]"
              >
                <span v-if="currentStepIndex > index">✓</span>
                <span v-else>{{ index + 1 }}</span>
              </div>

              <!-- Label -->
              <p
                :class="[
                  'text-[9px] font-medium leading-tight text-center truncate w-full',
                  currentStepIndex >= index
                    ? 'text-white font-semibold'
                    : currentStepIndex === index - 1
                    ? 'text-gray-300'
                    : 'text-gray-400'
                ]"
                :title="$t(step.titleKey)"
              >
                {{ $t(step.titleKey) }}
              </p>
            </div>

            <!-- Connector Line -->
            <div
              v-if="index < steps.length - 1"
              class="h-[2px] transition-all duration-300"
              style="flex: 0 0 1.5%;"
              :class="currentStepIndex > index ? 'bg-primary-600' : 'bg-[#2a3350]'"
            />
          </template>
        </div>
      </div>

      <!-- Step Content -->
      <div class="min-h-[400px]">
        <component
          :is="currentStepComponent"
          @next="handleNext"
          @back="handleBack"
        />
      </div>
    </div>
  </SetupLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import SetupLayout from '@/layouts/SetupLayout.vue'
import SetupEnvironmentStep from './steps/SetupEnvironmentStep.vue'
import SetupSystemCheckStep from './steps/SetupSystemCheckStep.vue'
import SetupDatabaseStep from './steps/SetupDatabaseStep.vue'
import SetupAdminStep from './steps/SetupAdminStep.vue'
import SetupOrganisationStep from './steps/SetupOrganisationStep.vue'
import SetupAIConfigStep from './steps/SetupAIConfigStep.vue'
import SetupSeedStep from './steps/SetupSeedStep.vue'
import SetupFinishStep from './steps/SetupFinishStep.vue'

const router = useRouter()
const { t } = useI18n()

interface Step {
  id: string
  titleKey: string
  component: any
}

const steps: Step[] = [
  { id: 'environment', titleKey: 'setup.steps.environment', component: SetupEnvironmentStep },
  { id: 'system', titleKey: 'setup.steps.system', component: SetupSystemCheckStep },
  { id: 'database', titleKey: 'setup.steps.database', component: SetupDatabaseStep },
  { id: 'admin', titleKey: 'setup.steps.admin', component: SetupAdminStep },
  { id: 'organisation', titleKey: 'setup.steps.organisation', component: SetupOrganisationStep },
  { id: 'ai', titleKey: 'setup.steps.ai', component: SetupAIConfigStep },
  { id: 'seed', titleKey: 'setup.steps.seed', component: SetupSeedStep },
  { id: 'finish', titleKey: 'setup.steps.finish', component: SetupFinishStep },
]

const currentStepIndex = ref(0)

const currentStepComponent = computed(() => steps[currentStepIndex.value].component)

const handleNext = () => {
  if (currentStepIndex.value < steps.length - 1) {
    currentStepIndex.value++
  }
}

const handleBack = () => {
  if (currentStepIndex.value > 0) {
    currentStepIndex.value--
  }
}
</script>
