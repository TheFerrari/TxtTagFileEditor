import React from 'react'

interface SidebarProps {
  rootPath: string
  minCount: number
  bannedText: string
  caseInsensitive: boolean
  sortLines: boolean
  onRootPathChange: (v: string) => void
  onMinCountChange: (v: number) => void
  onBannedTextChange: (v: string) => void
  onCaseInsensitiveChange: (v: boolean) => void
  onSortLinesChange: (v: boolean) => void
  onImport: () => void
  onExport: () => void
  onScan: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({
  rootPath,
  minCount,
  bannedText,
  caseInsensitive,
  sortLines,
  onRootPathChange,
  onMinCountChange,
  onBannedTextChange,
  onCaseInsensitiveChange,
  onSortLinesChange,
  onImport,
  onExport,
  onScan,
}) => {
  return (
    <aside className="w-80 bg-white shadow h-full p-4 space-y-4">
      <div>
        <label className="block text-sm font-medium text-slate-700">Root path</label>
        <input
          value={rootPath}
          onChange={(e) => onRootPathChange(e.target.value)}
          className="w-full mt-1 rounded border border-slate-300 px-2 py-1"
          placeholder="/path/to/logs"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700">Minimum count</label>
        <input
          type="number"
          value={minCount}
          onChange={(e) => onMinCountChange(Number(e.target.value))}
          className="w-full mt-1 rounded border border-slate-300 px-2 py-1"
          min={1}
        />
      </div>
      <div className="flex items-center justify-between">
        <label className="text-sm text-slate-700">Case-insensitive matching</label>
        <input type="checkbox" checked={caseInsensitive} onChange={(e) => onCaseInsensitiveChange(e.target.checked)} />
      </div>
      <div className="flex items-center justify-between">
        <label className="text-sm text-slate-700">Sort lines on write</label>
        <input type="checkbox" checked={sortLines} onChange={(e) => onSortLinesChange(e.target.checked)} />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700">Banned tags</label>
        <textarea
          value={bannedText}
          onChange={(e) => onBannedTextChange(e.target.value)}
          className="w-full h-40 mt-1 rounded border border-slate-300 px-2 py-1"
          placeholder="one rule per line"
        />
        <div className="flex gap-2 mt-2">
          <button className="px-3 py-1 bg-slate-100 rounded" onClick={onImport}>
            Import
          </button>
          <button className="px-3 py-1 bg-slate-100 rounded" onClick={onExport}>
            Export
          </button>
        </div>
      </div>
      <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded py-2" onClick={onScan}>
        Scan
      </button>
    </aside>
  )
}
