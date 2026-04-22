/**
 * Toast 组件测试
 */
import { render, screen, fireEvent } from '@testing-library/react'
import ToastContainer from '@/components/ui/Toast'
import { useToastStore } from '@/lib/store'

describe('ToastContainer', () => {
  beforeEach(() => {
    useToastStore.getState().clearToasts()
  })

  it('renders nothing when no toasts', () => {
    const { container } = render(<ToastContainer />)
    expect(container.firstChild).toBeNull()
  })

  it('renders toast messages', () => {
    useToastStore.getState().addToast({ type: 'success', message: 'Saved!' })
    useToastStore.getState().addToast({ type: 'error', message: 'Failed!' })

    render(<ToastContainer />)
    expect(screen.getByText('Saved!')).toBeInTheDocument()
    expect(screen.getByText('Failed!')).toBeInTheDocument()
  })

  it('removes toast when close button is clicked', () => {
    useToastStore.getState().addToast({ type: 'info', message: 'Closable', duration: 0 })

    render(<ToastContainer />)
    expect(screen.getByText('Closable')).toBeInTheDocument()

    fireEvent.click(screen.getByTitle('') || screen.getAllByRole('button')[0])
    expect(useToastStore.getState().toasts).toHaveLength(0)
  })

  it('renders different toast types with correct icons', () => {
    useToastStore.getState().addToast({ type: 'success', message: 'OK', duration: 0 })
    useToastStore.getState().addToast({ type: 'error', message: 'Err', duration: 0 })
    useToastStore.getState().addToast({ type: 'warning', message: 'Warn', duration: 0 })
    useToastStore.getState().addToast({ type: 'info', message: 'Info', duration: 0 })

    render(<ToastContainer />)
    expect(screen.getByText('✓')).toBeInTheDocument()
    expect(screen.getByText('✕')).toBeInTheDocument()
    expect(screen.getByText('⚠')).toBeInTheDocument()
    expect(screen.getByText('ℹ')).toBeInTheDocument()
  })
})
