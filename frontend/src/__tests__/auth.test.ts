/**
 * Auth 工具函数测试
 */
import { tokenStorage, userStorage } from '@/lib/auth'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} },
  }
})()

Object.defineProperty(window, 'localStorage', { value: localStorageMock })

describe('tokenStorage', () => {
  beforeEach(() => {
    localStorageMock.clear()
  })

  it('sets and gets token', () => {
    tokenStorage.set('test-token')
    expect(tokenStorage.get()).toBe('test-token')
  })

  it('returns null when no token', () => {
    expect(tokenStorage.get()).toBeNull()
  })

  it('removes token', () => {
    tokenStorage.set('test-token')
    tokenStorage.remove()
    expect(tokenStorage.get()).toBeNull()
  })

  it('checks authentication status', () => {
    expect(tokenStorage.isAuthenticated()).toBe(false)
    tokenStorage.set('test-token')
    expect(tokenStorage.isAuthenticated()).toBe(true)
  })
})

describe('userStorage', () => {
  beforeEach(() => {
    localStorageMock.clear()
  })

  it('sets and gets user', () => {
    const user = { id: '1', username: 'test', email: 'test@example.com', preferences: {} }
    userStorage.set(user)
    expect(userStorage.get()).toEqual(user)
  })

  it('returns null when no user', () => {
    expect(userStorage.get()).toBeNull()
  })

  it('removes user', () => {
    const user = { id: '1', username: 'test', email: 'test@example.com', preferences: {} }
    userStorage.set(user)
    userStorage.remove()
    expect(userStorage.get()).toBeNull()
  })
})
