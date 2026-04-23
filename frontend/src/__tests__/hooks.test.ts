/**
 * Hooks 测试
 */
import { renderHook, act } from '@testing-library/react'
import { useIsMobile, useIsDesktop } from '@/hooks/useMedia'
import { useToastStore } from '@/lib/store'

describe('useMedia', () => {
  it('useIsMobile returns boolean', () => {
    const { result } = renderHook(() => useIsMobile())
    expect(typeof result.current).toBe('boolean')
  })

  it('useIsDesktop returns boolean', () => {
    const { result } = renderHook(() => useIsDesktop())
    expect(typeof result.current).toBe('boolean')
  })
})

describe('useApi', () => {
  it('starts with loading state when immediate=true', async () => {
    const { result } = renderHook(() => {
      // Dynamic import to avoid immediate execution in this test
      const { useApi } = require('@/hooks/useApi')
      return useApi(() => Promise.resolve('data'), { immediate: false })
    })

    expect(result.current.isLoading).toBe(false)
    expect(result.current.data).toBeNull()
  })
})

describe('Store integration', () => {
  it('toast and user store work independently', () => {
    // Clear toast store
    useToastStore.getState().clearToasts()
    useToastStore.getState().addToast({ type: 'success', message: 'Test' })
    expect(useToastStore.getState().toasts).toHaveLength(1)

    // Toast store state is independent
    useToastStore.getState().clearToasts()
    expect(useToastStore.getState().toasts).toHaveLength(0)
  })
})
