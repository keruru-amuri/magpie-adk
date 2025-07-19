import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { fileApi } from '@/utils/api'
import { validateFiles, isCSVFile, readFileAsText } from '@/utils/fileUtils'
import type { FileStore, UploadedFile } from '@/types'

export const useFileStore = create<FileStore>()(
  devtools(
    (set, get) => ({
      files: [],
      uploadProgress: {},
      isUploading: false,

      uploadFile: async (file: File): Promise<UploadedFile> => {
        const fileId = crypto.randomUUID()
        
        // Validate file
        const { invalid } = validateFiles([file])
        if (invalid.length > 0) {
          throw new Error(invalid[0].errors.join(', '))
        }

        // Create initial file object
        const uploadedFile: UploadedFile = {
          id: fileId,
          name: file.name,
          size: file.size,
          type: file.type,
          uploadedAt: new Date(),
          status: 'uploading'
        }

        // Add to store
        set(state => ({
          files: [...state.files, uploadedFile],
          uploadProgress: {
            ...state.uploadProgress,
            [fileId]: { fileId, progress: 0, stage: 'reading' }
          },
          isUploading: true
        }))

        try {
          let result

          if (isCSVFile(file)) {
            // Handle CSV files with workaround
            set(state => ({
              uploadProgress: {
                ...state.uploadProgress,
                [fileId]: { fileId, progress: 25, stage: 'reading' }
              }
            }))

            const content = await readFileAsText(file)
            
            set(state => ({
              uploadProgress: {
                ...state.uploadProgress,
                [fileId]: { fileId, progress: 50, stage: 'uploading' }
              }
            }))

            result = await fileApi.uploadCSV(file, content, (progress) => {
              set(state => ({
                uploadProgress: {
                  ...state.uploadProgress,
                  [fileId]: { 
                    fileId, 
                    progress: 50 + (progress * 0.5), 
                    stage: 'uploading' 
                  }
                }
              }))
            })

            // Update file with content
            if (result.success && result.data) {
              result.data.content = content
            }
          } else {
            // Handle regular files
            set(state => ({
              uploadProgress: {
                ...state.uploadProgress,
                [fileId]: { fileId, progress: 0, stage: 'uploading' }
              }
            }))

            result = await fileApi.uploadFile(file, (progress) => {
              set(state => ({
                uploadProgress: {
                  ...state.uploadProgress,
                  [fileId]: { fileId, progress, stage: 'uploading' }
                }
              }))
            })
          }

          if (!result.success || !result.data) {
            throw new Error(result.error || 'Upload failed')
          }

          // Update file status
          set(state => ({
            files: state.files.map(f => 
              f.id === fileId 
                ? { 
                    ...f, 
                    ...result.data,
                    id: fileId, // Keep our generated ID
                    status: 'uploaded' as const
                  }
                : f
            ),
            uploadProgress: {
              ...state.uploadProgress,
              [fileId]: { fileId, progress: 100, stage: 'complete' }
            }
          }))

          // Clean up progress after delay
          setTimeout(() => {
            set(state => {
              const newProgress = { ...state.uploadProgress }
              delete newProgress[fileId]
              return {
                uploadProgress: newProgress,
                isUploading: Object.keys(newProgress).length > 0
              }
            })
          }, 2000)

          return get().files.find(f => f.id === fileId)!

        } catch (error) {
          // Update file with error status
          const errorMessage = error instanceof Error ? error.message : 'Upload failed'
          
          set(state => ({
            files: state.files.map(f => 
              f.id === fileId 
                ? { ...f, status: 'error' as const, errorMessage }
                : f
            ),
            uploadProgress: {
              ...state.uploadProgress,
              [fileId]: { fileId, progress: 0, stage: 'complete' }
            }
          }))

          // Clean up progress after delay
          setTimeout(() => {
            set(state => {
              const newProgress = { ...state.uploadProgress }
              delete newProgress[fileId]
              return {
                uploadProgress: newProgress,
                isUploading: Object.keys(newProgress).length > 0
              }
            })
          }, 2000)

          throw error
        }
      },

      uploadCSV: async (file: File): Promise<UploadedFile> => {
        // This is handled by uploadFile method
        return get().uploadFile(file)
      },

      removeFile: (fileId: string) => {
        set(state => ({
          files: state.files.filter(f => f.id !== fileId),
          uploadProgress: (() => {
            const newProgress = { ...state.uploadProgress }
            delete newProgress[fileId]
            return newProgress
          })()
        }))

        // Also try to delete from backend
        fileApi.deleteFile(fileId).catch(error => {
          console.error('Failed to delete file from backend:', error)
        })
      },

      getFileHistory: async (): Promise<UploadedFile[]> => {
        try {
          const response = await fileApi.getFileHistory()
          if (response.success && response.data) {
            set({ files: response.data })
            return response.data
          }
          return []
        } catch (error) {
          console.error('Failed to fetch file history:', error)
          return []
        }
      }
    }),
    {
      name: 'file-store',
    }
  )
)
