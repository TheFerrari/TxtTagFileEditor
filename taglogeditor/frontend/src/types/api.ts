export interface TagCounts {
  [namespace: string]: {
    [tag: string]: number
  }
}

export interface ScanResponse {
  files_found: string[]
  total_files: number
  counts: TagCounts
}

export interface FilePreview {
  file: string
  before: string[]
  after: string[]
  removed: number
}

export interface PreviewResponse {
  files_modified: number
  tags_removed: number
  previews: FilePreview[]
}

export interface ApplyResponse {
  backup_path: string
  files_modified: number
  tags_removed: number
}
