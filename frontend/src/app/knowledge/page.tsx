'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import ConversationSidebar from '@/components/chat/ConversationSidebar'
import { documentApi, userApi, type Document } from '@/lib/services'

interface UploadingFile {
  id: string
  name: string
  progress: number
  status: 'uploading' | 'processing' | 'completed' | 'failed'
  taskId?: string
}

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const docs = await documentApi.list()
      setDocuments(docs)
    } catch (error) {
      console.error('Failed to load documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setIsUploading(true)

    for (const file of Array.from(files)) {
      const fileId = Date.now().toString() + Math.random()
      const uploadingFile: UploadingFile = {
        id: fileId,
        name: file.name,
        progress: 0,
        status: 'uploading'
      }
      setUploadingFiles(prev => [...prev, uploadingFile])

      try {
        const result = await documentApi.upload(file, (progress) => {
          setUploadingFiles(prev => prev.map(f =>
            f.id === fileId ? { ...f, progress } : f
          ))
        })

        // 更新为处理中状态
        setUploadingFiles(prev => prev.map(f =>
          f.id === fileId ? { ...f, status: 'processing', taskId: result.task_id } : f
        ))

        // 轮询任务状态
        pollTaskStatus(result.task_id, fileId)
      } catch (error) {
        console.error('Upload error:', error)
        setUploadingFiles(prev => prev.map(f =>
          f.id === fileId ? { ...f, status: 'failed' } : f
        ))
      }
    }

    setIsUploading(false)
    e.target.value = ''
  }

  const pollTaskStatus = async (taskId: string, fileId: string) => {
    const maxAttempts = 30
    let attempts = 0

    const poll = async () => {
      if (attempts >= maxAttempts) {
        setUploadingFiles(prev => prev.map(f =>
          f.id === fileId ? { ...f, status: 'failed' } : f
        ))
        return
      }

      try {
        const status = await documentApi.getTaskStatus(taskId)
        
        if (status.status === 'SUCCESS') {
          setUploadingFiles(prev => prev.map(f =>
            f.id === fileId ? { ...f, status: 'completed' } : f
          ))
          loadDocuments() // 刷新文档列表
        } else if (status.status === 'FAILURE') {
          setUploadingFiles(prev => prev.map(f =>
            f.id === fileId ? { ...f, status: 'failed' } : f
          ))
        } else {
          attempts++
          setTimeout(poll, 2000)
        }
      } catch (error) {
        attempts++
        setTimeout(poll, 2000)
      }
    }

    poll()
  }

  const handleDelete = async (docId: string) => {
    try {
      await documentApi.delete(docId)
      setDocuments(documents.filter(d => d.id !== docId))
    } catch (error) {
      console.error('Delete error:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'indexed': case 'completed': return 'text-green-400'
      case 'processing': case 'uploading': return 'text-yellow-400'
      case 'pending': return 'text-sage-400'
      case 'failed': return 'text-red-400'
      default: return 'text-sage-400'
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  // 过滤文档
  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || doc.status === statusFilter
    return matchesSearch && matchesStatus
  })

  return (
    <div className="flex h-screen bg-sage-950">
      {/* Sidebar */}
      <ConversationSidebar activePath="/knowledge" />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-sage-900/50 backdrop-blur-sm border-b border-sage-800 px-6 py-4">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-white">Knowledge Base Management</h2>
            <div className="flex gap-3">
              <label className="px-4 py-2 bg-sage-600 text-white rounded-lg hover:bg-sage-700 cursor-pointer transition-colors flex items-center gap-2">
                📤 Upload
                <input
                  type="file"
                  className="hidden"
                  onChange={handleUpload}
                  disabled={isUploading}
                  multiple
                  accept=".pdf,.doc,.docx,.txt"
                />
              </label>
            </div>
          </div>
        </header>

        {/* Filters */}
        <div className="px-6 py-3 border-b border-sage-800 flex gap-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documents..."
            className="flex-1 bg-sage-800 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-sage-500 placeholder-sage-500"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-sage-800 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-sage-500"
          >
            <option value="all">All Status</option>
            <option value="indexed">Indexed</option>
            <option value="processing">Processing</option>
            <option value="pending">Pending</option>
          </select>
        </div>

        {/* Uploading Progress */}
        {uploadingFiles.length > 0 && (
          <div className="px-6 py-3 border-b border-sage-800">
            <h3 className="text-sm font-medium text-sage-400 mb-2">Upload Progress</h3>
            <div className="space-y-2">
              {uploadingFiles.map(file => (
                <div key={file.id} className="bg-sage-800/50 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-white text-sm truncate">{file.name}</span>
                    <span className={`text-xs ${getStatusColor(file.status)}`}>
                      {file.status === 'uploading' ? `${file.progress}%` : file.status}
                    </span>
                  </div>
                  {file.status === 'uploading' && (
                    <div className="w-full bg-sage-700 rounded-full h-2">
                      <div
                        className="bg-sage-500 h-2 rounded-full transition-all"
                        style={{ width: `${file.progress}%` }}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Document List */}
        <div className="flex-1 p-6 overflow-y-auto">
          {loading ? (
            <div className="text-center py-8 text-sage-500">Loading documents...</div>
          ) : filteredDocuments.length === 0 ? (
            <div className="text-center py-8 text-sage-500">
              {searchQuery || statusFilter !== 'all' ? 'No matching documents' : 'No documents yet. Upload your first document!'}
            </div>
          ) : (
            <div className="bg-sage-900/50 rounded-xl border border-sage-800 overflow-hidden">
              <table className="w-full">
                <thead className="bg-sage-800/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-sage-400 uppercase">Document Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-sage-400 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-sage-400 uppercase">Size</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-sage-400 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-sage-800">
                  {filteredDocuments.map((doc) => (
                    <tr key={doc.id} className="hover:bg-sage-800/30">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <span className="text-sage-400">📄</span>
                          <span className="text-white">{doc.name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`capitalize ${getStatusColor(doc.status)}`}>
                          {doc.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sage-300">
                        {formatFileSize(doc.file_size)}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button className="px-3 py-1 text-sm bg-sage-700 text-white rounded hover:bg-sage-600 mr-2">
                          View
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="px-3 py-1 text-sm bg-red-900/50 text-red-400 rounded hover:bg-red-900/70"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
