<!--
  Admin Learning Method Editor Panel - Phase D3.4

  Editor for Learning Method Instances (31 Methoden, LM00-LM32 ohne LM05/LM07).
  Manages learning methods attached to a specific module.

  Features:
  - List all learning methods for a module
  - Create/Edit/Delete learning method instances
  - Select from 31 method types (6 groups A-F)
  - Auto-save (debounced)
  - Drag & drop reordering
-->

<template>
  <div class="admin-learning-method-editor h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header with Chapter Context -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-4 py-3">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-[var(--color-text-secondary)]">
            {{ $t('features.learningMethodEditor.courseLabel') }} <span class="font-medium text-[var(--color-text-primary)]">{{ courseTitle }}</span>
          </p>
          <p class="text-xs text-[var(--color-text-tertiary)]">
            {{ $t('features.learningMethodEditor.chapterLabel') }} {{ chapterTitle }}
          </p>
        </div>
        <!-- Save Status Indicator -->
        <div class="flex items-center gap-2 text-xs">
          <span v-if="saveStatus === 'saving'" class="flex items-center gap-1" style="color: var(--color-info, #2563eb);">
            <svg class="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ $t('features.learningMethodEditor.saving') }}
          </span>
          <span v-else-if="saveStatus === 'saved'" class="flex items-center gap-1" style="color: var(--color-success, #16a34a);">
            <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            {{ $t('features.learningMethodEditor.saved') }}
          </span>
          <span v-else-if="saveStatus === 'error'" style="color: var(--color-error, #dc2626);">
            {{ $t('features.learningMethodEditor.saveError') }}
          </span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[var(--color-primary)] mx-auto mb-3"></div>
        <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('features.learningMethodEditor.loading') }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 p-6">
      <div class="rounded-lg p-4 border" style="background-color: var(--color-error-bg, #fee2e2); border-color: var(--color-error-border, #fecaca);">
        <p style="color: var(--color-error-text, #b91c1c);">{{ error }}</p>
        <button
          @click="loadLearningMethods"
          class="mt-3 px-3 py-1.5 text-white text-sm rounded"
          style="background-color: var(--color-error, #dc2626);"
        >
          {{ $t('features.learningMethodEditor.retry') }}
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="flex-1 flex flex-col overflow-hidden min-h-0">
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
      <div class="flex-1 overflow-hidden min-h-0 relative">
        <!-- Instances Tab - List of Learning Methods -->
        <div v-if="activeTab === 'instances'" class="h-full overflow-y-auto p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
              {{ $t('features.learningMethodEditor.tabs.instances') }} {{ methods.length > 0 ? `(${methods.length})` : '' }}
            </h3>
            <button
              @click="showMethodTypeSelector = true"
              class="px-3 py-1.5 bg-[var(--color-primary)] text-white text-sm rounded-lg hover:opacity-90 transition-colors flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              {{ $t('features.learningMethodEditor.addMethod') }}
            </button>
          </div>

          <!-- Empty State -->
          <div v-if="methods.length === 0" class="text-center py-12">
            <div class="text-5xl mb-3">🎯</div>
            <p class="text-[var(--color-text-secondary)] mb-2">{{ $t('features.learningMethodEditor.emptyTitle') }}</p>
            <p class="text-sm text-[var(--color-text-tertiary)]">
              {{ $t('features.learningMethodEditor.emptyDesc') }}
            </p>
          </div>

          <!-- Methods List with Drag & Drop -->
          <div v-else class="space-y-2">
            <div
              v-for="(method, index) in sortedMethods"
              :key="method.method_id"
              :draggable="true"
              @dragstart="handleDragStart(index)"
              @dragover.prevent="handleDragOver(index)"
              @drop="handleDrop(index)"
              @dragend="handleDragEnd"
              :class="[
                'method-item p-4 rounded-lg border transition-all cursor-move',
                dragState.draggedIndex === index
                  ? 'opacity-50 border-[var(--color-primary)]'
                  : 'bg-[var(--color-surface)] border-[var(--color-border)] hover:border-[var(--color-primary)]'
              ]"
            >
              <div class="flex items-start justify-between gap-3">
                <!-- Drag Handle + Content -->
                <div class="flex items-center gap-3 flex-1">
                  <svg class="w-5 h-5 text-[var(--color-text-tertiary)] flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M7 2a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 2zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 8zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 14zm6-8a2 2 0 1 0-.001-4.001A2 2 0 0 0 13 6zm0 2a2 2 0 1 0 .001 4.001A2 2 0 0 0 13 8zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 13 14z"></path>
                  </svg>

                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1 flex-wrap">
                      <span class="text-sm font-bold text-[var(--color-text-tertiary)]">
                        {{ method.order_index + 1 }}.
                      </span>
                      <span
                        class="text-xs px-2 py-0.5 rounded font-mono"
                        :style="getGroupStyle(getMethodGroup(method.method_type))"
                      >
                        {{ getGroupPositionById(method.method_type) }}
                      </span>
                      <h4 class="font-semibold text-[var(--color-text-primary)] truncate">
                        {{ method.title || getMethodTypeName(method.method_type) }}
                      </h4>
                      <span
                        v-if="method.published"
                        class="text-xs px-2 py-0.5 rounded"
                        style="background-color: var(--color-success-bg, #dcfce7); color: var(--color-success-text, #15803d);"
                      >
                        {{ $t('features.learningMethodEditor.published') }}
                      </span>
                    </div>
                    <div class="flex gap-4 text-xs text-[var(--color-text-secondary)]">
                      <span>{{ getMethodTypeName(method.method_type) }}</span>
                      <span v-if="method.duration_minutes">{{ method.duration_minutes }} {{ $t('features.learningMethodEditor.minutes') }}</span>
                      <span :style="getTierStyle(method.tier)">{{ getTierLabel(method.tier) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex gap-2 flex-shrink-0">
                  <button
                    @click="editMethod(method)"
                    class="p-1.5 rounded transition-colors"
                    style="color: var(--color-text-secondary);"
                    :title="$t('features.learningMethodEditor.edit')"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="togglePublish(method)"
                    class="p-1.5 rounded transition-colors"
                    :style="method.published ? 'color: var(--color-warning, #ea580c);' : 'color: var(--color-success, #16a34a);'"
                    :title="method.published ? $t('features.learningMethodEditor.withdraw') : $t('features.learningMethodEditor.publish')"
                  >
                    <svg v-if="method.published" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                    <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button
                    @click="deleteMethod(method.method_id)"
                    class="p-1.5 rounded transition-colors"
                    style="color: var(--color-error, #dc2626);"
                    :title="$t('features.learningMethodEditor.delete')"
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

        <!-- Catalog Tab - All 32 Method Types -->
        <div v-else-if="activeTab === 'catalog'" class="catalog-tab-container">
          <!-- Fixed Header -->
          <div class="catalog-header">
            <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-1">
              {{ $t('features.learningMethodEditor.catalogTitle') }}
            </h3>
            <!-- Group Tabs -->
            <div class="flex gap-1 mt-3">
              <button
                v-for="group in methodGroups"
                :key="group.id"
                @click="catalogActiveGroup = group.id"
                :class="[
                  'px-3 py-1.5 text-xs font-medium rounded-lg transition-all',
                  catalogActiveGroup === group.id
                    ? 'text-white shadow-sm'
                    : 'bg-[var(--color-background)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
                ]"
                :style="catalogActiveGroup === group.id ? getGroupStyleFilled(group.id) : ''"
              >
                {{ group.label }} ({{ group.count }})
              </button>
            </div>
          </div>

          <!-- Scrollable Content -->
          <div class="catalog-content">
            <div class="space-y-2">
              <div
                v-for="methodType in getMethodsByGroup(catalogActiveGroup)"
                :key="methodType.lm_id"
                @click="createMethodFromType(methodType)"
                class="method-type-card bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-3 hover:border-[var(--color-primary)] hover:shadow-md transition-all cursor-pointer"
              >
                <div class="flex items-center gap-3">
                  <div
                    class="w-9 h-9 rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0"
                    :style="getGroupStyle(methodType.group)"
                  >
                    {{ String(getGroupPosition(methodType)).padStart(2, '0') }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                      <h4 class="font-semibold text-[var(--color-text-primary)] text-sm">{{ methodType.name }}</h4>
                      <span
                        class="text-xs px-1.5 py-0.5 rounded"
                        :style="getTierStyle(getTierFromGroup(methodType.group))"
                      >
                        {{ getTierLabel(getTierFromGroup(methodType.group)) }}
                      </span>
                    </div>
                    <p class="text-xs text-[var(--color-text-secondary)] mt-0.5">{{ methodType.description }}</p>
                  </div>
                  <svg class="w-4 h-4 text-[var(--color-text-tertiary)] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Statistics Tab -->
        <div v-else-if="activeTab === 'stats'" class="h-full overflow-y-auto p-6">
          <div class="mb-6">
            <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-2">{{ $t('features.learningMethodEditor.stats.title') }}</h3>
            <p class="text-sm text-[var(--color-text-secondary)]">
              {{ $t('features.learningMethodEditor.stats.description') }}
            </p>
          </div>

          <div v-if="stats" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 text-center">
              <p class="text-3xl font-bold text-[var(--color-text-primary)]">{{ stats.total_methods }}</p>
              <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('features.learningMethodEditor.stats.total') }}</p>
            </div>
            <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 text-center">
              <p class="text-3xl font-bold" style="color: var(--color-success, #16a34a);">{{ stats.published_count }}</p>
              <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('features.learningMethodEditor.stats.publishedCount') }}</p>
            </div>
            <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 text-center">
              <p class="text-3xl font-bold text-[var(--color-primary)]">{{ stats.unique_types }}</p>
              <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('features.learningMethodEditor.stats.methodTypes') }}</p>
            </div>
            <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 text-center">
              <p class="text-3xl font-bold text-[var(--color-text-primary)]">{{ stats.total_duration }} {{ $t('features.learningMethodEditor.minutes') }}</p>
              <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('features.learningMethodEditor.stats.totalDuration') }}</p>
            </div>
          </div>

          <!-- Difficulty Distribution -->
          <div v-if="stats" class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
              <h4 class="font-medium text-[var(--color-text-primary)] mb-3">{{ $t('features.learningMethodEditor.stats.difficultyTitle') }}</h4>
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-[var(--color-text-secondary)]">{{ $t('features.learningMethodEditor.difficultyOptions.easy') }}</span>
                  <span class="font-medium" style="color: var(--color-success, #16a34a);">{{ stats.easy_count }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-[var(--color-text-secondary)]">{{ $t('features.learningMethodEditor.difficultyOptions.medium') }}</span>
                  <span class="font-medium" style="color: var(--color-warning, #ea580c);">{{ stats.medium_count }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-[var(--color-text-secondary)]">{{ $t('features.learningMethodEditor.difficultyOptions.hard') }}</span>
                  <span class="font-medium" style="color: var(--color-error, #dc2626);">{{ stats.hard_count }}</span>
                </div>
              </div>
            </div>

            <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
              <h4 class="font-medium text-[var(--color-text-primary)] mb-3">{{ $t('features.learningMethodEditor.stats.tierTitle') }}</h4>
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-[var(--color-text-secondary)]">Basic</span>
                  <span class="font-medium" style="color: var(--color-success, #16a34a);">{{ stats.basic_count }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-[var(--color-text-secondary)]">Premium</span>
                  <span class="font-medium" style="color: var(--color-warning, #ea580c);">{{ stats.premium_count }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-[var(--color-text-secondary)]">Pro</span>
                  <span class="font-medium" style="color: var(--color-premium-text, #6b21a8);">{{ stats.pro_count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Method Type Selector Modal -->
    <div
      v-if="showMethodTypeSelector"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showMethodTypeSelector = false"
    >
      <div class="bg-[var(--color-surface)] rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
        <div class="p-4 border-b border-[var(--color-border)] flex items-center justify-between">
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
            {{ $t('features.learningMethodEditor.selectMethod') }}
          </h3>
          <button
            @click="showMethodTypeSelector = false"
            class="p-1 rounded hover:bg-[var(--color-background)]"
          >
            <svg class="w-5 h-5 text-[var(--color-text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Group Tabs -->
        <div class="flex border-b border-[var(--color-border)] bg-[var(--color-background)]">
          <button
            v-for="group in methodGroups"
            :key="group.id"
            @click="selectorGroup = group.id"
            :class="[
              'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
              selectorGroup === group.id
                ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
            ]"
          >
            {{ group.label }}
          </button>
        </div>

        <!-- Method Types List -->
        <div class="p-4 overflow-y-auto max-h-[50vh]">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <button
              v-for="methodType in selectorMethodTypes"
              :key="methodType.lm_id"
              @click="createMethodFromType(methodType)"
              class="text-left p-3 rounded-lg border border-[var(--color-border)] hover:border-[var(--color-primary)] hover:bg-[var(--color-primary)]/5 transition-colors"
            >
              <div class="flex items-center gap-3">
                <span
                  class="text-sm font-mono px-2 py-1 rounded"
                  :style="getGroupStyle(methodType.group)"
                >
                  {{ String(getGroupPosition(methodType)).padStart(2, '0') }}
                </span>
                <div class="flex-1">
                  <p class="font-medium text-[var(--color-text-primary)]">{{ methodType.name }}</p>
                  <p class="text-xs text-[var(--color-text-secondary)]">{{ methodType.description }}</p>
                </div>
                <span
                  class="text-xs px-2 py-0.5 rounded"
                  :style="getTierStyle(getTierFromGroup(methodType.group))"
                >
                  {{ getTierLabel(getTierFromGroup(methodType.group)) }}
                </span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Method Modal -->
    <div
      v-if="editingMethod"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="editingMethod = null"
    >
      <div class="bg-[var(--color-surface)] rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
        <div class="p-4 border-b border-[var(--color-border)] flex items-center justify-between">
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
            {{ $t('features.learningMethodEditor.editMethod') }}
          </h3>
          <button
            @click="editingMethod = null"
            class="p-1 rounded hover:bg-[var(--color-background)]"
          >
            <svg class="w-5 h-5 text-[var(--color-text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-4 overflow-y-auto max-h-[60vh] space-y-4">
          <!-- Method Type (readonly) -->
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ $t('features.learningMethodEditor.methodType') }}
            </label>
            <div class="flex items-center gap-2">
              <span
                class="text-sm font-mono px-2 py-1 rounded"
                :style="getGroupStyle(getMethodGroup(editingMethod.method_type))"
              >
                {{ getGroupPositionById(editingMethod.method_type) }}
              </span>
              <span class="text-[var(--color-text-primary)]">
                {{ getMethodTypeName(editingMethod.method_type) }}
              </span>
            </div>
          </div>

          <!-- Title -->
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ $t('features.learningMethodEditor.methodTitle') }}
            </label>
            <input
              v-model="editForm.title"
              type="text"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              :placeholder="$t('features.learningMethodEditor.titlePlaceholder')"
            />
          </div>

          <!-- Instructions -->
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ $t('features.learningMethodEditor.instructions') }}
            </label>
            <textarea
              v-model="editForm.instructions"
              rows="3"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              :placeholder="$t('features.learningMethodEditor.instructionsPlaceholder')"
            ></textarea>
          </div>

          <!-- Duration & Difficulty -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                {{ $t('features.learningMethodEditor.duration') }}
              </label>
              <input
                v-model.number="editForm.duration_minutes"
                type="number"
                min="1"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                {{ $t('features.learningMethodEditor.difficulty') }}
              </label>
              <select
                v-model="editForm.difficulty"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              >
                <option value="easy">{{ $t('features.learningMethodEditor.difficultyOptions.easy') }}</option>
                <option value="medium">{{ $t('features.learningMethodEditor.difficultyOptions.medium') }}</option>
                <option value="hard">{{ $t('features.learningMethodEditor.difficultyOptions.hard') }}</option>
              </select>
            </div>
          </div>

          <!-- Tier -->
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ $t('features.learningMethodEditor.tier') }}
            </label>
            <select
              v-model="editForm.tier"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            >
              <option value="basic">{{ $t('features.learningMethodEditor.tierOptions.basic') }}</option>
              <option value="premium">{{ $t('features.learningMethodEditor.tierOptions.premium') }}</option>
              <option value="pro">{{ $t('features.learningMethodEditor.tierOptions.pro') }}</option>
            </select>
          </div>
        </div>

        <div class="p-4 border-t border-[var(--color-border)] flex justify-end gap-3">
          <button
            @click="editingMethod = null"
            class="px-4 py-2 text-sm border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-background)] transition-colors"
          >
            {{ $t('features.learningMethodEditor.cancel') }}
          </button>
          <button
            @click="saveEditedMethod"
            class="px-4 py-2 text-sm bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors"
          >
            {{ $t('features.learningMethodEditor.save') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/application/stores/modules/desktop'

const { t } = useI18n()
import type { LsxPanel } from '@/application/stores/modules/desktop'
import {
  adminGetLearningMethodTypes,
  adminGetChapterLearningMethods,
  adminCreateLearningMethod as _adminCreateLearningMethod,
  adminUpdateLearningMethod,
  adminDeleteLearningMethod,
  adminReorderLearningMethods,
  adminPublishLearningMethod,
  adminUnpublishLearningMethod,
  type AdminLearningMethod,
  type LearningMethodType,
  type LearningMethodGroup
} from '@/application/services/api/admin'

interface Props {
  panel: LsxPanel
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const panelStore = usePanelStore()

// State
const methods = ref<AdminLearningMethod[]>([])
const methodTypes = ref<LearningMethodType[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')
const activeTab = ref<'instances' | 'catalog' | 'stats'>('instances')

// Modals
const showMethodTypeSelector = ref(false)
const selectorGroup = ref<LearningMethodGroup>('A')
const selectedGroup = ref<LearningMethodGroup | null>(null)
const editingMethod = ref<AdminLearningMethod | null>(null)

// Catalog active group tab (includes all 6 groups A-F)
const catalogActiveGroup = ref<LearningMethodGroup>('A')

const getMethodsByGroup = (groupId: LearningMethodGroup): LearningMethodType[] => {
  // Simply filter by the group field from the backend
  return methodTypes.value.filter(mt => mt.group === groupId)
}

// Edit form
const editForm = ref({
  title: '',
  instructions: '',
  duration_minutes: 15,
  difficulty: 'medium' as 'easy' | 'medium' | 'hard',
  tier: 'basic' as 'basic' | 'premium' | 'pro'
})

// Statistics
const stats = ref<{
  total_methods: number
  published_count: number
  unique_types: number
  total_duration: number
  easy_count: number
  medium_count: number
  hard_count: number
  basic_count: number
  premium_count: number
  pro_count: number
} | null>(null)

// Drag & Drop State
const dragState = ref({
  draggedIndex: null as number | null,
  targetIndex: null as number | null
})

// Computed
const tabs = computed(() => [
  { id: 'instances', label: t('features.learningMethodEditor.tabs.instances'), icon: '🎯' },
  { id: 'catalog', label: t('features.learningMethodEditor.tabs.catalog'), icon: '📖' },
  { id: 'stats', label: t('features.learningMethodEditor.tabs.stats'), icon: '📊' }
])

const chapterId = computed(() => props.panel.payload?.chapterId as string)
const chapterTitle = computed(() => props.panel.payload?.chapterTitle as string || t('common.unknown'))
const courseId = computed(() => props.panel.payload?.courseId as string)
const courseTitle = computed(() => props.panel.payload?.courseTitle as string || t('common.unknown'))

const sortedMethods = computed(() => {
  return [...methods.value].sort((a, b) => (a.order_index || 0) - (b.order_index || 0))
})

const methodGroups = computed(() => [
  { id: 'A' as LearningMethodGroup, label: t('features.learningMethodEditor.groups.A'), count: 5 },
  { id: 'B' as LearningMethodGroup, label: t('features.learningMethodEditor.groups.B'), count: 6 },
  { id: 'C' as LearningMethodGroup, label: t('features.learningMethodEditor.groups.C'), count: 8 },
  { id: 'D' as LearningMethodGroup, label: t('features.learningMethodEditor.groups.D'), count: 5 },
  { id: 'E' as LearningMethodGroup, label: t('features.learningMethodEditor.groups.E'), count: 4 },
  { id: 'F' as LearningMethodGroup, label: t('features.learningMethodEditor.groups.F'), count: 7 }
])

const _filteredMethodTypes = computed(() => {
  if (!selectedGroup.value) return methodTypes.value
  return methodTypes.value.filter(mt => mt.group === selectedGroup.value)
})

const selectorMethodTypes = computed(() => {
  return methodTypes.value.filter(mt => mt.group === selectorGroup.value)
})

// Methods
const loadLearningMethods = async () => {
  if (!chapterId.value) {
    error.value = t('features.learningMethodEditor.noChapterId')
    loading.value = false
    return
  }

  loading.value = true
  error.value = null

  try {
    const [methodsResponse, typesData] = await Promise.all([
      adminGetChapterLearningMethods(chapterId.value),
      adminGetLearningMethodTypes()
    ])

    methods.value = methodsResponse.learning_methods
    methodTypes.value = typesData.types

    // Use stats from backend if available
    if (methodsResponse.statistics) {
      stats.value = methodsResponse.statistics
    } else {
      calculateStats()
    }
  } catch (err: any) {
    console.error('Error loading learning methods:', err)
    error.value = err.response?.data?.message || t('features.learningMethodEditor.loadError')
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  const m = methods.value
  stats.value = {
    total_methods: m.length,
    published_count: m.filter(x => x.published).length,
    unique_types: new Set(m.map(x => x.method_type)).size,
    total_duration: m.reduce((sum, x) => sum + (x.duration_minutes || 0), 0),
    easy_count: m.filter(x => x.difficulty === 'easy').length,
    medium_count: m.filter(x => x.difficulty === 'medium').length,
    hard_count: m.filter(x => x.difficulty === 'hard').length,
    basic_count: m.filter(x => x.tier === 'basic').length,
    premium_count: m.filter(x => x.tier === 'premium').length,
    pro_count: m.filter(x => x.tier === 'pro').length
  }
}

const getMethodTypeName = (methodType: number): string => {
  const type = methodTypes.value.find(t => t.lm_id === methodType)
  return type?.name || `Methode ${methodType}`
}

/**
 * Get position number within group (1-based) for display
 * This ensures new methods get proper sequential numbers within their group
 */
const getGroupPosition = (methodType: LearningMethodType): number => {
  const groupMethods = methodTypes.value
    .filter(mt => mt.group === methodType.group)
    .sort((a, b) => a.lm_id - b.lm_id)
  return groupMethods.findIndex(mt => mt.lm_id === methodType.lm_id) + 1
}

/**
 * Get position number within group by method_type ID (for existing instances)
 */
const getGroupPositionById = (methodTypeId: number): string => {
  const type = methodTypes.value.find(t => t.lm_id === methodTypeId)
  if (!type) return String(methodTypeId).padStart(2, '0')
  return String(getGroupPosition(type)).padStart(2, '0')
}

const getMethodGroup = (methodType: number): LearningMethodGroup => {
  const type = methodTypes.value.find(t => t.lm_id === methodType)
  return type?.group || 'A'
}

const getGroupStyle = (group: LearningMethodGroup): string => {
  return groupTier.getGroupStyle(group)
}

const getGroupStyleFilled = (group: LearningMethodGroup): string => {
  return groupTier.getGroupStyleFilled(group)
}

const getTierStyle = (tier: string): string => {
  return groupTier.getTierStyle(tier)
}

const getTierLabel = (tier: string): string => {
  const tierKeys: Record<string, string> = {
    basic: 'features.learningMethodEditor.tierOptions.basic',
    premium: 'features.learningMethodEditor.tierOptions.premium',
    pro: 'features.learningMethodEditor.tierOptions.pro'
  }
  return tierKeys[tier] ? t(tierKeys[tier]) : tier
}

const getTierFromGroup = (group: LearningMethodGroup): 'basic' | 'premium' | 'pro' => {
  const dbTier = groupTier.getTierFromGroup(group)
  const tierMap: Record<string, string> = {
    'basic': 'basic',
    'premium': 'premium',
    'enterprise': 'pro'
  }
  return (tierMap[dbTier] || 'basic') as 'basic' | 'premium' | 'pro'
}

const createMethodFromType = (methodType: LearningMethodType) => {
  if (!chapterId.value) return

  showMethodTypeSelector.value = false

  // Open the specific form panel for this method type
  const panelType = `learning-method-${methodType.lm_id}-form` as any
  panelStore.openPanel({
    type: panelType,
    title: t('features.learningMethodEditor.createPanelTitle', { name: methodType.name }),
    icon: '📝',
    payload: {
      chapterId: chapterId.value,
      chapterTitle: chapterTitle.value,
      courseId: courseId.value,
      courseTitle: courseTitle.value,
      methodCode: methodType.lm_id
    },
    preferredPosition: { x: 120, y: 30 },
    size: { width: 600, height: 700 }
  })
}

const editMethod = (method: AdminLearningMethod) => {
  // Open the specific form panel for this method type with edit data
  const panelType = `learning-method-${method.method_type}-form` as any
  const methodTypeInfo = methodTypes.value.find(mt => mt.lm_id === method.method_type)

  panelStore.openPanel({
    type: panelType,
    title: t('features.learningMethodEditor.editPanelTitle', { name: methodTypeInfo?.name || t('features.learningMethodEditor.defaultMethodName') }),
    icon: '✏️',
    payload: {
      chapterId: chapterId.value,
      chapterTitle: chapterTitle.value,
      courseId: courseId.value,
      courseTitle: courseTitle.value,
      methodCode: method.method_type,
      instanceId: method.method_id,
      instanceData: {
        title: method.title,
        instructions: method.instructions,
        duration_minutes: method.duration_minutes,
        difficulty: method.difficulty,
        tier: method.tier,
        data: method.data || {}
      }
    },
    preferredPosition: { x: 120, y: 30 },
    size: { width: 600, height: 700 }
  })
}

const saveEditedMethod = async () => {
  if (!editingMethod.value) return

  saveStatus.value = 'saving'

  try {
    const updated = await adminUpdateLearningMethod(editingMethod.value.method_id, {
      title: editForm.value.title,
      instructions: editForm.value.instructions || undefined,
      duration_minutes: editForm.value.duration_minutes,
      difficulty: editForm.value.difficulty,
      tier: editForm.value.tier
    })

    // Update in local list
    const index = methods.value.findIndex(m => m.method_id === updated.method_id)
    if (index !== -1) {
      methods.value[index] = updated
    }

    editingMethod.value = null
    calculateStats()
    saveStatus.value = 'saved'
    setTimeout(() => { saveStatus.value = 'idle' }, 2000)
  } catch (err: any) {
    console.error('Error updating learning method:', err)
    saveStatus.value = 'error'
    setTimeout(() => { saveStatus.value = 'idle' }, 3000)
  }
}

const togglePublish = async (method: AdminLearningMethod) => {
  saveStatus.value = 'saving'

  try {
    const updated = method.published
      ? await adminUnpublishLearningMethod(method.method_id)
      : await adminPublishLearningMethod(method.method_id)

    const index = methods.value.findIndex(m => m.method_id === method.method_id)
    if (index !== -1) {
      methods.value[index] = updated
    }

    calculateStats()
    saveStatus.value = 'saved'
    setTimeout(() => { saveStatus.value = 'idle' }, 2000)
  } catch (err: any) {
    console.error('Error toggling publish:', err)
    saveStatus.value = 'error'
    setTimeout(() => { saveStatus.value = 'idle' }, 3000)
  }
}

const deleteMethod = async (methodId: string) => {
  if (!confirm(t('features.learningMethodEditor.deleteConfirm'))) return

  saveStatus.value = 'saving'

  try {
    await adminDeleteLearningMethod(methodId)
    methods.value = methods.value.filter(m => m.method_id !== methodId)
    calculateStats()
    saveStatus.value = 'saved'
    setTimeout(() => { saveStatus.value = 'idle' }, 2000)
  } catch (err: any) {
    console.error('Error deleting learning method:', err)
    saveStatus.value = 'error'
    setTimeout(() => { saveStatus.value = 'idle' }, 3000)
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

  // Reorder locally
  const methodsCopy = [...sortedMethods.value]
  const [removed] = methodsCopy.splice(draggedIndex, 1)
  methodsCopy.splice(targetIndex, 0, removed)

  // Update order_index
  methodsCopy.forEach((method, idx) => {
    method.order_index = idx
  })

  methods.value = methodsCopy

  // Persist to backend
  if (chapterId.value) {
    try {
      await adminReorderLearningMethods(chapterId.value, methodsCopy.map(m => m.method_id))
    } catch (err: any) {
      console.error('Error reordering:', err)
      await loadLearningMethods()
    }
  }

  dragState.value.draggedIndex = null
  dragState.value.targetIndex = null
}

const handleDragEnd = () => {
  dragState.value.draggedIndex = null
  dragState.value.targetIndex = null
}

// Event handler for form updates
const handleLearningMethodUpdate = () => {
  loadLearningMethods()
}

// Lifecycle
onMounted(() => {
  loadLearningMethods()

  // Handle pre-selected group from payload (when opening from chapter editor)
  const preSelectedGroup = props.panel.payload?.preSelectedGroup as LearningMethodGroup | undefined
  if (preSelectedGroup && ['A', 'B', 'C', 'D', 'E', 'F'].includes(preSelectedGroup)) {
    selectedGroup.value = preSelectedGroup
    selectorGroup.value = preSelectedGroup
    catalogActiveGroup.value = preSelectedGroup
    // Switch to catalog tab to show the pre-selected group
    activeTab.value = 'catalog'
  }

  // Listen for updates from form panels
  window.addEventListener('learning-method-updated', handleLearningMethodUpdate)
})

onUnmounted(() => {
  window.removeEventListener('learning-method-updated', handleLearningMethodUpdate)
})
</script>

<style scoped>
.method-item {
  user-select: none;
}

.method-item:hover {
  cursor: grab;
}

.method-item:active {
  cursor: grabbing;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Method card hover effect */
.method-type-card {
  transition: all 0.15s ease;
}

.method-type-card:hover {
  transform: translateX(4px);
}

/* Catalog Tab Layout - using absolute positioning for reliable scroll */
.catalog-tab-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.catalog-header {
  flex-shrink: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.catalog-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  min-height: 0;
}
</style>
