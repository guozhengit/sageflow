/** API 基础配置 */
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/** API 端点 */
export const API_ENDPOINTS = {
  // 用户
  REGISTER: '/api/users/register',
  LOGIN: '/api/users/login',
  PROFILE: '/api/users/profile',
  
  // 对话
  CONVERSATIONS: '/api/chat/conversations',
  CONVERSATION: (id: string) => `/api/chat/conversations/${id}`,
  MESSAGE: '/api/chat/message',
  STREAM: '/api/chat/stream',
  
  // 文档
  DOCUMENTS: '/api/documents',
  UPLOAD: '/api/documents/upload',
  TASK_STATUS: (taskId: string) => `/api/documents/tasks/${taskId}`,
  
  // LLM
  MODELS: '/api/llm/models',
  SWITCH_MODEL: '/api/llm/switch',
} as const
