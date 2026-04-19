'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import MarkdownRenderer from '@/components/ui/MarkdownRenderer'
import ConversationSidebar from '@/components/chat/ConversationSidebar'
import { conversationApi, userApi } from '@/lib/services'
import { userStorage } from '@/lib/auth'
import { exportToMarkdown, exportToJSON, exportToText, downloadFile } from '@/lib/export'
import { useShortcuts, SHORTCUTS } from '@/hooks/useShortcuts'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{ document: string; page: number; content: string }>
  created_at?: string
}

export default function ChatPage() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m SageFlow, your intelligent Q&A assistant. How can I help you today?'
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>(undefined)
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const exportMenuRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // 快捷键
  useShortcuts([
    {
      ...SHORTCUTS.SEND_MESSAGE,
      handler: () => {
        if (inputRef.current && document.activeElement === inputRef.current) {
          // 如果已经在输入框中，让表单处理
          return
        }
        inputRef.current?.focus()
      },
    },
    {
      ...SHORTCUTS.NEW_CONVERSATION,
      handler: handleNewConversation,
    },
  ])

  // 检查认证状态
  useEffect(() => {
    if (!userApi.isAuthenticated()) {
      router.push('/login')
    }
  }, [router])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 点击外部关闭导出菜单
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

    // 创建助手消息占位符
    const assistantMessageId = (Date.now() + 1).toString()
    setMessages(prev => [...prev, {
      id: assistantMessageId,
      role: 'assistant',
      content: ''
    }])

    try {
      await conversationApi.sendMessageStream(
        {
          message: userMessage.content,
          conversation_id: currentConversationId
        },
        // onChunk
        (chunk) => {
          setMessages(prev => prev.map(msg =>
            msg.id === assistantMessageId
              ? { ...msg, content: msg.content + chunk }
              : msg
          ))
        },
        // onSources
        (sources) => {
          setMessages(prev => prev.map(msg =>
            msg.id === assistantMessageId
              ? { ...msg, sources }
              : msg
          ))
        },
        // onDone
        (conversationId) => {
          if (!currentConversationId) {
            setCurrentConversationId(conversationId)
          }
          setIsLoading(false)
        },
        // onError
        (error) => {
          console.error('Stream error:', error)
          setMessages(prev => prev.map(msg =>
            msg.id === assistantMessageId
              ? { ...msg, content: msg.content || `Error: ${error}` }
              : msg
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

  const handleNewConversation = () => {
    setCurrentConversationId(undefined)
    setMessages([{
      id: Date.now().toString(),
      role: 'assistant',
      content: 'Hello! I\'m SageFlow, your intelligent Q&A assistant. How can I help you today?'
    }])
  }

  const handleExport = (format: 'markdown' | 'json' | 'text') => {
    const title = currentConversationId ? `Conversation ${currentConversationId}` : 'SageFlow Conversation'
    let content: string
    let filename: string
    let mimeType: string

    switch (format) {
      case 'markdown':
        content = exportToMarkdown(messages, title)
        filename = `${title.replace(/\s+/g, '_')}.md`
        mimeType = 'text/markdown'
        break
      case 'json':
        content = exportToJSON(messages, title)
        filename = `${title.replace(/\s+/g, '_')}.json`
        mimeType = 'application/json'
        break
      case 'text':
        content = exportToText(messages, title)
        filename = `${title.replace(/\s+/g, '_')}.txt`
        mimeType = 'text/plain'
        break
    }

    downloadFile(content, filename, mimeType)
    setShowExportMenu(false)
  }

  return (
    <div className="flex h-screen bg-sage-950">
      {/* Sidebar */}
      <ConversationSidebar
        activePath="/chat"
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        mobileOpen={mobileSidebarOpen}
        onMobileClose={() => setMobileSidebarOpen(false)}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-sage-900/50 backdrop-blur-sm border-b border-sage-800 px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-3">
            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg bg-sage-800 text-white hover:bg-sage-700"
            >
              ☰
            </button>
            <h2 className="text-lg font-semibold text-white">Q&A Interface</h2>
          </div>
          
          {/* Export Menu */}
          <div className="relative" ref={exportMenuRef}>
            <button
              onClick={() => setShowExportMenu(!showExportMenu)}
              className="px-3 py-2 bg-sage-800 text-sage-300 rounded-lg hover:bg-sage-700 transition-colors flex items-center gap-2"
            >
              📥 Export
            </button>
            {showExportMenu && (
              <div className="absolute right-0 top-full mt-2 bg-sage-800 border border-sage-700 rounded-lg shadow-lg py-2 min-w-[160px] z-50">
                <button
                  onClick={() => handleExport('markdown')}
                  className="w-full text-left px-4 py-2 text-sage-300 hover:bg-sage-700 hover:text-white transition-colors"
                >
                  📄 Markdown (.md)
                </button>
                <button
                  onClick={() => handleExport('json')}
                  className="w-full text-left px-4 py-2 text-sage-300 hover:bg-sage-700 hover:text-white transition-colors"
                >
                  📋 JSON (.json)
                </button>
                <button
                  onClick={() => handleExport('text')}
                  className="w-full text-left px-4 py-2 text-sage-300 hover:bg-sage-700 hover:text-white transition-colors"
                >
                  📝 Plain Text (.txt)
                </button>
              </div>
            )}
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-3 sm:p-4 lg:p-6 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-sage-600 text-white'
                    : 'bg-sage-800 text-sage-100'
                }`}
              >
                {message.role === 'user' ? (
                  <p className="whitespace-pre-wrap">{message.content}</p>
                ) : (
                  <MarkdownRenderer content={message.content} />
                )}
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-sage-700">
                    <p className="text-xs text-sage-400 mb-2">Sources:</p>
                    {message.sources.map((source, idx) => (
                      <div key={idx} className="text-xs text-sage-300">
                        📄 {source.document} (Page {source.page})
                      </div>
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

        {/* Input */}
        <form onSubmit={handleSubmit} className="border-t border-sage-800 p-3 sm:p-4">
          <div className="flex gap-2 sm:gap-3">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
              placeholder="Type your question..."
              className="flex-1 bg-sage-800 text-white px-3 sm:px-4 py-2 sm:py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-sage-500 placeholder-sage-500 text-sm sm:text-base"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-4 sm:px-6 py-2 sm:py-3 bg-sage-600 text-white rounded-xl hover:bg-sage-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm sm:text-base"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
