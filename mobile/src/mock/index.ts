import Mock from 'mockjs'

// 开发环境初始化提示
console.log('🔧 Mock.js 初始化开始...')

// 银行数据
const banks = [
  { id: '1', name: '招商银行', code: 'CMB', color: '#DC143C' },
  { id: '2', name: '工商银行', code: 'ICBC', color: '#C41E3A' },
  { id: '3', name: '建设银行', code: 'CCB', color: '#003399' },
  { id: '4', name: '中国银行', code: 'BOC', color: '#B22222' },
  { id: '5', name: '交通银行', code: 'BOCOM', color: '#0066CC' },
  { id: '6', name: '浦发银行', code: 'SPDB', color: '#4169E1' },
  { id: '7', name: '中信银行', code: 'CITIC', color: '#8B0000' },
  { id: '8', name: '光大银行', code: 'CEB', color: '#9932CC' },
]

// 年费类型
const feeTypes = [
  { type: 'rigid', name: '刚性年费', canWaive: false },
  { type: 'transaction_count', name: '刷卡次数减免', canWaive: true },
  { type: 'transaction_amount', name: '刷卡金额减免', canWaive: true },
  { type: 'points_exchange', name: '积分兑换', canWaive: true },
]

// Mock 配置
Mock.setup({
  timeout: '200-600'
})

console.log('📊 注册 Mock 接口...')

// 信用卡数据
Mock.mock('/api/cards', 'get', () => {
  console.log('🎯 Mock 拦截到请求: /api/cards')
  return {
    code: 200,
    msg: '获取成功',
    message: '获取成功',
    data: {
      list: Array.from({ length: 8 }, (_, index) => {
        const bank = banks[index % banks.length]
        const feeType = feeTypes[index % feeTypes.length]
        return {
          id: (index + 1).toString(),
          bankId: bank.id,
          bankName: bank.name,
          bankCode: bank.code,
          bankColor: bank.color,
          cardName: Mock.Random.pick(['信用卡', '金卡', '白金卡', '钻石卡', '无限卡']),
          cardNumber: Mock.Random.replace('################'),
          cardNumberLast4: Mock.Random.replace('####'),
          creditLimit: Mock.Random.integer(50000, 500000),
          usedAmount: Mock.Random.integer(10000, 50000),
          availableAmount: Mock.Random.integer(40000, 450000),
          billingDay: Mock.Random.integer(1, 31),
          dueDay: Mock.Random.integer(1, 31),
          nextBillingDate: Mock.Random.date('yyyy-MM-dd'),
          nextDueDate: Mock.Random.date('yyyy-MM-dd'),
          annualFee: Mock.Random.integer(0, 2000),
          annualFeeStatus: Mock.Random.pick(['pending', 'waived', 'paid', 'overdue']),
          feeType: feeType.type,
          waiverProgress: Mock.Random.integer(0, 100),
          waiverCondition: feeType.name,
          isActive: Mock.Random.boolean(),
          cardLevel: Mock.Random.pick(['普卡', '金卡', '白金卡', '钻石卡']),
          cardType: Mock.Random.pick(['VISA', 'MasterCard', '银联', 'JCB']),
          activationDate: Mock.Random.date('yyyy-MM-dd'),
          expiryDate: Mock.Random.date('yyyy-MM-dd'),
        }
      }),
      total: 68,
      summary: {
        totalCards: 12,
        activeCards: 8,
        totalCreditLimit: 1250000,
        totalUsedAmount: 350000,
        totalAvailableAmount: 900000,
        freeDays: 18,
        totalAnnualFee: 1200,
        waivedAnnualFee: 800,
      }
    }
  }
})

// 消费记录数据
Mock.mock('/api/transactions', 'get', () => {
  console.log('🎯 Mock 拦截到请求: /api/transactions')
  return {
    code: 200,
    msg: '获取成功',
    message: '获取成功',
    data: {
      list: Array.from({ length: 20 }, (_, index) => ({
        id: (index + 1).toString(),
        cardId: Mock.Random.integer(1, 10).toString(),
        amount: Mock.Random.integer(100, 5000),
        merchantName: Mock.Random.pick([
          '沃尔玛超市', '星巴克咖啡', '中石化加油站', '麦当劳', '肯德基',
          '苹果专卖店', '华为商城', '京东商城', '天猫超市', '盒马鲜生',
          '海底捞火锅', '西贝莜面村', '太平洋影城', '健身房', '药店'
        ]),
        category: Mock.Random.pick([
          '餐饮美食', '购物消费', '交通出行', '生活服务', '娱乐休闲',
          '医疗健康', '教育培训', '旅游度假', '数码3C', '服装配饰'
        ]),
        transactionDate: Mock.Random.datetime('yyyy-MM-dd HH:mm:ss'),
        transactionType: Mock.Random.pick(['消费', '退款', '转账', '取现']),
        status: Mock.Random.pick(['已入账', '未入账', '已还款']),
        installment: Mock.Random.integer(0, 24),
        points: Mock.Random.integer(10, 100),
        location: Mock.Random.city(),
        description: '测试交易记录'
      })),
      total: 256,
      summary: {
        totalAmount: 45600,
        monthlyAmount: 12800,
        totalTransactions: 156,
        monthlyTransactions: 28,
      }
    }
  }
})

// 通知数据
Mock.mock('/api/notifications', 'get', () => {
  console.log('🎯 Mock 拦截到请求: /api/notifications')
  return {
    code: 200,
    msg: '获取成功',
    message: '获取成功',
    data: {
      list: Array.from({ length: 10 }, (_, index) => ({
        id: (index + 1).toString(),
        title: Mock.Random.pick([
          '信用卡长城环球通用卡',
          '工商银行宇宙星座信用卡',
          '招商银行全币种国际信用卡',
          '年费即将到期提醒',
          '账单已出，请及时还款',
          '新的积分活动开始了'
        ]),
        content: '这是一条测试通知内容',
        type: Mock.Random.pick(['warning', 'info', 'success', 'error']),
        isRead: Mock.Random.boolean(),
        createTime: Mock.Random.datetime('yyyy-MM-dd HH:mm:ss'),
        cardInfo: {
          bankName: Mock.Random.pick(banks).name,
          cardNumber: Mock.Random.replace('****####'),
        }
      })),
      unreadCount: 8,
    }
  }
})

// 统计数据
Mock.mock('/api/statistics', 'get', () => {
  console.log('🎯 Mock 拦截到请求: /api/statistics')
  return {
    code: 200,
    msg: '获取成功',
    message: '获取成功',
    data: {
      overview: {
        totalCards: 12,
        activeCards: 8,
        totalCreditLimit: 1250000,
        totalUsedAmount: 350000,
        totalAvailableAmount: 900000,
        utilizationRate: 28,
        freeDays: 18,
      },
      monthlyTrend: Array.from({ length: 12 }, (_, index) => ({
        month: (index + 1).toString().padStart(2, '0'),
        amount: Mock.Random.integer(5000, 50000),
        transactions: Mock.Random.integer(10, 100),
      })),
      categoryStats: Array.from({ length: 8 }, (_, index) => ({
        category: Mock.Random.pick([
          '餐饮美食', '购物消费', '交通出行', '生活服务', '娱乐休闲',
          '医疗健康', '教育培训', '旅游度假', '数码3C', '服装配饰'
        ]),
        amount: Mock.Random.integer(1000, 20000),
        count: Mock.Random.integer(5, 50),
        percentage: Mock.Random.integer(5, 25),
      }))
    }
  }
})

// 其他接口简化版本
Mock.mock('/api/annual-fees', 'get', () => {
  console.log('🎯 Mock 拦截到请求: /api/annual-fees')
  return {
    code: 200,
    msg: '获取成功',
    data: { list: [], summary: {} }
  }
})

Mock.mock('/api/fees', 'get', () => {
  console.log('🎯 Mock 拦截到请求: /api/fees')
  return {
    code: 200,
    msg: '获取成功',
    data: { list: [], summary: {} }
  }
})

Mock.mock('/api/user/info', 'get', () => {
  console.log('🎯 Mock 拦截到请求: /api/user/info')
  return {
    code: 200,
    msg: '获取成功',
    data: {
      id: '1',
      username: 'test_user',
      avatar: '',
      nickname: '测试用户',
      email: 'test@example.com'
    }
  }
})

console.log('✅ Mock.js 初始化完成!')
console.log('🎯 已注册的 Mock 接口:', [
  '/api/cards',
  '/api/transactions', 
  '/api/notifications',
  '/api/statistics',
  '/api/annual-fees',
  '/api/fees',
  '/api/user/info'
])

// 在 H5 平台暴露到全局
// #ifdef H5
if (typeof window !== 'undefined') {
  (window as any).Mock = Mock
  console.log('🌐 Mock.js 已暴露到全局 window.Mock')
}
// #endif

export default Mock 