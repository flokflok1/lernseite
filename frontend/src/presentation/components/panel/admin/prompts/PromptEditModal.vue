<!--
  PromptEditModal - Create/Edit modal for prompt templates

  Displays a two-column form: basic info + TTS settings on the left,
  prompt content (system prompt, user prompt, JSON schema) on the right.
-->

<template>
  <div
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div class="bg-[var(--color-surface)] rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-[var(--color-border)] flex justify-between items-center">
        <h2 class="text-xl font-bold text-[var(--color-text-primary)]">
          {{ template.template_id ? 'Template bearbeiten' : 'Neues Template erstellen' }}
        </h2>
        <button @click="$emit('close')" class="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">
          X
        </button>
      </div>

      <!-- Modal Body -->
      <div class="flex-1 overflow-y-auto p-6">
        <div class="grid grid-cols-2 gap-6">
          <!-- Left Column: Basic Info -->
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Name *</label>
              <input
                v-model="template.name"
                type="text"
                class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                placeholder="z.B. Theorieblatt ADHS-freundlich"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Code *</label>
              <input
                v-model="template.code"
                type="text"
                class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] font-mono"
                placeholder="z.B. theory_adhs"
              />
              <p class="text-xs text-[var(--color-text-secondary)] mt-1">Eindeutiger Identifier (keine Leerzeichen)</p>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Kategorie *</label>
                <select
                  v-model="template.category"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                >
                  <option value="theory">Theorieblatt</option>
                  <option value="lesson">Lektionsschritte</option>
                  <option value="quiz">Quiz</option>
                  <option value="flashcard">Karteikarten</option>
                  <option value="summary">Zusammenfassung</option>
                  <option value="explanation">Erklaerung</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Stil *</label>
                <select
                  v-model="template.style"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                >
                  <option value="standard">Standard</option>
                  <option value="adhs">ADHS-freundlich</option>
                  <option value="detailed">Ausfuehrlich</option>
                  <option value="short">Kurz & Kompakt</option>
                  <option value="exam_focus">Pruefungsfokus</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Beschreibung</label>
              <textarea
                v-model="template.description"
                rows="2"
                class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                placeholder="Kurze Beschreibung des Templates..."
              ></textarea>
            </div>

            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Model</label>
                <select
                  v-model="template.model"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                >
                  <option value="gpt-4o-mini">GPT-4o Mini</option>
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                  <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                  <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Temperatur</label>
                <input
                  v-model.number="template.temperature"
                  type="number"
                  min="0"
                  max="2"
                  step="0.1"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Max Tokens</label>
                <input
                  v-model.number="template.max_tokens"
                  type="number"
                  min="100"
                  max="16000"
                  step="100"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                />
              </div>
            </div>

            <!-- TTS Settings -->
            <div class="border-t border-[var(--color-border)] pt-4 mt-4">
              <h3 class="font-medium text-[var(--color-text-primary)] mb-3">TTS-Einstellungen (Audio)</h3>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Standard-Stimme</label>
                  <select
                    v-model="template.tts_voice"
                    class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                  >
                    <option value="nova">Nova (weiblich, freundlich)</option>
                    <option value="alloy">Alloy (neutral)</option>
                    <option value="echo">Echo (maennlich, warm)</option>
                    <option value="fable">Fable (neutral, expressiv)</option>
                    <option value="onyx">Onyx (maennlich, tief)</option>
                    <option value="shimmer">Shimmer (weiblich, sanft)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">TTS Model</label>
                  <select
                    v-model="template.tts_model"
                    class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                  >
                    <option value="tts-1">TTS-1 (schnell)</option>
                    <option value="tts-1-hd">TTS-1-HD (hohe Qualitaet)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column: Prompt Content -->
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">System Prompt *</label>
              <textarea
                v-model="template.system_prompt"
                rows="8"
                class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] font-mono text-sm"
                placeholder="Du bist ein erfahrener IT-Ausbilder..."
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">User Prompt Template *</label>
              <textarea
                v-model="template.user_prompt"
                rows="10"
                class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] font-mono text-sm"
                placeholder="Erstelle ein Theorieblatt fuer {{chapter_title}}..."
              ></textarea>
              <p class="text-xs text-[var(--color-text-secondary)] mt-1">
                Variablen: <code>{{ '{{chapter_title}}' }}</code>, <code>{{ '{{course_title}}' }}</code>,
                <code>{{ '{{chapter_description}}' }}</code>, <code>{{ '{{lesson_titles}}' }}</code>,
                <code>{{ '{{target_audience}}' }}</code>
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
                Erwartete JSON-Struktur (optional)
              </label>
              <textarea
                v-model="template.expected_json"
                rows="4"
                class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] font-mono text-sm"
                placeholder='{"overview": "...", "learningGoals": [...], ...}'
              ></textarea>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-4 border-t border-[var(--color-border)] flex justify-between items-center">
        <div>
          <label class="flex items-center gap-2 text-sm text-[var(--color-text-primary)]">
            <input
              v-model="template.is_default"
              type="checkbox"
              class="rounded border-[var(--color-border)]"
            />
            Als Standard fuer diese Kategorie/Stil setzen
          </label>
        </div>
        <div class="flex gap-3">
          <button
            @click="$emit('close')"
            class="px-4 py-2 border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] hover:bg-[var(--color-bg)] transition-colors"
          >
            Abbrechen
          </button>
          <button
            @click="$emit('save')"
            :disabled="saving"
            class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors disabled:opacity-50"
          >
            {{ saving ? 'Speichern...' : 'Speichern' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PromptTemplate } from './types/prompt.types.ts'

defineProps<{
  template: PromptTemplate
  saving: boolean
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'save'): void
}>()
</script>
