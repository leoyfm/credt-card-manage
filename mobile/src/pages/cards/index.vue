<!-- 信用卡列表页面 -->
<route lang="json5">
{
  style: {
    navigationBarTitleText: '我的卡片',
    enablePullDownRefresh: true,
  },
}
</route>

<template>
  <view class="cards-page">
    <!-- 未登录状态 -->
    <view v-if="!userStore.isLoggedIn" class="login-prompt text-center py-16">
      <text class="text-4xl mb-4 block">🔐</text>
      <text class="text-gray-500 text-base mb-4 block">请先登录查看您的信用卡</text>
      <button class="btn-primary" @click="goToLogin">立即登录</button>
    </view>

    <!-- 已登录状态 -->
    <template v-else>
      <!-- 搜索栏 -->
      <view class="search-bar bg-white px-4 py-3 sticky top-0 z-10">
        <view class="flex items-center bg-gray-100 rounded-full px-4 py-2">
          <text class="iconfont icon-search text-gray-400 mr-2">🔍</text>
          <input
            v-model="searchKeyword"
            placeholder="搜索银行或卡片名称"
            class="flex-1 text-sm"
            @input="handleSearch"
          />
          <text v-if="searchKeyword" class="text-gray-400 ml-2" @click="clearSearch">✕</text>
        </view>
      </view>

      <!-- 筛选栏 -->
      <view class="filter-bar bg-white px-4 py-3 border-b border-gray-100">
        <view class="flex space-x-3">
          <view
            v-for="filter in filterOptions"
            :key="filter.key"
            class="filter-item px-3 py-1 rounded-full text-sm transition-all"
            :class="
              activeFilter === filter.key ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600'
            "
            @click="handleFilter(filter.key)"
          >
            {{ filter.label }}
          </view>
        </view>
      </view>

      <!-- 统计信息 -->
      <view class="stats-bar bg-blue-50 px-4 py-3">
        <view class="flex justify-between text-sm">
          <text class="text-gray-600">共 {{ filteredCards.length }} 张卡片</text>
          <text class="text-blue-600">总额度 ¥{{ formatMoney(totalCreditLimit) }}</text>
        </view>
      </view>

      <!-- 加载状态 -->
      <view v-if="isLoading" class="loading-container text-center py-16">
        <wd-loading />
        <text class="text-gray-500 text-sm mt-4 block">加载信用卡列表中...</text>
      </view>

      <!-- 错误状态 -->
      <view v-else-if="isError" class="error-container text-center py-16">
        <text class="text-4xl mb-4 block">❌</text>
        <text class="text-red-500 text-base mb-4 block">加载失败，请重试</text>
        <button class="btn-primary" @click="refetchCards">重新加载</button>
      </view>

      <!-- 卡片列表 -->
      <view v-else class="card-list px-4 py-2">
        <CreditCard
          v-for="card in filteredCards"
          :key="card.id"
          :card="card"
          :is-best-card="false"
          @card-click="goToCardDetail"
          @card-updated="refetchCards"
        />
      </view>

      <!-- 空状态 -->
      <view
        v-if="!isLoading && !isError && filteredCards.length === 0"
        class="empty-state text-center py-16"
      >
        <text class="text-4xl mb-4 block">💳</text>
        <text class="text-gray-500 text-base mb-4 block">
          {{
            searchKeyword || activeFilter !== 'all' ? '没有找到符合条件的卡片' : '还没有添加信用卡'
          }}
        </text>
        <button
          v-if="!searchKeyword && activeFilter === 'all'"
          class="btn-primary"
          @click="addCard"
        >
          添加第一张信用卡
        </button>
      </view>

      <!-- 底部操作栏 -->
      <view
        class="bottom-actions fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-3 safe-area-inset-bottom"
      >
        <view class="flex space-x-3">
          <button class="btn-secondary flex-1" @click="importCards">批量导入</button>
          <button class="btn-primary flex-1" @click="addCard">添加卡片</button>
        </view>
      </view>

      <!-- 底部安全区域 -->
      <view class="h-20"></view>
    </template>

    <!-- Toast 组件 -->
    <wd-toast />
  </view>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useToast } from 'wot-design-uni'
import { useUserStore } from '@/store/user'
import { getCreditCardsApiV1UserCardsGetQueryOptions } from '@/service/app/v1Yonghugongneng.vuequery'
import CreditCard from '@/components/CreditCard.vue'
import type { CreditCard as CreditCardType } from '@/types/card'
import type * as API from '@/service/app/types'

defineOptions({
  name: 'CardsPage',
})

const toast = useToast()
const userStore = useUserStore()

// 响应式数据
const searchKeyword = ref('')
const activeFilter = ref('all')

// 使用Vue Query获取信用卡列表
const {
  data: creditCardsResponse,
  isLoading,
  isError,
  refetch: refetchCards,
} = useQuery({
  ...getCreditCardsApiV1UserCardsGetQueryOptions({
    params: {
      // 只传递有值的参数，避免空参数导致API报错
      ...(searchKeyword.value && { keyword: searchKeyword.value }),
      ...(activeFilter.value !== 'all' && { status: activeFilter.value }),
    },
  }),
  enabled: userStore.isLoggedIn, // 只有在已登录时才启用查询
})

// mutation 已移至 CreditCard 组件中

// 筛选选项
const filterOptions = [
  { key: 'all', label: '全部' },
  { key: 'active', label: '正常' },
  { key: 'inactive', label: '停用' },
  { key: 'high_limit', label: '高额度' },
  { key: 'fee_due', label: '年费待缴' },
]

// 处理API响应数据
const creditCards = computed(() => {
  if (!creditCardsResponse.value) {
    return []
  }

  // 智能检测API响应格式
  let cardsData = null
  if (creditCardsResponse.value.data && Array.isArray(creditCardsResponse.value.data)) {
    cardsData = creditCardsResponse.value.data
  } else if (Array.isArray(creditCardsResponse.value)) {
    cardsData = creditCardsResponse.value
  }

  if (!cardsData) {
    console.log('未找到有效的信用卡数据')
    return []
  }

  // 转换API数据为组件需要的格式
  return cardsData.map((apiCard: any) => {
    // 计算可用额度
    const creditLimit = Number(apiCard.credit_limit) || 0
    const usedAmount = Number(apiCard.used_limit) || 0
    const availableAmount = creditLimit - usedAmount

    // 处理银行信息
    const bankName = apiCard.bank?.bank_name || apiCard.bank_name || '未知银行'
    const bankCode = bankName.substring(0, 2)

    // 处理有效期
    let expiryDate = ''
    if (apiCard.expiry_month && apiCard.expiry_year) {
      const month = String(apiCard.expiry_month).padStart(2, '0')
      const year = String(apiCard.expiry_year).slice(-2)
      expiryDate = `${month}/${year}`
    }

    // 计算下次账单日期
    const nextBillingDate = calculateNextBillingDate(apiCard.billing_date)

    // 年费状态判断
    const annualFeeStatus = determineAnnualFeeStatus(apiCard)

    // 年费减免进度
    const waiverProgress = calculateWaiverProgress(apiCard)

    return {
      id: apiCard.id,
      bankName,
      bankCode,
      bankColor: apiCard.bank_color || '#3B82F6',
      cardName: apiCard.card_name || '信用卡',
      cardType: apiCard.card_type || 'credit',
      cardLevel: getCardLevel(apiCard.card_type),
      cardNumberLast4: apiCard.card_number || '0000',
      expiryDate,
      creditLimit,
      usedAmount,
      availableAmount,
      billingDay: apiCard.billing_date || 1,
      dueDay: apiCard.due_date || 1,
      dueDate: apiCard.due_date || 1, // CreditCard 组件需要的字段
      nextBillingDate,
      annualFee: Number(apiCard.annual_fee) || 0,
      annualFeeStatus,
      feeType: apiCard.fee_waivable ? 'waivable' : 'rigid', // 修正为 CreditCard 组件期望的值
      waiverCondition: getWaiverCondition(apiCard),
      waiverProgress,
      isActive: apiCard.status === 'active',
    }
  })
})

// 计算属性
const filteredCards = computed(() => {
  let filtered = creditCards.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(
      (card) =>
        card.bankName.toLowerCase().includes(keyword) ||
        card.cardName.toLowerCase().includes(keyword) ||
        card.cardNumberLast4.includes(keyword),
    )
  }

  // 状态过滤
  switch (activeFilter.value) {
    case 'active':
      filtered = filtered.filter((card) => card.isActive)
      break
    case 'inactive':
      filtered = filtered.filter((card) => !card.isActive)
      break
    case 'high_limit':
      filtered = filtered.filter((card) => card.creditLimit >= 100000)
      break
    case 'fee_due':
      filtered = filtered.filter((card) => card.annualFeeStatus === 'pending')
      break
  }

  return filtered
})

const totalCreditLimit = computed(() => {
  return filteredCards.value.reduce((sum, card) => sum + card.creditLimit, 0)
})

// 页面生命周期
onMounted(() => {
  // 如果未登录，跳转到登录页
  if (!userStore.isLoggedIn) {
    uni.navigateTo({
      url: '/pages/login/index',
    })
  }
})

// 下拉刷新
onPullDownRefresh(async () => {
  await refetchCards()
  uni.stopPullDownRefresh()
})

// 搜索功能
const handleSearch = (event: any) => {
  const keyword = event.detail?.value || event.target?.value || ''
  console.log('搜索关键词:', keyword)
  searchKeyword.value = keyword
}

const clearSearch = () => {
  searchKeyword.value = ''
}

// 筛选功能
const handleFilter = (filter: string) => {
  console.log('筛选条件:', filter)
  activeFilter.value = filter
}

// 监听搜索和筛选参数变化，重新查询
watch(
  [searchKeyword, activeFilter],
  () => {
    if (userStore.isLoggedIn) {
      refetchCards()
    }
  },
  { deep: true },
)

// 工具函数
const formatMoney = (amount: number) => {
  if (!amount) return '0'
  if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return amount.toLocaleString()
}

const formatDate = (dateStr: string, format: string = 'YYYY-MM-DD') => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  if (format === 'MM/YY') {
    return `${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getFullYear()).slice(2)}`
  } else if (format === 'MM-DD') {
    return `${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  }
  return dateStr
}

// 样式类函数已移至 CreditCard 组件中

// 业务逻辑函数
const calculateNextBillingDate = (billingDay: number): string => {
  const now = new Date()
  const currentMonth = now.getMonth()
  const currentYear = now.getFullYear()

  let nextBillingDate = new Date(currentYear, currentMonth, billingDay)

  // 如果本月账单日已过，计算下月
  if (nextBillingDate <= now) {
    nextBillingDate = new Date(currentYear, currentMonth + 1, billingDay)
  }

  return nextBillingDate.toISOString().split('T')[0]
}

const determineAnnualFeeStatus = (apiCard: any): string => {
  // 根据API数据判断年费状态
  if (apiCard.fee_waivable && apiCard.annual_fee > 0) {
    // 可减免的年费，需要检查减免条件
    return 'pending'
  } else if (apiCard.annual_fee === 0) {
    return 'waived'
  } else {
    return 'paid'
  }
}

const calculateWaiverProgress = (apiCard: any): number => {
  // 根据备注信息计算减免进度
  if (!apiCard.notes || !apiCard.fee_waivable) {
    return 0
  }

  // 这里可以根据实际的消费记录计算进度
  // 暂时返回随机进度作为示例
  return Math.floor(Math.random() * 100)
}

const getCardLevel = (cardType: string): string => {
  const levels = {
    visa: 'Visa',
    mastercard: 'MasterCard',
    unionpay: '银联',
    americanexpress: 'AE',
  }
  return levels[cardType] || '普通卡'
}

const getWaiverCondition = (apiCard: any): string => {
  if (!apiCard.fee_waivable) {
    return '刚性年费'
  }

  // 从备注中解析减免条件
  if (apiCard.notes && apiCard.notes.includes('刷卡')) {
    if (apiCard.notes.includes('次')) {
      return '刷卡次数达标'
    } else if (apiCard.notes.includes('元')) {
      return '刷卡金额达标'
    }
  }

  return '条件减免'
}

// 导航函数
const goToLogin = () => {
  uni.navigateTo({ url: '/pages/login/index' })
}

const goToCardDetail = (cardId: string) => {
  uni.navigateTo({ url: `/pages/cards/detail?id=${cardId}` })
}

const addCard = () => {
  uni.navigateTo({ url: '/pages/cards/add' })
}

const importCards = () => {
  uni.showToast({
    title: '功能开发中',
    icon: 'none',
  })
}

// 编辑、删除、状态切换功能已移至 CreditCard 组件中
</script>

<style lang="scss">
.cards-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.filter-item {
  cursor: pointer;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.95);
  }
}

// .card-item 样式已移至 CreditCard 组件中

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

.empty-state {
  margin-top: 10vh;
}
</style>
