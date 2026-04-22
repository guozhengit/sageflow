/** Data fetching Hook with loading/error states */
'use client'

import { useState, useEffect, useCallback, useRef } from 'react'

interface ApiState<T> {
  data: T | null
  error: string | null
  isLoading: boolean
}

interface UseApiOptions {
  immediate?: boolean  // Fetch on mount (default: true)
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  options: UseApiOptions = {}
) {
  const { immediate = true } = options
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    error: null,
    isLoading: immediate,
  })
  const fetcherRef = useRef(fetcher)
  fetcherRef.current = fetcher

  const execute = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }))
    try {
      const data = await fetcherRef.current()
      setState({ data, error: null, isLoading: false })
      return data
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Request failed'
      setState((prev) => ({ ...prev, error: message, isLoading: false }))
      throw error
    }
  }, [])

  useEffect(() => {
    if (immediate) {
      execute()
    }
  }, [immediate, execute])

  const reset = useCallback(() => {
    setState({ data: null, error: null, isLoading: false })
  }, [])

  return {
    ...state,
    execute,
    reset,
  }
}
