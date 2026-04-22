/**
 * Store 测试 - Zustand 状态管理
 */
import { useToastStore, toast, useLoadingStore } from '@/lib/store'

describe('useToastStore', () => {
  beforeEach(() => {
    useToastStore.getState().clearToasts()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  it('adds a toast', () => {
    useToastStore.getState().addToast({ type: 'success', message: 'Test' })
    expect(useToastStore.getState().toasts).toHaveLength(1)
    expect(useToastStore.getState().toasts[0].message).toBe('Test')
    expect(useToastStore.getState().toasts[0].type).toBe('success')
  })

  it('removes a toast', () => {
    useToastStore.getState().addToast({ type: 'info', message: 'To remove' })
    const id = useToastStore.getState().toasts[0].id
    useToastStore.getState().removeToast(id)
    expect(useToastStore.getState().toasts).toHaveLength(0)
  })

  it('clears all toasts', () => {
    useToastStore.getState().addToast({ type: 'success', message: 'A' })
    useToastStore.getState().addToast({ type: 'error', message: 'B' })
    useToastStore.getState().clearToasts()
    expect(useToastStore.getState().toasts).toHaveLength(0)
  })

  it('auto-removes toast after duration', () => {
    useToastStore.getState().addToast({ type: 'info', message: 'Auto', duration: 1000 })
    expect(useToastStore.getState().toasts).toHaveLength(1)
    jest.advanceTimersByTime(1000)
    expect(useToastStore.getState().toasts).toHaveLength(0)
  })

  it('does not auto-remove toast when duration is 0', () => {
    useToastStore.getState().addToast({ type: 'info', message: 'Persistent', duration: 0 })
    jest.advanceTimersByTime(10000)
    expect(useToastStore.getState().toasts).toHaveLength(1)
  })
})

describe('toast convenience methods', () => {
  beforeEach(() => {
    useToastStore.getState().clearToasts()
  })

  it('toast.success adds success toast', () => {
    toast.success('OK')
    const t = useToastStore.getState().toasts[0]
    expect(t.type).toBe('success')
    expect(t.message).toBe('OK')
  })

  it('toast.error adds error toast', () => {
    toast.error('Fail')
    expect(useToastStore.getState().toasts[0].type).toBe('error')
  })

  it('toast.warning adds warning toast', () => {
    toast.warning('Careful')
    expect(useToastStore.getState().toasts[0].type).toBe('warning')
  })

  it('toast.info adds info toast', () => {
    toast.info('FYI')
    expect(useToastStore.getState().toasts[0].type).toBe('info')
  })
})

describe('useLoadingStore', () => {
  it('sets loading state', () => {
    useLoadingStore.getState().setLoading(true, 'Loading data...')
    expect(useLoadingStore.getState().isLoading).toBe(true)
    expect(useLoadingStore.getState().loadingText).toBe('Loading data...')
  })

  it('resets loading state with default text', () => {
    useLoadingStore.getState().setLoading(true, 'Custom')
    useLoadingStore.getState().setLoading(false)
    expect(useLoadingStore.getState().isLoading).toBe(false)
    expect(useLoadingStore.getState().loadingText).toBe('Loading...')
  })
})
