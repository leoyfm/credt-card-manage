<template>
  <view 
    class="card-item bg-white rounded-xl p-4 shadow-sm"
    @click="$emit('cardClick', card.id)"
  >
    <!-- 银行信息 -->
    <view class="flex items-center justify-between mb-3">
      <view class="flex items-center">
        <view 
          class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3"
          :style="{ backgroundColor: card.bankColor }"
        >
          {{ card.bankCode }}
        </view>
        <view>
          <text class="font-semibold text-gray-800">{{ card.bankName }}{{ card.cardName }}</text>
          <text class="text-xs text-gray-500 block">**** {{ card.cardNumberLast4 }}</text>
        </view>
      </view>
      <view class="text-right">
        <text class="text-sm font-semibold" :class="getCardStatusClass(card.isActive)">
          {{ card.isActive ? '正常' : '停用' }}
        </text>
      </view>
    </view>

    <!-- 额度信息 -->
    <view class="mb-3">
      <view class="flex justify-between items-center mb-1">
        <text class="text-sm text-gray-600">可用额度</text>
        <text class="text-sm font-semibold text-green-600">¥{{ formatMoney(card.availableAmount) }}</text>
      </view>
      <view class="bg-gray-200 rounded-full h-2">
        <view 
          class="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full transition-all duration-300"
          :style="{ width: (card.availableAmount / card.creditLimit * 100) + '%' }"
        ></view>
      </view>
      <view class="flex justify-between text-xs text-gray-500 mt-1">
        <text>总额度 ¥{{ formatMoney(card.creditLimit) }}</text>
        <text>已用 ¥{{ formatMoney(card.usedAmount) }}</text>
      </view>
    </view>

    <!-- 年费信息 -->
    <view class="flex items-center justify-between">
      <view class="flex items-center">
        <text class="text-sm text-gray-600">年费状态:</text>
        <text class="text-sm ml-1" :class="getFeeStatusClass(card.annualFeeStatus)">
          {{ getFeeStatusText(card.annualFeeStatus) }}
        </text>
      </view>
      <view v-if="card.feeType !== 'rigid'" class="text-right">
        <text class="text-xs text-gray-500">减免进度</text>
        <text class="text-sm font-semibold text-blue-600 ml-1">{{ card.waiverProgress }}%</text>
      </view>
    </view>
  </view>
</template>

<script lang="ts" setup>
import type { CreditCard } from '@/types/card'

interface Props {
  card: CreditCard
}

defineProps<Props>()

defineEmits<{
  cardClick: [cardId: string]
}>()

// 工具函数
const formatMoney = (amount: number) => {
  if (!amount) return '0.00'
  return (amount / 10000).toFixed(1) + '万'
}

const getCardStatusClass = (isActive: boolean) => {
  return isActive ? 'text-green-600' : 'text-red-600'
}

const getFeeStatusClass = (status: string) => {
  const classes = {
    pending: 'text-orange-600',
    waived: 'text-green-600',
    paid: 'text-blue-600',
    overdue: 'text-red-600'
  }
  return classes[status] || 'text-gray-600'
}

const getFeeStatusText = (status: string) => {
  const texts = {
    pending: '待缴费',
    waived: '已减免',
    paid: '已缴费',
    overdue: '已逾期'
  }
  return texts[status] || '未知'
}
</script>

<style lang="scss" scoped>
.card-item {
  transition: transform 0.2s ease;
  cursor: pointer;
  
  &:active {
    transform: scale(0.98);
  }
}
</style> 