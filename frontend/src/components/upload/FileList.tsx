import React, { useState } from 'react'
import { 
  File, 
  FileText, 
  Image, 
  Download, 
  Trash2, 
  Eye, 

  CheckCircle,
  AlertCircle,
  Clock,
  X
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import type { UploadedFile } from '@/types'

const fileIcons: Record<string, React.ComponentType<any>> = {
  'text/csv': FileText,
  'application/json': FileText,
  'text/plain': FileText,
  'image/png': Image,
  'image/jpeg': Image,
  'image/jpg': Image,
  'image/gif': Image,
}

interface FileListProps {
  files: UploadedFile[]
  onRemoveFile?: (fileId: string) => void
  onDownloadFile?: (file: UploadedFile) => void
  onPreviewFile?: (file: UploadedFile) => void
  showActions?: boolean
  compact?: boolean
  className?: string
}

export function FileList({
  files,
  onRemoveFile,
  onDownloadFile,
  onPreviewFile,
  showActions = true,
  compact = false,
  className = ''
}: FileListProps) {
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null)
  const [showPreview, setShowPreview] = useState(false)

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString([], {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getFileIcon = (type: string) => {
    return fileIcons[type] || File
  }

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploaded':
      case 'processed':
        return CheckCircle
      case 'error':
        return AlertCircle
      case 'uploading':
      case 'processing':
        return Clock
      default:
        return File
    }
  }

  const getStatusColor = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploaded':
      case 'processed':
        return 'text-green-500'
      case 'error':
        return 'text-red-500'
      case 'uploading':
      case 'processing':
        return 'text-blue-500'
      default:
        return 'text-gray-500'
    }
  }

  const getStatusBadge = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploaded':
        return <Badge variant="success" size="sm">Uploaded</Badge>
      case 'processed':
        return <Badge variant="success" size="sm">Processed</Badge>
      case 'error':
        return <Badge variant="error" size="sm">Error</Badge>
      case 'uploading':
        return <Badge variant="info" size="sm">Uploading</Badge>
      case 'processing':
        return <Badge variant="info" size="sm">Processing</Badge>
      default:
        return <Badge variant="secondary" size="sm">Unknown</Badge>
    }
  }

  const handlePreview = (file: UploadedFile) => {
    setSelectedFile(file)
    setShowPreview(true)
    onPreviewFile?.(file)
  }

  const handleDownload = (file: UploadedFile) => {
    if (file.content) {
      // Create download link for files with content
      const blob = new Blob([file.content], { type: file.type })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.name
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
    onDownloadFile?.(file)
  }

  if (files.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 ${className}`}>
        <File className="w-8 h-8 mx-auto mb-2" />
        <p>No files uploaded yet</p>
      </div>
    )
  }

  if (compact) {
    return (
      <div className={`space-y-2 ${className}`}>
        {files.map((file) => {
          const FileIcon = getFileIcon(file.type)
          const StatusIcon = getStatusIcon(file.status)
          
          return (
            <div key={file.id} className="flex items-center space-x-3 p-2 bg-white border border-gray-200 rounded-lg">
              <FileIcon className="w-4 h-4 text-gray-500 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {file.name}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(file.size)}
                </p>
              </div>
              <StatusIcon className={`w-4 h-4 ${getStatusColor(file.status)}`} />
              {showActions && onRemoveFile && (
                <button
                  onClick={() => onRemoveFile(file.id)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <>
      <div className={`space-y-3 ${className}`}>
        {files.map((file) => {
          const FileIcon = getFileIcon(file.type)
          
          return (
            <div key={file.id} className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                    <FileIcon className="w-5 h-5 text-gray-600" />
                  </div>
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {file.name}
                      </h4>
                      <div className="flex items-center space-x-3 mt-1 text-xs text-gray-500">
                        <span>{formatFileSize(file.size)}</span>
                        <span>•</span>
                        <span>{formatDate(file.uploadedAt)}</span>
                        {file.type === 'text/csv' && file.status === 'processed' && file.processedData?.rows && (
                          <>
                            <span>•</span>
                            <span className="text-green-600">{file.processedData.rows} rows</span>
                          </>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {getStatusBadge(file.status)}
                      {showActions && (
                        <div className="flex items-center space-x-1">
                          {file.content && (
                            <Button
                              variant="outline"
                              size="sm"
                              icon={<Eye className="w-3 h-3" />}
                              onClick={() => handlePreview(file)}
                            >
                            </Button>
                          )}
                          <Button
                            variant="outline"
                            size="sm"
                            icon={<Download className="w-3 h-3" />}
                            onClick={() => handleDownload(file)}
                          >
                          </Button>
                          {onRemoveFile && (
                            <Button
                              variant="outline"
                              size="sm"
                              icon={<Trash2 className="w-3 h-3" />}
                              onClick={() => onRemoveFile(file.id)}
                              className="text-red-600 hover:text-red-700"
                            >
                            </Button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {file.status === 'error' && file.errorMessage && (
                    <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                      {file.errorMessage}
                    </div>
                  )}
                  
                  {file.status === 'processed' && file.processedData && (
                    <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-xs text-green-700">
                      File processed successfully
                      {file.processedData.headers && (
                        <span className="ml-1">
                          • {file.processedData.headers.length} columns detected
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* File Preview Modal */}
      {showPreview && selectedFile && (
        <Modal
          isOpen={showPreview}
          onClose={() => setShowPreview(false)}
          title={`Preview: ${selectedFile.name}`}
          size="lg"
        >
          <div className="space-y-4">
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-8 h-8 bg-white rounded flex items-center justify-center">
                {React.createElement(getFileIcon(selectedFile.type), {
                  className: "w-4 h-4 text-gray-600"
                })}
              </div>
              <div>
                <p className="font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {formatFileSize(selectedFile.size)} • {selectedFile.type}
                </p>
              </div>
            </div>
            
            {selectedFile.content && (
              <div className="max-h-96 overflow-auto">
                <pre className="text-xs bg-gray-100 p-3 rounded border whitespace-pre-wrap">
                  {selectedFile.content.slice(0, 5000)}
                  {selectedFile.content.length > 5000 && '\n... (truncated)'}
                </pre>
              </div>
            )}
            
            {selectedFile.processedData && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900">Processed Data</h4>
                <pre className="text-xs bg-gray-100 p-3 rounded border">
                  {JSON.stringify(selectedFile.processedData, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </Modal>
      )}
    </>
  )
}
