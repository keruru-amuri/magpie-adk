import { useState, useCallback } from 'react'
import { useFileStore } from '@/stores/fileStore'
import { validateFiles } from '@/utils/fileUtils'
import type { UploadedFile } from '@/types'

export interface UseFileUploadOptions {
  maxFileSize?: number
  acceptedTypes?: string[]
  multiple?: boolean
  onSuccess?: (files: UploadedFile[]) => void
  onError?: (error: string) => void
}

export interface UseFileUploadReturn {
  uploadFiles: (files: File[]) => Promise<UploadedFile[]>
  uploadSingleFile: (file: File) => Promise<UploadedFile>
  isUploading: boolean
  uploadProgress: { [fileId: string]: number }
  error: string | null
  clearError: () => void
}

export function useFileUpload(options: UseFileUploadOptions = {}): UseFileUploadReturn {
  const {
    multiple = true,
    onSuccess,
    onError
  } = options

  const { uploadFile, isUploading, uploadProgress } = useFileStore()
  const [error, setError] = useState<string | null>(null)
  const [localProgress] = useState<{ [fileId: string]: number }>({})

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const uploadSingleFile = useCallback(async (file: File): Promise<UploadedFile> => {
    setError(null)

    try {
      // Validate file
      const { invalid } = validateFiles([file])
      if (invalid.length > 0) {
        const errorMessage = `${file.name}: ${invalid[0].errors.join(', ')}`
        setError(errorMessage)
        onError?.(errorMessage)
        throw new Error(errorMessage)
      }

      // Upload file
      const uploadedFile = await uploadFile(file)
      onSuccess?.([ uploadedFile])
      return uploadedFile

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed'
      setError(errorMessage)
      onError?.(errorMessage)
      throw err
    }
  }, [uploadFile, onSuccess, onError])

  const uploadFiles = useCallback(async (files: File[]): Promise<UploadedFile[]> => {
    setError(null)

    if (!multiple && files.length > 1) {
      const errorMessage = 'Multiple files not allowed'
      setError(errorMessage)
      onError?.(errorMessage)
      throw new Error(errorMessage)
    }

    try {
      // Validate all files first
      const { valid, invalid } = validateFiles(files)
      
      if (invalid.length > 0) {
        const errorMessage = `Invalid files: ${invalid.map(i => `${i.file.name} (${i.errors.join(', ')})`).join(', ')}`
        setError(errorMessage)
        onError?.(errorMessage)
        throw new Error(errorMessage)
      }

      // Upload all valid files
      const uploadPromises = valid.map(file => uploadFile(file))
      const uploadedFiles = await Promise.all(uploadPromises)
      
      onSuccess?.(uploadedFiles)
      return uploadedFiles

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed'
      setError(errorMessage)
      onError?.(errorMessage)
      throw err
    }
  }, [uploadFile, multiple, onSuccess, onError])

  // Combine store progress with local progress
  const combinedProgress = { ...uploadProgress, ...localProgress }

  return {
    uploadFiles,
    uploadSingleFile,
    isUploading,
    uploadProgress: Object.fromEntries(
      Object.entries(combinedProgress).map(([fileId, progress]) => [
        fileId,
        typeof progress === 'object' ? progress.progress : progress
      ])
    ),
    error,
    clearError
  }
}

// Hook specifically for CSV uploads
export function useCSVUpload(options: Omit<UseFileUploadOptions, 'acceptedTypes'> = {}) {
  return useFileUpload({
    ...options,
    acceptedTypes: ['text/csv']
  })
}

// Hook for image uploads
export function useImageUpload(options: Omit<UseFileUploadOptions, 'acceptedTypes'> = {}) {
  return useFileUpload({
    ...options,
    acceptedTypes: ['image/*']
  })
}

// Hook for drag and drop functionality
export function useDragAndDrop(onDrop: (files: File[]) => void) {
  const [isDragActive, setIsDragActive] = useState(false)

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      onDrop(files)
    }
  }, [onDrop])

  return {
    isDragActive,
    dragProps: {
      onDragEnter: handleDragEnter,
      onDragLeave: handleDragLeave,
      onDragOver: handleDragOver,
      onDrop: handleDrop
    }
  }
}
