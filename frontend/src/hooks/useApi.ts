import { useState, useCallback, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/utils/api'
import type { APIResponse } from '@/types'

// Generic hook for API requests
export function useApiRequest<T>(
  queryKey: string[],
  queryFn: () => Promise<APIResponse<T>>,
  options?: {
    enabled?: boolean
    staleTime?: number
    refetchInterval?: number
  }
) {
  const { enabled = true, staleTime = 5 * 60 * 1000, refetchInterval } = options || {}

  return useQuery({
    queryKey,
    queryFn: async () => {
      const response = await queryFn()
      if (!response.success) {
        throw new Error(response.error || 'API request failed')
      }
      return response.data!
    },
    enabled,
    staleTime,
    refetchInterval,
    retry: 1,
  })
}

// Hook for agent-related API calls
export function useAgentApi() {
  const queryClient = useQueryClient()

  const agentsQuery = useApiRequest(
    ['agents'],
    api.agent.getAgents,
    { staleTime: 10 * 60 * 1000 } // 10 minutes
  )

  const currentAgentQuery = useApiRequest(
    ['agents', 'current'],
    api.agent.getCurrentAgent,
    { staleTime: 1 * 60 * 1000 } // 1 minute
  )

  const switchAgentMutation = useMutation({
    mutationFn: (agentId: string) => api.agent.switchAgent(agentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents', 'current'] })
    },
  })

  const getCapabilities = useCallback(async (agentId: string) => {
    const response = await api.agent.getAgentCapabilities(agentId)
    if (!response.success) {
      throw new Error(response.error || 'Failed to get capabilities')
    }
    return response.data!
  }, [])

  return {
    agents: agentsQuery.data || [],
    currentAgent: currentAgentQuery.data,
    isLoading: agentsQuery.isLoading || currentAgentQuery.isLoading,
    error: agentsQuery.error || currentAgentQuery.error,
    switchAgent: switchAgentMutation.mutateAsync,
    isSwitching: switchAgentMutation.isPending,
    getCapabilities,
    refetch: () => {
      agentsQuery.refetch()
      currentAgentQuery.refetch()
    }
  }
}

// Hook for file-related API calls
export function useFileApi() {
  const queryClient = useQueryClient()

  const fileHistoryQuery = useApiRequest(
    ['files'],
    api.file.getFileHistory,
    { staleTime: 2 * 60 * 1000 } // 2 minutes
  )

  const uploadFileMutation = useMutation({
    mutationFn: ({ file, onProgress }: { file: File; onProgress?: (progress: number) => void }) =>
      api.file.uploadFile(file, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] })
    },
  })

  const uploadCSVMutation = useMutation({
    mutationFn: ({ 
      file, 
      content, 
      onProgress 
    }: { 
      file: File
      content: string
      onProgress?: (progress: number) => void 
    }) => api.file.uploadCSV(file, content, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] })
    },
  })

  const deleteFileMutation = useMutation({
    mutationFn: (fileId: string) => api.file.deleteFile(fileId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] })
    },
  })

  return {
    files: fileHistoryQuery.data || [],
    isLoading: fileHistoryQuery.isLoading,
    error: fileHistoryQuery.error,
    uploadFile: uploadFileMutation.mutateAsync,
    uploadCSV: uploadCSVMutation.mutateAsync,
    deleteFile: deleteFileMutation.mutateAsync,
    isUploading: uploadFileMutation.isPending || uploadCSVMutation.isPending,
    isDeleting: deleteFileMutation.isPending,
    refetch: fileHistoryQuery.refetch
  }
}

// Hook for system status
export function useSystemStatus() {
  return useApiRequest(
    ['system', 'status'],
    api.system.getStatus,
    { 
      refetchInterval: 30 * 1000, // 30 seconds
      staleTime: 10 * 1000 // 10 seconds
    }
  )
}

// Hook for handling API errors
export function useApiError() {
  const [error, setError] = useState<string | null>(null)

  const handleError = useCallback((err: unknown) => {
    if (err instanceof Error) {
      setError(err.message)
    } else if (typeof err === 'string') {
      setError(err)
    } else {
      setError('An unknown error occurred')
    }
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    error,
    handleError,
    clearError,
    hasError: error !== null
  }
}

// Hook for retry logic
export function useRetry() {
  const [retryCount, setRetryCount] = useState(0)
  const [isRetrying, setIsRetrying] = useState(false)

  const retry = useCallback(async <T>(
    operation: () => Promise<T>,
    maxRetries: number = 3,
    delay: number = 1000
  ): Promise<T> => {
    setIsRetrying(true)
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const result = await operation()
        setRetryCount(0)
        setIsRetrying(false)
        return result
      } catch (error) {
        setRetryCount(attempt + 1)
        
        if (attempt === maxRetries) {
          setIsRetrying(false)
          throw error
        }
        
        // Exponential backoff
        const waitTime = delay * Math.pow(2, attempt)
        await new Promise(resolve => setTimeout(resolve, waitTime))
      }
    }
    
    throw new Error('Max retries exceeded')
  }, [])

  const reset = useCallback(() => {
    setRetryCount(0)
    setIsRetrying(false)
  }, [])

  return {
    retry,
    retryCount,
    isRetrying,
    reset
  }
}

// Hook for polling data
export function usePolling<T>(
  queryFn: () => Promise<APIResponse<T>>,
  interval: number = 30000, // 30 seconds
  enabled: boolean = true
) {
  const [data, setData] = useState<T | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    if (!enabled) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await queryFn()
      if (response.success && response.data) {
        setData(response.data)
      } else {
        setError(response.error || 'Failed to fetch data')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }, [queryFn, enabled])

  useEffect(() => {
    if (!enabled) return

    // Initial fetch
    fetchData()

    // Set up polling
    const intervalId = setInterval(fetchData, interval)

    return () => clearInterval(intervalId)
  }, [fetchData, interval, enabled])

  return {
    data,
    isLoading,
    error,
    refetch: fetchData
  }
}

// Hook for debounced API calls
export function useDebouncedApi<T>(
  apiCall: (query: string) => Promise<APIResponse<T>>,
  delay: number = 300
) {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Debounce the query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query)
    }, delay)

    return () => clearTimeout(timer)
  }, [query, delay])

  // Make API call when debounced query changes
  useEffect(() => {
    if (!debouncedQuery) {
      setData(null)
      return
    }

    const fetchData = async () => {
      setIsLoading(true)
      setError(null)

      try {
        const response = await apiCall(debouncedQuery)
        if (response.success && response.data) {
          setData(response.data)
        } else {
          setError(response.error || 'Search failed')
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [debouncedQuery, apiCall])

  return {
    query,
    setQuery,
    data,
    isLoading,
    error,
    clearError: () => setError(null)
  }
}
