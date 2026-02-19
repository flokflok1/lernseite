/**
 * File Types - Course Materials & Uploads
 *
 * Defines types for file management in course authoring.
 *
 * @module course-builder/types/file
 */

/**
 * Course File
 *
 * A file uploaded to a course authoring session.
 */
export interface CourseFile {
  /** Unique file identifier */
  id: string

  /** File name with extension */
  name: string

  /** File MIME type or extension */
  type: string

  /** File size in bytes */
  size: number

  /** Whether file has been parsed for AI context */
  parsed: boolean

  /** Parsed text content (if available) */
  parsed_content?: string

  /** File URL for preview/download */
  url?: string

  /** Upload timestamp */
  uploaded_at?: string

  /** Associated session ID */
  session_id?: string
}

/**
 * File Upload Progress
 *
 * Track upload progress for files.
 */
export interface FileUploadProgress {
  /** File being uploaded */
  file: File

  /** Upload progress (0-100) */
  progress: number

  /** Upload status */
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error'

  /** Error message if failed */
  error?: string

  /** Resulting CourseFile if successful */
  result?: CourseFile
}

/**
 * File Selection State
 *
 * Tracks which files are selected for AI context.
 */
export interface FileSelectionState {
  /** IDs of selected files */
  selectedIds: string[]

  /** All files */
  allSelected: boolean

  /** Some but not all selected */
  someSelected: boolean
}
