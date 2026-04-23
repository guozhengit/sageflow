'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import MarkdownRenderer from '@/components/ui/MarkdownRenderer'
import ConversationSidebar from '@/components/chat/ConversationSidebar'
import { conversationApi } from '@/lib/services'
import { useAuth } from '@/hooks/useAuth'
import { useConversationStore } from '@/lib/store'
import { useIsMobile } from '@/hooks/useMedia'
import { exportToMarkdown, exportToJSON, exportToText, downloadFile } from '@/lib/export'
import { useShortcuts, SHORTCUTS } from '@/hooks/useShortcuts'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{ document: string; page: number; content: string }>
  created_at?: string
}

const WELCOME_MESSAGE: Message = {
  id: '1',
  role: 'assistant',
  content: "Hello! I'm SageFlow, your intelligent Q&A assistant. How can I help you today?"
}

export default function ChatPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const isMobile = useIsMobile()
  const { currentConversationId, setCurrentConversationId } = useConversationStore()

  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(isMobile ? false : false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const exportMenuRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleNewConversation = useCallback(() => {
    setCurrentConversationId(null)
    setMessages([{ ...WELCOME_MESSAGE, id: Date.now().toString() }])
  }, [setCurrentConversationId])

  useShortcuts([
    {
      ...SHORTCUTS.SEND_MESSAGE,
      handler: () => {
        if (inputRef.current && document.activeElement === inputRef.current) return
        inputRef.current?.focus()
      },
    },
    {
      ...SHORTCUTS.NEW_CONVERSATION,
      handler: handleNewConversation,
    },
  ])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (exportMenuRef.current && !exportMenuRef.current.contains(e.target as Node)) {
        setShowExportMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    const assistantMessageId = (Date.now() + 1).toString()
    setMessages(prev => [...prev, { id: assistantMessageId, role: 'assistant', content: '' }])

    try {
      await conversationApi.sendMessageStream(
        { message: userMessage.content, conversation_id: currentConversationId || undefined },
        (chunk) => {
          setMessages(prev => prev.map(msg =>
            msg.id === assistantMessageId ? { ...msg, content: msg.content + chunk } : msg
          ))
        },
        (sources) => {
          setMessages(prev => prev.map(msg =>
            msg.id === assistantMessageId ? { ...msg, sources } : msg
          ))
        },
        (conversationId) => {
          if (!currentConversationId) setCurrentConversationId(conversationId)
          setIsLoading(false)
        },
        (error) => {
          console.error('Stream error:', error)
          setMessages(prev => prev.map(msg =>
            msg.id === assistantMessageId ? { ...msg, content: msg.content || `Error: ${error}` } : msg
          ))
          setIsLoading(false)
        }
      )
    } catch (error) {
      console.error('Error:', error)
      setIsLoading(false)
    }
  }

  const handleSelectConversation = async (id: string) => {
    setCurrentConversationId(id)
    try {
      const conversation = await conversationApi.get(id)
      setMessages(conversation.messages)
    } catch (error) {
      console.error('Failed to load conversation:', error)
    }
  }

  const handleExport = (format: 'markdown' | 'json' | 'text') => {
    const title = currentConversationId ? `Conversation ${currentConversationId}` : 'SageFlow Conversation'
    const exporters = {
      markdown: () => ({ content: exportToMarkdown(messages, title), ext: '.md', type: 'text/markdown' }),
      json: () => ({ content: exportToJSON(messages, title), ext: '.json', type: 'application/json' }),
      text: () => ({ content: exportToText(messages, title), ext: '.txt', type: 'text/plain' }),
    }
    const { content, ext, type } = exporters[format]()
    downloadFile(content, `${title.replace(/\s+/g, '_')}${ext}`, type)
    setShowExportMenu(false)
  }

  if (authLoading) {
    return <div className="flex h-screen bg-sage-950 items-center justify-center text-sage-400">Loading...</div>
  }

  if (!isAuthenticated) {
    if (typeof window !== 'undefined') window.location.href = '/login'
    return null
  }

  return (
    <div className="flex h-screen bg-sage-950">
      <ConversationSidebar
        activePath="/chat"
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        mobileOpen={mobileSidebarOpen}
        onMobileClose={() => setMobileSidebarOpen(false)}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <header className="bg-sage-900/50 backdrop-blur-sm border-b border-sage-800 px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-3">
            {isMobile && (
              <button onClick={() => setMobileSidebarOpen(true)} className="p-2 rounded-lg bg-sage-800 text-white hover:bg-sage-700">☰</button>
            )}
            <h2 className="text-lg font-semibold text-white">Q&A Interface</h2>
          </div>

          <div className="relative" ref={exportMenuRef}>
            <button
              onClick={() => setShowExportMenu(!showExportMenu)}
              className="px-3 py-2 bg-sage-800 text-sage-300 rounded-lg hover:bg-sage-700 transition-colors flex items-center gap-2"
            >
              📥 Export
            </button>
            {showExportMenu && (
              <div className="absolute right-0 top-full mt-2 bg-sage-800 border border-sage-700 rounded-lg shadow-lg py-2 min-w-[160px] z-50">
                <button onClick={() => handleExport('markdown')} className="w-full text-left px-4 py-2 text-sage-300 hover:bg-sage-700 hover:text-white transition-colors">📄 Markdown (.md)</button>
                <button onClick={() => handleExport('json')} className="w-full text-left px-4 py-2 text-sage-300 hover:bg-sage-700 hover:text-white transition-colors">📋 JSON (.json)</button>
                <button onClick={() => handleExport('text')} className="w-full text-left px-4 py-2 text-sage-300 hover:bg-sage-700 hover:text-white transition-colors">📝 Plain Text (.txt)</button>
              </div>
            )}
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-3 sm:p-4 lg:p-6 space-y-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.role === 'user' ? 'bg-sage-600 text-white' : 'bg-sage-800 text-sage-100'}`}>
                {message.role === 'user' ? (
                  <p className="whitespace-pre-wrap">{message.content}</p>
                ) : (
                  <MarkdownRenderer content={message.content} />
                )}
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-sage-700">
                    <p className="text-xs text-sage-400 mb-2">Sources:</p>
                    {message.sources.map((source, idx) => (
                      <div key={idx} className="text-xs text-sage-300">📄 {source.document} (Page {source.page})</div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-sage-800 rounded-2xl px-4 py-3">
                <div className="flex gap-2">
                  <div className="w-2 h-2 bg-sage-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-sage-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-sage-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="border-t border-sage-800 p-3 sm:p-4">
          <div className="flex gap-2 sm:gap-3">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(e) } }}
              placeholder="Type your question..."
              className="flex-1 bg-sage-800 text-white px-3 sm:px-4 py-2 sm:py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-sage-500 placeholder-sage-500 text-sm sm:text-base"
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !input.trim()} className="px-4 sm:px-6 py-2 sm:py-3 bg-sage-600 text-white rounded-xl hover:bg-sage-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm sm:text-base">Send</button>
          </div>
        </form>
      </div>
    </div>
  )
}
