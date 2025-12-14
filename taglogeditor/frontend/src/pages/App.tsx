import React, { useMemo, useState } from 'react'
import { applyChanges, previewChanges, scanDirectory, exportBanned, importBanned } from '../lib/api'
import { TagCounts } from '../types/api'
import { Sidebar } from '../components/Sidebar'
import { TagList } from '../components/TagList'
import { PreviewModal } from '../components/PreviewModal'

const emptyCounts: TagCounts = {}

const App: React.FC = () => {
  const [rootPath, setRootPath] = useState('')
  const [minCount, setMinCount] = useState(5)
  const [bannedText, setBannedText] = useState('')
  const [caseInsensitive, setCaseInsensitive] = useState(false)
  const [sortLines, setSortLines] = useState(false)
  const [counts, setCounts] = useState<TagCounts>(emptyCounts)
  const [selected, setSelected] = useState<Record<string, Set<string>>>({})
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [previewData, setPreviewData] = useState<any>(null)

  const bannedRules = useMemo(() => bannedText.split('\n').map((r) => r.trim()).filter(Boolean), [bannedText])

  const handleToggle = (ns: string, tag: string) => {
    setSelected((prev) => {
      const next = { ...prev }
      const current = new Set(prev[ns] ?? [])
      if (current.has(tag)) {
        current.delete(tag)
      } else {
        current.add(tag)
      }
      next[ns] = current
      return next
    })
  }

  const handleScan = async () => {
    setLoading(true)
    setMessage('')
    try {
      const res = await scanDirectory({
        root_path: rootPath,
        min_count: minCount,
        banned_rules: bannedRules,
        case_insensitive: caseInsensitive,
      })
      setCounts(res.counts)
      setMessage(`Scanned ${res.total_files} files`)
    } catch (err: any) {
      setMessage(err?.message || 'Scan failed')
    } finally {
      setLoading(false)
    }
  }

  const selectedToPayload = useMemo(() => {
    const obj: Record<string, string[]> = {}
    Object.entries(selected).forEach(([ns, set]) => {
      obj[ns] = Array.from(set)
    })
    return obj
  }, [selected])

  const handlePreview = async () => {
    setLoading(true)
    setMessage('')
    try {
      const res = await previewChanges({
        root_path: rootPath,
        selected_to_remove: selectedToPayload,
        banned_rules: bannedRules,
        case_insensitive: caseInsensitive,
        sort_lines: sortLines,
      })
      setPreviewData(res)
    } catch (err: any) {
      setMessage(err?.message || 'Preview failed')
    } finally {
      setLoading(false)
    }
  }

  const handleApply = async () => {
    setLoading(true)
    setMessage('')
    try {
      const res = await applyChanges({
        root_path: rootPath,
        selected_to_remove: selectedToPayload,
        banned_rules: bannedRules,
        case_insensitive: caseInsensitive,
        sort_lines: sortLines,
      })
      setMessage(`Updated ${res.files_modified} files. Backup: ${res.backup_path}`)
    } catch (err: any) {
      setMessage(err?.message || 'Apply failed')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    const content = await exportBanned(bannedRules, caseInsensitive)
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '.taglogeditor_banned.txt'
    a.click()
  }

  const handleImport = async () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.txt'
    input.onchange = async () => {
      const file = input.files?.[0]
      if (!file) return
      const text = await file.text()
      const rules = await importBanned(text)
      setBannedText(rules.join('\n'))
    }
    input.click()
  }

  return (
    <div className="h-screen flex">
      <Sidebar
        rootPath={rootPath}
        minCount={minCount}
        bannedText={bannedText}
        caseInsensitive={caseInsensitive}
        sortLines={sortLines}
        onRootPathChange={setRootPath}
        onMinCountChange={setMinCount}
        onBannedTextChange={setBannedText}
        onCaseInsensitiveChange={setCaseInsensitive}
        onSortLinesChange={setSortLines}
        onImport={handleImport}
        onExport={handleExport}
        onScan={handleScan}
      />
      <main className="flex-1 p-6 overflow-y-auto space-y-4">
        <div className="flex items-center justify-between">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border border-slate-300 rounded px-3 py-2 w-80"
            placeholder="Search tags"
          />
          <div className="space-x-2">
            <button
              className="px-4 py-2 bg-slate-100 rounded border border-slate-200"
              disabled={loading}
              onClick={handlePreview}
            >
              Preview
            </button>
            <button className="px-4 py-2 bg-indigo-600 text-white rounded" disabled={loading} onClick={handleApply}>
              Apply
            </button>
          </div>
        </div>
        {message && <div className="text-sm text-slate-700">{message}</div>}
        {loading && <div className="text-sm text-indigo-600">Working...</div>}
        <TagList counts={counts} search={search} minCount={minCount} onToggle={handleToggle} selected={selected} />
      </main>
      <PreviewModal data={previewData} onClose={() => setPreviewData(null)} />
    </div>
  )
}

export default App
