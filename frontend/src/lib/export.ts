/** 对话导出工具 */
import type { Message } from '@/lib/services'

/** 导出为 Markdown */
export function exportToMarkdown(messages: Message[], title: string = 'Conversation'): string {
  let content = `# ${title}\n\n`
  content += `Exported from SageFlow\n`
  content += `Date: ${new Date().toISOString()}\n\n---\n\n`

  messages.forEach((msg) => {
    const role = msg.role === 'user' ? '👤 **You**' : '🤖 **SageFlow**'
    content += `### ${role}\n\n${msg.content}\n\n`
    
    if (msg.sources && msg.sources.length > 0) {
      content += '**Sources:**\n\n'
      msg.sources.forEach((source, idx) => {
        content += `${idx + 1}. 📄 ${source.document} (Page ${source.page})\n`
      })
      content += '\n'
    }
    
    content += '---\n\n'
  })

  return content
}

/** 导出为 JSON */
export function exportToJSON(messages: Message[], title: string = 'Conversation'): string {
  const data = {
    title,
    exportedAt: new Date().toISOString(),
    messageCount: messages.length,
    messages: messages.map(msg => ({
      role: msg.role,
      content: msg.content,
      sources: msg.sources,
      timestamp: msg.created_at
    }))
  }
  return JSON.stringify(data, null, 2)
}

/** 导出为 TXT (纯文本) */
export function exportToText(messages: Message[], title: string = 'Conversation'): string {
  let content = `${title}\n${'='.repeat(title.length)}\n\n`
  content += `Exported from SageFlow - ${new Date().toLocaleString()}\n\n`

  messages.forEach((msg) => {
    const role = msg.role === 'user' ? 'You' : 'SageFlow'
    content += `${role}:\n${msg.content}\n\n`
  })

  return content
}

/** 下载文件 */
export function downloadFile(content: string, filename: string, mimeType: string = 'text/plain'): void {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/** 导出对话框选项 */
export const exportFormats = [
  { id: 'markdown', label: 'Markdown (.md)', mimeType: 'text/markdown' },
  { id: 'json', label: 'JSON (.json)', mimeType: 'application/json' },
  { id: 'text', label: 'Plain Text (.txt)', mimeType: 'text/plain' },
] as const
