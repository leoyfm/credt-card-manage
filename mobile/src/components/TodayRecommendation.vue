<template>
  <view class="today-recommendation bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl p-4 shadow-lg text-white relative overflow-hidden">
    <!-- 推荐标签 -->
    <view class="flex items-center justify-between mb-3">
      <view class="flex items-center">
        <text class="text-lg mr-2">⭐</text>
        <text class="text-lg font-semibold">今日推荐</text>
      </view>
      <view class="bg-white bg-opacity-20 text-white px-2 py-1 rounded-full text-xs font-medium">
        最优选择
      </view>
    </view>

    <!-- 推荐内容 -->
    <view class="flex items-center justify-between">
      <view class="flex-1">
        <text class="text-xl font-bold mb-2 block">{{ recommendation.bankName }}{{ recommendation.cardName }}</text>
        <text class="text-sm opacity-90 block">{{ recommendation.description }}</text>
      </view>
      
      <!-- 推荐指标 -->
      <view class="text-center ml-4">
        <text class="text-3xl font-bold block">{{ recommendation.highlightValue }}</text>
        <text class="text-xs opacity-80">{{ recommendation.highlightLabel }}</text>
      </view>
    </view>

    <!-- 推荐理由 -->
    <view v-if="recommendation.reasons.length > 0" class="mt-3 flex flex-wrap gap-1">
      <view 
        v-for="reason in recommendation.reasons" 
        :key="reason"
        class="bg-white bg-opacity-15 px-2 py-1 rounded-md text-xs"
      >
        {{ reason }}
      </view>
    </view>

    <!-- 装饰性背景 -->
    <view class="absolute top-0 right-0 w-20 h-20 bg-white opacity-10 rounded-full transform translate-x-10 -translate-y-10"></view>
    <view class="absolute bottom-0 left-0 w-16 h-16 bg-white opacity-5 rounded-full transform -translate-x-8 translate-y-8"></view>
    
    <!-- 点击区域 -->
    <view class="absolute inset-0" @click="handleRecommendationClick"></view>
  </view>
</template>

<script lang="ts" setup>
import { computed } from 'vue'
import type { CreditCard } from '@/types/card'

interface Props {
  cards: CreditCard[]
}

const props = defineProps<Props>()

defineEmits<{
  recommendationClick: [card: CreditCard]
}>()

// 推荐算法
const recommendation = computed(() => {
  const activeCards = props.cards.filter(card => card.isActive)
  
  if (activeCards.length === 0) {
    return {
      bankName: '建设银行',
      cardName: '龙卡信用卡',
      description: '免息期长，刷卡享优惠',
      highlightValue: '18',
      highlightLabel: '免息天数',
      reasons: ['新用户推荐', '免年费'],
      card: null
    }
  }

  // 根据不同维度评分选择推荐卡片
  const scoredCards = activeCards.map(card => {
    let score = 0
    const reasons: string[] = []
    
    // 免息天数评分
    const interestFreeDays = getInterestFreeDays(card)
    if (interestFreeDays >= 50) {
      score += 30
      reasons.push('超长免息')
    } else if (interestFreeDays >= 40) {
      score += 20
      reasons.push('免息期长')
    }
    
    // 年费状态评分
    if (card.annualFeeStatus === 'waived') {
      score += 25
      reasons.push('免年费')
    } else if (card.feeType === 'waivable' && card.waiverProgress >= 80) {
      score += 20
      reasons.push('接近减免')
    }
    
    // 额度利用率评分（低利用率更好）
    const utilization = (card.usedAmount / card.creditLimit) * 100
    if (utilization < 30) {
      score += 20
      reasons.push('额度充足')
    } else if (utilization < 50) {
      score += 10
    }
    
    // 还款日期评分（临近还款日的卡片优先推荐）
    const daysToPayment = getDaysToPayment(card)
    if (daysToPayment <= 7 && daysToPayment > 0) {
      score += 15
      reasons.push('临近还款')
    }
    
    return {
      card,
      score,
      reasons: reasons.slice(0, 3) // 最多显示3个理由
    }
  })
  
  // 选择得分最高的卡片
  const bestCard = scoredCards.reduce((best, current) => 
    current.score > best.score ? current : best
  )
  
  const card = bestCard.card
  const interestFreeDays = getInterestFreeDays(card)
  
  return {
    bankName: card.bankName,
    cardName: card.cardName,
    description: getCardDescription(card),
    highlightValue: interestFreeDays.toString(),
    highlightLabel: '免息天数',
    reasons: bestCard.reasons,
    card: card
  }
})

// 工具函数
const getInterestFreeDays = (card: CreditCard) => {
  // 根据还款日计算免息天数
  if (!card.dueDate) return 45
  
  const today = new Date()
  const currentDay = today.getDate()
  
  // 如果已过还款日，计算到下个月还款日的天数
  if (currentDay > card.dueDate) {
    const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, card.dueDate)
    const diffTime = nextMonth.getTime() - today.getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 25 // 加上账单日到还款日的天数
  } else {
    return card.dueDate - currentDay + 25
  }
}

const getDaysToPayment = (card: CreditCard) => {
  if (!card.dueDate) return 30
  
  const today = new Date()
  const currentDay = today.getDate()
  
  if (currentDay <= card.dueDate) {
    return card.dueDate - currentDay
  } else {
    const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, card.dueDate)
    const diffTime = nextMonth.getTime() - today.getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  }
}

const getCardDescription = (card: CreditCard) => {
  const reasons = []
  
  if (card.annualFeeStatus === 'waived') {
    reasons.push('免年费')
  }
  
  const utilization = (card.usedAmount / card.creditLimit) * 100
  if (utilization < 30) {
    reasons.push('额度充足')
  }
  
  const interestFreeDays = getInterestFreeDays(card)
  if (interestFreeDays >= 50) {
    reasons.push('超长免息')
  } else if (interestFreeDays >= 40) {
    reasons.push('免息期长')
  }
  
  if (reasons.length === 0) {
    reasons.push('性价比高')
  }
  
  return reasons.slice(0, 2).join('，')
}

// 事件处理
const handleRecommendationClick = () => {
  if (recommendation.value.card) {
    // 发送推荐点击事件
    console.log('Recommendation clicked:', recommendation.value.card)
    // 可以跳转到卡片详情或使用建议页面
  }
}
</script>

<style lang="scss" scoped>
.today-recommendation {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  
  &:active {
    transform: scale(0.98);
    box-shadow: 0 8px 25px rgba(147, 51, 234, 0.3);
  }
}

.flex-wrap {
  flex-wrap: wrap;
}

.gap-1 > :not(:first-child) {
  margin-left: 0.25rem;
}

@media (max-width: 640px) {
  .today-recommendation {
    &:active {
      transform: scale(0.98);
    }
  }
}
</style> 