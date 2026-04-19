/** 快捷键 Hook */
'use client'

import { useEffect, useCallback } from 'react'

interface ShortcutConfig {
  key: string
  ctrlKey?: boolean
  shiftKey?: boolean
  altKey?: boolean
  handler: () => void
}

export function useShortcuts(shortcuts: ShortcutConfig[]) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      for (const shortcut of shortcuts) {
        const matches =
          e.key.toLowerCase() === shortcut.key.toLowerCase() &&
          !!e.ctrlKey === !!shortcut.ctrlKey &&
          !!e.shiftKey === !!shortcut.shiftKey &&
          !!e.altKey === !!shortcut.altKey

        if (matches) {
          e.preventDefault()
          shortcut.handler()
        }
      }
    },
    [shortcuts]
  )

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])
}

/** 常用快捷键配置 */
export const SHORTCUTS = {
  SEND_MESSAGE: { key: 'Enter', ctrlKey: true },
  NEW_CONVERSATION: { key: 'n', ctrlKey: true },
  FOCUS_INPUT: { key: '/', ctrlKey: true },
  TOGGLE_SIDEBAR: { key: 'b', ctrlKey: true },
} as const
