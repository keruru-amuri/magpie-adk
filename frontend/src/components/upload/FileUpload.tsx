import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, FileText, Image, AlertCircle, CheckCircle, X } from 'lucide-react'
import { fileApi } from '@/utils/api'
import type { UploadedFile, FileUploadProps } from '@/types'

const fileIcons: Record<string, React.ComponentType<any>> = {
  'text/csv': FileText,
  'application/json': FileText,
  'text/plain': FileText,
  'image/png': Image,
  'image/jpeg': Image,
  'image/jpg': Image,
  'image/gif': Image,
}

export function FileUpload({ 
  className, 
  maxFileSize = 10 * 1024 * 1024, // 10MB
  acceptedTypes = ['text/csv', 'application/json', 'text/plain', 'image/*'],
  onFileUploaded 
}: FileUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<{ [fileId: string]: number }>({})

  const handleFileUpload = useCallback(async (acceptedFiles: File[]) => {
    setIsUploading(true)
    
    for (const file of acceptedFiles) {
      const fileId = crypto.randomUUID()
      const newFile: UploadedFile = {
        id: fileId,
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date(),
        status: 'uploading'
      }
      
      setUploadedFiles(prev => [...prev, newFile])
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }))
      
      try {
        if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
          // CSV Workaround: Read content before processing
          const content = await file.text()

          setUploadProgress(prev => ({ ...prev, [fileId]: 50 }))

          // Process CSV using API function
          const response = await fileApi.uploadCSV(
            file,
            content,
            (progress) => {
              setUploadProgress(prev => ({ ...prev, [fileId]: progress }))
            }
          )

          if (response.success && response.data) {
            // Update file with processed data
            const updatedFile = {
              id: fileId,
              name: file.name,
              size: file.size,
              type: file.type,
              uploadedAt: new Date(),
              status: 'processed' as const,
              content,
              processedData: response.data?.processedData
            }

            setUploadedFiles(prev => prev.map(f =>
              f.id === fileId ? updatedFile : f
            ))

            // Call callback with the updated file
            if (onFileUploaded) {
              onFileUploaded(updatedFile)
            }
          } else {
            throw new Error(response.error || 'Failed to process CSV')
          }
        } else {
          // Standard file upload for non-CSV files
          const response = await fileApi.uploadFile(
            file,
            (progress) => {
              setUploadProgress(prev => ({ ...prev, [fileId]: progress }))
            }
          )

          if (response.success && response.data) {
            const updatedFile = {
              id: fileId,
              name: file.name,
              size: file.size,
              type: file.type,
              uploadedAt: new Date(),
              status: 'uploaded' as const,
              processedData: response.data?.processedData
            }

            setUploadedFiles(prev => prev.map(f =>
              f.id === fileId ? updatedFile : f
            ))

            // Call callback with the updated file
            if (onFileUploaded) {
              onFileUploaded(updatedFile)
            }
          } else {
            throw new Error(response.error || 'Failed to upload file')
          }
        }
        
        setUploadProgress(prev => ({ ...prev, [fileId]: 100 }))
        
      } catch (error) {
        console.error('Upload failed:', error)
        setUploadedFiles(prev => prev.map(f =>
          f.id === fileId
            ? {
                ...f,
                status: 'error',
                errorMessage: error instanceof Error
                  ? error.message
                  : 'Upload failed'
              }
            : f
        ))
      }
    }
    
    setIsUploading(false)
  }, [onFileUploaded, uploadedFiles])

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop: handleFileUpload,
    accept: acceptedTypes.reduce((acc, type) => {
      acc[type] = type.includes('*') ? [] : [`.${type.split('/')[1]}`]
      return acc
    }, {} as Record<string, string[]>),
    maxSize: maxFileSize,
    multiple: true
  })

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId))
    setUploadProgress(prev => {
      const newProgress = { ...prev }
      delete newProgress[fileId]
      return newProgress
    })
  }

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

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploaded':
      case 'processed':
        return CheckCircle
      case 'error':
        return AlertCircle
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

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-sm text-gray-600">
          {isDragActive
            ? 'Drop files here...'
            : 'Drag & drop files or click to browse'}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Supports CSV, JSON, TXT, Images (max {formatFileSize(maxFileSize)})
        </p>
        {fileRejections.length > 0 && (
          <div className="mt-2 text-xs text-red-600">
            Some files were rejected: {fileRejections[0].errors[0].message}
          </div>
        )}
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span className="text-sm text-blue-800">Uploading files...</span>
          </div>
        </div>
      )}

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">Uploaded Files</h4>
          {uploadedFiles.map((file) => {
            const FileIcon = getFileIcon(file.type)
            const StatusIcon = getStatusIcon(file.status)
            const progress = uploadProgress[file.id] || 0
            
            return (
              <div key={file.id} className="bg-white border border-gray-200 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <FileIcon className="w-5 h-5 text-gray-500 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {file.name}
                      </p>
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        <span>{formatFileSize(file.size)}</span>
                        <span>•</span>
                        <span className="capitalize">{file.status}</span>
                        {file.type === 'text/csv' && file.status === 'processed' && (
                          <>
                            <span>•</span>
                            <span className="text-green-600">CSV Processed</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <StatusIcon className={`w-4 h-4 ${getStatusColor(file.status)}`} />
                    <button
                      onClick={() => removeFile(file.id)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                {/* Progress Bar */}
                {(file.status === 'uploading' || file.status === 'processing') && (
                  <div className="mt-2">
                    <div className="bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                )}
                
                {/* Error Message */}
                {file.status === 'error' && file.errorMessage && (
                  <div className="mt-2 text-xs text-red-600">
                    {file.errorMessage}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
