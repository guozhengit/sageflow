'use client'

import { useTheme } from '@/lib/theme'

export default function ThemeToggle() {
  const { resolvedTheme, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg bg-sage-800 hover:bg-sage-700 transition-colors"
      title={resolvedTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
      aria-label={resolvedTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
    >
      {resolvedTheme === 'dark' ? '☀️' : '🌙'}
    </button>
  )
}
