import React from 'react'
import { TagCounts } from '../types/api'

interface Props {
  counts: TagCounts
  search: string
  minCount: number
  onToggle: (namespace: string, tag: string) => void
  selected: Record<string, Set<string>>
}

export const TagList: React.FC<Props> = ({ counts, search, onToggle, selected }) => {
  const namespaces = Object.keys(counts).sort()

  return (
    <div className="space-y-4">
      {namespaces.map((ns) => {
        const tags = counts[ns]
        const filtered = Object.entries(tags).filter(([tag]) =>
          tag.toLowerCase().includes(search.toLowerCase()),
        )
        if (filtered.length === 0) return null
        return (
          <div key={ns} className="bg-white rounded-lg shadow p-4">
            <div className="font-semibold text-slate-700 mb-2">{ns}</div>
            <div className="divide-y">
              {filtered.map(([tag, count]) => {
                const checked = selected[ns]?.has(tag) ?? false
                return (
                  <label key={tag} className="flex items-center justify-between py-2">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        className="h-4 w-4"
                        checked={checked}
                        onChange={() => onToggle(ns, tag)}
                      />
                      <span className="text-slate-800">{tag}</span>
                    </div>
                    <span className="text-sm text-slate-500">{count}</span>
                  </label>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}
