import { FILE_UPLOAD_CONFIG, FILE_TYPE_ICONS } from './constants'

// File size formatting
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// File type validation
export function isValidFileType(file: File): boolean {
  const supportedTypes = Object.keys(FILE_UPLOAD_CONFIG.supportedTypes)
  
  return supportedTypes.some(type => {
    if (type.includes('*')) {
      // Handle wildcard types like 'image/*'
      const baseType = type.split('/')[0]
      return file.type.startsWith(baseType + '/')
    }
    return file.type === type
  })
}

// File size validation
export function isValidFileSize(file: File): boolean {
  return file.size <= FILE_UPLOAD_CONFIG.maxFileSize
}

// Get file extension
export function getFileExtension(filename: string): string {
  return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2).toLowerCase()
}

// Check if file is CSV
export function isCSVFile(file: File): boolean {
  return file.type === 'text/csv' || file.name.toLowerCase().endsWith('.csv')
}

// Check if file is image
export function isImageFile(file: File): boolean {
  return file.type.startsWith('image/')
}

// Check if file is text-based
export function isTextFile(file: File): boolean {
  const textTypes = ['text/plain', 'text/csv', 'application/json']
  return textTypes.includes(file.type)
}

// Read file as text
export async function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (event) => {
      if (event.target?.result) {
        resolve(event.target.result as string)
      } else {
        reject(new Error('Failed to read file'))
      }
    }
    
    reader.onerror = () => {
      reject(new Error('Error reading file'))
    }
    
    reader.readAsText(file)
  })
}

// Read file as data URL (for images)
export async function readFileAsDataURL(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (event) => {
      if (event.target?.result) {
        resolve(event.target.result as string)
      } else {
        reject(new Error('Failed to read file'))
      }
    }
    
    reader.onerror = () => {
      reject(new Error('Error reading file'))
    }
    
    reader.readAsDataURL(file)
  })
}

// Validate CSV content structure
export function validateCSVContent(content: string): { isValid: boolean; errors: string[] } {
  const errors: string[] = []
  
  if (!content.trim()) {
    errors.push('CSV file is empty')
    return { isValid: false, errors }
  }
  
  const lines = content.split('\n').filter(line => line.trim())
  
  if (lines.length < 2) {
    errors.push('CSV file must have at least a header row and one data row')
    return { isValid: false, errors }
  }
  
  // Check if all rows have the same number of columns
  const headerColumns = lines[0].split(',').length
  const inconsistentRows = lines.slice(1).filter(line => {
    const columns = line.split(',').length
    return columns !== headerColumns
  })
  
  if (inconsistentRows.length > 0) {
    errors.push(`Found ${inconsistentRows.length} rows with inconsistent column count`)
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

// Parse CSV content to get basic statistics
export function getCSVStats(content: string): {
  rows: number
  columns: number
  headers: string[]
  sampleData: string[][]
} {
  const lines = content.split('\n').filter(line => line.trim())
  
  if (lines.length === 0) {
    return { rows: 0, columns: 0, headers: [], sampleData: [] }
  }
  
  const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
  const sampleData = lines.slice(1, 6).map(line => 
    line.split(',').map(cell => cell.trim().replace(/"/g, ''))
  )
  
  return {
    rows: lines.length - 1, // Exclude header
    columns: headers.length,
    headers,
    sampleData
  }
}

// Generate unique file ID
export function generateFileId(): string {
  return crypto.randomUUID()
}

// Get file icon name based on type
export function getFileIconName(fileType: string): string {
  return FILE_TYPE_ICONS[fileType as keyof typeof FILE_TYPE_ICONS] || 'File'
}

// Create file preview data
export function createFilePreview(file: File): {
  id: string
  name: string
  size: string
  type: string
  extension: string
  isImage: boolean
  isText: boolean
  isCSV: boolean
} {
  return {
    id: generateFileId(),
    name: file.name,
    size: formatFileSize(file.size),
    type: file.type,
    extension: getFileExtension(file.name),
    isImage: isImageFile(file),
    isText: isTextFile(file),
    isCSV: isCSVFile(file)
  }
}

// Validate multiple files
export function validateFiles(files: File[]): {
  valid: File[]
  invalid: Array<{ file: File; errors: string[] }>
} {
  const valid: File[] = []
  const invalid: Array<{ file: File; errors: string[] }> = []
  
  files.forEach(file => {
    const errors: string[] = []
    
    if (!isValidFileType(file)) {
      errors.push('File type not supported')
    }
    
    if (!isValidFileSize(file)) {
      errors.push(`File size exceeds ${formatFileSize(FILE_UPLOAD_CONFIG.maxFileSize)} limit`)
    }
    
    if (errors.length === 0) {
      valid.push(file)
    } else {
      invalid.push({ file, errors })
    }
  })
  
  return { valid, invalid }
}

// Download file content as blob
export function downloadFile(content: string, filename: string, mimeType: string = 'text/plain'): void {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// Copy text to clipboard
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
      return true
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      
      const success = document.execCommand('copy')
      document.body.removeChild(textArea)
      return success
    }
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
    return false
  }
}

// Debounce function for file operations
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout)
    }
    
    timeout = setTimeout(() => {
      func(...args)
    }, wait)
  }
}
