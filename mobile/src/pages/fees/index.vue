<!-- 费用管理页面 -->
<route lang="json5">
{
  style: {
    navigationBarTitleText: '费用管理',
    enablePullDownRefresh: true,
  },
}
</route>

<template>
  <view class="fees-page">
    <!-- 状态栏占位 -->
    <view
      :style="{ height: safeAreaInsets?.top + 'px' }"
      class="bg-gradient-to-r from-purple-500 to-pink-500"
    ></view>
    <!-- 未登录状态 -->
    <view
      v-if="!userStore.isLoggedIn"
      class="login-prompt bg-gradient-to-r from-purple-500 to-pink-500 text-white p-8 text-center"
    >
      <view
        class="w-20 h-20 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-4"
      >
        <text class="text-3xl">💰</text>
      </view>
      <text class="text-lg font-bold mb-2 block">费用管理需要登录</text>
      <text class="text-sm opacity-80 mb-6 block">登录后查看您的年费和费用统计</text>
      <view class="bg-white bg-opacity-20 px-6 py-3 rounded-full inline-block" @click="goToLogin">
        <text class="text-white font-medium">立即登录</text>
      </view>
    </view>

    <!-- 已登录状态 -->
    <template v-else>
      <!-- 加载状态 -->
      <view
        v-if="loading"
        class="loading-state bg-gradient-to-r from-purple-500 to-pink-500 text-white p-4"
      >
        <view class="text-center mb-4">
          <text class="text-lg font-semibold opacity-90">加载中...</text>
        </view>
        <view class="flex justify-around mb-4">
          <view class="text-center">
            <view class="w-16 h-8 bg-white bg-opacity-20 rounded mb-2"></view>
            <text class="text-sm opacity-80">年费总额</text>
          </view>
          <view class="text-center">
            <view class="w-16 h-8 bg-white bg-opacity-20 rounded mb-2"></view>
            <text class="text-sm opacity-80">利息支出</text>
          </view>
          <view class="text-center">
            <view class="w-16 h-8 bg-white bg-opacity-20 rounded mb-2"></view>
            <text class="text-sm opacity-80">其他费用</text>
          </view>
        </view>
      </view>

      <!-- 错误状态 -->
      <view
        v-else-if="isStatsError || isCardsError"
        class="error-state bg-gradient-to-r from-red-500 to-pink-500 text-white p-4 text-center"
      >
        <text class="text-lg font-semibold mb-2 block">加载失败</text>
        <text class="text-sm opacity-80 mb-4 block">请检查网络连接后重试</text>
        <view
          class="bg-white bg-opacity-20 px-6 py-3 rounded-full inline-block"
          @click="handleRetry"
        >
          <text class="text-white font-medium">重新加载</text>
        </view>
      </view>

      <!-- 顶部统计 -->
      <view v-else class="stats-header bg-gradient-to-r from-purple-500 to-pink-500 text-white p-4">
        <view class="text-center mb-4">
          <text class="text-lg font-semibold opacity-90">本年费用支出</text>
        </view>
        <view class="flex justify-around mb-4">
          <view class="text-center">
            <text class="text-2xl font-bold block">¥{{ summary.totalAnnualFees }}</text>
            <text class="text-sm opacity-80">年费总额</text>
          </view>
          <view class="text-center">
            <text class="text-2xl font-bold block">¥{{ summary.totalInterest }}</text>
            <text class="text-sm opacity-80">利息支出</text>
          </view>
          <view class="text-center">
            <text class="text-2xl font-bold block">¥{{ summary.totalOtherFees }}</text>
            <text class="text-sm opacity-80">其他费用</text>
          </view>
        </view>
      </view>
    </template>

    <!-- 功能菜单 -->
    <view
      v-if="userStore.isLoggedIn && !loading"
      class="function-menu bg-white mx-4 -mt-6 rounded-xl p-4 shadow-lg mb-4"
    >
      <view class="flex justify-around">
        <view class="text-center" @click="goToAnnualFeeCalc">
          <view
            class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2"
          >
            <text class="text-blue-600 text-xl">💰</text>
          </view>
          <text class="text-xs text-gray-600">年费计算</text>
        </view>
        <view class="text-center" @click="goToInterestCalc">
          <view
            class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2"
          >
            <text class="text-green-600 text-xl">📊</text>
          </view>
          <text class="text-xs text-gray-600">利息计算</text>
        </view>
        <view class="text-center" @click="goToWaiverProgress">
          <view
            class="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-2"
          >
            <text class="text-orange-600 text-xl">🎯</text>
          </view>
          <text class="text-xs text-gray-600">减免进度</text>
        </view>
        <view class="text-center" @click="goToFeeStatistics">
          <view
            class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2"
          >
            <text class="text-purple-600 text-xl">📈</text>
          </view>
          <text class="text-xs text-gray-600">费用统计</text>
        </view>
      </view>
    </view>

    <!-- 筛选栏 -->
    <view
      v-if="userStore.isLoggedIn && !loading && !isStatsError && !isCardsError"
      class="filter-section bg-white px-4 py-3 shadow-sm mb-4"
    >
      <view class="flex space-x-2">
        <view
          v-for="filter in feeTypeFilters"
          :key="filter.key"
          class="filter-tag px-3 py-1 rounded-full text-sm transition-all"
          :class="
            activeFeeType === filter.key ? 'bg-purple-500 text-white' : 'bg-gray-100 text-gray-600'
          "
          @click="setFeeTypeFilter(filter.key)"
        >
          {{ filter.label }}
        </view>
      </view>
    </view>

    <!-- 费用列表 -->
    <view
      v-if="userStore.isLoggedIn && !loading && !isStatsError && !isCardsError"
      class="fee-list px-4"
    >
      <!-- 年费卡片 -->
      <view v-if="activeFeeType === 'all' || activeFeeType === 'annual'" class="fee-section mb-6">
        <view class="section-header flex items-center justify-between mb-3">
          <text class="text-lg font-semibold text-gray-800">年费管理</text>
          <text class="text-sm text-purple-600" @click="goToAnnualFeeList">查看全部</text>
        </view>

        <view class="space-y-3">
          <view
            v-for="fee in annualFeeList"
            :key="fee.id"
            class="fee-card bg-white rounded-xl p-4 shadow-sm"
            @click="goToAnnualFeeDetail(fee.id)"
          >
            <!-- 卡片信息 -->
            <view class="flex items-center justify-between mb-3">
              <view class="flex items-center">
                <view
                  class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3"
                  :style="{ backgroundColor: fee.bankColor }"
                >
                  {{ fee.bankCode }}
                </view>
                <view>
                  <text class="font-semibold text-gray-800">
                    {{ fee.bankName }}{{ fee.cardName }}
                  </text>
                  <text class="text-xs text-gray-500 block">**** {{ fee.cardNumberLast4 }}</text>
                </view>
              </view>
              <view class="text-right">
                <text class="text-lg font-bold text-purple-600">¥{{ fee.annualFee }}</text>
                <text class="text-xs text-gray-500 block">年费</text>
              </view>
            </view>

            <!-- 年费状态 -->
            <view class="flex items-center justify-between py-2 bg-gray-50 rounded-lg px-3">
              <view class="flex items-center">
                <text class="text-sm text-gray-600">状态：</text>
                <text class="text-sm ml-1" :class="getFeeStatusClass(fee.status)">
                  {{ getFeeStatusText(fee.status) }}
                </text>
              </view>
              <view v-if="fee.dueDate" class="text-right">
                <text class="text-xs text-gray-500">{{ getDueDateText(fee.dueDate) }}</text>
              </view>
            </view>

            <!-- 减免进度 -->
            <view v-if="fee.feeType !== 'rigid'" class="mt-3">
              <view class="flex items-center justify-between mb-2">
                <text class="text-sm text-gray-600">{{ fee.waiverCondition }}</text>
                <text class="text-sm font-semibold text-blue-600">{{ fee.waiverProgress }}%</text>
              </view>
              <view class="bg-gray-200 rounded-full h-2">
                <view
                  class="bg-gradient-to-r from-blue-400 to-blue-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: fee.waiverProgress + '%' }"
                ></view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 利息费用 -->
      <view v-if="activeFeeType === 'all' || activeFeeType === 'interest'" class="fee-section mb-6">
        <view class="section-header flex items-center justify-between mb-3">
          <text class="text-lg font-semibold text-gray-800">利息支出</text>
          <text class="text-sm text-purple-600" @click="goToInterestList">查看全部</text>
        </view>

        <view class="bg-white rounded-xl p-4 shadow-sm">
          <view class="grid grid-cols-2 gap-4">
            <view class="interest-item text-center p-3 bg-red-50 rounded-lg">
              <text class="text-2xl font-bold text-red-600 block">
                ¥{{ summary.monthlyInterest }}
              </text>
              <text class="text-sm text-gray-600">本月利息</text>
            </view>
            <view class="interest-item text-center p-3 bg-orange-50 rounded-lg">
              <text class="text-2xl font-bold text-orange-600 block">
                ¥{{ summary.overdueInterest }}
              </text>
              <text class="text-sm text-gray-600">逾期利息</text>
            </view>
          </view>

          <view class="mt-4 pt-4 border-t border-gray-100">
            <view class="flex items-center justify-between text-sm">
              <text class="text-gray-600">预计下月利息</text>
              <text class="font-semibold text-red-600">¥{{ summary.nextMonthInterest }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 其他费用 -->
      <view v-if="activeFeeType === 'all' || activeFeeType === 'other'" class="fee-section mb-6">
        <view class="section-header flex items-center justify-between mb-3">
          <text class="text-lg font-semibold text-gray-800">其他费用</text>
          <text class="text-sm text-purple-600" @click="goToOtherFeesList">查看全部</text>
        </view>

        <view class="space-y-3">
          <view
            v-for="fee in otherFeesList"
            :key="fee.id"
            class="fee-card bg-white rounded-xl p-4 shadow-sm"
          >
            <view class="flex items-center justify-between">
              <view class="flex items-center">
                <view
                  class="w-10 h-10 rounded-full flex items-center justify-center mr-3"
                  :style="{ backgroundColor: getFeeTypeColor(fee.feeType) }"
                >
                  <text class="text-white text-sm">{{ getFeeTypeIcon(fee.feeType) }}</text>
                </view>
                <view>
                  <text class="font-medium text-gray-800">{{ fee.feeName }}</text>
                  <text class="text-xs text-gray-500 block">{{ fee.description }}</text>
                </view>
              </view>
              <view class="text-right">
                <text class="text-lg font-bold text-red-600">¥{{ fee.amount }}</text>
                <text class="text-xs text-gray-500 block">{{ formatDate(fee.feeDate) }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view
      v-if="userStore.isLoggedIn && !loading && !isStatsError && !isCardsError && isEmpty"
      class="empty-state text-center py-16"
    >
      <text class="text-4xl mb-4 block">💸</text>
      <text class="text-gray-500 text-base mb-4 block">暂无费用记录</text>
      <text class="text-gray-400 text-sm">优秀的理财从控制费用开始</text>
    </view>

    <!-- 底部安全区域 -->
    <view class="h-20"></view>
  </view>
</template>

<script lang="ts" setup>
import { useQuery } from '@tanstack/vue-query'
import { useUserStore } from '@/store/user'
import {
  getUserStatisticsApiV1UserProfileStatisticsGetQueryOptions,
  getCreditCardsApiV1UserCardsGetQueryOptions,
} from '@/service/app/v1Yonghugongneng.vuequery'
import type * as API from '@/service/app/types'

defineOptions({
  name: 'FeesPage',
})

// 获取屏幕边界到安全区域距离
let safeAreaInsets: any = null
try {
  const systemInfo = uni.getSystemInfoSync()
  safeAreaInsets = systemInfo.safeAreaInsets
} catch (e) {
  console.warn('获取安全区域失败', e)
}

// 获取用户状态
const userStore = useUserStore()

// 使用Vue Query获取用户统计数据
const {
  data: userStatsResponse,
  isLoading: isStatsLoading,
  isError: isStatsError,
  refetch: refetchStats,
} = useQuery({
  ...getUserStatisticsApiV1UserProfileStatisticsGetQueryOptions({
    options: undefined,
  }),
  enabled: computed(() => userStore.isLoggedIn),
})

// 使用Vue Query获取信用卡列表（包含年费信息）
const {
  data: cardsResponse,
  isLoading: isCardsLoading,
  isError: isCardsError,
  refetch: refetchCards,
} = useQuery({
  ...getCreditCardsApiV1UserCardsGetQueryOptions({
    params: {
      page: 1,
      page_size: 100, // 获取所有卡片
    },
    options: undefined,
  }),
  enabled: computed(() => userStore.isLoggedIn),
})

// 智能处理API响应数据
const userStats = computed(() => {
  if (!userStatsResponse.value) return null

  // 智能检测响应格式
  const response = userStatsResponse.value as any
  if (response.data && typeof response.data === 'object') {
    return response.data as API.UserStatisticsResponse
  }
  return response as API.UserStatisticsResponse
})

const creditCards = computed(() => {
  if (!cardsResponse.value) return []

  // 智能检测响应格式
  const response = cardsResponse.value as any
  let cardsData = []

  if (response.data && Array.isArray(response.data)) {
    cardsData = response.data
  } else if (Array.isArray(response)) {
    cardsData = response
  }

  return cardsData
})

// 响应式数据
const activeFeeType = ref('all')
const loading = computed(() => isStatsLoading.value || isCardsLoading.value)

// 计算年费列表
const annualFeeList = computed(() => {
  return creditCards.value.map((card: any) => {
    // 获取银行信息
    const bankName = card.bank?.bank_name || card.bank_name || '未知银行'
    const bankCode = bankName.substring(0, 2)

    // 计算年费状态
    let feeStatus = 'pending'
    let waiverProgress = 0
    let waiverCondition = '无减免条件'

    if (card.fee_waivable) {
      // 这里可以根据实际业务逻辑计算减免进度
      waiverProgress = Math.floor(Math.random() * 100) // 临时随机值
      waiverCondition = '年消费满10万元减免'

      if (waiverProgress >= 100) {
        feeStatus = 'waived'
      }
    }

    return {
      id: card.id,
      bankName,
      bankCode,
      bankColor: card.bank_color || '#6366f1',
      cardName: card.card_name,
      cardNumberLast4: card.card_number?.slice(-4) || '****',
      annualFee: card.annual_fee || 0,
      status: feeStatus,
      feeType: card.fee_waivable ? 'waivable' : 'rigid',
      waiverCondition,
      waiverProgress,
      dueDate: card.fee_due_month
        ? `2024-${card.fee_due_month.toString().padStart(2, '0')}-01`
        : null,
    }
  })
})

// 计算费用摘要
const summary = computed(() => {
  if (!userStats.value) {
    return {
      totalAnnualFees: 0,
      totalInterest: 0,
      totalOtherFees: 0,
      monthlyInterest: 0,
      overdueInterest: 0,
      nextMonthInterest: 0,
    }
  }

  const stats = userStats.value
  return {
    totalAnnualFees: stats.total_annual_fees || 0,
    totalInterest: 0, // 暂时没有利息数据
    totalOtherFees: 0, // 暂时没有其他费用数据
    monthlyInterest: 0,
    overdueInterest: 0,
    nextMonthInterest: 0,
  }
})

// 其他费用列表（暂时为空，等待后续API）
const otherFeesList = ref<any[]>([])

// 筛选选项
const feeTypeFilters = [
  { key: 'all', label: '全部' },
  { key: 'annual', label: '年费' },
  { key: 'interest', label: '利息' },
  { key: 'other', label: '其他' },
]

// 计算属性
const isEmpty = computed(() => {
  return (
    annualFeeList.value.length === 0 &&
    otherFeesList.value.length === 0 &&
    summary.value.totalInterest === 0
  )
})

// 页面生命周期
onLoad(async () => {
  // Vue Query 会自动加载数据
})

onPullDownRefresh(async () => {
  await Promise.all([refetchStats(), refetchCards()])
  uni.stopPullDownRefresh()
})

// 监听登录状态变化
watch(
  () => userStore.isLoggedIn,
  (isLoggedIn) => {
    if (isLoggedIn) {
      refetchStats()
      refetchCards()
    }
  },
)

// 筛选处理
const setFeeTypeFilter = (feeType: string) => {
  activeFeeType.value = feeType
}

// 工具函数
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

const getFeeStatusClass = (status: string) => {
  const classes = {
    pending: 'text-orange-600',
    waived: 'text-green-600',
    paid: 'text-blue-600',
    overdue: 'text-red-600',
  }
  return classes[status] || 'text-gray-600'
}

const getFeeStatusText = (status: string) => {
  const texts = {
    pending: '待缴费',
    waived: '已减免',
    paid: '已缴费',
    overdue: '已逾期',
  }
  return texts[status] || '未知'
}

const getDueDateText = (dueDateStr: string) => {
  const dueDate = new Date(dueDateStr)
  const today = new Date()
  const timeDiff = dueDate.getTime() - today.getTime()
  const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24))

  if (daysDiff < 0) {
    return `已逾期 ${Math.abs(daysDiff)} 天`
  } else if (daysDiff === 0) {
    return '今日到期'
  } else if (daysDiff <= 7) {
    return `${daysDiff} 天后到期`
  } else {
    return `${dueDate.getMonth() + 1}月${dueDate.getDate()}日到期`
  }
}

const getFeeTypeColor = (feeType: string) => {
  const colors = {
    withdrawal: '#FF6B6B',
    cash_advance: '#4ECDC4',
    foreign_transaction: '#45B7D1',
    late_payment: '#FFA726',
    overlimit: '#AB47BC',
    installment: '#66BB6A',
  }
  return colors[feeType] || '#78909C'
}

const getFeeTypeIcon = (feeType: string) => {
  const icons = {
    withdrawal: '💸',
    cash_advance: '💰',
    foreign_transaction: '🌍',
    late_payment: '⏰',
    overlimit: '⚠️',
    installment: '📅',
  }
  return icons[feeType] || '💳'
}

// 导航函数
const goToLogin = () => {
  uni.navigateTo({ url: '/pages/auth/login' })
}

const handleRetry = async () => {
  await Promise.all([refetchStats(), refetchCards()])
}

const goToAnnualFeeDetail = (feeId: string) => {
  uni.navigateTo({ url: `/pages/fees/annual-detail?id=${feeId}` })
}

const goToAnnualFeeList = () => {
  uni.navigateTo({ url: '/pages/fees/annual-list' })
}

const goToInterestList = () => {
  uni.navigateTo({ url: '/pages/fees/interest-list' })
}

const goToOtherFeesList = () => {
  uni.navigateTo({ url: '/pages/fees/other-list' })
}

const goToAnnualFeeCalc = () => {
  uni.navigateTo({ url: '/pages/tools/annual-fee-calc' })
}

const goToInterestCalc = () => {
  uni.navigateTo({ url: '/pages/tools/interest-calc' })
}

const goToWaiverProgress = () => {
  uni.navigateTo({ url: '/pages/fees/waiver-progress' })
}

const goToFeeStatistics = () => {
  uni.navigateTo({ url: '/pages/fees/statistics' })
}
</script>

<style lang="scss">
.fees-page {
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

.fee-card {
  transition: transform 0.2s ease;

  &:active {
    transform: scale(0.98);
  }
}

.grid {
  display: flex;
  flex-wrap: wrap;
}

.grid-cols-2 {
  & > * {
    flex: 0 0 calc(50% - 8px);
  }
}

.gap-4 {
  gap: 16px;
}

.interest-item {
  cursor: pointer;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.98);
  }
}
</style>
