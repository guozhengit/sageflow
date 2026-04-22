/**
 * API 服务层测试
 */
import { userApi, documentApi, statsApi, llmApi } from '@/lib/services'
import apiClient from '@/lib/httpClient'
import { tokenStorage, userStorage } from '@/lib/auth'

// Mock axios client
jest.mock('@/lib/httpClient', () => ({
  defaults: { baseURL: 'http://localhost:8000' },
  get: jest.fn(),
  post: jest.fn(),
  delete: jest.fn(),
}))

// Mock auth
jest.mock('@/lib/auth', () => ({
  tokenStorage: {
    get: jest.fn(),
    set: jest.fn(),
    remove: jest.fn(),
    isAuthenticated: jest.fn(),
  },
  userStorage: {
    get: jest.fn(),
    set: jest.fn(),
    remove: jest.fn(),
  },
}))

const mockedGet = apiClient.get as jest.Mock
const mockedPost = apiClient.post as jest.Mock
const mockedDelete = apiClient.delete as jest.Mock

describe('userApi', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('register', () => {
    it('calls POST /api/users/register', async () => {
      const mockUser = { id: '1', username: 'test', email: 'test@example.com', preferences: {} }
      mockedPost.mockResolvedValue({ data: mockUser })

      const result = await userApi.register({ username: 'test', email: 'test@example.com', password: '123456' })

      expect(mockedPost).toHaveBeenCalledWith('/api/users/register', {
        username: 'test', email: 'test@example.com', password: '123456',
      })
      expect(result).toEqual(mockUser)
    })
  })

  describe('login', () => {
    it('stores token on successful login', async () => {
      mockedPost.mockResolvedValue({ data: { access_token: 'jwt-token', token_type: 'bearer' } })

      await userApi.login({ username: 'test', password: '123456' })

      expect(tokenStorage.set).toHaveBeenCalledWith('jwt-token')
    })
  })

  describe('getProfile', () => {
    it('fetches and caches user profile', async () => {
      const mockProfile = { id: '1', username: 'test', email: 'test@example.com', preferences: {} }
      mockedGet.mockResolvedValue({ data: mockProfile })

      const result = await userApi.getProfile()

      expect(mockedGet).toHaveBeenCalledWith('/api/users/profile')
      expect(userStorage.set).toHaveBeenCalledWith(mockProfile)
      expect(result).toEqual(mockProfile)
    })
  })

  describe('logout', () => {
    it('removes token and user data', () => {
      userApi.logout()
      expect(tokenStorage.remove).toHaveBeenCalled()
      expect(userStorage.remove).toHaveBeenCalled()
    })
  })

  describe('isAuthenticated', () => {
    it('delegates to tokenStorage', () => {
      (tokenStorage.isAuthenticated as jest.Mock).mockReturnValue(true)
      expect(userApi.isAuthenticated()).toBe(true)
    })
  })
})

describe('documentApi', () => {
  beforeEach(() => jest.clearAllMocks())

  it('lists documents', async () => {
    const docs = [{ id: '1', name: 'test.pdf', status: 'indexed', file_type: 'pdf', file_size: 1024 }]
    mockedGet.mockResolvedValue({ data: { documents: docs } })

    const result = await documentApi.list()
    expect(mockedGet).toHaveBeenCalledWith('/api/documents')
    expect(result).toEqual(docs)
  })

  it('gets task status', async () => {
    mockedGet.mockResolvedValue({ data: { task_id: 't1', status: 'completed' } })

    const result = await documentApi.getTaskStatus('t1')
    expect(mockedGet).toHaveBeenCalledWith('/api/documents/tasks/t1')
    expect(result.status).toBe('completed')
  })

  it('deletes a document', async () => {
    mockedDelete.mockResolvedValue({ data: {} })
    await documentApi.delete('doc1')
    expect(mockedDelete).toHaveBeenCalledWith('/api/documents/doc1')
  })
})

describe('statsApi', () => {
  beforeEach(() => jest.clearAllMocks())

  it('gets system stats', async () => {
    const mockStats = { users: 10, conversations: 50, messages: 200, vectors: 1000 }
    mockedGet.mockResolvedValue({ data: mockStats })

    const result = await statsApi.getSystem()
    expect(mockedGet).toHaveBeenCalledWith('/api/stats/system')
    expect(result).toEqual(mockStats)
  })

  it('gets user stats', async () => {
    mockedGet.mockResolvedValue({ data: { conversations: 5, messages: 20 } })
    const result = await statsApi.getUser()
    expect(result.conversations).toBe(5)
  })
})

describe('llmApi', () => {
  beforeEach(() => jest.clearAllMocks())

  it('gets available models', async () => {
    const mockResp = { models: [], current_model: 'qwen2.5:3b' }
    mockedGet.mockResolvedValue({ data: mockResp })

    const result = await llmApi.getModels()
    expect(result.current_model).toBe('qwen2.5:3b')
  })

  it('switches model', async () => {
    mockedPost.mockResolvedValue({ data: { message: 'Switched', current_model: 'new-model' } })

    const result = await llmApi.switchModel('new-model')
    expect(mockedPost).toHaveBeenCalledWith('/api/llm/switch', { model_name: 'new-model' })
    expect(result.current_model).toBe('new-model')
  })
})
