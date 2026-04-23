/** Token 存储工具 */

const TOKEN_KEY = 'sageflow_token'
const USER_KEY = 'sageflow_user'

export const tokenStorage = {
  /** 获取 Token */
  get(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(TOKEN_KEY)
  },
  
  /** 设置 Token */
  set(token: string): void {
    if (typeof window === 'undefined') return
    localStorage.setItem(TOKEN_KEY, token)
  },
  
  /** 移除 Token */
  remove(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem(TOKEN_KEY)
  },
  
  /** 检查是否已登录 */
  isAuthenticated(): boolean {
    return !!this.get()
  },
}

export const userStorage = {
  /** 获取用户信息 */
  get(): any | null {
    if (typeof window === 'undefined') return null
    const data = localStorage.getItem(USER_KEY)
    return data ? JSON.parse(data) : null
  },
  
  /** 设置用户信息 */
  set(user: any): void {
    if (typeof window === 'undefined') return
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },
  
  /** 移除用户信息 */
  remove(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem(USER_KEY)
  },
}
