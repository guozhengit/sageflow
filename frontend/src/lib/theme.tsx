/** Theme provider and hooks. */
'use client'

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'

type Theme = 'dark' | 'light' | 'system'

interface ThemeContextType {
  theme: Theme
  resolvedTheme: 'dark' | 'light'
  toggleTheme: () => void
  setTheme: (theme: Theme) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)
const THEME_STORAGE_KEY = 'sageflow_theme'

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>('system')
  const [resolvedTheme, setResolvedTheme] = useState<'dark' | 'light'>('dark')

  const getResolvedTheme = useCallback((value: Theme): 'dark' | 'light' => {
    if (value === 'system') {
      if (typeof window !== 'undefined') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      }
      return 'dark'
    }
    return value
  }, [])

  const applyTheme = useCallback((resolved: 'dark' | 'light') => {
    const root = document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(resolved)

    const metaThemeColor = document.querySelector('meta[name="theme-color"]')
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', resolved === 'dark' ? '#0f172a' : '#f8fafc')
    }
  }, [])

  useEffect(() => {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as Theme | null
    const initialTheme = savedTheme || 'system'
    setThemeState(initialTheme)

    const resolved = getResolvedTheme(initialTheme)
    setResolvedTheme(resolved)
    applyTheme(resolved)
  }, [applyTheme, getResolvedTheme])

  useEffect(() => {
    if (theme !== 'system') return

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = (e: MediaQueryListEvent) => {
      const nextResolved = e.matches ? 'dark' : 'light'
      setResolvedTheme(nextResolved)
      applyTheme(nextResolved)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme, applyTheme])

  const setTheme = useCallback((nextTheme: Theme) => {
    setThemeState(nextTheme)
    localStorage.setItem(THEME_STORAGE_KEY, nextTheme)

    const resolved = getResolvedTheme(nextTheme)
    setResolvedTheme(resolved)
    applyTheme(resolved)
  }, [applyTheme, getResolvedTheme])

  const toggleTheme = useCallback(() => {
    const nextTheme = resolvedTheme === 'dark' ? 'light' : 'dark'
    setTheme(nextTheme)
  }, [resolvedTheme, setTheme])

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
