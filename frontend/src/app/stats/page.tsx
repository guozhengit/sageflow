'use client'

import { useState, useEffect } from 'react'
import ConversationSidebar from '@/components/chat/ConversationSidebar'
import { statsApi, userApi, type UserProfile } from '@/lib/services'
import { userStorage } from '@/lib/auth'

interface Stats {
  conversations: number
  messages: number
}

export default function StatsPage() {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const cachedUser = userStorage.get()
      if (cachedUser) {
        setUser(cachedUser)
      } else {
        const profile = await userApi.getProfile()
        setUser(profile)
      }

      const userStats = await statsApi.getUser()
      setStats(userStats)
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    { label: 'Total Conversations', value: stats?.conversations ?? 0, icon: '💬', color: 'from-blue-500 to-blue-600' },
    { label: 'Total Messages', value: stats?.messages ?? 0, icon: '📨', color: 'from-green-500 to-green-600' },
    { label: 'Documents Uploaded', value: 0, icon: '📄', color: 'from-purple-500 to-purple-600' },
    { label: 'Knowledge Base Size', value: '0 MB', icon: '💾', color: 'from-orange-500 to-orange-600' },
  ]

  return (
    <div className="flex h-screen bg-sage-950">
      <ConversationSidebar activePath="/stats" />

      <div className="flex-1 flex flex-col">
        <header className="bg-sage-900/50 backdrop-blur-sm border-b border-sage-800 px-6 py-4">
          <h2 className="text-lg font-semibold text-white">Usage Statistics</h2>
        </header>

        <div className="flex-1 p-6 overflow-y-auto">
          {loading ? (
            <div className="text-center py-8 text-sage-500">Loading statistics...</div>
          ) : (
            <>
              {/* Stat Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {statCards.map((card, idx) => (
                  <div key={idx} className="bg-sage-900/50 rounded-xl border border-sage-800 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-3xl">{card.icon}</span>
                      <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${card.color} flex items-center justify-center`}>
                        <span className="text-white text-lg font-bold">
                          {typeof card.value === 'number' ? card.value : card.value[0]}
                        </span>
                      </div>
                    </div>
                    <h3 className="text-sage-400 text-sm">{card.label}</h3>
                    <p className="text-white text-2xl font-bold mt-1">
                      {card.value}
                    </p>
                  </div>
                ))}
              </div>

              {/* User Info */}
              {user && (
                <div className="bg-sage-900/50 rounded-xl border border-sage-800 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Account Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sage-400 text-sm">Username</p>
                      <p className="text-white">{user.username}</p>
                    </div>
                    <div>
                      <p className="text-sage-400 text-sm">Email</p>
                      <p className="text-white">{user.email}</p>
                    </div>
                    <div>
                      <p className="text-sage-400 text-sm">Member Since</p>
                      <p className="text-white">April 2026</p>
                    </div>
                    <div>
                      <p className="text-sage-400 text-sm">Plan</p>
                      <p className="text-white">Free Tier</p>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
