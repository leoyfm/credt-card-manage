<template>
  <!-- 顶部状态栏区域 -->
  <view class="header-section bg-white">
    <!-- 应用头部 -->
    <view class="px-4 py-6">
      <view class="flex items-center justify-between mb-4">
        <view>
          <text class="text-2xl font-bold text-gray-900 block">信用卡管家</text>
          <text class="text-sm text-gray-500">智能管理您的信用卡</text>
        </view>
        <view class="flex items-center gap-2">
          <!-- 通知按钮 -->
          <view 
            class="relative p-2 bg-gray-100 rounded-lg"
            @click="handleNotificationClick"
          >
            <text class="text-lg">🔔</text>
            <view 
              v-if="unreadNotifications > 0" 
              class="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center"
            >
              <text class="text-white text-xs">{{ unreadNotifications > 9 ? '9+' : unreadNotifications }}</text>
            </view>
          </view>
          <!-- 设置按钮 -->
          <view 
            class="p-2 bg-gray-100 rounded-lg"
            @click="handleSettingsClick"
          >
            <text class="text-lg">⚙️</text>
          </view>
        </view>
      </view>

      <!-- 快速统计 -->
      <view v-if="summary.activeCards > 0" class="grid grid-cols-3 gap-3 mb-4">
        <view class="text-center">
          <text class="text-lg font-bold text-blue-600 block">{{ summary.activeCards }}</text>
          <text class="text-xs text-gray-500">活跃卡片</text>
        </view>
        <view class="text-center">
          <text class="text-lg font-bold text-green-600 block">{{ formatMoney(summary.totalCredit) }}</text>
          <text class="text-xs text-gray-500">可用额度</text>
        </view>
        <view class="text-center">
          <text class="text-lg font-bold text-orange-600 block">{{ getBestCardInterestFreeDays() }}</text>
          <text class="text-xs text-gray-500">免息天数</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import type { CreditCard } from '@/types/card'

interface Props {
  cards: CreditCard[]
}

const props = defineProps<Props>()

// 移除emit定义，组件内部直接处理导航

// 通知相关数据
const unreadNotifications = ref(3) // 演示数据

// 计算属性
const summary = computed(() => ({
  activeCards: props.cards.filter(card => card.isActive).length,
  totalCredit: props.cards.reduce((sum, card) => sum + card.availableAmount, 0),
}))

// 最佳卡片计算
const bestCard = computed(() => {
  const activeCards = props.cards.filter(card => card.isActive)
  if (activeCards.length === 0) return null
  
  // 选择年费状态最好且免息天数最长的卡片
  return activeCards.reduce((best, current) => {
    const currentScore = getCardScore(current)
    const bestScore = getCardScore(best)
    return currentScore > bestScore ? current : best
  })
})

// 工具函数
const formatMoney = (amount: number) => {
  if (!amount) return '0.00'
  return (amount / 10000).toFixed(1) + '万'
}

const getCardScore = (card: CreditCard) => {
  let score = 0
  
  // 年费状态评分
  if (card.annualFeeStatus === 'waived') score += 50
  else if (card.annualFeeStatus === 'pending' && card.waiverProgress >= 80) score += 30
  else if (card.annualFeeStatus === 'pending') score += 10
  
  // 免息天数评分
  const interestFreeDays = calculateInterestFreeDays(card)
  score += Math.min(interestFreeDays, 50)
  
  return score
}

const calculateInterestFreeDays = (card: CreditCard) => {
  if (!card.dueDate) return 0
  
  const today = new Date()
  const currentDate = today.getDate()
  
  // 计算到下个还款日的天数
  let dueMonth = today.getMonth()
  let dueYear = today.getFullYear()
  
  if (currentDate > card.dueDate) {
    dueMonth += 1
    if (dueMonth > 11) {
      dueMonth = 0
      dueYear += 1
    }
  }
  
  const dueDate = new Date(dueYear, dueMonth, card.dueDate)
  const diffTime = dueDate.getTime() - today.getTime()
  return Math.max(0, Math.ceil(diffTime / (1000 * 3600 * 24)))
}

const getBestCardInterestFreeDays = () => {
  if (!bestCard.value) return 0
  return calculateInterestFreeDays(bestCard.value)
}

// 事件处理
const handleNotificationClick = () => {
  console.log('Notification clicked')
  // 跳转到通知中心页面
  uni.navigateTo({
    url: '/pages/notifications/index'
  })
}

const handleSettingsClick = () => {
  console.log('Settings clicked')
  // 跳转到通知设置页面
  uni.navigateTo({
    url: '/pages/notifications/settings'
  })
}
</script>

<style lang="scss" scoped>
.header-section {
  transition: box-shadow 0.2s ease;
}

.grid {
  display: grid;
}

.grid-cols-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.gap-3 {
  gap: 0.75rem;
}

.gap-2 {
  gap: 0.5rem;
}

.gap-2 > :not(:first-child) {
  margin-left: 0.5rem;
}

@media (max-width: 640px) {
  .px-4 {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .py-6 {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
  }
}
</style> 