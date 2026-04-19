/**
 * Toast 通知组件
 */
'use client'

import { useToastStore, ToastType } from '@/lib/store'

const toastStyles: Record<ToastType, string> = {
  success: 'bg-green-600 border-green-500',
  error: 'bg-red-600 border-red-500',
  warning: 'bg-yellow-600 border-yellow-500',
  info: 'bg-blue-600 border-blue-500',
}

const toastIcons: Record<ToastType, string> = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
}

export default function ToastContainer() {
  const { toasts, removeToast } = useToastStore()

  if (toasts.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`
            ${toastStyles[toast.type]}
            border-l-4 rounded-lg shadow-lg p-4
            flex items-start gap-3
            animate-slide-in
            transition-all duration-300
          `}
        >
          <span className="text-lg">{toastIcons[toast.type]}</span>
          <p className="text-white text-sm flex-1">{toast.message}</p>
          <button
            onClick={() => removeToast(toast.id)}
            className="text-white/70 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>
      ))}

      <style jsx>{`
        @keyframes slide-in {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
    </div>
  )
}
