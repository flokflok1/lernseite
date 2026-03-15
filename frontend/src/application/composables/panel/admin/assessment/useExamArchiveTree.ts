/**
 * Dynamic tree builder for exam archive folder explorer.
 *
 * Builds a nested tree from flat session rows using a configurable
 * grouping order. The admin can reorder/toggle grouping levels via UI,
 * config is persisted in localStorage.
 */

import { ref, computed, watch, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { SessionRow } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface GroupLevel {
  field: string
  labelKey: string
  enabled: boolean
}

export interface TreeNode {
  key: string
  label: string
  icon?: string
  level: number
  groupField: string
  groupValue: string
  children: TreeNode[]
  sessions: SessionLeaf[]
  examCount: number
  readyCount: number
  totalQuestions: number
}

export interface SessionLeaf {
  session_id: string
  year: number
  season: string
  seasonLabel: string
  exam_count: number
  ready_count: number
  total_questions: number
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const STORAGE_KEY = 'lsx:exam-archive:group-config'

const DEFAULT_LEVELS: GroupLevel[] = [
  { field: 'program_key', labelKey: 'panel.examArchive.groupBy.program', enabled: true },
  { field: 'region', labelKey: 'panel.examArchive.groupBy.region', enabled: true },
  { field: 'exam_type', labelKey: 'panel.examArchive.groupBy.examType', enabled: true },
  { field: 'year', labelKey: 'panel.examArchive.groupBy.year', enabled: true },
  { field: 'season', labelKey: 'panel.examArchive.groupBy.season', enabled: true },
]

// ---------------------------------------------------------------------------
// Composable
// ---------------------------------------------------------------------------

export function useExamArchiveTree(rows: Ref<SessionRow[]>) {
  const { t, locale } = useI18n()

  const groupLevels = ref<GroupLevel[]>(loadConfig())

  watch(groupLevels, (val) => saveConfig(val), { deep: true })

  const tree = computed<TreeNode[]>(() =>
    buildTree(rows.value, groupLevels.value, locale.value, t),
  )

  // Flat session list for move dialog dropdown
  const allSessions = computed(() =>
    rows.value.map((r) => ({
      session_id: r.session_id,
      label: buildFullPath(r, locale.value, t),
    })),
  )

  function toggleLevel(field: string) {
    const level = groupLevels.value.find((l) => l.field === field)
    if (level) level.enabled = !level.enabled
  }

  function moveLevelUp(index: number) {
    if (index <= 0) return
    const item = groupLevels.value.splice(index, 1)[0]
    groupLevels.value.splice(index - 1, 0, item)
  }

  function moveLevelDown(index: number) {
    if (index >= groupLevels.value.length - 1) return
    const item = groupLevels.value.splice(index, 1)[0]
    groupLevels.value.splice(index + 1, 0, item)
  }

  function resetConfig() {
    groupLevels.value = DEFAULT_LEVELS.map((l) => ({ ...l }))
  }

  return {
    groupLevels,
    tree,
    allSessions,
    toggleLevel,
    moveLevelUp,
    moveLevelDown,
    resetConfig,
  }
}

// ---------------------------------------------------------------------------
// Persistence
// ---------------------------------------------------------------------------

function loadConfig(): GroupLevel[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored) as GroupLevel[]
      const fieldSet = new Set(parsed.map((l) => l.field))
      for (const def of DEFAULT_LEVELS) {
        if (!fieldSet.has(def.field)) parsed.push({ ...def })
      }
      return parsed.filter((l) =>
        DEFAULT_LEVELS.some((d) => d.field === l.field),
      )
    }
  } catch {
    /* ignore corrupt storage */
  }
  return DEFAULT_LEVELS.map((l) => ({ ...l }))
}

function saveConfig(levels: GroupLevel[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(levels))
  } catch {
    /* quota exceeded etc. */
  }
}

// ---------------------------------------------------------------------------
// Label helpers
// ---------------------------------------------------------------------------

function resolveI18n(names: Record<string, string>, loc: string): string {
  return names?.[loc] || names?.de || Object.values(names || {})[0] || ''
}

function seasonText(season: string, t: (k: string) => string): string {
  const key = `panel.examArchive.session.season.${season}`
  const result = t(key)
  return result !== key ? result : season
}

function labelForField(
  field: string,
  row: SessionRow,
  loc: string,
  t: (k: string) => string,
): string {
  switch (field) {
    case 'program_key':
      return resolveI18n(row.program_name, loc)
    case 'region':
      return resolveI18n(row.region_name, loc)
    case 'exam_type':
      return resolveI18n(row.type_display_name, loc)
    case 'year':
      return String(row.year)
    case 'season':
      return seasonText(row.season, t)
    default:
      return String((row as Record<string, unknown>)[field] || '')
  }
}

function iconForField(field: string, row: SessionRow): string | undefined {
  if (field === 'program_key') return row.icon || undefined
  return undefined
}

function sortKeyForField(field: string, row: SessionRow): number | string {
  switch (field) {
    case 'program_key':
      return row.program_sort
    case 'exam_type':
      return row.type_sort
    case 'year':
      return -row.year // DESC
    case 'season':
      return row.season === 'sommer' ? 0 : 1
    case 'region':
      return row.region
    default:
      return String((row as Record<string, unknown>)[field] || '')
  }
}

function buildFullPath(
  row: SessionRow,
  loc: string,
  t: (k: string) => string,
): string {
  const parts = [
    resolveI18n(row.program_name, loc),
    resolveI18n(row.region_name, loc),
    resolveI18n(row.type_display_name, loc),
    `${seasonText(row.season, t)} ${row.year}`,
  ].filter(Boolean)
  return parts.join(' \u203A ')
}

// ---------------------------------------------------------------------------
// Tree builder
// ---------------------------------------------------------------------------

function buildTree(
  rows: SessionRow[],
  levels: GroupLevel[],
  loc: string,
  t: (k: string) => string,
): TreeNode[] {
  const active = levels.filter((l) => l.enabled)
  return groupAtLevel(rows, active, 0, loc, t)
}

function groupAtLevel(
  rows: SessionRow[],
  levels: GroupLevel[],
  depth: number,
  loc: string,
  t: (k: string) => string,
): TreeNode[] {
  if (rows.length === 0) return []

  if (depth >= levels.length) {
    // No more group levels — won't produce TreeNodes,
    // caller handles session leaves directly
    return []
  }

  const level = levels[depth]
  const groups = new Map<string, SessionRow[]>()
  const sortKeys = new Map<string, number | string>()

  for (const row of rows) {
    const key = String((row as Record<string, unknown>)[level.field] || '_')
    if (!groups.has(key)) {
      groups.set(key, [])
      sortKeys.set(key, sortKeyForField(level.field, row))
    }
    groups.get(key)!.push(row)
  }

  const sorted = [...groups.entries()].sort((a, b) => {
    const sa = sortKeys.get(a[0])!
    const sb = sortKeys.get(b[0])!
    if (typeof sa === 'number' && typeof sb === 'number') return sa - sb
    return String(sa).localeCompare(String(sb))
  })

  return sorted.map(([key, groupRows]) => {
    const first = groupRows[0]
    const isLeafLevel = depth + 1 >= levels.length
    const children = isLeafLevel
      ? []
      : groupAtLevel(groupRows, levels, depth + 1, loc, t)

    // Sort sessions: year DESC, season DESC
    const sessionRows = isLeafLevel
      ? [...groupRows].sort((a, b) =>
          a.year !== b.year
            ? b.year - a.year
            : b.season.localeCompare(a.season),
        )
      : []

    const sessions: SessionLeaf[] = sessionRows.map((r) => ({
      session_id: r.session_id,
      year: r.year,
      season: r.season,
      seasonLabel: seasonText(r.season, t),
      exam_count: r.exam_count,
      ready_count: r.ready_count,
      total_questions: r.total_questions,
    }))

    return {
      key: `${level.field}:${key}`,
      label: labelForField(level.field, first, loc, t),
      icon: iconForField(level.field, first),
      level: depth,
      groupField: level.field,
      groupValue: key,
      children,
      sessions,
      examCount: groupRows.reduce((s, r) => s + r.exam_count, 0),
      readyCount: groupRows.reduce((s, r) => s + r.ready_count, 0),
      totalQuestions: groupRows.reduce(
        (s, r) => s + (r.total_questions || 0),
        0,
      ),
    }
  })
}
