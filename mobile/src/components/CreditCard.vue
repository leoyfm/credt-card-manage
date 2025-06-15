<template>
  <view class="relative mb-4">
    <!-- 主卡片 -->
    <view
      class="card-container overflow-hidden rounded-xl shadow-lg transition-all duration-300"
      :class="[
        isBestCard ? 'ring-2 ring-green-400 shadow-xl' : 'shadow-md',
        !card.isActive ? 'opacity-60' : '',
      ]"
      :style="{ background: `linear-gradient(135deg, ${card.bankColor}20, ${card.bankColor}10)` }"
      @click="$emit('cardClick', card.id)"
    >
      <!-- 推荐标识 -->
      <view v-if="isBestCard" class="absolute top-2 right-2 z-10">
        <view
          class="bg-green-500 text-white px-2 py-1 rounded-full text-xs font-medium flex items-center"
        >
          <text class="mr-1">⭐</text>
          <text>推荐</text>
        </view>
      </view>

      <!-- 卡片头部 - 模拟真实信用卡 -->
      <view
        class="relative p-6 text-white flex flex-col justify-between"
        :style="{ background: `linear-gradient(135deg, ${card.bankColor}, ${card.bankColor}dd)` }"
      >
        <!-- 顶部信息 -->
        <view class="flex justify-between items-start">
          <view>
            <text class="text-sm opacity-90 block">{{ card.bankName }}</text>
            <text class="text-lg font-bold block">{{ card.cardName }}</text>
          </view>
          <view class="flex items-center space-x-2">
            <text class="text-xs opacity-75">{{ card.cardType?.toUpperCase() || 'CREDIT' }}</text>
            <view class="w-8 h-8 flex items-center justify-center" @click.stop="toggleActions">
              <text class="text-white text-lg">⋮</text>
            </view>
          </view>
        </view>

        <!-- 卡号区域 -->
        <view class="space-y-2">
          <text class="text-xl font-mono tracking-wider block">
            •••• •••• •••• {{ card.cardNumberLast4 }}
          </text>
          <view class="flex justify-between items-end">
            <view>
              <text class="text-xs opacity-75 block">可用额度</text>
              <text class="text-lg font-semibold block">
                {{ formatCurrency(card.availableAmount) }}
              </text>
            </view>
            <view class="text-right">
              <text class="text-xs opacity-75 block">还款日</text>
              <text class="text-sm block">{{ card.dueDate || '--' }}号</text>
            </view>
          </view>
        </view>

        <!-- 装饰性芯片 -->
        <view class="absolute top-16 left-6 w-12 h-8 bg-white bg-opacity-20 rounded-md"></view>
      </view>

      <!-- 卡片详情 -->
      <view class="p-4 bg-white space-y-4">
        <!-- 基础信息网格 -->
        <view class="grid grid-cols-3 gap-4 text-center">
          <view>
            <text class="text-xs text-gray-500 block mb-1">总额度</text>
            <text class="font-semibold text-sm block">{{ formatCurrency(card.creditLimit) }}</text>
          </view>
          <view>
            <text class="text-xs text-gray-500 block mb-1">已用额度</text>
            <text class="font-semibold text-sm block">{{ formatCurrency(card.usedAmount) }}</text>
          </view>
          <view>
            <text class="text-xs text-gray-500 block mb-1">免息天数</text>
            <view
              class="font-semibold text-sm flex items-center justify-center"
              :class="getInterestFreeDaysClass()"
            >
              <text class="mr-1">📅</text>
              <text>{{ card.interestFreeDays }}天</text>
            </view>
          </view>
        </view>

        <!-- 使用率进度条 -->
        <view class="space-y-2">
          <view class="flex justify-between items-center">
            <text class="text-xs text-gray-500">使用率</text>
            <text class="text-xs font-semibold" :class="getUtilizationClass()">
              {{ getUtilizationPercentage().toFixed(1) }}%
            </text>
          </view>
          <view class="w-full bg-gray-100 rounded-full h-2">
            <view
              class="h-2 rounded-full transition-all duration-300"
              :class="getUtilizationBarClass()"
              :style="{ width: Math.min(getUtilizationPercentage(), 100) + '%' }"
            ></view>
          </view>
        </view>

        <!-- 年费信息区域 -->
        <view class="border-t pt-3 space-y-3">
          <view class="flex items-center justify-between">
            <view class="flex items-center space-x-2">
              <text>{{ getAnnualFeeTypeIcon() }}</text>
              <text class="text-sm font-medium">年费信息</text>
            </view>
            <view
              class="px-2 py-1 rounded-full text-xs font-medium"
              :class="getAnnualFeeStatusClass()"
            >
              {{ getAnnualFeeStatusText() }}
            </view>
          </view>

          <view class="grid grid-cols-2 gap-3 text-xs">
            <view>
              <text class="text-gray-500 block">年费金额:</text>
              <text class="font-semibold block">{{ formatCurrency(card.annualFee || 0) }}</text>
            </view>
            <view>
              <text class="text-gray-500 block">{{ getAnnualFeeTypeText() }}:</text>
              <text class="font-semibold block">{{ getAnnualFeeProgressText() }}</text>
            </view>
          </view>

          <!-- 年费减免进度条 -->
          <view v-if="card.feeType === 'waivable'" class="space-y-2">
            <view class="flex justify-between items-center">
              <text class="text-xs text-gray-500">减免进度</text>
              <text class="text-xs font-semibold">{{ card.waiverProgress }}%</text>
            </view>
            <view class="w-full bg-gray-100 rounded-full h-2">
              <view
                class="h-2 rounded-full transition-all duration-300"
                :class="getWaiverProgressBarClass()"
                :style="{ width: Math.min(card.waiverProgress, 100) + '%' }"
              ></view>
            </view>
            <view v-if="getRemainingDays() > 0" class="flex justify-between text-xs text-gray-500">
              <text>剩余 {{ getRemainingDays() }} 天</text>
              <text>{{ getRemainingTarget() }}</text>
            </view>
          </view>

          <!-- 年费状态提示 -->
          <view
            v-if="getAnnualFeeHint()"
            class="p-2 rounded-lg text-xs"
            :class="getAnnualFeeHintClass()"
          >
            <view class="flex items-center space-x-2">
              <text>{{ getAnnualFeeHintIcon() }}</text>
              <text :class="getAnnualFeeHintTextClass()">{{ getAnnualFeeHint() }}</text>
            </view>
          </view>
        </view>

        <!-- 警告提示 -->
        <view
          v-if="getUtilizationPercentage() > 80"
          class="flex items-center space-x-2 p-2 bg-red-50 rounded-lg"
        >
          <text>⚠️</text>
          <text class="text-xs text-red-700">使用率过高，建议及时还款</text>
        </view>

        <view
          v-if="(card.interestFreeDays || 0) <= 7 && card.usedAmount > 0"
          class="flex items-center space-x-2 p-2 bg-yellow-50 rounded-lg"
        >
          <text>📅</text>
          <text class="text-xs text-yellow-700">还款日临近，请及时还款</text>
        </view>
      </view>
    </view>

    <!-- 操作菜单 -->
    <view
      v-if="showActions"
      class="absolute top-16 right-4 bg-white rounded-lg shadow-lg border z-20 min-w-32"
      @click.stop
    >
      <view class="py-2">
        <view class="w-full px-4 py-2 text-left text-sm hover:bg-gray-50" @click="handleEdit">
          <text>编辑</text>
        </view>
        <view
          class="w-full px-4 py-2 text-left text-sm hover:bg-gray-50"
          @click="handleToggleActive"
        >
          <text>{{ card.isActive ? '停用' : '启用' }}</text>
        </view>
        <view
          class="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50"
          @click="handleDelete"
        >
          <text>删除</text>
        </view>
      </view>
    </view>

    <!-- 点击外部关闭菜单 -->
    <view v-if="showActions" class="fixed inset-0 z-10" @click="showActions = false"></view>

    <!-- Toast 组件 -->
    <wd-toast />
  </view>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { useToast } from 'wot-design-uni'
import {
  useDeleteCreditCardApiV1UserCardsCardIdDeleteMutation,
  useUpdateCardStatusApiV1UserCardsCardIdStatusPatchMutation,
} from '@/service/app/v1Yonghugongneng.vuequery'
import type { CreditCard } from '@/types/card'

interface Props {
  card: CreditCard
  isBestCard?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isBestCard: false,
})

const emit = defineEmits<{
  cardClick: [cardId: string]
  cardUpdated: [] // 通知父组件刷新数据
}>()

const showActions = ref(false)
const toast = useToast()

// 删除信用卡的 mutation
const deleteCardMutation = useDeleteCreditCardApiV1UserCardsCardIdDeleteMutation({
  onSuccess: () => {
    toast.success('删除成功')
    // 通知父组件刷新数据
    emit('cardUpdated')
  },
  onError: (error) => {
    console.error('删除信用卡失败:', error)
    toast.error('删除失败，请重试')
  },
})

// 更新信用卡状态的 mutation
const updateCardStatusMutation = useUpdateCardStatusApiV1UserCardsCardIdStatusPatchMutation({
  onSuccess: () => {
    toast.success('状态更新成功')
    // 通知父组件刷新数据
    emit('cardUpdated')
  },
  onError: (error) => {
    console.error('更新状态失败:', error)
    toast.error('状态更新失败，请重试')
  },
})

// 工具函数
const formatCurrency = (amount: number) => {
  if (!amount) return '¥0.00'
  return '¥' + (amount / 10000).toFixed(1) + '万'
}

const getUtilizationPercentage = () => {
  if (!props.card.creditLimit) return 0
  return (props.card.usedAmount / props.card.creditLimit) * 100
}

// calculateInterestFreeDays 函数已移除，直接使用 card.interestFreeDays

const getRemainingDays = () => {
  // 模拟年费周期剩余天数
  return Math.max(0, Math.floor(Math.random() * 365))
}

const getRemainingTarget = () => {
  if (props.card.feeType === 'rigid') return ''

  const remaining = 100 - props.card.waiverProgress
  if (remaining <= 0) return '已完成'

  return `还需${remaining}%`
}

// 样式类函数
const getUtilizationClass = () => {
  const percentage = getUtilizationPercentage()
  if (percentage > 80) return 'text-red-500'
  if (percentage > 50) return 'text-yellow-500'
  return 'text-green-500'
}

const getUtilizationBarClass = () => {
  const percentage = getUtilizationPercentage()
  if (percentage > 80) return 'bg-red-400'
  if (percentage > 50) return 'bg-yellow-400'
  return 'bg-green-400'
}

const getInterestFreeDaysClass = () => {
  const days = props.card.interestFreeDays || 0
  if (days > 20) return 'text-green-600'
  if (days > 10) return 'text-yellow-600'
  return 'text-red-600'
}

const getAnnualFeeTypeIcon = () => {
  switch (props.card.feeType) {
    case 'waivable':
      return '🔄'
    case 'rigid':
      return '💰'
    default:
      return '💳'
  }
}

const getAnnualFeeTypeText = () => {
  switch (props.card.feeType) {
    case 'waivable':
      return '可减免'
    case 'rigid':
      return '刚性年费'
    default:
      return '年费类型'
  }
}

const getAnnualFeeProgressText = () => {
  if (props.card.feeType === 'rigid') return '不可减免'
  return `${props.card.waiverProgress}%`
}

const getAnnualFeeStatusText = () => {
  if (props.card.annualFee === 0) return '免费'
  if (props.card.feeType === 'rigid') return '刚性年费'
  if (props.card.waiverProgress >= 100) return '已达标'
  if (props.card.waiverProgress >= 80) return '进行中'
  return '需关注'
}

const getAnnualFeeStatusClass = () => {
  const status = getAnnualFeeStatusText()
  switch (status) {
    case '免费':
    case '已达标':
      return 'bg-green-50 text-green-600'
    case '刚性年费':
      return 'bg-red-50 text-red-600'
    case '需关注':
      return 'bg-orange-50 text-orange-600'
    default:
      return 'bg-blue-50 text-blue-600'
  }
}

const getWaiverProgressBarClass = () => {
  if (props.card.waiverProgress >= 100) return 'bg-green-500'
  if (props.card.waiverProgress >= 70) return 'bg-blue-500'
  if (getRemainingDays() <= 30) return 'bg-orange-500'
  return 'bg-gray-400'
}

const getAnnualFeeHint = () => {
  if (props.card.annualFee === 0) return '此卡终身免年费'
  if (props.card.feeType === 'rigid') return '此卡年费为刚性收费，无法减免'
  if (props.card.waiverProgress >= 100) return '恭喜！已达成年费减免条件'
  if (getRemainingDays() <= 30 && props.card.waiverProgress < 80) return '时间紧迫，请加快消费进度'
  if (props.card.waiverProgress < 100) return '按当前进度可顺利达成减免条件'
  return ''
}

const getAnnualFeeHintClass = () => {
  const hint = getAnnualFeeHint()
  if (hint.includes('恭喜') || hint.includes('终身免年费')) return 'bg-green-50'
  if (hint.includes('时间紧迫')) return 'bg-orange-50'
  if (hint.includes('刚性收费')) return 'bg-red-50'
  return 'bg-blue-50'
}

const getAnnualFeeHintTextClass = () => {
  const hint = getAnnualFeeHint()
  if (hint.includes('恭喜') || hint.includes('终身免年费')) return 'text-green-600'
  if (hint.includes('时间紧迫')) return 'text-orange-600'
  if (hint.includes('刚性收费')) return 'text-red-600'
  return 'text-blue-600'
}

const getAnnualFeeHintIcon = () => {
  const hint = getAnnualFeeHint()
  if (hint.includes('恭喜') || hint.includes('终身免年费')) return '✅'
  if (hint.includes('时间紧迫')) return '⚠️'
  if (hint.includes('刚性收费')) return '💰'
  return '🏆'
}

// 事件处理
const toggleActions = () => {
  showActions.value = !showActions.value
}

const handleEdit = () => {
  // 导航到编辑页面，传递卡片ID
  uni.navigateTo({
    url: `/pages/cards/edit?id=${props.card.id}`,
  })
  showActions.value = false
}

const handleDelete = () => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这张信用卡吗？删除后无法恢复。',
    confirmText: '删除',
    confirmColor: '#ff4757',
    success: (res) => {
      if (res.confirm) {
        // 调用删除API
        deleteCardMutation.mutate({
          params: {
            card_id: props.card.id,
          },
        })
      }
    },
  })
  showActions.value = false
}

const handleToggleActive = () => {
  const newStatus = props.card.isActive ? 'frozen' : 'active'

  // 调用API更新状态
  updateCardStatusMutation.mutate({
    params: {
      card_id: props.card.id,
    },
    body: {
      status: newStatus,
      reason: `用户${props.card.isActive ? '停用' : '启用'}信用卡`,
    },
  })
  showActions.value = false
}
</script>

<style lang="scss" scoped>
.card-container {
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  cursor: pointer;

  &:active {
    transform: scale(0.98);
  }
}

.grid {
  display: grid;
}

.grid-cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid-cols-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.gap-3 {
  gap: 0.75rem;
}

.gap-4 {
  gap: 1rem;
}

.space-x-2 > :not(:first-child) {
  margin-left: 0.5rem;
}

.space-y-2 > :not(:first-child) {
  margin-top: 0.5rem;
}

.space-y-3 > :not(:first-child) {
  margin-top: 0.75rem;
}

.space-y-4 > :not(:first-child) {
  margin-top: 1rem;
}

.min-h-48 {
  min-height: 12rem;
}
</style>
