import { vi } from 'vitest'

// 模拟 uni-app 的全局对象
global.uni = {
  // 导航相关
  navigateTo: vi.fn(),
  navigateBack: vi.fn(),
  redirectTo: vi.fn(),
  switchTab: vi.fn(),
  reLaunch: vi.fn(),

  // 存储相关
  setStorageSync: vi.fn(),
  getStorageSync: vi.fn(),
  removeStorageSync: vi.fn(),

  // 提示相关
  showToast: vi.fn(),
  showModal: vi.fn(),
  showLoading: vi.fn(),
  hideLoading: vi.fn(),

  // 请求相关
  request: vi.fn(),
}

// 模拟 console 对象（如果需要）
global.console = {
  ...console,
  log: vi.fn(),
  error: vi.fn(),
  warn: vi.fn(),
}
