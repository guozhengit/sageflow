/**
 * Login 页面测试
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import LoginPage from '@/app/login/page'
import { useAuth } from '@/hooks/useAuth'

// Mock useAuth
jest.mock('@/hooks/useAuth', () => ({
  useAuth: jest.fn(),
}))

const mockLogin = jest.fn()
const mockUseAuth = useAuth as jest.Mock

beforeEach(() => {
  mockUseAuth.mockReturnValue({
    login: mockLogin,
    isAuthenticated: false,
    isLoading: false,
    user: null,
    logout: jest.fn(),
    refreshProfile: jest.fn(),
  })
  mockLogin.mockClear()
})

describe('LoginPage', () => {
  it('renders login form', () => {
    render(<LoginPage />)
    expect(screen.getByText('Sign In')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Enter your username')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Enter your password')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('shows SageFlow branding', () => {
    render(<LoginPage />)
    expect(screen.getByText('SageFlow')).toBeInTheDocument()
    expect(screen.getByText('Smart Q&A Solutions')).toBeInTheDocument()
  })

  it('has link to register page', () => {
    render(<LoginPage />)
    expect(screen.getByText('Sign up')).toBeInTheDocument()
  })

  it('calls login on form submit', async () => {
    mockLogin.mockResolvedValue(undefined)
    render(<LoginPage />)

    fireEvent.change(screen.getByPlaceholderText('Enter your username'), { target: { value: 'testuser' } })
    fireEvent.change(screen.getByPlaceholderText('Enter your password'), { target: { value: '123456' } })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('testuser', '123456')
    })
  })

  it('shows error on login failure', async () => {
    mockLogin.mockRejectedValue(new Error('Invalid credentials'))
    render(<LoginPage />)

    fireEvent.change(screen.getByPlaceholderText('Enter your username'), { target: { value: 'wrong' } })
    fireEvent.change(screen.getByPlaceholderText('Enter your password'), { target: { value: 'wrong' } })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(screen.getByText(/login failed/i)).toBeInTheDocument()
    })
  })
})
