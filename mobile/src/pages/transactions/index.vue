<!-- 消费记录页面 -->
<route lang="json5">
{
  style: {
    navigationBarTitleText: '消费记录',
    enablePullDownRefresh: true,
  },
}
</route>

<template>
  <view class="transactions-page">
    <!-- 顶部统计 -->
    <view class="stats-header bg-gradient-to-r from-green-500 to-blue-500 text-white p-4">
      <view class="flex justify-around">
        <view class="text-center">
          <text class="text-2xl font-bold block">{{ summary.monthlyTransactions }}</text>
          <text class="text-sm opacity-80">本月笔数</text>
        </view>
        <view class="text-center">
          <text class="text-2xl font-bold block">¥{{ formatMoney(summary.monthlyAmount) }}</text>
          <text class="text-sm opacity-80">本月消费</text>
        </view>
        <view class="text-center">
          <text class="text-2xl font-bold block">¥{{ formatMoney(summary.totalAmount) }}</text>
          <text class="text-sm opacity-80">总消费</text>
        </view>
      </view>
    </view>

    <!-- 筛选栏 -->
    <view class="filter-section bg-white px-4 py-3 shadow-sm">
      <!-- 第一行：快速筛选 -->
      <view class="flex space-x-2 mb-3">
        <view
          v-for="filter in quickFilters"
          :key="filter.key"
          class="filter-tag px-3 py-1 rounded-full text-sm transition-all"
          :class="
            activeFilters.includes(filter.key)
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-600'
          "
          @click="toggleFilter(filter.key)"
        >
          {{ filter.label }}
        </view>
      </view>

      <!-- 第二行：下拉筛选 -->
      <view class="flex space-x-3">
        <picker
          :value="cardFilterIndex"
          :range="cardOptions"
          range-key="label"
          @change="onCardFilterChange"
          class="flex-1"
        >
          <view
            class="filter-select flex items-center justify-between py-2 px-3 bg-gray-50 rounded"
          >
            <text class="text-sm">{{ cardOptions[cardFilterIndex].label }}</text>
            <text class="text-gray-400 text-xs">▼</text>
          </view>
        </picker>

        <picker
          :value="categoryFilterIndex"
          :range="categoryOptions"
          range-key="label"
          @change="onCategoryFilterChange"
          class="flex-1"
        >
          <view
            class="filter-select flex items-center justify-between py-2 px-3 bg-gray-50 rounded"
          >
            <text class="text-sm">{{ categoryOptions[categoryFilterIndex].label }}</text>
            <text class="text-gray-400 text-xs">▼</text>
          </view>
        </picker>

        <picker mode="date" :value="dateFilter" @change="onDateFilterChange" class="flex-1">
          <view
            class="filter-select flex items-center justify-between py-2 px-3 bg-gray-50 rounded"
          >
            <text class="text-sm">{{ dateFilter || '选择日期' }}</text>
            <text class="text-gray-400 text-xs">▼</text>
          </view>
        </picker>
      </view>
    </view>

    <!-- 搜索栏 -->
    <view class="search-section bg-white px-4 py-3 border-t border-gray-100">
      <view class="flex items-center bg-gray-50 rounded-full px-4 py-2">
        <text class="text-gray-400 mr-2">🔍</text>
        <input
          v-model="searchKeyword"
          placeholder="搜索商户或描述"
          class="flex-1 text-sm bg-transparent"
          @input="handleSearch"
        />
        <text v-if="searchKeyword" class="text-gray-400 ml-2" @click="clearSearch">✕</text>
      </view>
    </view>

    <!-- 消费记录列表 -->
    <view class="transaction-list px-4 py-2">
      <!-- 统计信息 -->
      <view class="list-stats bg-white rounded-lg p-3 mb-4 shadow-sm">
        <view class="flex justify-between text-sm">
          <text class="text-gray-600">共 {{ filteredTransactions.length }} 笔交易</text>
          <text class="text-blue-600">合计 ¥{{ formatMoney(filteredTotal) }}</text>
        </view>
      </view>

      <!-- 按日期分组的交易列表 -->
      <view v-for="(group, date) in groupedTransactions" :key="date" class="date-group mb-4">
        <!-- 日期头部 -->
        <view class="date-header flex items-center justify-between py-2">
          <text class="text-gray-800 font-medium">{{ formatGroupDate(date) }}</text>
          <text class="text-sm text-gray-500">
            {{ group.length }}笔 ¥{{ formatMoney(group.reduce((sum, t) => sum + t.amount, 0)) }}
          </text>
        </view>

        <!-- 该日期的交易 -->
        <view class="bg-white rounded-lg overflow-hidden shadow-sm">
          <view
            v-for="(transaction, index) in group"
            :key="transaction.id"
            class="transaction-item flex items-center p-4 transition-all"
            :class="{ 'border-t border-gray-100': index > 0 }"
            @click="goToTransactionDetail(transaction.id)"
          >
            <!-- 分类图标 -->
            <view
              class="category-icon w-10 h-10 rounded-full flex items-center justify-center mr-3"
              :style="{ backgroundColor: getCategoryColor(transaction.category) }"
            >
              <text class="text-white text-sm">{{ getCategoryIcon(transaction.category) }}</text>
            </view>

            <!-- 交易信息 -->
            <view class="transaction-info flex-1">
              <view class="flex items-center justify-between mb-1">
                <text class="font-medium text-gray-800">{{ transaction.merchantName }}</text>
                <text class="font-bold" :class="getAmountClass(transaction.transactionType)">
                  {{ transaction.transactionType === '退款' ? '+' : '-' }}¥{{
                    formatMoney(transaction.amount)
                  }}
                </text>
              </view>

              <view class="flex items-center justify-between">
                <view class="flex items-center space-x-2">
                  <text class="text-xs text-gray-500">{{ transaction.category }}</text>
                  <text class="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                    {{ transaction.transactionType }}
                  </text>
                </view>
                <text class="text-xs text-gray-500">
                  {{ formatTime(transaction.transactionDate) }}
                </text>
              </view>

              <view v-if="transaction.installment > 0" class="mt-1">
                <text class="text-xs bg-orange-100 text-orange-600 px-2 py-0.5 rounded">
                  {{ transaction.installment }}期分期
                </text>
              </view>
            </view>

            <!-- 右箭头 -->
            <text class="text-gray-300 ml-2">›</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view v-if="filteredTransactions.length === 0" class="empty-state text-center py-16">
      <text class="text-4xl mb-4 block">📝</text>
      <text class="text-gray-500 text-base mb-4 block">
        {{ hasFiltersActive ? '没有找到符合条件的交易记录' : '还没有消费记录' }}
      </text>
      <button v-if="!hasFiltersActive" class="btn-primary" @click="addTransaction">
        添加第一笔消费记录
      </button>
    </view>

    <!-- 底部操作栏 -->
    <view
      class="bottom-actions fixed left-0 right-0 bg-white border-t border-gray-200 px-4 py-3 safe-area-inset-bottom z-10"
    >
      <view class="flex space-x-3">
        <button class="btn-secondary flex-1" @click="exportRecords">导出记录</button>
        <button class="btn-primary flex-1" @click="addTransaction">添加消费</button>
      </view>
    </view>

    <!-- 底部安全区域 -->
    <view class="h-20 pb-safe"></view>
  </view>
</template>

<script lang="ts" setup>
import { getTransactionsApiV1UserTransactionsListGetQueryOptions } from '@/service/app/yonghujiaoyiguanli.vuequery'
import { getCreditCardsApiV1UserCardsGetQueryOptions } from '@/service/app/xinyongkaguanli.vuequery'
import { useQuery } from '@tanstack/vue-query'

defineOptions({
  name: 'TransactionsPage',
})

// 定义交易记录类型
interface Transaction {
  id: string
  merchantName: string
  amount: number
  category: string
  transactionType: string
  transactionDate: string
  installment: number
  cardId: string
  description: string
}

// 响应式数据
const transactionList = ref<Transaction[]>([])
const cardList = ref<any[]>([])
const searchKeyword = ref('')
const activeFilters = ref<string[]>([])
const cardFilterIndex = ref(0)
const categoryFilterIndex = ref(0)
const dateFilter = ref('')
const loading = ref(false)
const summary = ref({
  totalAmount: 0,
  monthlyAmount: 0,
  totalTransactions: 0,
  monthlyTransactions: 0,
})

// 筛选选项
const quickFilters = [
  { key: 'this_month', label: '本月' },
  { key: 'last_month', label: '上月' },
  { key: 'large_amount', label: '大额消费' },
  { key: 'installment', label: '分期交易' },
]

const cardOptions = ref([{ value: 'all', label: '所有卡片' }])

const categoryOptions = [
  { value: 'all', label: '所有类别' },
  { value: '餐饮美食', label: '餐饮美食' },
  { value: '购物消费', label: '购物消费' },
  { value: '交通出行', label: '交通出行' },
  { value: '生活服务', label: '生活服务' },
  { value: '娱乐休闲', label: '娱乐休闲' },
  { value: '医疗健康', label: '医疗健康' },
  { value: '教育培训', label: '教育培训' },
  { value: '旅游度假', label: '旅游度假' },
  { value: '数码3C', label: '数码3C' },
  { value: '服装配饰', label: '服装配饰' },
]

// 计算属性
const filteredTransactions = computed(() => {
  let filtered: Transaction[] = transactionList.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(
      (t: Transaction) =>
        t.merchantName.toLowerCase().includes(keyword) ||
        t.description.toLowerCase().includes(keyword) ||
        t.category.toLowerCase().includes(keyword),
    )
  }

  // 卡片过滤
  if (cardFilterIndex.value > 0) {
    const selectedCard = cardOptions.value[cardFilterIndex.value]
    filtered = filtered.filter((t: Transaction) => t.cardId === selectedCard.value)
  }

  // 分类过滤
  if (categoryFilterIndex.value > 0) {
    const selectedCategory = categoryOptions[categoryFilterIndex.value]
    filtered = filtered.filter((t: Transaction) => t.category === selectedCategory.value)
  }

  // 日期过滤
  if (dateFilter.value) {
    const selectedDate = new Date(dateFilter.value)
    filtered = filtered.filter((t: Transaction) => {
      const transactionDate = new Date(t.transactionDate)
      return transactionDate.toDateString() === selectedDate.toDateString()
    })
  }

  // 快速过滤
  activeFilters.value.forEach((filter) => {
    switch (filter) {
      case 'this_month':
        const thisMonth = new Date()
        filtered = filtered.filter((t: Transaction) => {
          const transactionDate = new Date(t.transactionDate)
          return (
            transactionDate.getMonth() === thisMonth.getMonth() &&
            transactionDate.getFullYear() === thisMonth.getFullYear()
          )
        })
        break
      case 'last_month':
        const lastMonth = new Date()
        lastMonth.setMonth(lastMonth.getMonth() - 1)
        filtered = filtered.filter((t: Transaction) => {
          const transactionDate = new Date(t.transactionDate)
          return (
            transactionDate.getMonth() === lastMonth.getMonth() &&
            transactionDate.getFullYear() === lastMonth.getFullYear()
          )
        })
        break
      case 'large_amount':
        filtered = filtered.filter((t: Transaction) => t.amount >= 1000)
        break
      case 'installment':
        filtered = filtered.filter((t: Transaction) => t.installment > 0)
        break
    }
  })

  return filtered
})

const groupedTransactions = computed(() => {
  const groups: Record<string, Transaction[]> = {}
  filteredTransactions.value.forEach((transaction) => {
    const date = transaction.transactionDate.split(' ')[0] // 获取日期部分
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(transaction)
  })

  // 按日期倒序排列
  const sortedGroups: Record<string, Transaction[]> = {}
  Object.keys(groups)
    .sort((a, b) => new Date(b).getTime() - new Date(a).getTime())
    .forEach((date) => {
      sortedGroups[date] = groups[date].sort(
        (a, b) => new Date(b.transactionDate).getTime() - new Date(a.transactionDate).getTime(),
      )
    })

  return sortedGroups
})

const filteredTotal = computed(() => {
  return filteredTransactions.value.reduce((sum, t) => sum + t.amount, 0)
})

const hasFiltersActive = computed(() => {
  return (
    searchKeyword.value ||
    activeFilters.value.length > 0 ||
    cardFilterIndex.value > 0 ||
    categoryFilterIndex.value > 0 ||
    dateFilter.value
  )
})

// 页面生命周期
onLoad(() => {
  // Vue Query会自动加载数据
})

onPullDownRefresh(async () => {
  await refetchTransactions()
  uni.stopPullDownRefresh()
})

// 构建查询参数
const queryParams = computed(() => ({
  page: 1,
  page_size: 100,
  ...(searchKeyword.value && { keyword: searchKeyword.value }),
  ...(activeFilters.value.length > 0 && { filters: activeFilters.value.join(',') }),
  ...(cardFilterIndex.value > 0 && { card_id: cardOptions.value[cardFilterIndex.value].value }),
  ...(categoryFilterIndex.value > 0 && {
    category: categoryOptions[categoryFilterIndex.value].value,
  }),
  ...(dateFilter.value && { date: dateFilter.value }),
}))

// 使用Vue Query获取交易记录
const {
  data: transactionsData,
  isLoading: transactionsLoading,
  refetch: refetchTransactions,
} = useQuery(
  computed(() =>
    getTransactionsApiV1UserTransactionsListGetQueryOptions({
      params: queryParams.value,
    }),
  ),
)

// 使用Vue Query获取信用卡列表
const { data: creditCardsData, isLoading: cardsLoading } = useQuery({
  ...getCreditCardsApiV1UserCardsGetQueryOptions({
    params: {},
  }),
  enabled: true,
})

// 监听交易数据变化
watch(
  transactionsData,
  (newData) => {
    console.log('=== 交易数据变化 ===')
    console.log('原始数据:', newData)
    console.log('数据类型:', typeof newData)
    console.log('是否为数组:', Array.isArray(newData))

    if (newData) {
      try {
        // @ts-ignore - 忽略类型错误以便调试
        let data = newData

        // 检查是否有包装格式
        // @ts-ignore
        if (newData.success !== undefined && newData.data !== undefined) {
          console.log('检测到包装格式，提取data字段')
          // @ts-ignore
          data = newData.data
        }

        console.log('提取后的数据:', data)
        console.log('提取后数据类型:', typeof data)
        console.log('提取后是否为数组:', Array.isArray(data))

        let transactions: any[] = []

        if (Array.isArray(data)) {
          console.log('数据是直接数组格式，长度:', data.length)
          transactions = data
        } else if (data && typeof data === 'object') {
          console.log('数据是对象格式，查找items/list字段')
          // @ts-ignore
          const items = data.items || data.list || data.transactions || []
          console.log('找到的items:', items)
          console.log('items长度:', Array.isArray(items) ? items.length : 'not array')
          transactions = Array.isArray(items) ? items : []

          // 处理统计数据
          // @ts-ignore
          if (data.summary) {
            // @ts-ignore
            summary.value = data.summary
            console.log('更新统计数据:', summary.value)
          }
        }

        console.log('最终交易数据:', transactions)

        // 转换数据格式
        transactionList.value = transactions.map((item: any) => {
          const converted = {
            id: item.id || Math.random().toString(),
            merchantName: item.merchant_name || item.merchantName || '未知商户',
            amount: Number(item.amount) || 0,
            category: item.category || '其他',
            transactionType: item.transaction_type || item.transactionType || '消费',
            transactionDate:
              item.transaction_date || item.transactionDate || new Date().toISOString(),
            installment: Number(item.installment_months || item.installment) || 0,
            cardId: item.card_id || item.cardId || '',
            description: item.description || '',
          }
          console.log('转换项目:', item, '->', converted)
          return converted
        })

        console.log('最终处理后的交易列表:', transactionList.value)
        console.log('交易列表长度:', transactionList.value.length)
      } catch (error) {
        console.error('处理交易数据时出错:', error)
      }
    } else {
      console.log('没有接收到数据')
    }
  },
  { immediate: true },
)

// 监听信用卡数据变化
watch(
  creditCardsData,
  (newData) => {
    console.log('=== 信用卡数据变化 ===')
    console.log('原始数据:', newData)

    if (newData) {
      try {
        // @ts-ignore
        let data = newData

        // @ts-ignore
        if (newData.success !== undefined && newData.data !== undefined) {
          console.log('检测到包装格式，提取data字段')
          // @ts-ignore
          data = newData.data
        }

        console.log('提取后的数据:', data)

        let cards: any[] = []
        if (Array.isArray(data)) {
          console.log('数据是直接数组格式，长度:', data.length)
          cards = data
        } else if (data && typeof data === 'object') {
          console.log('数据是对象格式，查找items/list字段')
          // @ts-ignore
          cards = data.items || data.list || []
          console.log('找到的cards:', cards)
        }

        cardOptions.value = [
          { value: 'all', label: '所有卡片' },
          ...cards.map((card: any) => ({
            value: card.id,
            label: `${card.bank_name || card.bankName}${card.card_name || card.cardName}(${card.card_number_last4 || card.cardNumberLast4})`,
          })),
        ]

        console.log('处理后的卡片选项:', cardOptions.value)
      } catch (error) {
        console.error('处理信用卡数据时出错:', error)
      }
    } else {
      console.log('没有接收到信用卡数据')
    }
  },
  { immediate: true },
)

// Vue Query会自动监听queryKey的变化，无需手动监听

// 筛选处理
const toggleFilter = (filterKey: string) => {
  const index = activeFilters.value.indexOf(filterKey)
  if (index > -1) {
    activeFilters.value.splice(index, 1)
  } else {
    activeFilters.value.push(filterKey)
  }
}

const onCardFilterChange = (e: any) => {
  cardFilterIndex.value = e.detail.value
}

const onCategoryFilterChange = (e: any) => {
  categoryFilterIndex.value = e.detail.value
}

const onDateFilterChange = (e: any) => {
  dateFilter.value = e.detail.value
}

// 搜索处理
const handleSearch = () => {
  // 实时搜索，已通过计算属性实现
}

const clearSearch = () => {
  searchKeyword.value = ''
}

// 工具函数
const formatMoney = (amount: number) => {
  if (!amount) return '0.00'
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatGroupDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  if (date.toDateString() === today.toDateString()) {
    return '今天'
  } else if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  } else {
    return `${date.getMonth() + 1}月${date.getDate()}日`
  }
}

const formatTime = (dateTimeStr: string) => {
  const date = new Date(dateTimeStr)
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const getCategoryIcon = (category: string) => {
  const icons = {
    餐饮美食: '🍽️',
    购物消费: '🛍️',
    交通出行: '🚗',
    生活服务: '🏠',
    娱乐休闲: '🎮',
    医疗健康: '💊',
    教育培训: '📚',
    旅游度假: '✈️',
    数码3C: '📱',
    服装配饰: '👕',
  }
  return icons[category] || '💳'
}

const getCategoryColor = (category: string) => {
  const colors = {
    餐饮美食: '#FF6B6B',
    购物消费: '#4ECDC4',
    交通出行: '#45B7D1',
    生活服务: '#96CEB4',
    娱乐休闲: '#FECA57',
    医疗健康: '#FF9FF3',
    教育培训: '#54A0FF',
    旅游度假: '#5F27CD',
    数码3C: '#00D2D3',
    服装配饰: '#FF9F43',
  }
  return colors[category] || '#A4B0BE'
}

const getAmountClass = (type: string) => {
  return type === '退款' ? 'text-green-600' : 'text-red-600'
}

// 导航函数
const goToTransactionDetail = (transactionId: string) => {
  uni.navigateTo({ url: `/pages/transactions/detail?id=${transactionId}` })
}

const addTransaction = () => {
  uni.navigateTo({ url: '/pages/transactions/add' })
}

const exportRecords = () => {
  uni.showToast({
    title: '功能开发中',
    icon: 'none',
  })
}
</script>

<style lang="scss">
.transactions-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.filter-tag {
  cursor: pointer;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.95);
  }
}

.filter-select {
  cursor: pointer;
  transition: all 0.2s ease;

  &:active {
    background: #e5e7eb;
  }
}

.transaction-item {
  cursor: pointer;

  &:active {
    background: #f9fafb;
  }
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.98);
  }
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 1px solid #667eea;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.98);
    background: #f8f9ff;
  }
}

.bottom-actions {
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  /* 使用 UniApp 提供的 CSS 变量来正确定位底部操作栏 */
  bottom: var(--window-bottom);
}

.pb-safe {
  padding-bottom: env(safe-area-inset-bottom);
  /* 为底部安全区域添加额外的高度，确保内容不被遮挡 */
  height: calc(80px + var(--window-bottom));
}
</style>
