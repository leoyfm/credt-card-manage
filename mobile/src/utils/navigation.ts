/**
 * 导航工具函数
 */

/**
 * 智能后退功能
 * 如果有后退页面则后退，否则跳转到首页
 * @param fallbackUrl 可选的回退页面URL，默认为首页
 */
export const smartGoBack = (fallbackUrl: string = '/pages/index/index') => {
  // 获取当前页面栈
  const pages = getCurrentPages()
  
  // 如果页面栈长度大于1，说明有后退页面
  if (pages.length > 1) {
    uni.navigateBack()
  } else {
    // 没有后退页面时，跳转到指定页面（默认首页）
    uni.reLaunch({
      url: fallbackUrl
    })
  }
}

/**
 * 强制跳转到首页
 * 清空页面栈并跳转到首页
 */
export const goToHome = () => {
  uni.reLaunch({
    url: '/pages/index/index'
  })
}

/**
 * 安全的页面跳转
 * 自动处理页面栈层级限制
 * @param url 要跳转的页面URL
 * @param options 跳转选项
 */
export const safeNavigateTo = (url: string, options?: UniApp.NavigateToOptions) => {
  const pages = getCurrentPages()
  
  // 如果页面栈接近上限（一般为10层），使用redirectTo代替navigateTo
  if (pages.length >= 9) {
    uni.redirectTo({
      url,
      ...options
    })
  } else {
    uni.navigateTo({
      url,
      ...options
    })
  }
} 