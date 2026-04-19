'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { userApi } from '@/lib/services'

export default function LoginPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await userApi.login(formData)
      router.push('/chat')
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-sage-950 via-sage-900 to-sage-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-sage-400 to-sage-600 flex items-center justify-center">
              <span className="text-3xl">🌿</span>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-white">SageFlow</h1>
          <p className="text-sage-400 mt-2">Smart Q&A Solutions</p>
        </div>

        {/* Login Form */}
        <div className="bg-sage-900/50 backdrop-blur-sm rounded-2xl border border-sage-800 p-8">
          <h2 className="text-xl font-semibold text-white mb-6">Sign In</h2>

          {error && (
            <div className="bg-red-900/50 border border-red-800 text-red-300 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-sage-300 mb-2">Username</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="w-full bg-sage-800 text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-sage-500 placeholder-sage-500"
                placeholder="Enter your username"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-300 mb-2">Password</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full bg-sage-800 text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-sage-500 placeholder-sage-500"
                placeholder="Enter your password"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-sage-500 to-sage-600 text-white font-semibold py-3 rounded-xl hover:from-sage-600 hover:to-sage-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sage-400">
              Don't have an account?{' '}
              <Link href="/register" className="text-sage-400 hover:text-sage-300 underline">
                Sign up
              </Link>
            </p>
          </div>
        </div>

        <div className="mt-6 text-center">
          <Link href="/" className="text-sage-500 hover:text-sage-400 text-sm">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}
