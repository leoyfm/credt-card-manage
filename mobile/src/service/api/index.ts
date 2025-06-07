import { http } from '@/utils/http'

// 使用项目中的IResData类型
export type ApiResponse<T = any> = IResData<T>

// 信用卡相关接口
export const cardApi = {
  // 获取信用卡列表
  getCards: (params?: any): Promise<ApiResponse> => {
    return http.get('/api/cards', { params })
  },
  
  // 获取单张信用卡详情
  getCardDetail: (id: string): Promise<ApiResponse> => {
    return http.get(`/api/cards/${id}`)
  },
  
  // 添加信用卡
  addCard: (data: any): Promise<ApiResponse> => {
    return http.post('/api/cards', data)
  },
  
  // 更新信用卡
  updateCard: (id: string, data: any): Promise<ApiResponse> => {
    return http.put(`/api/cards/${id}`, data)
  },
  
  // 删除信用卡
  deleteCard: (id: string): Promise<ApiResponse> => {
    return http.delete(`/api/cards/${id}`)
  }
}

// 消费记录相关接口
export const transactionApi = {
  // 获取消费记录列表
  getTransactions: (params?: any): Promise<ApiResponse> => {
    return http.get('/api/transactions', { params })
  },
  
  // 获取消费记录详情
  getTransactionDetail: (id: string): Promise<ApiResponse> => {
    return http.get(`/api/transactions/${id}`)
  },
  
  // 添加消费记录
  addTransaction: (data: any): Promise<ApiResponse> => {
    return http.post('/api/transactions', data)
  },
  
  // 更新消费记录
  updateTransaction: (id: string, data: any): Promise<ApiResponse> => {
    return http.put(`/api/transactions/${id}`, data)
  },
  
  // 删除消费记录
  deleteTransaction: (id: string): Promise<ApiResponse> => {
    return http.delete(`/api/transactions/${id}`)
  }
}

// 年费相关接口
export const annualFeeApi = {
  // 获取年费列表
  getAnnualFees: (params?: any): Promise<ApiResponse> => {
    return http.get('/api/annual-fees', { params })
  },
  
  // 获取年费统计
  getAnnualFeeStatistics: (userId: string): Promise<ApiResponse> => {
    return http.get(`/api/annual-fees/statistics/${userId}`)
  },
  
  // 检查年费减免条件
  checkWaiverCondition: (cardId: string, year: number): Promise<ApiResponse> => {
    return http.get(`/api/annual-fees/waiver-check/${cardId}/${year}`)
  }
}

// 通知相关接口
export const notificationApi = {
  // 获取通知列表
  getNotifications: (params?: any): Promise<ApiResponse> => {
    return http.get('/api/notifications', { params })
  },
  
  // 标记通知为已读
  markAsRead: (id: string): Promise<ApiResponse> => {
    return http.put(`/api/notifications/${id}/read`)
  },
  
  // 清空所有通知
  clearAll: (): Promise<ApiResponse> => {
    return http.delete('/api/notifications')
  }
}

// 统计相关接口
export const statisticsApi = {
  // 获取统计概览
  getOverview: (): Promise<ApiResponse> => {
    return http.get('/api/statistics')
  },
  
  // 获取月度趋势
  getMonthlyTrend: (months: number = 12): Promise<ApiResponse> => {
    return http.get('/api/statistics/monthly-trend', { params: { months } })
  },
  
  // 获取分类统计
  getCategoryStats: (): Promise<ApiResponse> => {
    return http.get('/api/statistics/category')
  }
}

// 费用相关接口
export const feeApi = {
  // 获取费用信息
  getFees: (params?: any): Promise<ApiResponse> => {
    return http.get('/api/fees', { params })
  },
  
  // 获取年费记录
  getAnnualFees: (params?: any): Promise<ApiResponse> => {
    return http.get('/api/fees/annual', { params })
  },
  
  // 获取利息记录
  getInterestFees: (params?: any): Promise<ApiResponse> => {
    return http.get('/api/fees/interest', { params })
  },
  
  // 获取其他费用
  getOtherFees: (params?: any): Promise<ApiResponse> => {
    return http.get('/api/fees/other', { params })
  }
}

// 用户相关接口
export const userApi = {
  // 获取用户信息
  getUserInfo: (): Promise<ApiResponse> => {
    return http.get('/api/user/info')
  },
  
  // 更新用户信息
  updateUserInfo: (data: any): Promise<ApiResponse> => {
    return http.put('/api/user/info', data)
  },
  
  // 用户登录
  login: (data: any): Promise<ApiResponse> => {
    return http.post('/api/user/login', data)
  },
  
  // 用户注册
  register: (data: any): Promise<ApiResponse> => {
    return http.post('/api/user/register', data)
  },
  
  // 用户退出
  logout: (): Promise<ApiResponse> => {
    return http.post('/api/user/logout')
  }
} 