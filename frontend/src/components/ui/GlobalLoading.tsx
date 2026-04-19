/**
 * 全局 Loading 组件
 */
'use client'

import { useLoadingStore } from '@/lib/store'

export default function GlobalLoading() {
  const { isLoading, loadingText } = useLoadingStore()

  if (!isLoading) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-sage-950/80 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-4">
        {/* Spinner */}
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 border-4 border-sage-700 rounded-full"></div>
          <div className="absolute inset-0 border-4 border-transparent border-t-sage-400 rounded-full animate-spin"></div>
        </div>

        {/* Loading Text */}
        <p className="text-sage-300 text-sm animate-pulse">{loadingText}</p>
      </div>
    </div>
  )
}
