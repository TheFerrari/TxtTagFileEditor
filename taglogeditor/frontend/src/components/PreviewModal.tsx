import React from 'react'
import { PreviewResponse } from '../types/api'

interface Props {
  data: PreviewResponse | null
  onClose: () => void
}

export const PreviewModal: React.FC<Props> = ({ data, onClose }) => {
  if (!data) return null
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-6">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-semibold">Preview changes</h3>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-700">
            Close
          </button>
        </div>
        <div className="p-4 space-y-4">
          <div className="flex gap-4 text-sm text-slate-700">
            <span>Files modified: {data.files_modified}</span>
            <span>Tags removed: {data.tags_removed}</span>
          </div>
          {data.previews.map((preview) => (
            <div key={preview.file} className="border rounded p-3">
              <div className="text-sm font-medium text-slate-700 mb-2">{preview.file}</div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="font-semibold text-red-600 mb-1">Before</div>
                  <pre className="bg-slate-50 p-2 rounded whitespace-pre-wrap">{preview.before.join('\n')}</pre>
                </div>
                <div>
                  <div className="font-semibold text-green-600 mb-1">After</div>
                  <pre className="bg-slate-50 p-2 rounded whitespace-pre-wrap">{preview.after.join('\n')}</pre>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
