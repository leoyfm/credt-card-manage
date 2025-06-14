import { defineStore } from 'pinia'
import { ref } from 'vue'
import { toast } from '@/utils/toast'
import {
  loginUsernameApiV1PublicAuthLoginUsernamePost,
  refreshTokenApiV1PublicAuthRefreshTokenPost,
  registerApiV1PublicAuthRegisterPost,
} from '@/service/app/renzheng'
import {
  logoutApiV1UserProfileLogoutPost,
  getUserInfoApiV1UserProfileInfoGet,
} from '@/service/app/v1Yonghugerenziliao'
import type * as API from '@/service/app/types'

// 用户状态接口定义，基于新的API类型
interface IUserState {
  /** 用户基本信息 */
  userInfo: API.UserProfileResponse | null
  /** JWT访问令牌 */
  token: string
  /** 刷新令牌 */
  refreshToken?: string
  /** 是否已登录 */
  isLoggedIn: boolean
}

// 初始化状态
const initialState: IUserState = {
  userInfo: null,
  token: '',
  refreshToken: '',
  isLoggedIn: false,
}

export const useUserStore = defineStore('user', () => {
  // 用户状态
  const userInfo = ref<API.UserProfileResponse | null>(null)
  const token = ref<string>('')
  const refreshToken = ref<string>('')
  const isLoggedIn = ref<boolean>(false)

  /**
   * 设置用户信息和token（基于AuthResponse）
   * @param authData 认证响应数据
   */
  const setAuthData = (authData: API.AuthResponse) => {
    // 将AuthResponse转换为UserProfileResponse格式
    userInfo.value = {
      id: authData.user_id,
      username: authData.username,
      email: authData.email,
      nickname: authData.nickname,
      phone: authData.phone,
      avatar_url: authData.avatar_url,
      is_active: authData.is_active || false,
      is_verified: authData.is_verified || false,
      timezone: authData.timezone || 'Asia/Shanghai',
      language: authData.language || 'zh-CN',
      currency: authData.currency || 'CNY',
      last_login_at: authData.last_login_at,
      email_verified_at: authData.email_verified_at,
      created_at: authData.created_at || new Date().toISOString(),
    }

    token.value = authData.access_token
    refreshToken.value = authData.refresh_token
    isLoggedIn.value = true

    // 保存到本地存储
    uni.setStorageSync('token', authData.access_token)
    uni.setStorageSync('refreshToken', authData.refresh_token)
    uni.setStorageSync('userInfo', userInfo.value)
    uni.setStorageSync('isLoggedIn', true)

    console.log('用户登录成功，保存用户信息:', userInfo.value)
  }

  /**
   * 设置用户信息（仅更新用户资料，不更新token）
   * @param user 用户信息
   */
  const setUserInfo = (user: API.UserProfileResponse) => {
    userInfo.value = user
    uni.setStorageSync('userInfo', user)
    console.log('更新用户信息:', user)
  }

  /**
   * 清除用户信息
   */
  const clearUserInfo = () => {
    userInfo.value = null
    token.value = ''
    refreshToken.value = ''
    isLoggedIn.value = false

    // 清除本地存储
    uni.removeStorageSync('token')
    uni.removeStorageSync('refreshToken')
    uni.removeStorageSync('userInfo')
    uni.removeStorageSync('isLoggedIn')

    console.log('清除用户信息')
  }

  /**
   * 从本地存储恢复用户状态
   */
  const restoreUserState = () => {
    try {
      const storedToken = uni.getStorageSync('token')
      const storedRefreshToken = uni.getStorageSync('refreshToken')
      const storedUserInfo = uni.getStorageSync('userInfo')
      const storedIsLoggedIn = uni.getStorageSync('isLoggedIn')

      if (storedToken && storedUserInfo && storedIsLoggedIn) {
        token.value = storedToken
        refreshToken.value = storedRefreshToken || ''
        userInfo.value = storedUserInfo
        isLoggedIn.value = true
        console.log('从本地存储恢复用户状态')
      }
    } catch (error) {
      console.error('恢复用户状态失败:', error)
      clearUserInfo()
    }
  }

  /**
   * 账号密码登录
   * @param credentials 登录凭据
   */
  const loginWithUsername = async (credentials: { username: string; password: string }) => {
    try {
      const requestBody: API.LoginRequest = {
        username: credentials.username,
        password: credentials.password,
      }

      const response = await loginUsernameApiV1PublicAuthLoginUsernamePost({
        body: requestBody,
      })

      // response 直接是 AuthResponse 类型
      setAuthData(response)
      toast.success('登录成功')
      return { success: true, data: response }
    } catch (error: any) {
      console.error('账号密码登录失败:', error)
      let errorMsg = '登录失败，请稍后重试'

      if (error.response?.data?.message) {
        errorMsg = error.response.data.message
      } else if (error.message) {
        errorMsg = error.message
      }

      toast.error(errorMsg)
      return { success: false, message: errorMsg }
    }
  }

  /**
   * 用户注册
   * @param userData 注册数据
   */
  const register = async (userData: API.RegisterRequest) => {
    try {
      const response = await registerApiV1PublicAuthRegisterPost({
        body: userData,
      })

      // response 直接是 AuthResponse 类型
      setAuthData(response)
      toast.success('注册成功')
      return { success: true, data: response }
    } catch (error: any) {
      console.error('用户注册失败:', error)
      let errorMsg = '注册失败，请稍后重试'

      if (error.response?.data?.message) {
        errorMsg = error.response.data.message
      } else if (error.message) {
        errorMsg = error.message
      }

      toast.error(errorMsg)
      return { success: false, message: errorMsg }
    }
  }

  /**
   * 获取当前用户信息
   */
  const getCurrentUser = async () => {
    try {
      const response = await getUserInfoApiV1UserProfileInfoGet({})

      // response 是 ApiResponseUserProfileResponse_ 类型，包含 success, data 等字段
      if (response.success && response.data) {
        setUserInfo(response.data)
        return { success: true, data: response.data }
      } else {
        const errorMsg = response.message || '获取用户信息失败'
        return { success: false, message: errorMsg }
      }
    } catch (error: any) {
      console.error('获取用户信息失败:', error)
      let errorMsg = '获取用户信息失败，请稍后重试'

      if (error.response?.data?.message) {
        errorMsg = error.response.data.message
      } else if (error.message) {
        errorMsg = error.message
      }

      return { success: false, message: errorMsg }
    }
  }

  /**
   * 刷新token
   * @param refreshTokenValue 刷新令牌
   */
  const refreshAccessToken = async (refreshTokenValue?: string) => {
    try {
      const tokenToRefresh = refreshTokenValue || refreshToken.value

      if (!tokenToRefresh) {
        throw new Error('没有有效的刷新令牌')
      }

      const requestBody: API.RefreshTokenRequest = {
        refresh_token: tokenToRefresh,
      }

      const response = await refreshTokenApiV1PublicAuthRefreshTokenPost({
        body: requestBody,
      })

      // response 直接是 TokenResponse 类型
      token.value = response.access_token
      refreshToken.value = response.refresh_token

      // 保存到本地存储
      uni.setStorageSync('token', response.access_token)
      uni.setStorageSync('refreshToken', response.refresh_token)

      return { success: true, data: response }
    } catch (error: any) {
      console.error('Token刷新失败:', error)
      let errorMsg = 'Token刷新失败，请重新登录'

      if (error.response?.data?.message) {
        errorMsg = error.response.data.message
      } else if (error.message) {
        errorMsg = error.message
      }

      // Token刷新失败，清除用户信息
      clearUserInfo()
      return { success: false, message: errorMsg }
    }
  }

  /**
   * 用户登出
   * @param allDevices 是否登出所有设备
   */
  const logout = async (allDevices: boolean = false) => {
    try {
      await logoutApiV1UserProfileLogoutPost({})

      clearUserInfo()
      toast.success('登出成功')

      // 跳转到登录页面
      uni.reLaunch({ url: '/pages/auth/login' })

      return { success: true }
    } catch (error: any) {
      console.error('登出失败:', error)
      // 即使登出API失败，也要清除本地数据
      clearUserInfo()
      uni.reLaunch({ url: '/pages/auth/login' })
      return { success: false, message: error.message }
    }
  }

  /**
   * 检查登录状态
   */
  const checkLoginStatus = () => {
    return isLoggedIn.value && !!token.value && !!userInfo.value
  }

  // 应用启动时恢复用户状态
  restoreUserState()

  return {
    // 状态
    userInfo,
    token,
    refreshToken,
    isLoggedIn,

    // 动作
    setAuthData,
    setUserInfo,
    clearUserInfo,
    restoreUserState,
    loginWithUsername,
    register,
    getCurrentUser,
    refreshAccessToken,
    logout,
    checkLoginStatus,
  }
})
