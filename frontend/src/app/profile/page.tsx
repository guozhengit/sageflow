'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { userApi, conversationApi, statsApi } from '@/lib/services'
import { userStorage, tokenStorage } from '@/lib/auth'
import { toast } from '@/lib/store'
import type { UserProfile } from '@/lib/services'

interface ActivityItem {
  id: string
  title: string
  updated_at: string
}

export default function ProfilePage() {
  const router = useRouter()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [recentConversations, setRecentConversations] = useState<ActivityItem[]>([])
  const [userStats, setUserStats] = useState<{ conversations: number; messages: number } | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!tokenStorage.isAuthenticated()) {
      router.push('/login')
      return
    }

    const fetchData = async () => {
      try {
        const [profileData, conversations, stats] = await Promise.allSettled([
          userApi.getProfile(),
          conversationApi.list(),
          statsApi.getUser(),
        ])

        if (profileData.status === 'fulfilled') {
          setProfile(profileData.value)
        } else {
          toast.error('Failed to load profile')
        }

        if (conversations.status === 'fulfilled') {
          const recent = conversations.value
            .slice(0, 5)
            .map((c) => ({
              id: c.id,
              title: c.title,
              updated_at: c.updated_at || '',
            }))
          setRecentConversations(recent)
        }

        if (stats.status === 'fulfilled') {
          setUserStats(stats.value)
        }
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [router])

  const handleLogout = () => {
    userApi.logout()
    toast.success('Logged out successfully')
    router.push('/login')
  }

  const formatDate = (dateStr: string) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const preferences = profile?.preferences
    ? Object.entries(profile.preferences).map(([key, value]) => ({
        key,
        label: String(value),
      }))
    : []

  if (isLoading) {
    return (
      <div className="flex h-screen bg-sage-950 items-center justify-center">
        <div className="text-sage-400">Loading profile...</div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-sage-950">
      {/* Sidebar */}
      <aside className="w-64 bg-sage-900 border-r border-sage-800 p-4 flex flex-col">
        <div className="flex items-center gap-2 mb-8">
          <span className="text-2xl">🌿</span>
          <span className="text-xl font-bold text-white">SageFlow</span>
        </div>

        <nav className="space-y-2 flex-1">
          <Link href="/" className="flex items-center gap-3 px-3 py-2 text-sage-300 hover:bg-sage-800 rounded-lg">
            <span>🏠</span> Home
          </Link>
          <Link href="/chat" className="flex items-center gap-3 px-3 py-2 text-sage-300 hover:bg-sage-800 rounded-lg">
            <span>💬</span> Intelligent Answers
          </Link>
          <Link href="/knowledge" className="flex items-center gap-3 px-3 py-2 text-sage-300 hover:bg-sage-800 rounded-lg">
            <span>📚</span> Knowledge Base
          </Link>
          <Link href="/profile" className="flex items-center gap-3 px-3 py-2 bg-sage-800 text-white rounded-lg">
            <span>👤</span> User Profile
          </Link>
        </nav>

        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2 text-sage-400 hover:bg-sage-800 hover:text-red-400 rounded-lg transition-colors"
        >
          <span>🚪</span> Logout
        </button>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-sage-900/50 backdrop-blur-sm border-b border-sage-800 px-6 py-4">
          <h2 className="text-lg font-semibold text-white">User Profile</h2>
        </header>

        {/* Profile Content */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-2xl mx-auto space-y-6">
            {/* User Info Card */}
            <div className="bg-sage-900/50 rounded-xl border border-sage-800 p-6">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 rounded-full bg-sage-700 flex items-center justify-center text-2xl">
                  {profile?.username?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white">{profile?.username || 'User'}</h3>
                  <p className="text-sage-400">{profile?.email || ''}</p>
                  {profile?.created_at && (
                    <p className="text-sage-500 text-sm mt-1">
                      Joined {new Date(profile.created_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Stats */}
            {userStats && (
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-sage-900/50 rounded-xl border border-sage-800 p-4 text-center">
                  <div className="text-2xl font-bold text-white">{userStats.conversations}</div>
                  <div className="text-sage-400 text-sm">Conversations</div>
                </div>
                <div className="bg-sage-900/50 rounded-xl border border-sage-800 p-4 text-center">
                  <div className="text-2xl font-bold text-white">{userStats.messages}</div>
                  <div className="text-sage-400 text-sm">Messages</div>
                </div>
              </div>
            )}

            {/* Preferences */}
            <div className="bg-sage-900/50 rounded-xl border border-sage-800 p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Preferences</h3>
              {preferences.length > 0 ? (
                <div className="space-y-3">
                  {preferences.map((pref) => (
                    <div key={pref.key} className="flex items-center gap-3 p-3 bg-sage-800/50 rounded-lg">
                      <span className="text-sage-400 font-mono text-sm">{pref.key}:</span>
                      <span className="text-sage-200">{pref.label}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sage-500">No preferences set yet. Start chatting to personalize your experience.</p>
              )}
            </div>

            {/* Recent Activity */}
            <div className="bg-sage-900/50 rounded-xl border border-sage-800 p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Recent Conversations</h3>
              {recentConversations.length > 0 ? (
                <div className="space-y-3">
                  {recentConversations.map((conv) => (
                    <Link
                      key={conv.id}
                      href={`/chat?conversation=${conv.id}`}
                      className="flex items-center justify-between p-3 bg-sage-800/50 rounded-lg hover:bg-sage-800 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span>💬</span>
                        <span className="text-sage-200 truncate max-w-xs">{conv.title}</span>
                      </div>
                      <span className="text-sage-500 text-sm flex-shrink-0">{formatDate(conv.updated_at)}</span>
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-sage-500">No conversations yet. Start a new chat to see your activity here.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
