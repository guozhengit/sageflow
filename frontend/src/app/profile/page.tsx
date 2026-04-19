'use client'

import Link from 'next/link'

export default function ProfilePage() {
  const preferences = [
    { icon: '💻', label: 'Technology' },
    { icon: '🤖', label: 'AI & Machine Learning' },
    { icon: '✈️', label: 'Travel Tips' },
  ]

  const recentActivity = [
    { id: '1', icon: '✅', content: 'AI Guide: how two neural networks dance?', time: '1 hours ago' },
    { id: '2', icon: '💚', content: 'Best destinations for adventure travel?', time: '3 days ago' },
    { id: '3', icon: '📍', content: 'Latest trends in AI?', time: '5 days ago' },
  ]

  return (
    <div className="flex h-screen bg-sage-950">
      {/* Sidebar */}
      <aside className="w-64 bg-sage-900 border-r border-sage-800 p-4">
        <div className="flex items-center gap-2 mb-8">
          <span className="text-2xl">🌿</span>
          <span className="text-xl font-bold text-white">SageFlow</span>
        </div>

        <nav className="space-y-2">
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
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-sage-900/50 backdrop-blur-sm border-b border-sage-800 px-6 py-4">
          <h2 className="text-lg font-semibold text-white">User Profile</h2>
        </header>

        {/* Profile Content */}
        <div className="flex-1 p-6">
          <div className="max-w-2xl mx-auto">
            {/* Preferences */}
            <div className="bg-sage-900/50 rounded-xl border border-sage-800 p-6 mb-6">
              <h3 className="text-lg font-semibold text-white mb-4">Preferences</h3>
              <div className="space-y-3">
                {preferences.map((pref, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-3 bg-sage-800/50 rounded-lg">
                    <span className="text-xl">{pref.icon}</span>
                    <span className="text-sage-200">{pref.label}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-sage-900/50 rounded-xl border border-sage-800 p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
              <div className="space-y-3">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-center justify-between p-3 bg-sage-800/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <span>{activity.icon}</span>
                      <span className="text-sage-200">{activity.content}</span>
                    </div>
                    <span className="text-sage-500 text-sm">{activity.time}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
