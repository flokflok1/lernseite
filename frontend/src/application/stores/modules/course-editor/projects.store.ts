/**
 * projects.store.ts
 *
 * Projects state management.
 * Handles user's course editing projects.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Project {
  id: string
  title: string
  description: string
  lastModified: Date
  status: 'draft' | 'published' | 'archived'
}

export const useProjectsStore = defineStore('courseEditor/projects', () => {
  const projects = ref<Project[]>([])
  const isLoading = ref(false)

  const loadProjects = async () => {
    isLoading.value = true
    try {
      // TODO: Load from API
    } finally {
      isLoading.value = false
    }
  }

  const createProject = async (title: string, description: string) => {
    // TODO: Create project via API
    const newProject: Project = {
      id: Date.now().toString(),
      title,
      description,
      lastModified: new Date(),
      status: 'draft'
    }
    projects.value.push(newProject)
    return newProject
  }

  return {
    projects,
    isLoading,
    loadProjects,
    createProject
  }
})
