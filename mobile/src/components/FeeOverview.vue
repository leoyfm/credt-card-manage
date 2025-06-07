<template>
  <view class="fee-overview bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 shadow-sm border border-purple-200 border-solid">
    <!-- 标题栏 -->
    <view class="flex items-center mb-4">
      <text class="text-xl mr-2">🏆</text>
      <text class="text-lg font-semibold text-purple-800">年费概览</text>
    </view>
    
    <!-- 核心统计 -->
    <view class="grid grid-cols-2 gap-4 mb-4">
      <view class="text-center">
        <text class="text-2xl font-bold text-purple-600 block">{{ formatCurrency(stats.totalAnnualFee) }}</text>
        <text class="text-sm text-purple-700">总年费</text>
      </view>
      <view class="text-center">
        <text class="text-2xl font-bold text-green-600 block">{{ stats.freeCards }}</text>
        <text class="text-sm text-green-700">免费卡片</text>
      </view>
    </view>

    <!-- 状态分类 -->
    <view class="space-y-2 mb-4">
      <!-- 免费卡片 -->
      <view class="flex items-center justify-between">
        <view class="flex items-center">
          <text class="text-green-500 mr-2">✅</text>
          <text class="text-sm text-gray-700">免费卡片</text>
        </view>
        <view class="bg-green-50 text-green-700 px-2 py-1 rounded-full text-xs font-medium">
          {{ stats.freeCards }}张
        </view>
      </view>

      <!-- 需要关注 -->
      <view v-if="stats.urgentCards > 0" class="flex items-center justify-between">
        <view class="flex items-center">
          <text class="text-orange-500 mr-2">⚠️</text>
          <text class="text-sm text-gray-700">需要关注</text>
        </view>
        <view class="bg-orange-50 text-orange-700 px-2 py-1 rounded-full text-xs font-medium">
          {{ stats.urgentCards }}张
        </view>
      </view>

      <!-- 进行中 -->
      <view v-if="stats.inProgressCards > 0" class="flex items-center justify-between">
        <view class="flex items-center">
          <text class="text-blue-500 mr-2">⏰</text>
          <text class="text-sm text-gray-700">进行中</text>
        </view>
        <view class="bg-blue-50 text-blue-700 px-2 py-1 rounded-full text-xs font-medium">
          {{ stats.inProgressCards }}张
        </view>
      </view>

      <!-- 已逾期 -->
      <view v-if="stats.overdueCards > 0" class="flex items-center justify-between">
        <view class="flex items-center">
          <text class="text-red-500 mr-2">❌</text>
          <text class="text-sm text-gray-700">已逾期</text>
        </view>
        <view class="bg-red-50 text-red-700 px-2 py-1 rounded-full text-xs font-medium">
          {{ stats.overdueCards }}张
        </view>
      </view>
    </view>

    <!-- 详细信息 -->
    <view v-if="showDetail" class="border-t border-purple-100 pt-3 mb-4">
      <view class="flex justify-between items-center mb-2">
        <text class="text-sm text-gray-600">已节省金额</text>
        <text class="text-sm font-semibold text-green-600">{{ formatCurrency(stats.savedAmount) }}</text>
      </view>
      <view class="flex justify-between items-center mb-2">
        <text class="text-sm text-gray-600">节省率</text>
        <text 
          class="text-sm font-semibold"
          :class="getSavingRateClass()"
        >
          {{ getSavingRate() }}%
        </text>
      </view>
      <view class="flex justify-between items-center">
        <text class="text-sm text-gray-600">减免进度</text>
        <text class="text-sm font-semibold text-purple-600">{{ getWaiverProgress() }}%</text>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view v-if="showActions" class="flex space-x-2 mb-3">
      <view 
        class="flex-1 bg-purple-500 text-white text-center py-2 rounded-lg"
        @click="$emit('viewDetail')"
      >
        <text class="text-sm font-medium">查看详情</text>
      </view>
      <view 
        class="flex-1 bg-purple-100 text-purple-700 text-center py-2 rounded-lg"
        @click="$emit('manageWaiver')"
      >
        <text class="text-sm font-medium">减免管理</text>
      </view>
    </view>

    <!-- 智能提醒 -->
    <view v-if="getSmartReminder()" class="p-2 rounded-lg" :class="getReminderClass()">
      <view class="flex items-center">
        <text class="mr-2">{{ getReminderIcon() }}</text>
        <text class="text-xs flex-1" :class="getReminderTextClass()">{{ getSmartReminder() }}</text>
      </view>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { computed } from 'vue'
import type { CreditCard } from '@/types/card'

interface Props {
  cards: CreditCard[]
  showDetail?: boolean
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDetail: false,
  showActions: false
})

defineEmits<{
  viewDetail: []
  manageWaiver: []
}>()

// 计算统计数据
const stats = computed(() => {
  const activeCards = props.cards.filter(card => card.isActive)
  
  // 总年费
  const totalAnnualFee = activeCards.reduce((sum, card) => sum + card.annualFee, 0)
  
  // 免费卡片数量（已减免 + 年费为0）
  const freeCards = activeCards.filter(card => 
    card.annualFeeStatus === 'waived' || card.annualFee === 0
  ).length
  
  // 需要关注的卡片（减免进度低且临近截止日期）
  const urgentCards = activeCards.filter(card => {
    if (card.annualFeeStatus !== 'pending' || card.feeType === 'rigid') return false
    return card.waiverProgress < 80 && getDaysUntilDue(card) <= 30
  }).length
  
  // 进行中的卡片
  const inProgressCards = activeCards.filter(card => 
    card.annualFeeStatus === 'pending' && !isUrgentCard(card)
  ).length
  
  // 已逾期卡片
  const overdueCards = activeCards.filter(card => 
    card.annualFeeStatus === 'overdue'
  ).length
  
  // 已节省金额
  const savedAmount = activeCards
    .filter(card => card.annualFeeStatus === 'waived')
    .reduce((sum, card) => sum + card.annualFee, 0)
  
  return {
    totalAnnualFee,
    freeCards,
    urgentCards,
    inProgressCards, 
    overdueCards,
    savedAmount,
    totalCards: activeCards.length
  }
})

// 工具函数
const formatCurrency = (amount: number) => {
  return '¥' + amount.toLocaleString()
}

const getDaysUntilDue = (card: CreditCard) => {
  if (!card.dueDate) return 365
  const today = new Date()
  const currentMonth = today.getMonth()
  const currentYear = today.getFullYear()
  
  let dueMonth = currentMonth
  let dueYear = currentYear
  
  // 如果已过当月还款日，计算下个月
  if (today.getDate() > card.dueDate) {
    dueMonth += 1
    if (dueMonth > 11) {
      dueMonth = 0
      dueYear += 1
    }
  }
  
  const dueDateTime = new Date(dueYear, dueMonth, card.dueDate).getTime()
  const todayTime = today.getTime()
  
  return Math.ceil((dueDateTime - todayTime) / (1000 * 60 * 60 * 24))
}

const isUrgentCard = (card: CreditCard) => {
  if (card.annualFeeStatus !== 'pending' || card.feeType === 'rigid') return false
  return card.waiverProgress < 80 && getDaysUntilDue(card) <= 30
}

const getSavingRate = () => {
  if (!stats.value.totalAnnualFee) return 0
  return Math.round((stats.value.savedAmount / stats.value.totalAnnualFee) * 100)
}

const getSavingRateClass = () => {
  const rate = getSavingRate()
  if (rate >= 80) return 'text-green-600'
  if (rate >= 50) return 'text-blue-600'
  if (rate >= 30) return 'text-orange-600'
  return 'text-red-600'
}

const getWaiverProgress = () => {
  if (!stats.value.totalCards) return 0
  return Math.round((stats.value.freeCards / stats.value.totalCards) * 100)
}

const getSmartReminder = () => {
  if (stats.value.overdueCards > 0) {
    return `${stats.value.overdueCards}张卡片年费已逾期，请立即处理避免影响信用记录`
  }
  if (stats.value.urgentCards > 0) {
    return `${stats.value.urgentCards}张卡片的年费减免进度需要关注，请及时消费达标`
  }
  if (stats.value.freeCards === stats.value.totalCards && stats.value.totalCards > 0) {
    return '🎉 恭喜！所有卡片年费均已减免，为您节省了' + formatCurrency(stats.value.savedAmount)
  }
  return ''
}

const getReminderClass = () => {
  if (stats.value.overdueCards > 0) return 'bg-red-50'
  if (stats.value.urgentCards > 0) return 'bg-orange-50'
  return 'bg-green-50'
}

const getReminderTextClass = () => {
  if (stats.value.overdueCards > 0) return 'text-red-700'
  if (stats.value.urgentCards > 0) return 'text-orange-700'
  return 'text-green-700'
}

const getReminderIcon = () => {
  if (stats.value.overdueCards > 0) return '⚠️'
  if (stats.value.urgentCards > 0) return '💡'
  return '🎉'
}
</script>

<style lang="scss" scoped>
.fee-overview {
  transition: box-shadow 0.2s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

.grid {
  display: grid;
}

.grid-cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.gap-4 {
  gap: 1rem;
}

.space-x-2 > :not(:first-child) {
  margin-left: 0.5rem;
}
</style> 