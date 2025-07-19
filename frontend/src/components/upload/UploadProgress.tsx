import React from 'react'
import { 
  File, 
  FileText, 
  Image, 
  CheckCircle, 
  AlertCircle, 
  X, 
  Loader2,

  Database
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
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

interface UploadProgressProps {
  files: UploadedFile[]
  progress: { [fileId: string]: number }
  onCancelUpload?: (fileId: string) => void
  onRetryUpload?: (fileId: string) => void
  showDetails?: boolean
  className?: string
}

export function UploadProgress({
  files,
  progress,
  onCancelUpload,
  onRetryUpload,
  showDetails = true,
  className = ''
}: UploadProgressProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getFileIcon = (type: string) => {
    return fileIcons[type] || File
  }



  const getProgressColor = (status: UploadedFile['status'], progress: number) => {
    if (status === 'error') return 'bg-red-500'
    if (status === 'uploaded' || status === 'processed') return 'bg-green-500'
    if (progress === 100) return 'bg-green-500'
    return 'bg-blue-500'
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
        return Loader2
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

  // Filter files that are currently uploading or have errors
  const activeFiles = files.filter(file => 
    file.status === 'uploading' || 
    file.status === 'processing' || 
    file.status === 'error'
  )

  if (activeFiles.length === 0) {
    return null
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {activeFiles.map((file) => {
        const FileIcon = getFileIcon(file.type)
        const StatusIcon = getStatusIcon(file.status)
        const fileProgress = progress[file.id] || 0
        const isAnimated = file.status === 'uploading' || file.status === 'processing'
        
        return (
          <div key={file.id} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
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
                    <div className="flex items-center space-x-2 mt-1 text-xs text-gray-500">
                      <span>{formatFileSize(file.size)}</span>
                      <span>•</span>
                      <span className="capitalize">{file.status}</span>
                      {file.type === 'text/csv' && (
                        <>
                          <span>•</span>
                          <span className="text-blue-600">CSV Processing</span>
                        </>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <StatusIcon 
                      className={`w-4 h-4 ${getStatusColor(file.status)} ${
                        isAnimated ? 'animate-spin' : ''
                      }`} 
                    />
                    {onCancelUpload && file.status !== 'error' && (
                      <Button
                        variant="outline"
                        size="sm"
                        icon={<X className="w-3 h-3" />}
                        onClick={() => onCancelUpload?.(file.id)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                      </Button>
                    )}
                    {onRetryUpload && file.status === 'error' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onRetryUpload(file.id)}
                      >
                        Retry
                      </Button>
                    )}
                  </div>
                </div>
                
                {/* Progress Bar */}
                <div className="mt-3">
                  <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                    <span>{fileProgress}% complete</span>
                    {showDetails && file.status !== 'error' && (
                      <span>
                        {file.status === 'uploading' && 'Uploading to server...'}
                        {file.status === 'processing' && 'Processing file...'}
                        {file.status === 'uploaded' && 'Upload complete'}
                        {file.status === 'processed' && 'Processing complete'}
                      </span>
                    )}
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(file.status, fileProgress)}`}
                      style={{ width: `${fileProgress}%` }}
                    />
                  </div>
                </div>
                
                {/* CSV Processing Details */}
                {file.type === 'text/csv' && file.status === 'processing' && showDetails && (
                  <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs">
                    <div className="flex items-center space-x-2 text-blue-700">
                      <Database className="w-3 h-3" />
                      <span>Processing CSV content for ADK compatibility...</span>
                    </div>
                  </div>
                )}
                
                {/* Error Message */}
                {file.status === 'error' && file.errorMessage && (
                  <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                    <div className="flex items-start space-x-2">
                      <AlertCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                      <span>{file.errorMessage}</span>
                    </div>
                  </div>
                )}
                
                {/* Success Message */}
                {(file.status === 'uploaded' || file.status === 'processed') && showDetails && (
                  <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-xs text-green-700">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="w-3 h-3" />
                      <span>
                        {file.status === 'uploaded' && 'File uploaded successfully'}
                        {file.status === 'processed' && 'File processed and ready for use'}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

// Compact version for smaller spaces
export function UploadProgressCompact({
  files,
  progress,
  className = ''
}: Pick<UploadProgressProps, 'files' | 'progress' | 'className'>) {
  const activeFiles = files.filter(file => 
    file.status === 'uploading' || 
    file.status === 'processing' || 
    file.status === 'error'
  )

  if (activeFiles.length === 0) {
    return null
  }

  const totalProgress = activeFiles.reduce((sum, file) => {
    return sum + (progress[file.id] || 0)
  }, 0) / activeFiles.length

  return (
    <div className={`bg-blue-50 border border-blue-200 rounded-lg p-3 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
          <span className="text-sm font-medium text-blue-800">
            Uploading {activeFiles.length} file{activeFiles.length !== 1 ? 's' : ''}
          </span>
        </div>
        <span className="text-xs text-blue-600">
          {Math.round(totalProgress)}%
        </span>
      </div>
      
      <div className="w-full bg-blue-200 rounded-full h-1.5">
        <div
          className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
          style={{ width: `${totalProgress}%` }}
        />
      </div>
      
      {activeFiles.length === 1 && (
        <div className="mt-2 text-xs text-blue-700 truncate">
          {activeFiles[0].name}
        </div>
      )}
    </div>
  )
}
