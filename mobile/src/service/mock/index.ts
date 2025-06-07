import Mock from 'mockjs'

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

// 信用卡数据
Mock.mock('/api/cards', 'get', {
  code: 200,
  message: '获取成功',
  data: {
    'list|8-10': [{
      'id|+1': 1,
      'bankId': () => Mock.Random.pick(banks).id,
      'bankName': function() {
        return banks.find(b => b.id === this.bankId)?.name || '招商银行'
      },
      'bankCode': function() {
        return banks.find(b => b.id === this.bankId)?.code || 'CMB'
      },
      'bankColor': function() {
        return banks.find(b => b.id === this.bankId)?.color || '#DC143C'
      },
      'cardName': () => Mock.Random.pick(['信用卡', '金卡', '白金卡', '钻石卡', '无限卡']),
      'cardNumber': () => Mock.Random.replace('################'),
      'cardNumberLast4': function() {
        return this.cardNumber.slice(-4)
      },
      'creditLimit|50000-500000': 100000,
      'usedAmount|10000-50000': 25000,
      'availableAmount': function() {
        return this.creditLimit - this.usedAmount
      },
      'billingDay|1-31': 15,
      'dueDay|1-31': 5,
      'nextBillingDate': () => Mock.Random.date('yyyy-MM-dd'),
      'nextDueDate': () => Mock.Random.date('yyyy-MM-dd'),
      'annualFee|0-2000': 200,
      'annualFeeStatus': () => Mock.Random.pick(['pending', 'waived', 'paid', 'overdue']),
      'feeType': () => Mock.Random.pick(feeTypes.map(f => f.type)),
      'waiverProgress|0-100': 65,
      'waiverCondition': function() {
        const type = feeTypes.find(f => f.type === this.feeType)
        if (type?.type === 'transaction_count') return `年内刷卡${Mock.Random.integer(8, 20)}次`
        if (type?.type === 'transaction_amount') return `年内消费满${Mock.Random.integer(5, 20)}万元`
        if (type?.type === 'points_exchange') return `${Mock.Random.integer(20000, 80000)}积分兑换`
        return '不可减免'
      },
      'isActive': () => Mock.Random.boolean(),
      'cardLevel': () => Mock.Random.pick(['普卡', '金卡', '白金卡', '钻石卡']),
      'cardType': () => Mock.Random.pick(['VISA', 'MasterCard', '银联', 'JCB']),
      'activationDate': () => Mock.Random.date('yyyy-MM-dd'),
      'expiryDate': () => Mock.Random.date('yyyy-MM-dd'),
    }],
    'total|50-100': 68,
    'summary': {
      'totalCards|8-15': 12,
      'activeCards|5-12': 8,
      'totalCreditLimit|500000-2000000': 1250000,
      'totalUsedAmount|100000-800000': 350000,
      'totalAvailableAmount': function() {
        return this.totalCreditLimit - this.totalUsedAmount
      },
      'freeDays|15-60': 18,
      'totalAnnualFee|0-5000': 1200,
      'waivedAnnualFee|0-3000': 800,
    }
  }
})

// 消费记录数据
Mock.mock('/api/transactions', 'get', {
  code: 200,
  message: '获取成功',
  data: {
    'list|20-30': [{
      'id|+1': 1,
      'cardId|1-10': 1,
      'amount|100-5000': 1000,
      'merchantName': () => Mock.Random.pick([
        '沃尔玛超市', '星巴克咖啡', '中石化加油站', '麦当劳', '肯德基',
        '苹果专卖店', '华为商城', '京东商城', '天猫超市', '盒马鲜生',
        '海底捞火锅', '西贝莜面村', '太平洋影城', '健身房', '药店'
      ]),
      'category': () => Mock.Random.pick([
        '餐饮美食', '购物消费', '交通出行', '生活服务', '娱乐休闲',
        '医疗健康', '教育培训', '旅游度假', '数码3C', '服装配饰'
      ]),
      'transactionDate': () => Mock.Random.datetime('yyyy-MM-dd HH:mm:ss'),
      'transactionType': () => Mock.Random.pick(['消费', '退款', '转账', '取现']),
      'status': () => Mock.Random.pick(['已入账', '未入账', '已还款']),
      'installment|0-24': 0,
      'points|10-100': 50,
      'location': () => Mock.Random.city(),
      'description': function() {
        return `${this.merchantName} - ${this.category}`
      }
    }],
    'total|100-500': 256,
    'summary': {
      'totalAmount|10000-100000': 45600,
      'monthlyAmount|5000-30000': 12800,
      'totalTransactions|50-300': 156,
      'monthlyTransactions|10-50': 28,
    }
  }
})

// 年费数据
Mock.mock('/api/annual-fees', 'get', {
  code: 200,
  message: '获取成功',
  data: {
    'list|8-12': [{
      'id|+1': 1,
      'cardId|1-10': 1,
      'bankName': () => Mock.Random.pick(banks).name,
      'cardName': () => Mock.Random.pick(['信用卡', '金卡', '白金卡', '钻石卡']),
      'annualFee|0-2000': 300,
      'feeYear': () => new Date().getFullYear(),
      'dueDate': () => Mock.Random.date('yyyy-MM-dd'),
      'status': () => Mock.Random.pick(['pending', 'waived', 'paid', 'overdue']),
      'feeType': () => Mock.Random.pick(feeTypes.map(f => f.type)),
      'waiverCondition': function() {
        const type = feeTypes.find(f => f.type === this.feeType)
        if (type?.type === 'transaction_count') return `年内刷卡${Mock.Random.integer(8, 20)}次`
        if (type?.type === 'transaction_amount') return `年内消费满${Mock.Random.integer(5, 20)}万元`
        if (type?.type === 'points_exchange') return `${Mock.Random.integer(20000, 80000)}积分兑换`
        return '不可减免'
      },
      'currentProgress|0-100': 65,
      'progressDescription': function() {
        if (this.feeType === 'transaction_count') return `已刷卡${Mock.Random.integer(0, 20)}次`
        if (this.feeType === 'transaction_amount') return `已消费${Mock.Random.integer(0, 20)}万元`
        if (this.feeType === 'points_exchange') return `当前积分${Mock.Random.integer(10000, 100000)}`
        return '不可减免'
      },
      'daysRemaining|0-365': 90,
    }],
    'summary': {
      'totalAnnualFees|1000-10000': 3600,
      'waivedFees|500-5000': 1800,
      'paidFees|200-3000': 1200,
      'pendingFees|0-2000': 600,
      'overdueFees|0-1000': 0,
      'waiverRate|0-100': 75,
    }
  }
})

// 通知数据
Mock.mock('/api/notifications', 'get', {
  code: 200,
  message: '获取成功',
  data: {
    'list|10-20': [{
      'id|+1': 1,
      'title': () => Mock.Random.pick([
        '信用卡长城环球通用卡',
        '工商银行宇宙星座信用卡',
        '招商银行全币种国际信用卡',
        '年费即将到期提醒',
        '账单已出，请及时还款',
        '新的积分活动开始了'
      ]),
      'content': function() {
        if (this.title.includes('年费')) return `年费 ¥${Mock.Random.integer(200, 2000)} 将在${Mock.Random.integer(10, 90)}天后到期，请注意查看减免条件`
        if (this.title.includes('账单')) return `请在${Mock.Random.integer(3, 30)}天内还款 ¥${Mock.Random.integer(1000, 20000)} 元`
        return `使用率已达${Mock.Random.integer(80, 95)}%，建议及时还款以维护良好信用记录`
      },
      'type': () => Mock.Random.pick(['warning', 'info', 'success', 'error']),
      'isRead': () => Mock.Random.boolean(),
      'createTime': () => Mock.Random.datetime('yyyy-MM-dd HH:mm:ss'),
      'cardInfo': function() {
        const bank = Mock.Random.pick(banks)
        return {
          bankName: bank.name,
          cardNumber: Mock.Random.replace('****####'),
        }
      }
    }],
    'unreadCount|3-15': 8,
  }
})

// 统计数据
Mock.mock('/api/statistics', 'get', {
  code: 200,
  message: '获取成功',
  data: {
    'overview': {
      'totalCards|8-15': 12,
      'activeCards|5-12': 8,
      'totalCreditLimit|500000-2000000': 1250000,
      'totalUsedAmount|100000-800000': 350000,
      'totalAvailableAmount': function() {
        return this.totalCreditLimit - this.totalUsedAmount
      },
      'utilizationRate': function() {
        return Math.round((this.totalUsedAmount / this.totalCreditLimit) * 100)
      },
      'freeDays|15-60': 18,
    },
    'monthlyTrend|12': [{
      'month': () => Mock.Random.date('MM'),
      'amount|5000-50000': 15000,
      'transactions|10-100': 45,
    }],
    'categoryStats|8-12': [{
      'category': () => Mock.Random.pick([
        '餐饮美食', '购物消费', '交通出行', '生活服务', '娱乐休闲',
        '医疗健康', '教育培训', '旅游度假', '数码3C', '服装配饰'
      ]),
      'amount|1000-20000': 8500,
      'count|5-50': 25,
      'percentage|5-25': 15,
    }]
  }
})

export default Mock 