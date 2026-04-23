/** HTTP 客户端 - Axios 封装 (带自动重试) */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import axiosRetry from 'axios-retry'
import { API_BASE_URL } from './api'
import { tokenStorage } from './auth'

// 创建 Axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 配置自动重试
axiosRetry(apiClient, {
  retries: 3, // 最多重试 3 次
  retryDelay: axiosRetry.exponentialDelay, // 指数退避: 1s, 2s, 4s
  retryCondition: (error: AxiosError) => {
    // 网络错误或 5xx 服务器错误时重试
    if (!error.response) return true
    const status = error.response.status
    return status >= 500 && status < 600
  },
  onRetry: (retryCount, error, requestConfig) => {
    console.log(`[API Retry] Attempt ${retryCount} for ${requestConfig.url}: ${error.message}`)
  },
})

// 请求拦截器 - 自动添加 Token
apiClient.interceptors.request.use(
  (config) => {
    const token = tokenStorage.get()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理认证错误
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    // 401 未授权，清除 Token
    if (error.response?.status === 401) {
      tokenStorage.remove()
      // 可以在这里跳转到登录页
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
