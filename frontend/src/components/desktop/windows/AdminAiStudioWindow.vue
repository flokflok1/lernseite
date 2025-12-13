<!--
  Admin AI Studio Window - Split-View Layout

  KI-Authoring-Studio für die Erstellung und Bearbeitung von Kursinhalten.
  Chat-basierter Workflow mit Kurs-Kontext auf der linken Seite.

  Phase: D4 - KI-Authoring-Studio (Rebuild)
  Created: 2025-12-02
  Updated: 2025-12-03 (Split-View Redesign)
-->

<template>
  <div class="admin-ai-studio h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)]">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <h2 class="text-sm font-semibold text-[var(--color-text-primary)]">
            KI-Authoring-Studio
          </h2>
          <p class="text-xs text-[var(--color-text-secondary)]">
            {{ selectedCourse?.title || 'Kurs auswählen' }}
          </p>
        </div>
      </div>

      <!-- Session Mode Badge -->
      <div v-if="session" class="flex items-center gap-2">
        <span
          class="px-2 py-1 text-xs font-medium rounded-full"
          :class="session.mode === 'new_chapters'
            ? 'bg-green-100 text-green-700'
            : 'bg-blue-100 text-blue-700'"
        >
          {{ session.mode === 'new_chapters' ? 'Neue Kapitel' : 'Bearbeiten' }}
        </span>
      </div>
    </div>

    <!-- Main Content: Split View -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Left Panel: Kurs-Kontext -->
      <div
        class="flex flex-col border-r border-[var(--color-border)] bg-[var(--color-surface-secondary)]"
        :style="{ width: leftPanelWidth + 'px' }"
      >
        <!-- Course Selector -->
        <div class="p-3 border-b border-[var(--color-border)]">
          <select
            v-model="selectedCourseId"
            @change="onCourseChange"
            class="w-full px-3 py-2 text-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-primary)]"
          >
            <option value="">Kurs auswählen...</option>
            <option
              v-for="course in courses"
              :key="course.course_id"
              :value="course.course_id"
            >
              {{ course.title }}
            </option>
          </select>
        </div>

        <!-- Tabs -->
        <div class="flex border-b border-[var(--color-border)]">
          <button
            @click="activeTab = 'chapters'"
            class="flex-1 px-4 py-2.5 text-xs font-medium transition-colors relative"
            :class="activeTab === 'chapters'
              ? 'text-[var(--color-primary)]'
              : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'"
          >
            Kapitel
            <div
              v-if="activeTab === 'chapters'"
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--color-primary)]"
            ></div>
          </button>
          <button
            @click="activeTab = 'files'"
            class="flex-1 px-4 py-2.5 text-xs font-medium transition-colors relative"
            :class="activeTab === 'files'
              ? 'text-[var(--color-primary)]'
              : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'"
          >
            Dateien
            <span
              v-if="selectedFileIds.length > 0"
              class="ml-1 px-1.5 py-0.5 text-[10px] bg-[var(--color-primary)] text-white rounded-full"
            >
              {{ selectedFileIds.length }}
            </span>
            <div
              v-if="activeTab === 'files'"
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--color-primary)]"
            ></div>
          </button>
        </div>

        <!-- Tab Content -->
        <div class="flex-1 overflow-y-auto">
          <!-- Chapters Tab -->
          <div v-if="activeTab === 'chapters'" class="p-2 space-y-1">
            <div v-if="!selectedCourseId" class="p-4 text-center text-sm text-[var(--color-text-tertiary)]">
              Bitte wähle einen Kurs aus
            </div>
            <div v-else-if="chapters.length === 0" class="p-4 text-center text-sm text-[var(--color-text-tertiary)]">
              Keine Kapitel vorhanden
            </div>
            <template v-else>
              <div
                v-for="chapter in chapters"
                :key="chapter.chapter_id"
                class="rounded-lg border transition-colors"
                :class="selectedChapterId === chapter.chapter_id
                  ? 'bg-[var(--color-primary-subtle)] border-[var(--color-primary)]'
                  : 'border-transparent hover:bg-[var(--color-surface)]'"
              >
                <!-- Chapter Header (klickbar) -->
                <button
                  @click="toggleChapter(chapter)"
                  class="w-full p-2.5 text-left"
                >
                  <div class="flex items-start gap-2">
                    <!-- Expand/Collapse Icon -->
                    <svg
                      class="w-4 h-4 mt-0.5 text-[var(--color-text-tertiary)] transition-transform"
                      :class="expandedChapterId === chapter.chapter_id ? 'rotate-90' : ''"
                      fill="none" stroke="currentColor" viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                    <span class="text-xs text-[var(--color-text-tertiary)] font-mono mt-0.5">
                      {{ chapter.order_index + 1 }}.
                    </span>
                    <div class="flex-1 min-w-0">
                      <div class="text-sm font-medium text-[var(--color-text-primary)] truncate">
                        {{ chapter.title }}
                      </div>
                      <div class="text-xs text-[var(--color-text-secondary)] mt-0.5">
                        {{ chapter.lesson_count || 0 }} Lektionen
                      </div>
                    </div>
                  </div>
                </button>

                <!-- Lessons List (aufklappbar) -->
                <div
                  v-if="expandedChapterId === chapter.chapter_id"
                  class="pb-2 px-2"
                >
                  <div v-if="lessonsLoading" class="py-2 text-center text-xs text-[var(--color-text-tertiary)]">
                    Lade Lektionen...
                  </div>
                  <div v-else-if="lessons.length === 0" class="py-2 text-center text-xs text-[var(--color-text-tertiary)]">
                    Keine Lektionen
                  </div>
                  <template v-else>
                    <button
                      v-for="lesson in lessons"
                      :key="lesson.lesson_id"
                      @click.stop="selectLesson(lesson)"
                      class="w-full p-2 pl-8 rounded text-left text-xs transition-colors"
                      :class="selectedLessonId === lesson.lesson_id
                        ? 'bg-[var(--color-primary)] text-white'
                        : 'hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)]'"
                    >
                      <div class="flex items-center gap-2">
                        <span class="font-mono opacity-60">{{ lesson.order_index + 1 }}.</span>
                        <span class="flex-1 truncate">{{ lesson.title }}</span>
                        <span
                          v-if="lesson.content?.lm_primary"
                          class="px-1.5 py-0.5 rounded text-[10px] font-medium"
                          :class="selectedLessonId === lesson.lesson_id
                            ? 'bg-white/20 text-white'
                            : 'bg-[var(--color-primary-subtle)] text-[var(--color-primary)]'"
                        >
                          {{ lesson.content.lm_primary }}
                        </span>
                        <span
                          v-if="lesson.content?.pruefungs_relevanz === 'SEHR HOCH'"
                          class="text-red-500"
                          title="Sehr hohe Prüfungsrelevanz"
                        >!</span>
                      </div>
                    </button>

                    <!-- Batch Generate Button -->
                    <button
                      v-if="lessons.length > 0 && !isBatchGenerating"
                      @click.stop="startBatchGeneration(chapter)"
                      class="w-full mt-2 p-2 rounded-lg text-xs font-medium bg-gradient-to-r from-violet-500 to-purple-600 text-white hover:from-violet-600 hover:to-purple-700 transition-all flex items-center justify-center gap-2"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Kapitel komplett generieren ({{ lessons.length }})
                    </button>

                    <!-- Batch Progress -->
                    <div
                      v-if="isBatchGenerating && expandedChapterId === chapter.chapter_id"
                      class="mt-2 p-2 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)]"
                    >
                      <div class="flex items-center justify-between text-xs mb-1">
                        <span class="text-[var(--color-text-secondary)]">Generiere...</span>
                        <span class="font-mono text-[var(--color-primary)]">{{ batchProgress }}/{{ batchTotal }}</span>
                      </div>
                      <div class="w-full h-2 bg-[var(--color-border)] rounded-full overflow-hidden">
                        <div
                          class="h-full bg-gradient-to-r from-violet-500 to-purple-600 transition-all duration-300"
                          :style="{ width: `${(batchProgress / batchTotal) * 100}%` }"
                        ></div>
                      </div>
                      <div class="mt-1 text-[10px] text-[var(--color-text-tertiary)] truncate">
                        {{ batchCurrentLesson }}
                      </div>
                    </div>
                  </template>
                </div>
              </div>
            </template>

            <!-- Add New Chapter Button -->
            <button
              v-if="selectedCourseId"
              @click="startNewChapterMode"
              class="w-full p-2.5 rounded-lg text-left border border-dashed border-[var(--color-border)] hover:border-[var(--color-primary)] hover:bg-[var(--color-primary-subtle)] transition-colors group"
            >
              <div class="flex items-center gap-2 text-[var(--color-text-secondary)] group-hover:text-[var(--color-primary)]">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                <span class="text-sm font-medium">Neues Kapitel mit KI</span>
              </div>
            </button>
          </div>

          <!-- Files Tab -->
          <div v-if="activeTab === 'files'" class="p-2 space-y-1">
            <div v-if="!selectedCourseId" class="p-4 text-center text-sm text-[var(--color-text-tertiary)]">
              Bitte wähle einen Kurs aus
            </div>
            <div v-else-if="files.length === 0" class="p-4 text-center text-sm text-[var(--color-text-tertiary)]">
              Keine Dateien vorhanden
            </div>
            <template v-else>
              <label
                v-for="file in files"
                :key="file.course_file_id"
                class="flex items-center gap-3 p-2.5 rounded-lg cursor-pointer transition-colors"
                :class="selectedFileIds.includes(file.course_file_id)
                  ? 'bg-[var(--color-primary-subtle)]'
                  : 'hover:bg-[var(--color-surface)]'"
              >
                <input
                  type="checkbox"
                  :checked="selectedFileIds.includes(file.course_file_id)"
                  @change="toggleFileSelection(file.course_file_id)"
                  class="w-4 h-4 rounded border-[var(--color-border)] text-[var(--color-primary)]"
                />
                <div class="flex-1 min-w-0">
                  <div class="text-sm text-[var(--color-text-primary)] truncate">
                    {{ file.display_name || file.file_name || file.original_filename || 'Unbenannt' }}
                  </div>
                  <div class="text-xs text-[var(--color-text-tertiary)]">
                    {{ formatFileSize(file.file_size_bytes) }}
                  </div>
                </div>
                <span class="text-lg">{{ getFileIcon(file.mime_type) }}</span>
              </label>
            </template>
          </div>
        </div>
      </div>

      <!-- Resize Handle -->
      <div
        class="w-1 cursor-col-resize bg-[var(--color-border)] hover:bg-[var(--color-primary)] transition-colors"
        @mousedown="startResize"
      ></div>

      <!-- Right Panel: Chat Interface -->
      <div class="flex-1 flex flex-col min-w-0">
        <!-- Context Bar -->
        <div
          v-if="hasContext"
          class="px-4 py-2 border-b border-[var(--color-border)] bg-[var(--color-surface-secondary)]"
        >
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-xs text-[var(--color-text-tertiary)]">Kontext:</span>

            <!-- Selected Chapter -->
            <span
              v-if="selectedChapter"
              class="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              {{ selectedChapter.title }}
              <button @click="clearChapterSelection" class="hover:text-blue-900">×</button>
            </span>

            <!-- Selected Lesson -->
            <span
              v-if="selectedLesson"
              class="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {{ selectedLesson.title }}
              <span v-if="selectedLesson.content?.lm_primary" class="font-medium">
                ({{ selectedLesson.content.lm_primary }})
              </span>
              <button @click="selectedLessonId = null" class="hover:text-green-900">×</button>
            </span>

            <!-- Selected Files Count -->
            <span
              v-if="selectedFileIds.length > 0"
              class="inline-flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              {{ selectedFileIds.length }} Datei(en)
              <button @click="clearFileSelection" class="hover:text-purple-900">×</button>
            </span>

            <!-- Mode Badge -->
            <span
              v-if="session"
              class="inline-flex items-center gap-1 px-2 py-1 text-xs rounded-full"
              :class="session.mode === 'new_chapters'
                ? 'bg-green-100 text-green-700'
                : 'bg-amber-100 text-amber-700'"
            >
              {{ session.mode === 'new_chapters' ? '+ Neue Kapitel' : '✏️ Bearbeiten' }}
            </span>
          </div>
        </div>

        <!-- Chat Messages Area -->
        <div
          ref="chatContainer"
          class="flex-1 overflow-y-auto p-4 space-y-4"
        >
          <!-- Welcome Message -->
          <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center">
            <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center mb-4">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
              Willkommen im KI-Authoring-Studio
            </h3>
            <p class="text-sm text-[var(--color-text-secondary)] max-w-md mb-6">
              Wähle links einen Kurs und Dateien aus, um Kapitel und Lektionen mit KI zu erstellen oder zu bearbeiten.
            </p>

            <!-- Quick Actions -->
            <div class="flex flex-wrap gap-2 justify-center">
              <button
                @click="sendQuickAction('Was kann ich mit dem KI-Studio machen?')"
                class="px-3 py-1.5 text-xs font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded-full hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] transition-colors"
              >
                Was kann ich hier machen?
              </button>
              <button
                v-if="selectedCourseId && selectedFileIds.length > 0"
                @click="sendQuickAction('Analysiere die ausgewählten Dateien und schlage eine Kapitelstruktur vor.')"
                class="px-3 py-1.5 text-xs font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded-full hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] transition-colors"
              >
                Kapitelstruktur vorschlagen
              </button>
            </div>
          </div>

          <!-- Messages -->
          <template v-else>
            <div
              v-for="message in messages"
              :key="message.id"
              class="flex gap-3"
              :class="message.role === 'user' ? 'flex-row-reverse' : ''"
            >
              <!-- Avatar -->
              <div
                class="w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center"
                :class="message.role === 'user'
                  ? 'bg-[var(--color-primary)]'
                  : 'bg-gradient-to-br from-violet-500 to-purple-600'"
              >
                <svg v-if="message.role === 'user'" class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <svg v-else class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>

              <!-- Message Content -->
              <div
                class="max-w-[80%] rounded-xl px-4 py-3"
                :class="message.role === 'user'
                  ? 'bg-[var(--color-primary)] text-white'
                  : 'bg-[var(--color-surface)] border border-[var(--color-border)]'"
              >
                <div
                  class="text-sm whitespace-pre-wrap"
                  :class="message.role === 'user' ? 'text-white' : 'text-[var(--color-text-primary)]'"
                  v-html="formatMessage(message.content)"
                ></div>

                <!-- Actions from AI -->
                <div v-if="message.actions && message.actions.length > 0" class="mt-3 flex flex-wrap gap-2">
                  <button
                    v-for="action in message.actions"
                    :key="action.id"
                    @click="executeAction(action)"
                    class="px-3 py-1.5 text-xs font-medium rounded-lg transition-colors"
                    :class="action.type === 'primary'
                      ? 'bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)]'
                      : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] hover:bg-[var(--color-border)]'"
                  >
                    {{ action.label }}
                  </button>
                </div>

                <!-- Timestamp -->
                <div
                  class="text-[10px] mt-1"
                  :class="message.role === 'user' ? 'text-white/60' : 'text-[var(--color-text-tertiary)]'"
                >
                  {{ formatTime(message.timestamp) }}
                </div>
              </div>
            </div>

            <!-- Typing Indicator -->
            <div v-if="isTyping" class="flex gap-3">
              <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl px-4 py-3">
                <div class="flex gap-1">
                  <span class="w-2 h-2 bg-[var(--color-text-tertiary)] rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                  <span class="w-2 h-2 bg-[var(--color-text-tertiary)] rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                  <span class="w-2 h-2 bg-[var(--color-text-tertiary)] rounded-full animate-bounce" style="animation-delay: 300ms"></span>
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- Input Area -->
        <div class="p-4 border-t border-[var(--color-border)] bg-[var(--color-surface-secondary)]">
          <!-- Quick Actions Bar -->
          <div class="flex items-center gap-2 mb-3">
            <button
              @click="openActionMenu"
              class="p-2 rounded-lg hover:bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
              title="Aktionen"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </button>

            <div class="flex-1 flex gap-2 overflow-x-auto pb-1">
              <button
                v-if="selectedCourseId && selectedFileIds.length > 0"
                @click="sendQuickAction('Erstelle ein neues Kapitel basierend auf den ausgewählten Dateien.')"
                class="flex-shrink-0 px-3 py-1.5 text-xs font-medium bg-green-100 text-green-700 rounded-full hover:bg-green-200 transition-colors"
              >
                + Kapitel erstellen
              </button>
              <button
                v-if="selectedChapterId"
                @click="sendQuickAction('Erstelle Lektionen für das ausgewählte Kapitel.')"
                class="flex-shrink-0 px-3 py-1.5 text-xs font-medium bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
              >
                + Lektionen erstellen
              </button>
              <button
                v-if="selectedChapterId"
                @click="sendQuickAction('Erstelle Lernmethoden für das ausgewählte Kapitel.')"
                class="flex-shrink-0 px-3 py-1.5 text-xs font-medium bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200 transition-colors"
              >
                + Lernmethoden
              </button>
            </div>
          </div>

          <!-- Text Input -->
          <div class="flex gap-2">
            <textarea
              ref="inputRef"
              v-model="inputMessage"
              @keydown.enter.exact="handleEnter"
              @keydown.shift.enter.prevent="inputMessage += '\n'"
              rows="1"
              class="flex-1 px-4 py-2.5 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl text-sm text-[var(--color-text-primary)] placeholder-[var(--color-text-tertiary)] resize-none focus:outline-none focus:border-[var(--color-primary)] transition-colors"
              placeholder="Nachricht eingeben... (Enter zum Senden)"
              :disabled="isTyping"
            ></textarea>
            <button
              @click="sendMessage"
              :disabled="!inputMessage.trim() || isTyping"
              class="px-4 py-2.5 bg-[var(--color-primary)] text-white rounded-xl hover:bg-[var(--color-primary-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Menu Modal -->
    <div
      v-if="showActionMenu"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="showActionMenu = false"
    >
      <div class="bg-[var(--color-bg)] rounded-xl shadow-xl w-80 max-h-[60vh] overflow-hidden">
        <div class="p-4 border-b border-[var(--color-border)]">
          <h3 class="font-semibold text-[var(--color-text-primary)]">KI-Aktionen</h3>
        </div>
        <div class="p-2 max-h-80 overflow-y-auto">
          <button
            v-for="action in availableActions"
            :key="action.id"
            @click="selectAction(action)"
            class="w-full p-3 rounded-lg text-left hover:bg-[var(--color-surface)] transition-colors"
          >
            <div class="flex items-center gap-3">
              <span class="text-xl">{{ action.icon }}</span>
              <div>
                <div class="text-sm font-medium text-[var(--color-text-primary)]">
                  {{ action.label }}
                </div>
                <div class="text-xs text-[var(--color-text-secondary)]">
                  {{ action.description }}
                </div>
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import type { LsxWindow } from '@/store/window.store'
import { useWindowStore } from '@/store/window.store'

// ============================================================================
// Types
// ============================================================================

interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  actions?: ChatAction[]
}

interface ChatAction {
  id: string
  type: 'primary' | 'secondary'
  label: string
  action: string
  payload?: Record<string, unknown>
}

interface AiStudioSession {
  id: string
  course_id: string
  mode: 'new_chapters' | 'edit_existing'
  source_file_ids: string[]
  current_chapter_id?: string
  created_at: string
  updated_at: string
}

interface Course {
  course_id: string
  title: string
  description?: string
}

interface Chapter {
  chapter_id: string
  course_id: string
  title: string
  description?: string
  order_index: number
  lesson_count?: number
}

interface Lesson {
  lesson_id: string
  chapter_id: string
  title: string
  lesson_type: string
  content: {
    lm_primary?: string
    lm_secondary?: string | null
    topic?: string
    pruefungs_relevanz?: string
  } | null
  order_index: number
  published: boolean
}

interface CourseFile {
  course_file_id: string
  file_id: string | null
  course_id: string
  file_name: string
  display_name: string | null
  original_filename?: string
  file_size_bytes: number | null
  mime_type: string | null
  created_at: string
}

interface QuickAction {
  id: string
  icon: string
  label: string
  description: string
  prompt: string
  requiresCourse?: boolean
  requiresFiles?: boolean
  requiresChapter?: boolean
}

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()
const emit = defineEmits<{ (e: 'close'): void }>()

// ============================================================================
// State
// ============================================================================

const windowStore = useWindowStore()

// Layout
const leftPanelWidth = ref(280)
const isResizing = ref(false)

// Tabs
const activeTab = ref<'chapters' | 'files'>('chapters')

// Course & Data
const courses = ref<Course[]>([])
const selectedCourseId = ref<string>('')
const selectedCourse = computed(() => courses.value.find(c => c.course_id === selectedCourseId.value))

// Chapters
const chapters = ref<Chapter[]>([])
const selectedChapterId = ref<string | null>(null)
const selectedChapter = computed(() => chapters.value.find(c => c.chapter_id === selectedChapterId.value))
const expandedChapterId = ref<string | null>(null)

// Lessons
const lessons = ref<Lesson[]>([])
const lessonsLoading = ref(false)
const selectedLessonId = ref<string | null>(null)
const selectedLesson = computed(() => lessons.value.find(l => l.lesson_id === selectedLessonId.value))

// Batch Generation
const isBatchGenerating = ref(false)
const batchProgress = ref(0)
const batchTotal = ref(0)
const batchCurrentLesson = ref<string>('')

// Files
const files = ref<CourseFile[]>([])
const selectedFileIds = ref<string[]>([])

// Session
const session = ref<AiStudioSession | null>(null)

// Chat
const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const isTyping = ref(false)
const chatContainer = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)

// Action Menu
const showActionMenu = ref(false)

// ============================================================================
// Computed
// ============================================================================

const hasContext = computed(() => {
  return selectedChapterId.value || selectedLessonId.value || selectedFileIds.value.length > 0 || session.value
})

const availableActions = computed<QuickAction[]>(() => {
  const actions: QuickAction[] = [
    {
      id: 'analyze-files',
      icon: '🔍',
      label: 'Dateien analysieren',
      description: 'Analysiere ausgewählte Dateien und extrahiere Inhalte',
      prompt: 'Analysiere die ausgewählten Dateien und fasse die wichtigsten Themen zusammen.',
      requiresCourse: true,
      requiresFiles: true
    },
    {
      id: 'suggest-structure',
      icon: '📋',
      label: 'Struktur vorschlagen',
      description: 'Schlage eine Kapitel- und Lektionsstruktur vor',
      prompt: 'Basierend auf den Dateien, schlage eine Kapitelstruktur für den Kurs vor.',
      requiresCourse: true,
      requiresFiles: true
    },
    {
      id: 'create-chapter',
      icon: '📖',
      label: 'Kapitel erstellen',
      description: 'Erstelle ein neues Kapitel mit KI-Unterstützung',
      prompt: 'Erstelle ein neues Kapitel basierend auf den ausgewählten Dateien.',
      requiresCourse: true,
      requiresFiles: true
    },
    {
      id: 'create-lessons',
      icon: '📝',
      label: 'Lektionen erstellen',
      description: 'Erstelle Lektionen für das ausgewählte Kapitel',
      prompt: 'Erstelle Lektionen für das ausgewählte Kapitel.',
      requiresChapter: true
    },
    {
      id: 'create-methods',
      icon: '🎯',
      label: 'Lernmethoden erstellen',
      description: 'Generiere Lernmethoden für Lektionen',
      prompt: 'Erstelle passende Lernmethoden für das ausgewählte Kapitel.',
      requiresChapter: true
    },
    {
      id: 'improve-content',
      icon: '✨',
      label: 'Inhalt verbessern',
      description: 'Verbessere bestehende Inhalte mit KI',
      prompt: 'Verbessere den Inhalt des ausgewählten Kapitels.',
      requiresChapter: true
    }
  ]

  return actions.filter(action => {
    if (action.requiresCourse && !selectedCourseId.value) return false
    if (action.requiresFiles && selectedFileIds.value.length === 0) return false
    if (action.requiresChapter && !selectedChapterId.value) return false
    return true
  })
})

// ============================================================================
// Methods: Layout
// ============================================================================

function startResize(e: MouseEvent) {
  isResizing.value = true
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
}

function handleResize(e: MouseEvent) {
  if (!isResizing.value) return
  const newWidth = e.clientX - 8 // Account for window position
  leftPanelWidth.value = Math.max(200, Math.min(400, newWidth))
}

function stopResize() {
  isResizing.value = false
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
}

// ============================================================================
// Methods: Data Loading
// ============================================================================

async function loadCourses() {
  try {
    // Use admin endpoint to get all courses for admin users
    const response = await fetch('/api/v1/admin/courses', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      courses.value = data.data?.courses || data.courses || []
    }
  } catch (error) {
    console.error('Failed to load courses:', error)
  }
}

async function loadChapters(courseId: string) {
  try {
    // Use admin endpoint for chapters (supports UUID)
    const response = await fetch(`/api/v1/admin/courses/${courseId}/chapters`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      chapters.value = data.data?.chapters || data.chapters || []
    }
  } catch (error) {
    console.error('Failed to load chapters:', error)
    chapters.value = []
  }
}

async function loadFiles(courseId: string) {
  try {
    // Use admin endpoint for course files
    const response = await fetch(`/api/v1/admin/courses/${courseId}/files`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      files.value = data.data?.files || data.files || []
    }
  } catch (error) {
    console.error('Failed to load files:', error)
    files.value = []
  }
}

// ============================================================================
// Methods: Selection
// ============================================================================

function onCourseChange() {
  // Reset selections
  selectedChapterId.value = null
  selectedFileIds.value = []
  chapters.value = []
  files.value = []

  if (selectedCourseId.value) {
    loadChapters(selectedCourseId.value)
    loadFiles(selectedCourseId.value)

    // Create or update session
    createSession('new_chapters')
  } else {
    session.value = null
  }
}

function selectChapter(chapter: Chapter) {
  selectedChapterId.value = chapter.chapter_id

  // Switch to edit mode when selecting existing chapter
  if (session.value) {
    session.value.mode = 'edit_existing'
    session.value.current_chapter_id = chapter.chapter_id
  }
}

function toggleChapter(chapter: Chapter) {
  // Toggle expand/collapse
  if (expandedChapterId.value === chapter.chapter_id) {
    // Collapse
    expandedChapterId.value = null
    lessons.value = []
    selectedLessonId.value = null
  } else {
    // Expand and load lessons
    expandedChapterId.value = chapter.chapter_id
    selectedChapterId.value = chapter.chapter_id
    loadLessons(chapter.chapter_id)

    // Update session
    if (session.value) {
      session.value.mode = 'edit_existing'
      session.value.current_chapter_id = chapter.chapter_id
    }
  }
}

async function loadLessons(chapterId: string) {
  lessonsLoading.value = true
  try {
    const response = await fetch(`/api/v1/admin/chapters/${chapterId}/lessons`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      lessons.value = data.data?.lessons || data.lessons || []
    }
  } catch (error) {
    console.error('Failed to load lessons:', error)
    lessons.value = []
  } finally {
    lessonsLoading.value = false
  }
}

function selectLesson(lesson: Lesson) {
  selectedLessonId.value = lesson.lesson_id

  // Send context to chat
  const lmType = lesson.content?.lm_primary || 'LM00'
  const topic = lesson.content?.topic || lesson.title
  const relevanz = lesson.content?.pruefungs_relevanz || 'mittel'

  // Get LM-specific label and description
  const lmInfo = getLmInfo(lmType)

  // Auto-prompt for this lesson
  const prompt = `**${lesson.title}**

📚 **Lernmethode:** ${lmType} (${lmInfo.name})
📝 **Thema:** ${topic}
⭐ **Prüfungsrelevanz:** ${relevanz}

${lmInfo.description}`

  // Build context-aware actions
  const actions: ChatAction[] = [
    { id: 'gen-lm', type: 'primary', label: lmInfo.actionLabel, action: 'generate_lm', payload: { lesson_id: lesson.lesson_id, lm_type: lmType } }
  ]

  // Add secondary action only if it makes sense
  if (lmType !== 'LM00' && lmType !== 'LM25') {
    actions.push({ id: 'gen-theory', type: 'secondary', label: 'Zusätzlich Theorie (LM00)', action: 'generate_theory', payload: { lesson_id: lesson.lesson_id } })
  }
  if (lmType !== 'LM22' && lmType !== 'LM25') {
    actions.push({ id: 'gen-quiz', type: 'secondary', label: 'Quiz hinzufügen (LM22)', action: 'generate_quiz', payload: { lesson_id: lesson.lesson_id } })
  }

  const systemMessage: ChatMessage = {
    id: `msg-${Date.now()}`,
    role: 'assistant',
    content: prompt,
    timestamp: new Date().toISOString(),
    actions
  }
  messages.value.push(systemMessage)
  scrollToBottom()
}

function getLmInfo(lmType: string): { name: string; description: string; actionLabel: string } {
  const lmMap: Record<string, { name: string; description: string; actionLabel: string }> = {
    'LM00': { name: 'Tiefe Erklärung', description: 'Erstellt ein ausführliches Theorieblatt mit Erklärungen, Beispielen und Merksätzen.', actionLabel: '📖 Theorieblatt erstellen' },
    'LM09': { name: 'Code Sandbox', description: 'Erstellt interaktive Code-Übungen mit SQL oder Programmierung.', actionLabel: '💻 Code-Übung erstellen' },
    'LM10': { name: 'Netzwerk-Simulation', description: 'Erstellt eine visuelle Netzwerk-Übung mit Drag&Drop.', actionLabel: '🌐 Netzwerk-Simulation erstellen' },
    'LM11': { name: 'IT-Szenario', description: 'Erstellt eine Szenario-basierte Übung (z.B. Schutzbedarfsanalyse).', actionLabel: '🎯 Szenario-Übung erstellen' },
    'LM12': { name: 'Mathe-Interaktiv', description: 'Erstellt schrittweise Rechenaufgaben mit sofortigem Feedback.', actionLabel: '🔢 Mathe-Aufgaben erstellen' },
    'LM13': { name: 'Flashcards', description: 'Erstellt Karteikarten zum Lernen von Begriffen und Definitionen.', actionLabel: '🃏 Karteikarten erstellen' },
    'LM14': { name: 'Drag & Drop', description: 'Erstellt Zuordnungsaufgaben mit Drag&Drop-Elementen.', actionLabel: '🔀 Drag&Drop Übung erstellen' },
    'LM16': { name: 'Fehleranalyse', description: 'Erstellt Übungen zum Finden und Korrigieren von Fehlern in Code/SQL.', actionLabel: '🔍 Fehleranalyse erstellen' },
    'LM19': { name: 'IHK-Stil Aufgaben', description: 'Erstellt Aufgaben im Original-IHK-Prüfungsformat.', actionLabel: '📋 IHK-Aufgabe erstellen' },
    'LM21': { name: 'Zeitlimit-Training', description: 'Erstellt zeitgebundene Übungen zur Prüfungsvorbereitung.', actionLabel: '⏱️ Zeitlimit-Training erstellen' },
    'LM22': { name: 'Quiz', description: 'Erstellt Multiple-Choice und andere Quiz-Fragen.', actionLabel: '❓ Quiz erstellen' },
    'LM25': { name: 'Kapitel-Endprüfung', description: 'Erstellt eine umfassende Prüfung für das gesamte Kapitel.', actionLabel: '📝 Kapitelprüfung erstellen' }
  }

  return lmMap[lmType] || { name: lmType, description: 'Erstellt Content für diese Lernmethode.', actionLabel: `${lmType} Content erstellen` }
}

function clearChapterSelection() {
  selectedChapterId.value = null
  expandedChapterId.value = null
  lessons.value = []
  selectedLessonId.value = null
  if (session.value) {
    session.value.current_chapter_id = undefined
    session.value.mode = 'new_chapters'
  }
}

// ============================================================================
// Methods: Batch Generation
// ============================================================================

async function startBatchGeneration(chapter: Chapter) {
  if (isBatchGenerating.value || lessons.value.length === 0) return

  isBatchGenerating.value = true
  batchTotal.value = lessons.value.length
  batchProgress.value = 0

  // Add start message to chat
  const startMessage: ChatMessage = {
    id: `msg-${Date.now()}`,
    role: 'assistant',
    content: `**Batch-Generierung gestartet**\n\nGeneriere Content für **${chapter.title}** (${lessons.value.length} Lektionen)...\n\nDas kann je nach Anzahl der Lektionen einige Minuten dauern.`,
    timestamp: new Date().toISOString()
  }
  messages.value.push(startMessage)
  scrollToBottom()

  const results: { lesson: string; success: boolean; error?: string }[] = []

  // Process each lesson sequentially
  for (let i = 0; i < lessons.value.length; i++) {
    const lesson = lessons.value[i]
    batchCurrentLesson.value = lesson.title
    batchProgress.value = i

    try {
      const lmType = lesson.content?.lm_primary || 'LM00'
      const topic = lesson.content?.topic || lesson.title

      // Call the API to generate content for this lesson
      const response = await fetch('/api/v1/admin/ai-studio/generate-lm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          lesson_id: lesson.lesson_id,
          lm_type: lmType,
          topic: topic,
          course_id: selectedCourseId.value,
          chapter_id: chapter.chapter_id,
          context: {
            pruefungs_relevanz: lesson.content?.pruefungs_relevanz,
            dauer_min: lesson.content?.dauer_min
          }
        })
      })

      if (response.ok) {
        results.push({ lesson: lesson.title, success: true })
      } else {
        const errorData = await response.json().catch(() => ({}))
        results.push({ lesson: lesson.title, success: false, error: errorData.error?.message || `HTTP ${response.status}` })
      }
    } catch (error) {
      results.push({ lesson: lesson.title, success: false, error: String(error) })
    }

    // Small delay between requests to avoid rate limiting
    if (i < lessons.value.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 500))
    }
  }

  batchProgress.value = batchTotal.value
  isBatchGenerating.value = false
  batchCurrentLesson.value = ''

  // Generate summary message
  const successCount = results.filter(r => r.success).length
  const failedResults = results.filter(r => !r.success)

  let summaryContent = `**Batch-Generierung abgeschlossen**\n\n`
  summaryContent += `✅ **${successCount}/${results.length}** Lektionen erfolgreich generiert\n\n`

  if (failedResults.length > 0) {
    summaryContent += `⚠️ **Fehler bei ${failedResults.length} Lektion(en):**\n`
    failedResults.forEach(r => {
      summaryContent += `- ${r.lesson}: ${r.error}\n`
    })
  } else {
    summaryContent += `Alle Inhalte für **${chapter.title}** wurden erstellt! 🎉`
  }

  const summaryMessage: ChatMessage = {
    id: `msg-${Date.now()}`,
    role: 'assistant',
    content: summaryContent,
    timestamp: new Date().toISOString(),
    actions: failedResults.length > 0 ? [
      { id: 'retry-failed', type: 'primary', label: 'Fehlgeschlagene wiederholen', action: 'retry_failed', payload: { failed: failedResults.map(r => r.lesson) } }
    ] : undefined
  }
  messages.value.push(summaryMessage)
  scrollToBottom()
}

function toggleFileSelection(fileId: string) {
  const index = selectedFileIds.value.indexOf(fileId)
  if (index === -1) {
    selectedFileIds.value.push(fileId)
  } else {
    selectedFileIds.value.splice(index, 1)
  }

  // Update session
  if (session.value) {
    session.value.source_file_ids = [...selectedFileIds.value]
  }
}

function clearFileSelection() {
  selectedFileIds.value = []
  if (session.value) {
    session.value.source_file_ids = []
  }
}

function startNewChapterMode() {
  selectedChapterId.value = null
  if (session.value) {
    session.value.mode = 'new_chapters'
    session.value.current_chapter_id = undefined
  }

  // Send a prompt to start chapter creation
  sendQuickAction('Ich möchte ein neues Kapitel erstellen. Welche Dateien soll ich als Grundlage verwenden?')
}

// ============================================================================
// Methods: Session
// ============================================================================

function createSession(mode: 'new_chapters' | 'edit_existing') {
  session.value = {
    id: `session-${Date.now()}`,
    course_id: selectedCourseId.value,
    mode,
    source_file_ids: [...selectedFileIds.value],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
}

// ============================================================================
// Methods: Chat
// ============================================================================

function handleEnter(e: KeyboardEvent) {
  if (!e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

function sendMessage() {
  if (!inputMessage.value.trim() || isTyping.value) return

  const userMessage: ChatMessage = {
    id: `msg-${Date.now()}`,
    role: 'user',
    content: inputMessage.value.trim(),
    timestamp: new Date().toISOString()
  }

  messages.value.push(userMessage)
  const prompt = inputMessage.value.trim()
  inputMessage.value = ''

  // Scroll to bottom
  scrollToBottom()

  // Call backend API (with fallback)
  callChatApi(prompt)
}

function sendQuickAction(prompt: string) {
  inputMessage.value = prompt
  sendMessage()
}

async function callChatApi(prompt: string) {
  isTyping.value = true

  try {
    const response = await fetch('/api/v1/admin/ai-studio/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        message: prompt,
        course_id: selectedCourseId.value || undefined,
        context: {
          mode: session.value?.mode || 'new_chapters',
          chapter_id: selectedChapterId.value || undefined,
          file_ids: selectedFileIds.value,
          session_id: session.value?.id
        }
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = await response.json()

    if (data.success && data.response) {
      const aiMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: data.response.content || 'Keine Antwort erhalten.',
        timestamp: new Date().toISOString(),
        actions: data.response.actions?.map((a: any) => ({
          id: a.id,
          type: a.type,
          label: a.label,
          action: a.action,
          payload: a.payload
        }))
      }

      messages.value.push(aiMessage)
    } else {
      // Fallback to local response
      addFallbackResponse(prompt)
    }
  } catch (error) {
    console.error('Chat API error:', error)
    // Use fallback response on error
    addFallbackResponse(prompt)
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

function addFallbackResponse(prompt: string) {
  // Generate local fallback response
  let response = ''
  const actions: ChatAction[] = []
  const promptLower = prompt.toLowerCase()

  if (promptLower.includes('was kann ich')) {
    response = `Mit dem KI-Authoring-Studio kannst du:

• **Dateien analysieren** - Lade PDFs oder andere Dokumente hoch und lasse sie analysieren
• **Kapitelstruktur erstellen** - Die KI schlägt basierend auf deinen Inhalten eine Struktur vor
• **Lektionen generieren** - Erstelle automatisch Lektionen mit Theorie und Übungen
• **Lernmethoden hinzufügen** - Füge Quiz, Karteikarten und andere Methoden hinzu

Wähle links einen Kurs und Dateien aus, um zu starten.`
  } else if (promptLower.includes('kapitelstruktur') || promptLower.includes('struktur vorschlagen')) {
    if (selectedFileIds.value.length > 0) {
      response = `Basierend auf den ${selectedFileIds.value.length} ausgewählten Datei(en) schlage ich folgende Struktur vor:

**Kapitel 1: Einführung**
- Grundlagen und Überblick
- Wichtige Begriffe

**Kapitel 2: Hauptthemen**
- Kernkonzepte
- Praktische Anwendung

**Kapitel 3: Vertiefung**
- Fortgeschrittene Themen
- Zusammenfassung

Soll ich diese Kapitel erstellen?`
      actions.push(
        { id: 'create-all', type: 'primary', label: 'Alle Kapitel erstellen', action: 'create_chapters', payload: { count: 3 } },
        { id: 'edit-structure', type: 'secondary', label: 'Struktur anpassen', action: 'edit_structure' }
      )
    } else {
      response = 'Bitte wähle zuerst Dateien im "Dateien"-Tab aus, damit ich die Inhalte analysieren kann.'
    }
  } else if (promptLower.includes('neues kapitel') || promptLower.includes('kapitel erstellen')) {
    if (selectedFileIds.value.length > 0) {
      response = `Ich werde ein neues Kapitel basierend auf den ausgewählten Dateien erstellen.

Bitte gib mir noch folgende Informationen:
1. Wie soll das Kapitel heißen?
2. Welche Hauptthemen soll es abdecken?
3. Wie viele Lektionen soll es ungefähr haben?`
    } else {
      response = 'Um ein Kapitel zu erstellen, wähle bitte zuerst Quelldateien im "Dateien"-Tab aus.'
      activeTab.value = 'files'
    }
  } else if (promptLower.includes('lektionen erstellen')) {
    if (selectedChapterId.value) {
      response = `Ich erstelle Lektionen für "${selectedChapter.value?.title}".

Basierend auf dem Kapitelinhalt schlage ich folgende Lektionen vor:

1. **Einführung** - Überblick und Lernziele
2. **Grundlagen** - Basiswissen und Definitionen
3. **Praxis** - Anwendung und Übungen
4. **Zusammenfassung** - Kernpunkte und Wiederholung

Soll ich diese Lektionen erstellen?`
      actions.push(
        { id: 'create-lessons', type: 'primary', label: 'Lektionen erstellen', action: 'create_lessons' },
        { id: 'customize', type: 'secondary', label: 'Anpassen', action: 'customize_lessons' }
      )
    } else {
      response = 'Bitte wähle zuerst ein Kapitel im "Kapitel"-Tab aus.'
      activeTab.value = 'chapters'
    }
  } else if (promptLower.includes('lernmethoden')) {
    if (selectedChapterId.value) {
      response = `Für das ausgewählte Kapitel empfehle ich folgende Lernmethoden:

• **Quiz (LM20)** - Multiple-Choice Fragen zum Testen
• **Karteikarten (LM13)** - Wichtige Begriffe einprägen
• **Lückentext (LM15)** - Aktives Erinnern fördern
• **Mindmap (LM05)** - Zusammenhänge visualisieren

Welche Methoden soll ich erstellen?`
      actions.push(
        { id: 'all-methods', type: 'primary', label: 'Alle erstellen', action: 'create_all_methods' },
        { id: 'select-methods', type: 'secondary', label: 'Auswählen', action: 'select_methods' }
      )
    } else {
      response = 'Bitte wähle zuerst ein Kapitel aus, für das Lernmethoden erstellt werden sollen.'
    }
  } else {
    // Default response
    const hints: string[] = []
    if (!selectedCourseId.value) hints.push('Wähle zuerst einen Kurs aus')
    if (selectedFileIds.value.length === 0) hints.push('Wähle Quelldateien im Dateien-Tab aus')
    if (!selectedChapterId.value) hints.push('Oder wähle ein bestehendes Kapitel zum Bearbeiten')

    response = `Ich verstehe deine Anfrage. Um dir besser helfen zu können:

${hints.map(h => '• ' + h).join('\n')}

Was möchtest du als nächstes tun?`
  }

  const aiMessage: ChatMessage = {
    id: `msg-${Date.now()}`,
    role: 'assistant',
    content: response,
    timestamp: new Date().toISOString(),
    actions: actions.length > 0 ? actions : undefined
  }

  messages.value.push(aiMessage)
}

function executeAction(action: ChatAction) {
  // TODO: Implement actual actions
  console.log('Executing action:', action)

  switch (action.action) {
    case 'create_chapters':
      sendQuickAction(`Erstelle ${action.payload?.count || 3} Kapitel basierend auf der vorgeschlagenen Struktur.`)
      break
    case 'create_lessons':
      sendQuickAction('Erstelle die vorgeschlagenen Lektionen.')
      break
    case 'create_all_methods':
      sendQuickAction('Erstelle alle vorgeschlagenen Lernmethoden.')
      break
    default:
      sendQuickAction(`Führe Aktion "${action.label}" aus.`)
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// ============================================================================
// Methods: Action Menu
// ============================================================================

function openActionMenu() {
  showActionMenu.value = true
}

function selectAction(action: QuickAction) {
  showActionMenu.value = false
  sendQuickAction(action.prompt)
}

// ============================================================================
// Methods: Formatting
// ============================================================================

function formatMessage(content: string): string {
  // Simple markdown-like formatting
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code class="px-1 py-0.5 bg-black/10 rounded text-xs">$1</code>')
    .replace(/^• /gm, '&bull; ')
    .replace(/^\d+\. /gm, (match) => `<span class="text-[var(--color-primary)]">${match}</span>`)
}

function formatTime(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
}

function formatFileSize(bytes: number | null | undefined): string {
  if (bytes === null || bytes === undefined || isNaN(bytes)) return 'Unbekannt'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function getFileIcon(mimeType: string | null | undefined): string {
  if (!mimeType) return '📁'
  if (mimeType.includes('pdf')) return '📄'
  if (mimeType.includes('image')) return '🖼️'
  if (mimeType.includes('video')) return '🎥'
  if (mimeType.includes('audio')) return '🎵'
  if (mimeType.includes('word') || mimeType.includes('document')) return '📝'
  if (mimeType.includes('sheet') || mimeType.includes('excel')) return '📊'
  if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return '📽️'
  return '📁'
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  loadCourses()

  // Check if opened with courseId in payload
  const courseId = props.window.payload?.courseId as string | undefined
  if (courseId) {
    selectedCourseId.value = courseId
    onCourseChange()
  }

  // Focus input
  nextTick(() => {
    inputRef.value?.focus()
  })
})

onUnmounted(() => {
  // Cleanup resize listeners
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
})

// Watch for payload changes
watch(() => props.window.payload?.courseId, (newCourseId) => {
  if (newCourseId && newCourseId !== selectedCourseId.value) {
    selectedCourseId.value = newCourseId as string
    onCourseChange()
  }
})
</script>

<style scoped>
.admin-ai-studio {
  min-height: 500px;
  min-width: 700px;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-tertiary);
}

/* Animation for typing indicator */
@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-4px);
  }
}

.animate-bounce {
  animation: bounce 1.4s ease-in-out infinite;
}
</style>
