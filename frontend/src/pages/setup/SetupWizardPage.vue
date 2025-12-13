<template>
  <SetupLayout>
    <div class="bg-[#1a1f35] rounded-lg shadow-lg p-6">
      <!-- Progress Stepper -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div
            v-for="(step, index) in steps"
            :key="step.id"
            class="flex-1"
          >
            <div class="flex items-center">
              <div
                :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm',
                  currentStepIndex >= index
                    ? 'bg-primary-600 text-white'
                    : 'bg-[#2a3350] text-gray-500'
                ]"
              >
                {{ index + 1 }}
              </div>
              <div
                v-if="index < steps.length - 1"
                :class="[
                  'flex-1 h-1 mx-2',
                  currentStepIndex > index ? 'bg-primary-600' : 'bg-[#2a3350]'
                ]"
              />
            </div>
            <div class="mt-2">
              <p
                :class="[
                  'text-sm font-medium',
                  currentStepIndex >= index ? 'text-white' : 'text-gray-400'
                ]"
              >
                {{ step.title }}
              </p>
            </div>
          </div>
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

interface Step {
  id: string
  title: string
  component: any
}

const steps: Step[] = [
  { id: 'environment', title: 'Umgebung', component: SetupEnvironmentStep },
  { id: 'system', title: 'Konfiguration', component: SetupSystemCheckStep },
  { id: 'database', title: 'Datenbank', component: SetupDatabaseStep },
  { id: 'admin', title: 'Admin', component: SetupAdminStep },
  { id: 'organisation', title: 'Organisation', component: SetupOrganisationStep },
  { id: 'ai', title: 'KI-Config', component: SetupAIConfigStep },
  { id: 'seed', title: 'Daten', component: SetupSeedStep },
  { id: 'finish', title: 'Abschluss', component: SetupFinishStep },
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
