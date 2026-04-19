'use client'

import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-sage-950 via-sage-900 to-sage-950">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-sage-500/20 via-transparent to-transparent" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
          <div className="text-center">
            {/* Logo */}
            <div className="flex justify-center mb-8">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-sage-400 to-sage-600 flex items-center justify-center">
                <span className="text-4xl">🌿</span>
              </div>
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-4">
              Welcome to <span className="text-sage-400">SageFlow</span>
            </h1>
            <p className="text-xl text-sage-200 mb-2">
              Smart Q&A Solutions for Your Knowledge Needs
            </p>
            <p className="text-lg text-sage-300 mb-12">
              智慧如流，洞察如光
            </p>
            
            {/* Feature Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-sage-700/50">
                <div className="text-4xl mb-4">💬</div>
                <h3 className="text-lg font-semibold text-white mb-2">Intelligent Answers</h3>
                <p className="text-sage-300 text-sm">精准、深度的智能回答</p>
              </div>
              
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-sage-700/50">
                <div className="text-4xl mb-4">📚</div>
                <h3 className="text-lg font-semibold text-white mb-2">Knowledge Base</h3>
                <p className="text-sage-300 text-sm">专属知识库管理</p>
              </div>
              
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-sage-700/50">
                <div className="text-4xl mb-4">💡</div>
                <h3 className="text-lg font-semibold text-white mb-2">Personalized Insights</h3>
                <p className="text-sage-300 text-sm">个性化洞察推荐</p>
              </div>
            </div>
            
            {/* CTA Button */}
            <Link
              href="/chat"
              className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-sage-500 to-sage-600 text-white font-semibold rounded-xl hover:from-sage-600 hover:to-sage-700 transition-all shadow-lg shadow-sage-500/25"
            >
              Get Started
              <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
          </div>
        </div>
      </section>
    </main>
  )
}
