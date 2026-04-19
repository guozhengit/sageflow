'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { conversationApi, userApi, type Conversation, type UserProfile } from '@/lib/services'
import { userStorage } from '@/lib/auth'
import ThemeToggle from '@/components/ui/ThemeToggle'

interface SidebarProps {
  activePath: string
  currentConversationId?: string
  onSelectConversation?: (id: string) => void
  onNewConversation?: () => void
  mobileOpen?: boolean
  onMobileClose?: () => void
}

export default function Sidebar({ activePath, currentConversationId, onSelectConversation, onNewConversation, mobileOpen, onMobileClose }: SidebarProps) {
  const router = useRouter()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      // 加载用户信息
      const cachedUser = userStorage.get()
      if (cachedUser) {
        setUser(cachedUser)
      } else {
        const profile = await userApi.getProfile()
        setUser(profile)
      }

      // 加载对话列表
      const convs = await conversationApi.list()
      setConversations(convs)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    userApi.logout()
    router.push('/login')
  }

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await conversationApi.delete(id)
      setConversations(conversations.filter(c => c.id !== id))
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    }
  }

  const navItems = [
    { href: '/', icon: '🏠', label: 'Home' },
    { href: '/chat', icon: '💬', label: 'Intelligent Answers' },
    { href: '/knowledge', icon: '📚', label: 'Knowledge Base' },
    { href: '/profile', icon: '👤', label: 'User Profile' },
  ]

  return (
    <>
      {/* Mobile Overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onMobileClose}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50 w-72 bg-sage-900 border-r border-sage-800 flex flex-col
        transform transition-transform duration-300 ease-in-out
        ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
      {/* Logo */}
      <div className="p-4 border-b border-sage-800 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl">🌿</span>
          <span className="text-xl font-bold text-white">SageFlow</span>
        </Link>
        <ThemeToggle />
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
              activePath === item.href
                ? 'bg-sage-800 text-white'
                : 'text-sage-300 hover:bg-sage-800'
            }`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      {/* Conversations */}
      <div className="flex-1 flex flex-col min-h-0">
        <div className="px-4 py-2 border-b border-sage-800">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-sage-400 uppercase">Conversations</h3>
            <button
              onClick={onNewConversation}
              className="text-sage-400 hover:text-white transition-colors"
              title="New Conversation"
            >
              ➕
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {loading ? (
            <div className="text-center py-4 text-sage-500">Loading...</div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-4 text-sage-500 text-sm">No conversations yet</div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => onSelectConversation?.(conv.id)}
                className={`group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                  currentConversationId === conv.id
                    ? 'bg-sage-700 text-white'
                    : 'text-sage-300 hover:bg-sage-800'
                }`}
              >
                <div className="flex-1 min-w-0">
                  <p className="truncate text-sm">{conv.title}</p>
                  {conv.message_count !== undefined && (
                    <p className="text-xs text-sage-500">{conv.message_count} messages</p>
                  )}
                </div>
                <button
                  onClick={(e) => handleDeleteConversation(conv.id, e)}
                  className="opacity-0 group-hover:opacity-100 text-sage-500 hover:text-red-400 transition-all p-1"
                >
                  🗑️
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* User Info */}
      {user && (
        <div className="p-4 border-t border-sage-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-8 h-8 rounded-full bg-sage-700 flex items-center justify-center flex-shrink-0">
                <span className="text-sm">{user.username[0]?.toUpperCase()}</span>
              </div>
              <span className="text-sm text-sage-300 truncate">{user.username}</span>
            </div>
            <button
              onClick={handleLogout}
              className="text-sage-500 hover:text-red-400 transition-colors"
              title="Logout"
            >
              🚪
            </button>
          </div>
        </div>
      )}
      </aside>
    </>
  )
}
