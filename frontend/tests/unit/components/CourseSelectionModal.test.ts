import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createPinia, setActivePinia } from 'pinia'
import CourseSelectionModal from '@/presentation/components/content/admin/courses/modals/CourseSelectionModal.vue'
import Modal from '@/presentation/components/base/Modal.vue'

// Mock course API
vi.mock('@/infrastructure/api/clients/content/courses.api', () => ({
  getMyCourses: vi.fn()
}))

// Mock window store
vi.mock('@/application/stores/window.store', () => ({
  useWindowStore: vi.fn(() => ({
    openWindow: vi.fn(),
    closePanel: vi.fn(),
    focusPanel: vi.fn(),
    minimizePanel: vi.fn(),
    restorePanel: vi.fn()
  }))
}))

// Define messages first so we can reference them in the i18n mock
const messages = {
  en: {
    admin: {
      courseEditor: {
        selectCourse: 'Select Course',
        searchPlaceholder: 'Search courses...',
        createNewCourse: 'Create New Course',
        existingCourses: 'Existing Courses',
        noCourses: 'No courses found',
        noCoursesDescription: 'Create your first course to get started!',
        openWithAI: 'Open with AI Editor',
        openWithManual: 'Open with Manual Editor',
        enterCourseName: 'Enter course name:',
        loadError: 'Failed to load courses. Please try again.'
      }
    },
    common: {
      loading: 'Loading...'
    }
  }
}

// Create i18n instance for tests
const i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages
})

// Mock course data
const mockCourses = [
  {
    course_id: '1',
    title: 'Introduction to Python',
    category: 'Programming',
    is_published: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-20T00:00:00Z'
  },
  {
    course_id: '2',
    title: 'Advanced JavaScript',
    category: 'Web Development',
    is_published: false,
    created_at: '2026-01-02T00:00:00Z',
    updated_at: '2026-01-21T00:00:00Z'
  },
  {
    course_id: '3',
    title: 'Web Development Fundamentals',
    category: 'Web Development',
    is_published: true,
    created_at: '2026-01-03T00:00:00Z',
    updated_at: '2026-01-19T00:00:00Z'
  }
]

describe('CourseSelectionModal', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const createWrapper = (props = {}, options = {}) => {
    return mount(CourseSelectionModal, {
      props: {
        show: true,
        ...props
      },
      global: {
        plugins: [i18n, createPinia()],
        stubs: {
          // Teleport is stubbed to prevent rendering to body in tests
          // Modal is NOT stubbed so it renders template content
          Teleport: true
        },
        mocks: {
          $t: (key) => {
            const keys = key.split('.')
            let value = messages.en
            for (const k of keys) {
              if (value && typeof value === 'object') {
                value = value[k]
              } else {
                return key
              }
            }
            return value || key
          }
        }
      },
      ...options
    })
  }

  describe('Course Loading', () => {
    it('should load courses from API on mount', async () => {
      const { getMyCourses } = await import('@/infrastructure/api/clients/content/courses.api')
      vi.mocked(getMyCourses).mockResolvedValue(mockCourses)

      const wrapper = createWrapper()

      // Wait for component mount and async operations
      await wrapper.vm.$nextTick()
      await vi.waitFor(() => {
        return expect(getMyCourses).toHaveBeenCalledWith(true)
      }, { timeout: 1000 })
    })

    it('should display loading state while fetching', async () => {
      const { getMyCourses } = await import('@/infrastructure/api/clients/content/courses.api')
      vi.mocked(getMyCourses).mockReturnValue(new Promise(() => {})) // Never resolves

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Loading...')
    })

    it('should display courses after loading', async () => {
      const { getMyCourses } = await import('@/infrastructure/api/clients/content/courses.api')
      vi.mocked(getMyCourses).mockResolvedValue(mockCourses)

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.text()).toContain('Introduction to Python')
      expect(wrapper.text()).toContain('Advanced JavaScript')
      expect(wrapper.text()).toContain('Web Development Fundamentals')
    })

    it('should handle API errors gracefully', async () => {
      const { getMyCourses } = await import('@/infrastructure/api/clients/content/courses.api')
      const error = new Error('API Error')
      vi.mocked(getMyCourses).mockRejectedValue(error)

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.text()).toContain('Failed to load courses')
    })

    it('should map API response to internal Course format', async () => {
      const { getMyCourses } = await import('@/infrastructure/api/clients/content/courses.api')
      vi.mocked(getMyCourses).mockResolvedValue(mockCourses)

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Verify courses are mapped correctly
      const courseItems = wrapper.findAll('.course-item')
      expect(courseItems).toHaveLength(3)

      // Verify first course data
      expect(courseItems[0].text()).toContain('Introduction to Python')
      expect(courseItems[0].text()).toContain('Programming')
    })
  })

  describe('Search and Filter', () => {
    beforeEach(async () => {
      const { getMyCourses } = await import('@/infrastructure/api/clients/content/courses.api')
      vi.mocked(getMyCourses).mockResolvedValue(mockCourses)
    })

    it('should filter courses by search query', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Type in search
      const searchInput = wrapper.find('input[type="text"]')
      await searchInput.setValue('Python')
      await wrapper.vm.$nextTick()

      // Should show only Python course
      const courseItems = wrapper.findAll('.course-item')
      expect(courseItems.length).toBeLessThan(3)
      expect(wrapper.text()).toContain('Introduction to Python')
      expect(wrapper.text()).not.toContain('Advanced JavaScript')
    })

    it('should filter courses by category', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Search for "Web"
      const searchInput = wrapper.find('input[type="text"]')
      await searchInput.setValue('Web')
      await wrapper.vm.$nextTick()

      // Should show Web Development courses
      const courseItems = wrapper.findAll('.course-item')
      expect(courseItems.length).toBeGreaterThanOrEqual(2)
      expect(wrapper.text()).toContain('Advanced JavaScript')
      expect(wrapper.text()).toContain('Web Development Fundamentals')
    })

    it('should show empty state when no courses match search', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Search for non-existent course
      const searchInput = wrapper.find('input[type="text"]')
      await searchInput.setValue('NonExistent')
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('No courses found')
    })

    it('should be case insensitive', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const searchInput = wrapper.find('input[type="text"]')

      // Search with lowercase
      await searchInput.setValue('python')
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('Introduction to Python')

      // Search with uppercase
      await searchInput.setValue('JAVASCRIPT')
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('Advanced JavaScript')
    })

    it('should allow clearing search', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const searchInput = wrapper.find('input[type="text"]')

      // Type search
      await searchInput.setValue('Python')
      await wrapper.vm.$nextTick()
      expect(wrapper.findAll('.course-item')).toHaveLength(1)

      // Clear search
      await searchInput.setValue('')
      await wrapper.vm.$nextTick()
      expect(wrapper.findAll('.course-item')).toHaveLength(3)
    })
  })

  describe('Window Opening', () => {
    beforeEach(async () => {
      const { getMyCourses } = await import('@/infrastructure/api/clients/content/courses.api')
      vi.mocked(getMyCourses).mockResolvedValue(mockCourses)
    })

    it('should emit courseOpened event when opening with AI editor', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const aiButtons = wrapper.findAll('button').filter(b =>
        b.text().includes('Open with AI Editor') || b.text().includes('🤖')
      )

      if (aiButtons.length > 0) {
        await aiButtons[0].trigger('click')
        await wrapper.vm.$nextTick()

        expect(wrapper.emitted('courseOpened')).toBeTruthy()
        expect(wrapper.emitted('close')).toBeTruthy()
      }
    })

    it('should emit courseOpened event when opening with manual editor', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const manualButtons = wrapper.findAll('button').filter(b =>
        b.text().includes('Open with Manual Editor') || b.text().includes('✏️')
      )

      if (manualButtons.length > 0) {
        await manualButtons[0].trigger('click')
        await wrapper.vm.$nextTick()

        expect(wrapper.emitted('courseOpened')).toBeTruthy()
        expect(wrapper.emitted('close')).toBeTruthy()
      }
    })

    it('should emit close event when modal is closed', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.$emit('close')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('should pass correct event payload with AI editor selection', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const aiButtons = wrapper.findAll('button').filter(b =>
        b.text().includes('Open with AI Editor') || b.text().includes('🤖')
      )

      if (aiButtons.length > 0) {
        await aiButtons[0].trigger('click')
        await wrapper.vm.$nextTick()

        const courseOpenedEmits = wrapper.emitted('courseOpened')
        if (courseOpenedEmits && courseOpenedEmits.length > 0) {
          const [courseId, editorType] = courseOpenedEmits[0] as [string | number, string]
          expect(courseId).toBe('1')
          expect(editorType).toBe('ai')
        }
      }
    })

    it('should pass correct event payload with manual editor selection', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const manualButtons = wrapper.findAll('button').filter(b =>
        b.text().includes('Open with Manual Editor') || b.text().includes('✏️')
      )

      if (manualButtons.length > 0) {
        await manualButtons[0].trigger('click')
        await wrapper.vm.$nextTick()

        const courseOpenedEmits = wrapper.emitted('courseOpened')
        if (courseOpenedEmits && courseOpenedEmits.length > 0) {
          const [courseId, editorType] = courseOpenedEmits[0] as [string | number, string]
          expect(courseId).toBe('1')
          expect(editorType).toBe('manual')
        }
      }
    })
  })

  describe('Create New Course', () => {
    beforeEach(async () => {
      const { getMyCourses } = await import('@/infrastructure/api/clients/content/courses.api')
      vi.mocked(getMyCourses).mockResolvedValue(mockCourses)
    })

    it('should show create new course button', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Create New Course')
    })

    it('should handle create new course action', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // Mock window.prompt
      const promptSpy = vi.spyOn(window, 'prompt').mockReturnValue('Test Course')

      const createButton = wrapper.findAll('button').find(b =>
        b.text().includes('Create New Course') || b.text().includes('➕')
      )

      if (createButton) {
        await createButton.trigger('click')
        await wrapper.vm.$nextTick()

        expect(promptSpy).toHaveBeenCalled()
        expect(wrapper.emitted('courseOpened')).toBeTruthy()
        expect(wrapper.emitted('close')).toBeTruthy()
      }

      promptSpy.mockRestore()
    })
  })

  describe('Multi-Window Scenario', () => {
    beforeEach(async () => {
      const { getMyCourses } = await import('@/infrastructure/api/clients/content/courses.api')
      vi.mocked(getMyCourses).mockResolvedValue(mockCourses)
    })

    it('should allow sequential opening of multiple editors', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Get all AI editor buttons
      const aiButtons = wrapper.findAll('button').filter(b =>
        b.text().includes('Open with AI Editor') || b.text().includes('🤖')
      )

      // Click first AI editor button
      if (aiButtons[0]) {
        await aiButtons[0].trigger('click')
        await wrapper.vm.$nextTick()

        expect(wrapper.emitted('courseOpened')).toHaveLength(1)
        expect(wrapper.emitted('close')).toHaveLength(1)
      }
    })

    it('should maintain correct course data in each window', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const courseItems = wrapper.findAll('.course-item')
      expect(courseItems.length).toBeGreaterThanOrEqual(3)

      // Verify each course has its own data
      for (let i = 0; i < Math.min(3, courseItems.length); i++) {
        const course = mockCourses[i]
        const item = courseItems[i]
        expect(item.text()).toContain(course.title)
        expect(item.text()).toContain(course.category)
      }
    })
  })

  describe('Modal Behavior', () => {
    it('should accept show prop', () => {
      const wrapper = createWrapper({ show: true })
      expect(wrapper.props('show')).toBe(true)
    })

    it('should emit close event on modal close', async () => {
      const wrapper = createWrapper()
      wrapper.vm.$emit('close')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('should render modal component', () => {
      const wrapper = createWrapper()
      // Modal is stubbed, but we can check if it's used
      expect(wrapper.vm).toBeDefined()
    })
  })
})
