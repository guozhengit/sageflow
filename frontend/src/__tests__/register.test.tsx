/**
 * Register 页面测试
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import RegisterPage from '@/app/register/page'

// Mock next/navigation
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}))

// Mock userApi
jest.mock('@/lib/services', () => ({
  userApi: {
    register: jest.fn(),
  },
}))

import { userApi } from '@/lib/services'
const mockRegister = userApi.register as jest.Mock

describe('RegisterPage', () => {
  beforeEach(() => {
    mockRegister.mockClear()
    mockPush.mockClear()
  })

  it('renders register form', () => {
    render(<RegisterPage />)
    expect(screen.getByText('Sign Up')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Choose a username')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('your@email.com')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('At least 6 characters')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Repeat your password')).toBeInTheDocument()
  })

  it('shows error when passwords do not match', async () => {
    render(<RegisterPage />)

    fireEvent.change(screen.getByPlaceholderText('Choose a username'), { target: { value: 'testuser' } })
    fireEvent.change(screen.getByPlaceholderText('your@email.com'), { target: { value: 'test@test.com' } })
    fireEvent.change(screen.getByPlaceholderText('At least 6 characters'), { target: { value: '123456' } })
    fireEvent.change(screen.getByPlaceholderText('Repeat your password'), { target: { value: '654321' } })
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }))

    await waitFor(() => {
      expect(screen.getByText('Passwords do not match')).toBeInTheDocument()
    })
    expect(mockRegister).not.toHaveBeenCalled()
  })

  it('shows error when password is too short', async () => {
    render(<RegisterPage />)

    fireEvent.change(screen.getByPlaceholderText('Choose a username'), { target: { value: 'testuser' } })
    fireEvent.change(screen.getByPlaceholderText('your@email.com'), { target: { value: 'test@test.com' } })
    fireEvent.change(screen.getByPlaceholderText('At least 6 characters'), { target: { value: '123' } })
    fireEvent.change(screen.getByPlaceholderText('Repeat your password'), { target: { value: '123' } })
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }))

    await waitFor(() => {
      expect(screen.getByText('Password must be at least 6 characters')).toBeInTheDocument()
    })
  })

  it('calls register and redirects on success', async () => {
    mockRegister.mockResolvedValue({ id: '1', username: 'newuser' })
    render(<RegisterPage />)

    fireEvent.change(screen.getByPlaceholderText('Choose a username'), { target: { value: 'newuser' } })
    fireEvent.change(screen.getByPlaceholderText('your@email.com'), { target: { value: 'new@test.com' } })
    fireEvent.change(screen.getByPlaceholderText('At least 6 characters'), { target: { value: '123456' } })
    fireEvent.change(screen.getByPlaceholderText('Repeat your password'), { target: { value: '123456' } })
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }))

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        username: 'newuser', email: 'new@test.com', password: '123456',
      })
      expect(mockPush).toHaveBeenCalledWith('/login')
    })
  })

  it('has link to login page', () => {
    render(<RegisterPage />)
    expect(screen.getByText('Sign in')).toBeInTheDocument()
  })
})
