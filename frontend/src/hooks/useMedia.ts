/** Responsive media query Hook */
'use client'

import { useState, useEffect } from 'react'

export function useMedia(query: string): boolean {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia(query)
    setMatches(mediaQuery.matches)

    const handler = (event: MediaQueryListEvent) => {
      setMatches(event.matches)
    }

    mediaQuery.addEventListener('change', handler)
    return () => mediaQuery.removeEventListener('change', handler)
  }, [query])

  return matches
}

/** Predefined breakpoint hooks (Tailwind defaults) */
export function useIsMobile() {
  return useMedia('(max-width: 767px)')
}

export function useIsTablet() {
  return useMedia('(min-width: 768px) and (max-width: 1023px)')
}

export function useIsDesktop() {
  return useMedia('(min-width: 1024px)')
}
