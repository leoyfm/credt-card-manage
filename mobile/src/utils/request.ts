import { CustomRequestOptions } from '@/interceptors/request'
import { useUserStore } from '@/store/user'

/**
 * 请求方法: 主要是对 uni.request 的封装，去适配 openapi-ts-request 的 request 方法
 * @param options 请求参数
 * @returns 返回 Promise 对象
 */
const http = <T>(options: CustomRequestOptions) => {
  // 1. 返回 Promise 对象
  return new Promise<T>((resolve, reject) => {
    uni.request({
      ...options,
      dataType: 'json',
      // #ifndef MP-WEIXIN
      responseType: 'json',
      // #endif
      // 响应成功
      success(res) {
        // 状态码 2xx，参考 axios 的设计
        if (res.statusCode >= 200 && res.statusCode < 300) {
          // 2.1 提取核心数据 res.data
          const responseData = res.data as any

          // 检查是否是包装格式 {success, code, message, data, timestamp}
          if (
            responseData &&
            typeof responseData === 'object' &&
            'success' in responseData &&
            'data' in responseData
          ) {
            // 如果是包装格式，提取 data 字段
            resolve(responseData.data as T)
          } else {
            // 如果不是包装格式，直接返回
            resolve(responseData as T)
          }
        } else if (res.statusCode === 401) {
          const userStore = useUserStore()
          // 401错误  -> 清理用户信息，跳转到登录页
          userStore.clearUserInfo()
          uni.navigateTo({ url: '/pages/auth/login' })
          reject(res)
        } else {
          // 其他错误 -> 根据后端错误信息轻提示
          const errorData = res.data as any
          let errorMessage = '请求错误'

          // 尝试提取错误信息
          if (errorData) {
            if (errorData.message) {
              errorMessage = errorData.message
            } else if (errorData.msg) {
              errorMessage = errorData.msg
            }
          }

          !options.hideErrorToast &&
            uni.showToast({
              icon: 'none',
              title: errorMessage,
            })
          reject(res)
        }
      },
      // 响应失败
      fail(err) {
        uni.showToast({
          icon: 'none',
          title: '网络错误，换个网络试试',
        })
        reject(err)
      },
    })
  })
}

/*
 * openapi-ts-request 工具的 request 跨客户端适配方法
 */
export default function request<T = unknown>(
  url: string,
  options: Omit<CustomRequestOptions, 'url'> & {
    params?: Record<string, unknown>
    headers?: Record<string, unknown>
  },
) {
  const requestOptions = {
    url,
    ...options,
  }

  if (options.params) {
    requestOptions.query = requestOptions.params
    delete requestOptions.params
  }

  if (options.headers) {
    requestOptions.header = options.headers
    delete requestOptions.headers
  }

  return http<T>(requestOptions)
}
