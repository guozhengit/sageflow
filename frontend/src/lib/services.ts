/** API 服务封装 */
import apiClient from './httpClient'
import { API_ENDPOINTS } from './api'
import { tokenStorage, userStorage } from './auth'

// ============ 用户 API ============

export interface RegisterData {
  username: string
  email: string
  password: string
}

export interface LoginData {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserProfile {
  id: string
  username: string
  email: string
  preferences: Record<string, any>
  created_at?: string
}

export const userApi = {
  /** 用户注册 */
  async register(data: RegisterData): Promise<UserProfile> {
    const response = await apiClient.post<UserProfile>(API_ENDPOINTS.REGISTER, data)
    return response.data
  },
  
  /** 用户登录 */
  async login(data: LoginData): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>(API_ENDPOINTS.LOGIN, data)
    // 存储 Token
    if (response.data.access_token) {
      tokenStorage.set(response.data.access_token)
    }
    return response.data
  },
  
  /** 获取用户信息 */
  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>(API_ENDPOINTS.PROFILE)
    // 缓存用户信息
    userStorage.set(response.data)
    return response.data
  },
  
  /** 登出 */
  logout(): void {
    tokenStorage.remove()
    userStorage.remove()
  },
  
  /** 检查是否已认证 */
  isAuthenticated(): boolean {
    return tokenStorage.isAuthenticated()
  },
}

// ============ 对话 API ============

export interface Conversation {
  id: string
  title: string
  message_count?: number
  updated_at?: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{ document: string; page: number; content: string }>
  created_at?: string
}

export interface ChatRequest {
  message: string
  conversation_id?: string
}

export interface ChatResponse {
  answer: string
  sources: Array<{ document: string; page: number; content: string }>
  conversation_id: string
}

export const conversationApi = {
  /** 获取对话列表 */
  async list(): Promise<Conversation[]> {
    const response = await apiClient.get<{ conversations: Conversation[] }>(API_ENDPOINTS.CONVERSATIONS)
    return response.data.conversations
  },
  
  /** 获取对话详情 */
  async get(conversationId: string): Promise<{ id: string; title: string; messages: Message[] }> {
    const response = await apiClient.get(API_ENDPOINTS.CONVERSATION(conversationId))
    return response.data
  },
  
  /** 发送消息 (非流式) */
  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>(API_ENDPOINTS.MESSAGE, data)
    return response.data
  },
  
  /** 发送消息 (流式) */
  async sendMessageStream(
    data: ChatRequest,
    onChunk: (chunk: string) => void,
    onSources: (sources: ChatResponse['sources']) => void,
    onDone: (conversationId: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    const token = tokenStorage.get()
    
    try {
      const response = await fetch(`${apiClient.defaults.baseURL}${API_ENDPOINTS.STREAM}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify(data),
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`)
      }
      
      const reader = response.body?.getReader()
      if (!reader) throw new Error('No reader available')
      
      const decoder = new TextDecoder()
      let buffer = ''
      let fullAnswer = ''
      let sources: ChatResponse['sources'] = []
      let conversationId = ''
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            
            if (data === '[DONE]') {
              onDone(conversationId)
              return
            } else if (data.startsWith('[ERROR]')) {
              onError(data.slice(8))
              return
            } else if (data.startsWith('[SOURCES]')) {
              try {
                sources = JSON.parse(data.slice(9))
                onSources(sources)
              } catch {}
            } else if (data.startsWith('[CONVERSATION_ID]')) {
              conversationId = data.slice(17)
            } else {
              fullAnswer += data
              onChunk(data)
            }
          }
        }
      }
      
      onDone(conversationId)
    } catch (error: any) {
      onError(error.message || 'Stream error')
    }
  },
  
  /** 删除对话 */
  async delete(conversationId: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.CONVERSATION(conversationId))
  },
}

// ============ 文档 API ============

export interface Document {
  id: string
  name: string
  status: 'pending' | 'processing' | 'indexed' | 'failed'
  file_type: string
  file_size: number
}

export interface UploadResponse {
  message: string
  document_id: string
  filename: string
  task_id: string
  status: string
}

export interface TaskStatus {
  task_id: string
  status: string
  result?: any
  error?: string
}

export const documentApi = {
  /** 获取文档列表 */
  async list(): Promise<Document[]> {
    const response = await apiClient.get<{ documents: Document[] }>(API_ENDPOINTS.DOCUMENTS)
    return response.data.documents
  },
  
  /** 上传文档 */
  async upload(file: File, onProgress?: (progress: number) => void): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post<UploadResponse>(API_ENDPOINTS.UPLOAD, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
    return response.data
  },
  
  /** 查询任务状态 */
  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    const response = await apiClient.get<TaskStatus>(API_ENDPOINTS.TASK_STATUS(taskId))
    return response.data
  },
  
  /** 删除文档 */
  async delete(docId: string): Promise<void> {
    await apiClient.delete(`${API_ENDPOINTS.DOCUMENTS}/${docId}`)
  },
}

// ============ 统计 API ============

export interface SystemStats {
  users: number
  conversations: number
  messages: number
  vectors: number
}

export interface UserStats {
  conversations: number
  messages: number
}

export const statsApi = {
  /** 获取系统统计 */
  async getSystem(): Promise<SystemStats> {
    const response = await apiClient.get<SystemStats>('/api/stats/system')
    return response.data
  },
  
  /** 获取用户统计 */
  async getUser(): Promise<UserStats> {
    const response = await apiClient.get<UserStats>('/api/stats/user')
    return response.data
  },
}

// ============ LLM API ============

export interface ModelInfo {
  name: string
  display_name: string
  description: string
  parameters: string
  context_length: number
}

export interface AvailableModelsResponse {
  models: ModelInfo[]
  current_model: string
}

export const llmApi = {
  /** 获取可用模型列表 */
  async getModels(): Promise<AvailableModelsResponse> {
    const response = await apiClient.get<AvailableModelsResponse>(API_ENDPOINTS.MODELS)
    return response.data
  },
  
  /** 切换模型 */
  async switchModel(modelName: string): Promise<{ message: string; current_model: string }> {
    const response = await apiClient.post(API_ENDPOINTS.SWITCH_MODEL, { model_name: modelName })
    return response.data
  },
}
