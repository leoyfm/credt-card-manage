<!-- 信用卡管理首页 -->
<!-- <route lang="json5" type="home">
{
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '信用卡管家',
  },
}
</route> -->

<template>
  <view class="index-container safe-area bg-gray-50 min-h-screen">
    <!-- 顶部状态栏区域 -->
    <HeaderSection />

    <!-- 今日推荐 -->
    <view class="p-4 pt-2">
      <TodayRecommendation :cards="creditCards" @recommendationClick="handleRecommendationClick" />
    </view>

    <!-- 年费概览 -->
    <view class="p-4 pt-2">
      <FeeOverview
        :cards="creditCards"
        :showDetail="true"
        :showActions="true"
        @viewDetail="handleViewFeeDetail"
        @manageWaiver="handleManageWaiver"
      />
    </view>

    <!-- 添加信用卡按钮 -->
    <view class="px-4 pb-4">
      <view
        class="add-card-btn bg-black text-white rounded-xl p-4 text-center"
        @click="handleAddCard"
      >
        <text class="text-lg font-semibold">+ 添加信用卡</text>
      </view>
    </view>

    <!-- 信用卡列表 -->
    <view class="px-4 pb-32">
      <view class="flex items-center justify-between mb-4">
        <text class="text-lg font-semibold text-gray-800">我的信用卡</text>
        <text
          v-if="userStore.isLoggedIn && creditCards.length > 0"
          class="text-sm text-blue-600"
          @click="handleViewAll"
        >
          查看全部
        </text>
      </view>

      <!-- 未登录状态 -->
      <view v-if="!userStore.isLoggedIn" class="text-center py-8">
        <text class="text-gray-500 text-sm">请先登录查看您的信用卡</text>
        <view class="mt-4">
          <view class="bg-blue-600 text-white rounded-lg px-6 py-3 inline-block" @click="goToLogin">
            <text class="text-sm">立即登录</text>
          </view>
        </view>
      </view>

      <!-- 已登录 - 加载状态 -->
      <view v-else-if="userStore.isLoggedIn && isCardsLoading" class="space-y-3">
        <view v-for="i in 3" :key="i" class="bg-white rounded-xl p-4 animate-pulse">
          <view class="flex items-center justify-between mb-3">
            <view class="w-16 h-4 bg-gray-200 rounded"></view>
            <view class="w-12 h-4 bg-gray-200 rounded"></view>
          </view>
          <view class="w-32 h-6 bg-gray-200 rounded mb-2"></view>
          <view class="w-24 h-4 bg-gray-200 rounded mb-4"></view>
          <view class="flex justify-between">
            <view class="w-20 h-4 bg-gray-200 rounded"></view>
            <view class="w-20 h-4 bg-gray-200 rounded"></view>
          </view>
        </view>
      </view>

      <!-- 已登录 - 错误状态 -->
      <view
        v-else-if="userStore.isLoggedIn && isCardsError && !isCardsLoading"
        class="text-center py-8"
      >
        <text class="text-gray-500 text-sm">信用卡数据加载失败</text>
        <view class="mt-4">
          <view
            class="bg-blue-600 text-white rounded-lg px-6 py-3 inline-block"
            @click="refetchCards"
          >
            <text class="text-sm">重新加载</text>
          </view>
        </view>
      </view>

      <!-- 已登录 - 空状态 -->
      <view
        v-else-if="
          userStore.isLoggedIn && !isCardsLoading && !isCardsError && creditCards.length === 0
        "
        class="text-center py-8"
      >
        <text class="text-gray-500 text-sm">您还没有添加信用卡</text>
        <view class="mt-4">
          <view
            class="bg-blue-600 text-white rounded-lg px-6 py-3 inline-block"
            @click="handleAddCard"
          >
            <text class="text-sm">添加信用卡</text>
          </view>
        </view>
      </view>

      <!-- 已登录 - 信用卡列表 -->
      <view
        v-else-if="userStore.isLoggedIn && !isCardsLoading && creditCards.length > 0"
        class="space-y-3"
      >
        <CreditCard
          v-for="(card, index) in creditCards"
          :key="card.id"
          :card="card"
          :isBestCard="index === 0"
          @cardClick="handleCardClick"
          @cardUpdated="refetchCards"
        />
      </view>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useUserStore } from '@/store/user'
import { getCreditCardsApiV1UserCardsGetQueryOptions } from '@/service/app/v1Yonghugongneng.vuequery'
import CreditCard from '@/components/CreditCard.vue'
import FeeOverview from '@/components/FeeOverview.vue'
import TodayRecommendation from '@/components/TodayRecommendation.vue'
import HeaderSection from '@/components/HeaderSection.vue'
import type { CreditCard as CreditCardType } from '@/types/card'
import type * as API from '@/service/app/types'

// 获取屏幕边界到安全区域距离
let safeAreaInsets: any = null
// #ifdef MP-WEIXIN
try {
  const wxSystemInfo = uni.getSystemInfoSync()
  safeAreaInsets = wxSystemInfo.safeAreaInsets
} catch (e) {
  console.warn('获取安全区域失败', e)
}
// #endif

// #ifndef MP-WEIXIN
try {
  const uniSystemInfo = uni.getSystemInfoSync()
  safeAreaInsets = uniSystemInfo.safeAreaInsets
} catch (e) {
  console.warn('获取安全区域失败', e)
}
// #endif

// 获取用户状态
const userStore = useUserStore()

// 使用Vue Query获取信用卡列表 - 只有在已登录时才启用
const {
  data: creditCardsResponse,
  isLoading: isCardsLoading,
  isError: isCardsError,
  refetch: refetchCards,
} = useQuery({
  ...getCreditCardsApiV1UserCardsGetQueryOptions({
    params: {
      // keyword: '',
      // status: 'all',
      // bank_id: '',
      // card_type: '',
      // is_primary: false,
      // expiring_soon: false,
    },
  }),
  enabled: userStore.isLoggedIn, // 只有在已登录时才启用查询
})

// 监听用户登录状态变化，登录成功后自动刷新数据
watch(
  () => userStore.isLoggedIn,
  (newValue, oldValue) => {
    console.log('首页用户登录状态变化:', { oldValue, newValue })
    if (newValue && !oldValue) {
      // 从未登录变为已登录，刷新信用卡数据
      console.log('用户登录成功，刷新首页信用卡数据')
      setTimeout(() => {
        refetchCards()
      }, 100) // 稍微延迟确保token已设置
    }
  },
  { immediate: false },
)

// 计算属性 - 从API响应中提取信用卡列表
const creditCards = computed(() => {
  console.log('creditCardsResponse', creditCardsResponse.value)

  // 检查响应数据结构
  let cardsData = null
  if (creditCardsResponse.value) {
    // 如果是包装格式 {data: [...]}
    if (creditCardsResponse.value.data && Array.isArray(creditCardsResponse.value.data)) {
      cardsData = creditCardsResponse.value.data
    }
    // 如果是直接的数组格式 [...]
    else if (Array.isArray(creditCardsResponse.value)) {
      cardsData = creditCardsResponse.value
    }
  }

  if (!cardsData || !Array.isArray(cardsData)) {
    console.log('没有找到有效的信用卡数据')
    return []
  }

  console.log('找到信用卡数据，数量:', cardsData.length)

  // 将API数据转换为组件需要的格式
  return (cardsData as any[]).map((apiCard: any) => {
    // 根据API返回的数据结构转换为CreditCardType格式
    const bankName = apiCard.bank?.bank_name || apiCard.bank_name || '未知银行'
    const card: CreditCardType = {
      id: apiCard.id || '',
      bankName: bankName,
      bankCode: bankName.charAt(0),
      bankColor: apiCard.bank_color,
      cardName: apiCard.card_name || '信用卡',
      cardType: apiCard.card_network?.toLowerCase() || 'unionpay',
      cardNumberLast4: apiCard.card_number ? apiCard.card_number.slice(-4) : '****',
      creditLimit: Number(apiCard.credit_limit) || 0,
      usedAmount: Number(apiCard.used_limit) || 0,
      availableAmount: Number(apiCard.available_limit) || 0,
      isActive: apiCard.status === 'active',
      annualFeeStatus: getAnnualFeeStatus(apiCard),
      feeType: apiCard.fee_waivable ? 'waivable' : 'rigid',
      waiverProgress: 0, // 需要根据实际业务逻辑计算
      annualFee: Number(apiCard.annual_fee) || 0,
      dueDate: apiCard.due_date || 15,
      interestFreeDays: apiCard.interest_free_days || 0,
    }
    return card
  })
})

// 调试用计算属性 - 显示当前状态
const debugInfo = computed(() => {
  const info = {
    isLoggedIn: userStore.isLoggedIn,
    isCardsLoading: isCardsLoading.value,
    isCardsError: isCardsError.value,
    creditCardsLength: creditCards.value.length,
    hasResponse: !!creditCardsResponse.value,
    responseData: creditCardsResponse.value?.data,
  }
  console.log('首页状态调试信息:', info)
  return info
})

// 工具函数 - 获取年费状态
const getAnnualFeeStatus = (apiCard: any) => {
  // 根据API返回的年费相关字段判断状态
  if (apiCard.annual_fee === 0) return 'waived'
  if (apiCard.fee_paid) return 'paid'
  if (apiCard.fee_overdue) return 'overdue'
  return 'pending'
}

// 事件处理
const handleCardClick = (cardId: string) => {
  console.log('Card clicked:', cardId)
  // 可以导航到卡片详情页
}

const handleAddCard = () => {
  console.log('Add card clicked')
  // 跳转到添加卡片页面
  uni.navigateTo({
    url: '/pages/cards/add',
  })
}

const handleViewAll = () => {
  console.log('View all clicked')
  uni.navigateTo({
    url: '/pages/cards/index',
  })
}

const handleViewFeeDetail = () => {
  console.log('View fee detail clicked')
  uni.navigateTo({
    url: '/pages/fees/index',
  })
}

const handleManageWaiver = () => {
  console.log('Manage waiver clicked')
  // 可以导航到年费减免管理页面
  uni.showToast({
    title: '减免管理功能开发中',
    icon: 'none',
  })
}

const handleRecommendationClick = (card: CreditCardType) => {
  console.log('Recommendation clicked:', card)
  // 可以跳转到推荐卡片的详情页面或使用建议
  uni.showToast({
    title: `推荐使用${card.bankName}${card.cardName}`,
    icon: 'success',
  })
}

const goToLogin = () => {
  console.log('Go to login clicked')
  uni.navigateTo({
    url: '/pages/auth/login',
  })
}

onMounted(() => {
  console.log('首页加载完成')

  // 监听信用卡更新事件
  uni.$on('refreshCardList', () => {
    console.log('首页收到刷新信用卡列表事件')
    if (userStore.isLoggedIn) {
      refetchCards()
    }
  })

  uni.$on('cardUpdated', (data) => {
    console.log('首页收到信用卡更新事件:', data)
    if (userStore.isLoggedIn) {
      refetchCards()
    }
  })
})

// 页面显示时刷新数据
onShow(() => {
  console.log('首页显示，刷新数据')
  if (userStore.isLoggedIn) {
    refetchCards()
  }
})

// 页面卸载时移除事件监听
onUnmounted(() => {
  uni.$off('refreshCardList')
  uni.$off('cardUpdated')
})
</script>

<style lang="scss">
.home-page {
  min-height: 100vh;
  background: #f5f5f5;
}

// 如果没有iconfont，可以使用文本替代
.iconfont {
  &.icon-add::before {
    content: '➕';
  }
  &.icon-transaction::before {
    content: '💳';
  }
  &.icon-chart::before {
    content: '📊';
  }
  &.icon-remind::before {
    content: '⏰';
  }
}

.card-item {
  transition: transform 0.2s ease;

  &:active {
    transform: scale(0.98);
  }
}
</style>
