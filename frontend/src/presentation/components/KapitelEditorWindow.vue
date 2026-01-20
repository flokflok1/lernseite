<!--
  Admin Kapitel Editor Window - Phase 5 Complete

  Full-featured chapter editor with:
  - Auto-save (debounced 800ms)
  - Chapter metadata editing
  - Lessons list with drag & drop reordering
  - Create/Edit/Delete lessons
  Updated: 2025-11-27 (Refactoring: modules → chapters)
-->

<template>
  <div class="admin-kapitel-editor-window h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header with Course Context & Save Status -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-4 py-3">
      <div class="flex items-center justify-between">
        <p class="text-sm text-[var(--color-text-secondary)]">
          Kurs: <span class="font-medium text-[var(--color-text-primary)]">{{ courseTitle }}</span>
        </p>
        <!-- Save Status Indicator -->
        <div class="flex items-center gap-2 text-xs">
          <span v-if="saveStatus === 'saving'" class="text-blue-600 flex items-center gap-1">
            <svg class="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Speichern...
          </span>
          <span v-else-if="saveStatus === 'saved'" class="text-green-600 flex items-center gap-1">
            <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            Gespeichert
          </span>
          <span v-else-if="saveStatus === 'error'" class="text-red-600">
            Fehler beim Speichern
          </span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[var(--color-primary)] mx-auto mb-3"></div>
        <p class="text-sm text-[var(--color-text-secondary)]">{{ isNewChapter ? 'Vorbereiten...' : 'Lade Kapitel...' }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 p-6">
      <div class="rounded-lg p-4 border" style="background-color: var(--color-error-bg, #fef2f2); border-color: var(--color-error-border, #fecaca);">
        <p style="color: var(--color-error-text, #b91c1c);">{{ error }}</p>
        <button
          v-if="!isNewChapter"
          @click="loadChapter"
          class="mt-3 px-3 py-1.5 bg-red-600 text-white text-sm rounded hover:bg-red-700"
        >
          Erneut versuchen
        </button>
      </div>
    </div>

    <!-- Module Editor Content -->
    <div v-else class="flex-1 flex flex-col overflow-hidden">
      <!-- Tabs -->
      <div class="border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <div class="flex px-4">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-4 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
            ]"
          >
            <span class="mr-2">{{ tab.icon }}</span>
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="flex-1 overflow-y-auto">
        <!-- Module Info Tab -->
        <div v-if="activeTab === 'info'" class="p-6">
          <div class="space-y-6 max-w-2xl">
            <!-- KI-Assistent Button -->
            <button
              @click="openAIKapitelGenerator"
              :disabled="isGenerating"
              class="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-medium rounded-lg transition-all flex items-center justify-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
              </svg>
              <span>{{ isGenerating ? 'KI generiert...' : 'Mit KI ausfüllen' }}</span>
            </button>
            <p class="text-xs text-[var(--color-text-secondary)] text-center -mt-4 mb-2">
              Nutzt die hochgeladenen Kurs-PDFs als Kontext
            </p>

            <!-- Title -->
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                Kapiteltitel *
              </label>
              <input
                v-model="form.title"
                @input="debouncedSave"
                type="text"
                required
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                :placeholder="$t('windows.kapitelEditor.titlePlaceholder')"
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                {{ $t('windows.kapitelEditor.descriptionLabel') }}
              </label>
              <textarea
                v-model="form.description"
                @input="debouncedSave"
                rows="6"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                :placeholder="$t('windows.kapitelEditor.descriptionPlaceholder')"
              ></textarea>
            </div>

            <!-- Create Button for New Modules -->
            <div v-if="isNewChapter" class="pt-6 border-t border-[var(--color-border)]">
              <div class="flex items-center justify-between">
                <p class="text-sm text-[var(--color-text-secondary)]">
                  💡 Speichern Sie das Kapitel, um Lernmethoden und Lektionen hinzufügen zu können.
                </p>
                <button
                  @click="saveChapter"
                  :disabled="!form.title.trim() || saveStatus === 'saving'"
                  class="px-6 py-2.5 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  style="background-color: var(--color-primary);"
                >
                  <svg v-if="saveStatus === 'saving'" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>{{ saveStatus === 'saving' ? 'Wird erstellt...' : 'Kapitel erstellen' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- C1.2: Theory Tab -->
        <div v-else-if="activeTab === 'theory'" class="p-6">
          <div class="max-w-4xl">
            <div class="flex items-center justify-between mb-6">
              <div>
                <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">Theorieblätter</h3>
                <p class="text-sm text-[var(--color-text-secondary)] mt-1">
                  Erstellen Sie strukturierte Theorieinhalte für dieses Kapitel
                </p>
              </div>
            </div>

            <!-- Rich Text Editor Placeholder -->
            <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-6">
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-3">
                Theorie-Inhalt
              </label>
              <textarea
                v-model="theoryContent"
                rows="15"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] font-mono text-sm"
                placeholder="Geben Sie hier den Theorieinhalt ein (Markdown-Unterstützung geplant)..."
              ></textarea>
              <p class="text-xs text-[var(--color-text-secondary)] mt-2">
                💡 Tipp: In einer späteren Phase wird hier ein Rich-Text-Editor integriert
              </p>
            </div>
          </div>
        </div>

        <!-- C1.2: Videos Tab -->
        <div v-else-if="activeTab === 'videos'" class="p-6">
          <div class="max-w-4xl">
            <div class="flex items-center justify-between mb-6">
              <div>
                <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">Videos</h3>
                <p class="text-sm text-[var(--color-text-secondary)] mt-1">
                  Fügen Sie Videos via URL oder Upload hinzu
                </p>
              </div>
              <button
                @click="addVideo"
                class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors flex items-center gap-2"
              >
                <span>+</span>
                <span>Video hinzufügen</span>
              </button>
            </div>

            <!-- Videos List -->
            <div v-if="videos.length === 0" class="text-center py-12 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
              <div class="text-4xl mb-3">🎥</div>
              <p class="text-[var(--color-text-secondary)]">{{ $t('windows.kapitelEditor.noVideos') }}</p>
              <p class="text-sm text-[var(--color-text-secondary)] mt-1">{{ $t('windows.kapitelEditor.noVideosHint') }}</p>
            </div>

            <div v-else class="space-y-4">
              <div
                v-for="(video, index) in videos"
                :key="index"
                class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4"
              >
                <div class="flex items-start gap-4">
                  <div class="flex-1">
                    <input
                      v-model="video.title"
                      type="text"
                      :placeholder="$t('windows.kapitelEditor.videoTitlePlaceholder')"
                      class="w-full px-3 py-2 mb-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    />
                    <input
                      v-model="video.url"
                      type="text"
                      :placeholder="$t('windows.kapitelEditor.videoUrlPlaceholder')"
                      class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    />
                  </div>
                  <button
                    @click="removeVideo(index)"
                    class="text-red-600 hover:text-red-700 p-2"
                    style="color: var(--color-error, #dc2626);"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- D3.4: Learning Methods Tab - Professional Overview -->
        <div v-else-if="activeTab === 'methods'" class="p-6">
          <div class="max-w-4xl">
            <!-- Header with Summary -->
            <div class="flex items-center justify-between mb-6">
              <div>
                <h3 class="text-lg font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
                  📚 Lernmethoden
                  <span
                    v-if="learningMethods.length > 0"
                    class="text-sm font-normal px-2 py-0.5 rounded-full"
                    style="background-color: var(--color-primary-bg, #eff6ff); color: var(--color-primary);"
                  >
                    {{ learningMethods.length }} aktiv
                  </span>
                </h3>
                <p class="text-sm text-[var(--color-text-secondary)] mt-1">
                  <span v-if="learningMethods.length > 0">
                    {{ learningMethods.filter(m => m.published).length }} {{ $t('windows.kapitelEditor.published') }},
                    {{ learningMethods.filter(m => !m.published).length }} {{ $t('windows.kapitelEditor.draft') }}
                  </span>
                  <span v-else>{{ $t('windows.kapitelEditor.noMethods') }}</span>
                </p>
              </div>
              <button
                @click="openLearningMethodsEditor()"
                :disabled="isNewChapter"
                class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                <span>Hinzufügen</span>
              </button>
            </div>

            <!-- New Chapter Notice -->
            <div v-if="isNewChapter" class="rounded-lg p-4 border flex items-center gap-3" style="background-color: var(--color-info-bg, #eff6ff); border-color: var(--color-info-border, #bfdbfe);">
              <span class="flex-1 text-sm" style="color: var(--color-info-text, #1e40af);">
                ℹ️ Bitte speichern Sie zuerst das Kapitel, bevor Sie Lernmethoden hinzufügen können.
              </span>
              <button
                @click="saveAndEnableTab"
                :disabled="!form.title.trim() || saveStatus === 'saving'"
                class="px-4 py-2 text-white text-sm font-medium rounded-lg transition-colors whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
                style="background-color: var(--color-primary);"
              >
                {{ saveStatus === 'saving' ? 'Wird gespeichert...' : 'Kapitel erstellen' }}
              </button>
            </div>

            <!-- Loading State -->
            <div v-else-if="loadingMethods" class="flex items-center justify-center py-8">
              <svg class="animate-spin h-6 w-6 text-[var(--color-primary)]" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="ml-2 text-[var(--color-text-secondary)]">Lade Lernmethoden...</span>
            </div>

            <!-- Interactive Group Cards -->
            <div v-else class="space-y-4">
              <!-- Group Cards Grid -->
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <button
                  v-for="group in ['A', 'B', 'C', 'D']"
                  :key="group"
                  @click="openLearningMethodsEditor(group)"
                  class="group p-4 rounded-xl border-2 transition-all hover:shadow-md cursor-pointer text-left"
                  :style="{
                    backgroundColor: getGroupInfo(group).colors.bg,
                    borderColor: methodStats[group].active > 0 ? getGroupInfo(group).colors.text : 'transparent'
                  }"
                >
                  <!-- Group Header -->
                  <div class="flex items-center justify-between mb-2">
                    <span
                      class="text-lg font-bold px-2 py-0.5 rounded"
                      :style="{ backgroundColor: getGroupInfo(group).colors.text, color: 'white' }"
                    >
                      {{ group }}
                    </span>
                    <span
                      v-if="getGroupInfo(group).tier !== 'Basic'"
                      class="text-[10px] font-medium px-1.5 py-0.5 rounded"
                      :style="{ backgroundColor: getGroupInfo(group).colors.text, color: 'white' }"
                    >
                      {{ getGroupInfo(group).tier }}
                    </span>
                  </div>

                  <!-- Group Name -->
                  <h4
                    class="font-semibold text-sm mb-2"
                    :style="{ color: getGroupInfo(group).colors.text }"
                  >
                    {{ getGroupInfo(group).name }}
                  </h4>

                  <!-- Stats -->
                  <div class="flex items-center justify-between text-xs">
                    <span :style="{ color: getGroupInfo(group).colors.text }">
                      {{ methodStats[group].total }} Typen
                    </span>
                    <span
                      v-if="methodStats[group].active > 0"
                      class="font-bold px-1.5 py-0.5 rounded"
                      :style="{ backgroundColor: getGroupInfo(group).colors.text, color: 'white' }"
                    >
                      {{ methodStats[group].active }} aktiv
                    </span>
                  </div>

                  <!-- Hover indicator -->
                  <div class="mt-3 text-xs opacity-0 group-hover:opacity-100 transition-opacity" :style="{ color: getGroupInfo(group).colors.text }">
                    Klicken zum Öffnen →
                  </div>
                </button>
              </div>

              <!-- Quick Stats Bar -->
              <div class="flex items-center justify-between p-3 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)]">
                <div class="flex items-center gap-4 text-sm">
                  <span class="text-[var(--color-text-secondary)]">
                    <strong class="text-[var(--color-text-primary)]">{{ methodTypes.length }}</strong> Methodentypen verfügbar
                  </span>
                  <span class="text-[var(--color-text-tertiary)]">|</span>
                  <span class="text-[var(--color-text-secondary)]">
                    <strong class="text-[var(--color-text-primary)]">{{ learningMethods.length }}</strong> in diesem Kapitel
                  </span>
                </div>
                <button
                  @click="openLearningMethodsEditor()"
                  class="text-sm text-[var(--color-primary)] hover:underline flex items-center gap-1"
                >
                  Alle verwalten
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Lessons Tab -->
        <div v-else-if="activeTab === 'lessons'" class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
              Lektionen {{ lessons.length > 0 ? `(${lessons.length})` : '' }}
            </h3>
            <button
              @click="addLesson"
              :disabled="isNewChapter"
              class="px-3 py-1.5 bg-[var(--color-primary)] text-white text-sm rounded-lg hover:bg-[var(--color-primary-hover)] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Neue Lektion
            </button>
          </div>

          <!-- New Module Notice with Create Button -->
          <div v-if="isNewChapter" class="rounded-lg p-4 border flex items-center gap-3" style="background-color: var(--color-info-bg, #eff6ff); border-color: var(--color-info-border, #bfdbfe);">
            <span class="flex-1 text-sm" style="color: var(--color-info-text, #1e40af);">
              ℹ️ Bitte speichern Sie zuerst das Kapitel, bevor Sie Lektionen hinzufügen können.
            </span>
            <button
              @click="saveAndEnableTab"
              :disabled="!form.title.trim() || saveStatus === 'saving'"
              class="px-4 py-2 text-white text-sm font-medium rounded-lg transition-colors whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
              style="background-color: var(--color-primary);"
            >
              {{ saveStatus === 'saving' ? 'Wird gespeichert...' : 'Kapitel erstellen' }}
            </button>
          </div>

          <!-- Loading Lessons -->
          <div v-else-if="loadingLessons" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)] mx-auto"></div>
          </div>

          <!-- Empty State -->
          <div v-else-if="lessons.length === 0" class="text-center py-12">
            <div class="text-5xl mb-3">📚</div>
            <p class="text-[var(--color-text-secondary)] mb-2">Noch keine Lektionen vorhanden</p>
            <p class="text-sm text-[var(--color-text-tertiary)]">Klicken Sie auf "Neue Lektion", um zu beginnen</p>
          </div>

          <!-- Lessons List with Drag & Drop -->
          <div v-else class="space-y-2">
            <div
              v-for="(lesson, index) in sortedLessons"
              :key="lesson.lesson_id"
              :draggable="true"
              @dragstart="handleDragStart(index)"
              @dragover.prevent="handleDragOver(index)"
              @drop="handleDrop(index)"
              @dragend="handleDragEnd"
              :class="[
                'lesson-item p-4 rounded-lg border transition-all cursor-move',
                dragState.draggedIndex === index
                  ? 'opacity-50 border-[var(--color-primary)]'
                  : 'bg-[var(--color-surface)] border-[var(--color-border)] hover:border-[var(--color-primary)]'
              ]"
            >
              <div class="flex items-start justify-between gap-3">
                <!-- Drag Handle -->
                <div class="flex items-center gap-3 flex-1">
                  <svg class="w-5 h-5 text-[var(--color-text-tertiary)] flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M7 2a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 2zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 8zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 14zm6-8a2 2 0 1 0-.001-4.001A2 2 0 0 0 13 6zm0 2a2 2 0 1 0 .001 4.001A2 2 0 0 0 13 8zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 13 14z"></path>
                  </svg>

                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                      <span class="text-sm font-medium text-[var(--color-text-tertiary)]">
                        {{ lesson.order_index }}.
                      </span>
                      <h4 class="font-semibold text-[var(--color-text-primary)] truncate">
                        {{ lesson.title }}
                      </h4>
                      <span v-if="lesson.lesson_type" class="text-xs px-2 py-0.5 bg-[var(--color-primary)]/10 text-[var(--color-primary)] rounded">
                        {{ getLessonTypeLabel(lesson.lesson_type) }}
                      </span>
                    </div>
                    <div class="flex gap-4 text-xs text-[var(--color-text-secondary)]">
                      <span v-if="lesson.duration_minutes">⏱️ {{ lesson.duration_minutes }} Min.</span>
                    </div>
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex gap-2 flex-shrink-0">
                  <button
                    @click="editLesson(lesson)"
                    class="p-1.5 rounded hover:bg-blue-500/10 text-[var(--color-text-secondary)] hover:text-blue-600 transition-colors"
                    :title="t('admin.actions.edit')"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="deleteLesson(lesson.lesson_id)"
                    class="p-1.5 rounded hover:bg-red-500/10 text-[var(--color-text-secondary)] hover:text-red-600 transition-colors"
                    :title="t('admin.actions.delete')"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWindowStore } from '@/application/stores/modules/desktop'
import type { LsxWindow } from '@/application/stores/modules/desktop'
import {
  adminCreateChapter,
  adminUpdateChapter,
  adminGetChapterLessons,
  adminDeleteLesson,
  adminReorderLessons,
  adminGetChapterLearningMethods,
  adminGetLearningMethodTypes,
  type AdminChapter,
  type AdminChapterCreateRequest,
  type AdminChapterUpdateRequest,
  type AdminLesson,
  type AdminLearningMethod,
  type LearningMethodType
} from '@/infrastructure/api/clients/admin'

const { t } = useI18n()

interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const windowStore = useWindowStore()

// State
const chapter = ref<AdminChapter | null>(null)
const lessons = ref<AdminLesson[]>([])
const loading = ref(true)
const loadingLessons = ref(false)
const error = ref<string | null>(null)
const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')
const activeTab = ref<'info' | 'theory' | 'videos' | 'methods' | 'lessons'>('info')
const isGenerating = ref(false)

// C1.2: New state for theory, videos, and learning methods
const theoryContent = ref('')
const videos = ref<Array<{ title: string; url: string }>>([])
const learningMethods = ref<AdminLearningMethod[]>([])
const methodTypes = ref<LearningMethodType[]>([])
const loadingMethods = ref(false)

// Learning method stats per group
interface MethodGroupStats {
  total: number
  active: number
  published: number
}
const methodStats = ref<Record<string, MethodGroupStats>>({
  A: { total: 8, active: 0, published: 0 },
  B: { total: 11, active: 0, published: 0 },
  C: { total: 8, active: 0, published: 0 },
  D: { total: 6, active: 0, published: 0 }
})

// Drag & Drop State
const dragState = ref({
  draggedIndex: null as number | null,
  targetIndex: null as number | null
})

// Form - vereinfacht (nur Titel + Beschreibung)
const form = ref({
  title: '',
  description: ''
})

// Auto-save timeout
let saveTimeout: number | null = null

// Computed
const tabs = computed(() => [
  { id: 'info', label: t('admin.chapters.tabs.info'), icon: '📝' },
  { id: 'theory', label: t('admin.chapters.tabs.theory'), icon: '📄' },
  { id: 'videos', label: t('admin.chapters.tabs.videos'), icon: '🎥' },
  { id: 'methods', label: t('admin.chapters.tabs.methods'), icon: '🎯' },
  { id: 'lessons', label: t('admin.chapters.tabs.lessons'), icon: '📚' }
])

const isNewChapter = computed(() => !props.window.payload?.chapterId)
const courseId = computed(() => props.window.payload?.courseId as string)  // UUID
const courseTitle = computed(() => props.window.payload?.courseTitle as string || 'Unbekannt')
const chapterId = computed(() => props.window.payload?.chapterId as string | undefined)

const sortedLessons = computed(() => {
  return [...lessons.value].sort((a, b) => (a.order_index || 0) - (b.order_index || 0))
})

// Methods
const loadChapter = async () => {
  if (isNewChapter.value) {
    loading.value = false
    return
  }

  if (!chapterId.value) {
    error.value = 'Keine Kapitel-ID angegeben'
    loading.value = false
    return
  }

  loading.value = true
  error.value = null

  try {
    if (props.window.payload?.chapter) {
      chapter.value = props.window.payload.chapter as AdminChapter
      populateForm()
    } else {
      error.value = 'Kapitel-Daten nicht verfügbar'
    }
  } catch (err: any) {
    console.error('Error loading chapter:', err)
    error.value = err.response?.data?.message || 'Fehler beim Laden des Kapitels'
  } finally {
    loading.value = false
  }
}

const loadLessons = async () => {
  if (!chapterId.value) return

  loadingLessons.value = true
  try {
    const data = await adminGetChapterLessons(chapterId.value)
    lessons.value = data
  } catch (err: any) {
    console.error('Error loading lessons:', err)
    // Show error but don't block the UI
    lessons.value = []
  } finally {
    loadingLessons.value = false
  }
}

const populateForm = () => {
  if (!chapter.value) return

  form.value = {
    title: chapter.value.title || '',
    description: chapter.value.description || ''
  }
}

const debouncedSave = () => {
  if (saveTimeout) {
    clearTimeout(saveTimeout)
  }

  saveTimeout = window.setTimeout(() => {
    saveChapter()
  }, 800) // 800ms debounce as per requirements
}

const saveChapter = async () => {
  if (!courseId.value || !form.value.title.trim()) return

  saveStatus.value = 'saving'

  try {
    // Vereinfachte Daten (nur Titel + Beschreibung)
    const data = {
      title: form.value.title.trim(),
      description: form.value.description.trim() || undefined
    }

    if (isNewChapter.value) {
      // Create new chapter
      const newChapter = await adminCreateChapter(courseId.value, data as AdminChapterCreateRequest)
      chapter.value = newChapter

      // Update window payload
      windowStore.updateWindowPayload(props.window.id, {
        chapterId: newChapter.chapter_id,
        chapter: newChapter
      })

      console.log('Kapitel erstellt:', newChapter.chapter_id)
    } else {
      // Update existing chapter
      if (!chapterId.value) return

      const updatedChapter = await adminUpdateChapter(chapterId.value, data as AdminChapterUpdateRequest)
      chapter.value = updatedChapter

      // Update window payload
      windowStore.updateWindowPayload(props.window.id, {
        chapter: updatedChapter
      })

      console.log('Kapitel aktualisiert:', chapterId.value)
    }

    saveStatus.value = 'saved'
    setTimeout(() => { saveStatus.value = 'idle' }, 2000)

    // Notify parent to refresh
    window.dispatchEvent(new CustomEvent('chapter-updated'))
  } catch (err: any) {
    console.error('Fehler beim Speichern:', err)
    saveStatus.value = 'error'
    setTimeout(() => { saveStatus.value = 'idle' }, 3000)
  }
}

// Save module and enable current tab (for use from info boxes)
const saveAndEnableTab = async () => {
  if (!form.value.title.trim()) {
    error.value = t('admin.chapters.errors.titleRequired')
    return
  }

  await saveChapter()

  // After save, if chapterId is now set, load data for current tab
  if (chapterId.value && activeTab.value === 'lessons') {
    loadLessons()
  }
}

const addLesson = () => {
  if (isNewChapter.value || !chapterId.value) {
    error.value = t('admin.chapters.errors.saveFirst')
    return
  }

  windowStore.openWindow({
    type: 'admin-lesson-editor',
    title: t('admin.lessons.createNew'),
    icon: '📄',
    payload: {
      courseId: courseId.value,
      chapterId: chapterId.value,
      lessonId: null,
      lesson: null
    }
  })
}

const editLesson = (lesson: AdminLesson) => {
  windowStore.openWindow({
    type: 'admin-lesson-editor',
    title: `${t('admin.lessons.edit')}: ${lesson.title}`,
    icon: '📄',
    payload: {
      courseId: courseId.value,
      chapterId: chapterId.value,
      lessonId: lesson.lesson_id,
      lesson: lesson
    }
  })
}

const deleteLesson = async (lessonId: string) => {
  if (!confirm(t('admin.lessons.confirmDelete'))) return

  try {
    await adminDeleteLesson(lessonId)
    // Reload lessons
    await loadLessons()
  } catch (err: any) {
    console.error('Error deleting lesson:', err)
    error.value = err.response?.data?.message || t('common.errors.deleteFailed')
  }
}

// Drag & Drop Handlers
const handleDragStart = (index: number) => {
  dragState.value.draggedIndex = index
}

const handleDragOver = (index: number) => {
  dragState.value.targetIndex = index
}

const handleDrop = async (targetIndex: number) => {
  const draggedIndex = dragState.value.draggedIndex
  if (draggedIndex === null || draggedIndex === targetIndex) return

  // Reorder lessons array
  const lessonsCopy = [...lessons.value]
  const [removed] = lessonsCopy.splice(draggedIndex, 1)
  lessonsCopy.splice(targetIndex, 0, removed)

  // Update order_index for all lessons
  lessonsCopy.forEach((lesson, idx) => {
    lesson.order_index = idx + 1
  })

  lessons.value = lessonsCopy

  // Call backend reorder endpoint
  if (chapterId.value) {
    try {
      await adminReorderLessons(chapterId.value, lessonsCopy.map(l => l.lesson_id))
    } catch (err: any) {
      console.error('Error reordering lessons:', err)
      // Reload on error to get correct order
      await loadLessons()
    }
  }

  dragState.value.draggedIndex = null
  dragState.value.targetIndex = null
}

const handleDragEnd = () => {
  dragState.value.draggedIndex = null
  dragState.value.targetIndex = null
}

const getLessonTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    text: '📄 Text',
    video: '🎥 Video',
    quiz: '❓ Quiz',
    interactive: '🎮 Interaktiv',
    exercise: '💪 Übung',
    ai: '🤖 KI',
    exam: '📝 Prüfung'
  }
  return labels[type] || type
}

// C1.2: Video Functions
const addVideo = () => {
  videos.value.push({ title: '', url: '' })
}

const removeVideo = (index: number) => {
  videos.value.splice(index, 1)
}

// D3.4: Load learning methods for statistics
const loadLearningMethodsStats = async () => {
  if (isNewChapter.value || !chapterId.value) return

  loadingMethods.value = true
  try {
    const [methodsResponse, typesData] = await Promise.all([
      adminGetChapterLearningMethods(chapterId.value),
      adminGetLearningMethodTypes()
    ])

    learningMethods.value = methodsResponse.learning_methods
    methodTypes.value = typesData.types

    // Calculate stats per group
    const stats: Record<string, MethodGroupStats> = {
      A: { total: 0, active: 0, published: 0 },
      B: { total: 0, active: 0, published: 0 },
      C: { total: 0, active: 0, published: 0 },
      D: { total: 0, active: 0, published: 0 }
    }

    // Count total types per group
    methodTypes.value.forEach(mt => {
      if (stats[mt.group]) {
        stats[mt.group].total++
      }
    })

    // Count active methods per group (methods in this chapter)
    learningMethods.value.forEach(method => {
      const type = methodTypes.value.find(t => t.lm_id === method.method_type)
      if (type && stats[type.group]) {
        stats[type.group].active++
        if (method.published) {
          stats[type.group].published++
        }
      }
    })

    methodStats.value = stats
  } catch (err) {
    console.error('Error loading learning methods stats:', err)
  } finally {
    loadingMethods.value = false
  }
}

// Helper to get group info
const getGroupInfo = (group: string) => {
  const groupNames: Record<string, string> = {
    A: 'Erklärend',
    B: 'Praxis',
    C: 'Prüfung',
    D: 'Pro'
  }
  const groupColors: Record<string, { bg: string; text: string }> = {
    A: { bg: 'var(--color-info-bg, #dbeafe)', text: 'var(--color-info-text, #1e40af)' },
    B: { bg: 'var(--color-success-bg, #dcfce7)', text: 'var(--color-success-text, #15803d)' },
    C: { bg: 'var(--color-warning-bg, #fef3c7)', text: 'var(--color-warning-text, #92400e)' },
    D: { bg: 'var(--color-premium-bg, #f3e8ff)', text: 'var(--color-premium-text, #6b21a8)' }
  }
  const groupTiers: Record<string, string> = {
    A: 'Basic',
    B: 'Basic',
    C: 'Premium',
    D: 'Pro'
  }
  return {
    name: groupNames[group] || group,
    colors: groupColors[group] || groupColors.A,
    tier: groupTiers[group] || 'Basic'
  }
}

// D3.4: Open Learning Methods Editor Window (with optional group filter)
const openLearningMethodsEditor = (preSelectedGroup?: string) => {
  if (isNewChapter.value || !chapterId.value) {
    error.value = t('admin.chapters.errors.saveFirst')
    return
  }

  windowStore.openWindow({
    type: 'admin-learning-method-editor',
    title: `${t('admin.methods.title')}: ${form.value.title || t('admin.chapters.chapter')}`,
    icon: '🎯',
    payload: {
      courseId: courseId.value,
      courseTitle: courseTitle.value,
      chapterId: chapterId.value,
      chapterTitle: form.value.title,
      preSelectedGroup
    },
    preferredPosition: { x: 150, y: 50 },
    size: { width: 750, height: 600 }
  })
}

// Watch for tab changes
watch(activeTab, (newTab) => {
  if (newTab === 'lessons' && !isNewChapter.value && lessons.value.length === 0) {
    loadLessons()
  }
  if (newTab === 'methods' && !isNewChapter.value && learningMethods.value.length === 0) {
    loadLearningMethodsStats()
  }
})

// Listen for lesson updates from child windows
const handleLessonUpdate = () => {
  if (activeTab.value === 'lessons' && !isNewChapter.value) {
    loadLessons()
  }
}

// KI-Generator Functions
const openAIKapitelGenerator = () => {
  windowStore.openWindow({
    type: 'admin-ai-kapitel-generator',
    title: 'KI-Kapitel-Generator',
    icon: '✨',
    payload: {
      courseId: courseId.value,
      chapterId: chapterId.value,
      onGenerate: handleAIResult
    }
  })
}

const handleAIResult = (result: { title?: string; description?: string; estimatedDuration?: number }) => {
  if (result.title) {
    form.value.title = result.title
  }
  if (result.description) {
    form.value.description = result.description
  }
  if (result.estimatedDuration) {
    form.value.duration_minutes = result.estimatedDuration
  }
  // Trigger auto-save
  debouncedSave()
}

// Lifecycle
onMounted(() => {
  loadChapter()

  // Register custom event listener for lesson updates
  window.addEventListener('lesson-updated', handleLessonUpdate)
})

// Cleanup
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('lesson-updated', handleLessonUpdate)
})
</script>

<style scoped>
.lesson-item {
  user-select: none;
}

.lesson-item:hover {
  cursor: grab;
}

.lesson-item:active {
  cursor: grabbing;
}
</style>
