/**
 * 全局状态管理 - 使用 Zustand
 */
import { create } from 'zustand'

// ============ Toast 状态 ============

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: string
  type: ToastType
  message: string
  duration?: number
}

interface ToastState {
  toasts: Toast[]
  addToast: (toast: Omit<Toast, 'id'>) => void
  removeToast: (id: string) => void
  clearToasts: () => void
}

export const useToastStore = create<ToastState>((set, get) => ({
  toasts: [],

  addToast: (toast) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    const newToast: Toast = { ...toast, id }

    set((state) => ({
      toasts: [...state.toasts, newToast]
    }))

    // 自动移除
    const duration = toast.duration ?? 5000
    if (duration > 0) {
      setTimeout(() => {
        get().removeToast(id)
      }, duration)
    }
  },

  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id)
    }))
  },

  clearToasts: () => {
    set({ toasts: [] })
  }
}))

// 便捷方法
export const toast = {
  success: (message: string, duration?: number) =>
    useToastStore.getState().addToast({ type: 'success', message, duration }),
  error: (message: string, duration?: number) =>
    useToastStore.getState().addToast({ type: 'error', message, duration }),
  warning: (message: string, duration?: number) =>
    useToastStore.getState().addToast({ type: 'warning', message, duration }),
  info: (message: string, duration?: number) =>
    useToastStore.getState().addToast({ type: 'info', message, duration }),
}

// ============ Loading 状态 ============

interface LoadingState {
  isLoading: boolean
  loadingText: string
  setLoading: (loading: boolean, text?: string) => void
}

export const useLoadingStore = create<LoadingState>((set) => ({
  isLoading: false,
  loadingText: 'Loading...',

  setLoading: (loading, text = 'Loading...') => {
    set({
      isLoading: loading,
      loadingText: text
    })
  }
}))

// ============ User 状态 ============

export interface UserInfo {
  id: string
  username: string
  email: string
  preferences: Record<string, any>
}

interface UserState {
  user: UserInfo | null
  isAuthenticated: boolean
  setUser: (user: UserInfo | null) => void
  clearUser: () => void
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  isAuthenticated: false,

  setUser: (user) => {
    set({ user, isAuthenticated: !!user })
  },

  clearUser: () => {
    set({ user: null, isAuthenticated: false })
  },
}))

// ============ Conversation 状态 ============

export interface ConversationInfo {
  id: string
  title: string
  message_count?: number
  updated_at?: string
}

interface ConversationState {
  conversations: ConversationInfo[]
  currentConversationId: string | null
  isLoading: boolean
  setConversations: (conversations: ConversationInfo[]) => void
  addConversation: (conversation: ConversationInfo) => void
  removeConversation: (id: string) => void
  setCurrentConversationId: (id: string | null) => void
  setLoading: (loading: boolean) => void
}

export const useConversationStore = create<ConversationState>((set) => ({
  conversations: [],
  currentConversationId: null,
  isLoading: false,

  setConversations: (conversations) => {
    set({ conversations })
  },

  addConversation: (conversation) => {
    set((state) => ({
      conversations: [conversation, ...state.conversations],
    }))
  },

  removeConversation: (id) => {
    set((state) => ({
      conversations: state.conversations.filter((c) => c.id !== id),
      currentConversationId: state.currentConversationId === id ? null : state.currentConversationId,
    }))
  },

  setCurrentConversationId: (id) => {
    set({ currentConversationId: id })
  },

  setLoading: (loading) => {
    set({ isLoading: loading })
  },
}))
