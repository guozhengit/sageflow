/** Authentication state Hook */
'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { userApi, type UserProfile } from '@/lib/services'
import { tokenStorage, userStorage } from '@/lib/auth'
import { toast } from '@/lib/store'

interface AuthState {
  user: UserProfile | null
  isAuthenticated: boolean
  isLoading: boolean
}

export function useAuth() {
  const router = useRouter()
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  })

  useEffect(() => {
    const token = tokenStorage.get()
    const cachedUser = userStorage.get()

    if (token && cachedUser) {
      setState({ user: cachedUser, isAuthenticated: true, isLoading: false })
    } else if (token) {
      // Token exists but no cached user, fetch profile
      userApi.getProfile()
        .then((profile) => {
          setState({ user: profile, isAuthenticated: true, isLoading: false })
        })
        .catch(() => {
          tokenStorage.remove()
          userStorage.remove()
          setState({ user: null, isAuthenticated: false, isLoading: false })
        })
    } else {
      setState({ user: null, isAuthenticated: false, isLoading: false })
    }
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    try {
      await userApi.login({ username, password })
      const profile = await userApi.getProfile()
      setState({ user: profile, isAuthenticated: true, isLoading: false })
      toast.success('Login successful')
      router.push('/chat')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed')
      throw error
    }
  }, [router])

  const logout = useCallback(() => {
    userApi.logout()
    setState({ user: null, isAuthenticated: false, isLoading: false })
    toast.success('Logged out')
    router.push('/login')
  }, [router])

  const refreshProfile = useCallback(async () => {
    try {
      const profile = await userApi.getProfile()
      setState((prev) => ({ ...prev, user: profile }))
    } catch {
      // Silently fail, keep cached data
    }
  }, [])

  return {
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    login,
    logout,
    refreshProfile,
  }
}
