import { defineStore } from 'pinia'
import { ref } from 'vue'
import { toast } from '@/utils/toast'
import { 
  loginWithUsernamePasswordApiAuthLoginUsernamePost,
  loginWithPhoneCodeApiAuthLoginPhoneCodePost,
  sendVerificationCodeApiAuthCodeSendPost,
  registerApiAuthRegisterPost,
  logoutApiAuthLogoutPost,
  getUserProfileApiAuthProfileGet,
  refreshAccessTokenApiAuthTokenRefreshPost
} from '@/service/app/yonghurenzheng'
import type * as API from '@/service/app/types'

// 用户状态接口定义，基于新的API类型
interface IUserState {
  /** 用户基本信息 */
  userInfo: API.UserProfile | null
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
  isLoggedIn: false
}

export const useUserStore = defineStore(
  'user',
  () => {
    // 用户状态
    const userInfo = ref<API.UserProfile | null>(null)
    const token = ref<string>('')
    const refreshToken = ref<string>('')
    const isLoggedIn = ref<boolean>(false)

    /**
     * 设置用户信息和token
     * @param loginData 登录响应数据
     */
    const setLoginData = (loginData: API.LoginResponse) => {
      userInfo.value = loginData.user
      token.value = loginData.access_token
      isLoggedIn.value = true
      
      // 保存到本地存储
      uni.setStorageSync('token', loginData.access_token)
      uni.setStorageSync('userInfo', loginData.user)
      uni.setStorageSync('isLoggedIn', true)
      
      console.log('用户登录成功，保存用户信息:', loginData.user)
    }

    /**
     * 设置用户信息（仅更新用户资料，不更新token）
     * @param user 用户信息
     */
    const setUserInfo = (user: API.UserProfile) => {
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
        const storedUserInfo = uni.getStorageSync('userInfo')
        const storedIsLoggedIn = uni.getStorageSync('isLoggedIn')
        
        if (storedToken && storedUserInfo && storedIsLoggedIn) {
          token.value = storedToken
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
    const loginWithUsername = async (credentials: {
      username: string
      password: string
      remember_me?: boolean
    }) => {
      try {
        const requestBody: API.UsernamePasswordLogin = {
          username: credentials.username,
          password: credentials.password,
          remember_me: credentials.remember_me ?? true
        }
        
        const response = await loginWithUsernamePasswordApiAuthLoginUsernamePost({
          body: requestBody
        })
        
        if (response.success && response.data) {
          setLoginData(response.data)
          toast.success('登录成功')
          return { success: true, data: response.data }
        } else {
          const errorMsg = response.message || '登录失败'
          toast.error(errorMsg)
          return { success: false, message: errorMsg }
        }
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
     * 手机验证码登录
     * @param credentials 登录凭据
     */
    const loginWithPhoneCode = async (credentials: {
      phone: string
      verification_code: string
    }) => {
      try {
        const requestBody: API.PhoneCodeLogin = {
          phone: credentials.phone,
          verification_code: credentials.verification_code
        }
        
        const response = await loginWithPhoneCodeApiAuthLoginPhoneCodePost({
          body: requestBody
        })
        
        if (response.success && response.data) {
          setLoginData(response.data)
          toast.success('登录成功')
          return { success: true, data: response.data }
        } else {
          const errorMsg = response.message || '登录失败'
          toast.error(errorMsg)
          return { success: false, message: errorMsg }
        }
      } catch (error: any) {
        console.error('手机验证码登录失败:', error)
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
     * 发送验证码
     * @param params 发送参数
     */
    const sendVerificationCode = async (params: {
      phone_or_email: string
      code_type: API.CodeType
    }) => {
      try {
        const requestBody: API.SendCodeRequest = {
          phone_or_email: params.phone_or_email,
          code_type: params.code_type
        }
        
        const response = await sendVerificationCodeApiAuthCodeSendPost({
          body: requestBody
        })
        
        if (response.success) {
          toast.success('验证码发送成功')
          return { success: true }
        } else {
          const errorMsg = response.message || '验证码发送失败'
          toast.error(errorMsg)
          return { success: false, message: errorMsg }
        }
      } catch (error: any) {
        console.error('发送验证码失败:', error)
        let errorMsg = '验证码发送失败，请稍后重试'
        
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
     const register = async (userData: API.UserRegisterRequest) => {
       try {
         const response = await registerApiAuthRegisterPost({
           body: userData
         })
         
         if (response.success && response.data) {
           // 注册接口只返回用户信息，不包含token，需要提示用户登录
           toast.success('注册成功，请登录')
           return { success: true, data: response.data }
         } else {
           const errorMsg = response.message || '注册失败'
           toast.error(errorMsg)
           return { success: false, message: errorMsg }
         }
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
         const response = await getUserProfileApiAuthProfileGet({})
         
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
          refresh_token: tokenToRefresh
        }
        
                 const response = await refreshAccessTokenApiAuthTokenRefreshPost({
           body: requestBody
         })
        
        if (response.success && response.data) {
          setLoginData(response.data)
          return { success: true, data: response.data }
        } else {
          const errorMsg = response.message || 'Token刷新失败'
          return { success: false, message: errorMsg }
        }
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
        const requestBody: API.LogoutRequest = {
          all_devices: allDevices
        }
        
        await logoutApiAuthLogoutPost({
          body: requestBody
        })
        
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
      setLoginData,
      setUserInfo,
      clearUserInfo,
      restoreUserState,
      loginWithUsername,
      loginWithPhoneCode,
      sendVerificationCode,
      register,
      getCurrentUser,
      refreshAccessToken,
      logout,
      checkLoginStatus
    }
  },
  {
    persist: true,
  },
)
