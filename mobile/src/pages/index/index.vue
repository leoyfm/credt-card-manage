<!-- 信用卡管理首页 -->
<route lang="json5" type="home">
{
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '信用卡管家',
  },
}
</route>

<template>
  <view class="index-container safe-area bg-gray-50 min-h-screen">
    <!-- 顶部状态栏区域 -->
    <HeaderSection 
      :cards="creditCards"
    />

    <!-- 今日推荐 -->
    <view class="p-4 pt-2">
      <TodayRecommendation 
        :cards="creditCards"
        @recommendationClick="handleRecommendationClick"
      />
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
      <view class="add-card-btn bg-black text-white rounded-xl p-4 text-center" @click="handleAddCard">
        <text class="text-lg font-semibold">+ 添加信用卡</text>
      </view>
    </view>

    <!-- 信用卡列表 -->
    <view class="px-4 pb-32">
      <view class="flex items-center justify-between mb-4">
        <text class="text-lg font-semibold text-gray-800">我的信用卡</text>
        <text class="text-sm text-blue-600" @click="handleViewAll">查看全部</text>
      </view>
      <view class="space-y-3">
        <CreditCard 
          v-for="(card, index) in creditCards" 
          :key="card.id" 
          :card="card"
          :isBestCard="index === 0"
          @cardClick="handleCardClick"
          @edit="handleEditCard"
          @delete="handleDeleteCard"
          @toggleActive="handleToggleActiveCard"
        />
      </view>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import CreditCard from '@/components/CreditCard.vue'
import FeeOverview from '@/components/FeeOverview.vue'
import TodayRecommendation from '@/components/TodayRecommendation.vue'
import HeaderSection from '@/components/HeaderSection.vue'
import type { CreditCard as CreditCardType } from '@/types/card'

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

// 演示数据
const creditCards = ref<CreditCardType[]>([
  {
    id: '1',
    bankName: '招商银行',
    bankCode: '招',
    bankColor: '#DC2626',
    cardName: '全币种国际卡',
    cardType: 'visa',
    cardNumberLast4: '8888',
    creditLimit: 500000,
    usedAmount: 125000,
    availableAmount: 375000,
    isActive: true,
    annualFeeStatus: 'paid',
    feeType: 'waivable',
    waiverProgress: 75,
    annualFee: 680,
    dueDate: 15
  },
  {
    id: '2',
    bankName: '工商银行',
    bankCode: '工',
    bankColor: '#DC2626',
    cardName: '宇宙星座卡',
    cardType: 'mastercard',
    cardNumberLast4: '6666',
    creditLimit: 300000,
    usedAmount: 45000,
    availableAmount: 255000,
    isActive: true,
    annualFeeStatus: 'waived',
    feeType: 'waivable',
    waiverProgress: 100,
    annualFee: 580,
    dueDate: 8
  },
  {
    id: '3',
    bankName: '建设银行',
    bankCode: '建',
    bankColor: '#2563EB',
    cardName: '龙卡信用卡',
    cardType: 'unionpay',
    cardNumberLast4: '9999',
    creditLimit: 200000,
    usedAmount: 110000,
    availableAmount: 90000,
    isActive: true,
    annualFeeStatus: 'pending',
    feeType: 'waivable',
    waiverProgress: 45,
    annualFee: 480,
    dueDate: 20
  },
  {
    id: '4',
    bankName: '中国银行',
    bankCode: '中',
    bankColor: '#DC2626',
    cardName: '长城环球通卡',
    cardType: 'visa',
    cardNumberLast4: '7777',
    creditLimit: 150000,
    usedAmount: 30000,
    availableAmount: 120000,
    isActive: true,
    annualFeeStatus: 'waived',
    feeType: 'waivable',
    waiverProgress: 100,
    annualFee: 360,
    dueDate: 25
  },
  {
    id: '5',
    bankName: '交通银行',
    bankCode: '交',
    bankColor: '#2563EB',
    cardName: '沃尔玛信用卡',
    cardType: 'mastercard',
    cardNumberLast4: '5555',
    creditLimit: 100000,
    usedAmount: 80000,
    availableAmount: 20000,
    isActive: true,
    annualFeeStatus: 'overdue',
    feeType: 'rigid',
    waiverProgress: 0,
    annualFee: 200,
    dueDate: 10
  },
  {
    id: '6',
    bankName: '光大银行',
    bankCode: '光',
    bankColor: '#7C3AED',
    cardName: '阳光信用卡',
    cardType: 'unionpay',
    cardNumberLast4: '4444',
    creditLimit: 80000,
    usedAmount: 26400,
    availableAmount: 53600,
    isActive: true,
    annualFeeStatus: 'pending',
    feeType: 'waivable',
    waiverProgress: 67,
    annualFee: 300,
    dueDate: 18
  }
])

// 计算属性
const pendingFeeCards = computed(() => 
  creditCards.value.filter(card => card.annualFeeStatus === 'pending' || card.annualFeeStatus === 'overdue').length
)

// 事件处理
const handleCardClick = (cardId: string) => {
  console.log('Card clicked:', cardId)
  // 可以导航到卡片详情页
}

const handleEditCard = (card: CreditCardType) => {
  console.log('Edit card:', card)
  // 可以导航到编辑页面
  uni.showToast({
    title: '编辑功能开发中',
    icon: 'none'
  })
}

const handleDeleteCard = (cardId: string) => {
  console.log('Delete card:', cardId)
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这张信用卡吗？',
    success: (res) => {
      if (res.confirm) {
        const index = creditCards.value.findIndex(card => card.id === cardId)
        if (index > -1) {
          creditCards.value.splice(index, 1)
          uni.showToast({
            title: '删除成功',
            icon: 'success'
          })
        }
      }
    }
  })
}

const handleToggleActiveCard = (cardId: string) => {
  console.log('Toggle active card:', cardId)
  const card = creditCards.value.find(card => card.id === cardId)
  if (card) {
    card.isActive = !card.isActive
    uni.showToast({
      title: card.isActive ? '已启用' : '已停用',
      icon: 'success'
    })
  }
}

const handleAddCard = () => {
  console.log('Add card clicked')
  // 跳转到添加卡片页面
  uni.navigateTo({
    url: '/pages/cards/add'
  })
}

const handleViewAll = () => {
  console.log('View all clicked')
  uni.navigateTo({
    url: '/pages/cards/index'
  })
}

const handleViewFeeDetail = () => {
  console.log('View fee detail clicked')
  uni.navigateTo({
    url: '/pages/fees/index'
  })
}

const handleManageWaiver = () => {
  console.log('Manage waiver clicked')
  // 可以导航到年费减免管理页面
  uni.showToast({
    title: '减免管理功能开发中',
    icon: 'none'
  })
}

const handleRecommendationClick = (card: CreditCardType) => {
  console.log('Recommendation clicked:', card)
  // 可以跳转到推荐卡片的详情页面或使用建议
  uni.showToast({
    title: `推荐使用${card.bankName}${card.cardName}`,
    icon: 'success'
  })
}

// HeaderSection 组件已经内部处理导航，移除了这两个方法

const handleTabClick = (tab: string) => {
  console.log('Tab clicked:', tab)
  const routes = {
    home: '/pages/index/index',
    cards: '/pages/cards/index',
    transactions: '/pages/transactions/index',
    fees: '/pages/fees/index',
    mine: '/pages/mine/index'
  }
  
  if (routes[tab] && routes[tab] !== '/pages/index/index') {
    uni.navigateTo({
      url: routes[tab]
    })
  }
}

onMounted(() => {
  console.log('首页加载完成')
})
</script>

<style lang="scss">
.home-page {
  min-height: 100vh;
  background: #f5f5f5;
}

// 如果没有iconfont，可以使用文本替代
.iconfont {
  &.icon-notification::before { content: '🔔'; }
  &.icon-setting::before { content: '⚙️'; }
  &.icon-add::before { content: '➕'; }
  &.icon-transaction::before { content: '💳'; }
  &.icon-chart::before { content: '📊'; }
  &.icon-remind::before { content: '⏰'; }
}

.card-item {
  transition: transform 0.2s ease;
  
  &:active {
    transform: scale(0.98);
  }
}
</style>
