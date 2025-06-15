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
          <view class="relative p-2 bg-gray-100 rounded-lg" @click="handleNotificationClick">
            <text class="text-lg">🔔</text>
            <view
              v-if="unreadNotifications > 0"
              class="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center"
            >
              <text class="text-white text-xs">
                {{ unreadNotifications > 9 ? '9+' : unreadNotifications }}
              </text>
            </view>
          </view>
          <!-- 设置按钮 -->
          <view class="p-2 bg-gray-100 rounded-lg" @click="handleSettingsClick">
            <text class="text-lg">⚙️</text>
          </view>
        </view>
      </view>

      <!-- 未登录状态 -->
      <view v-if="!userStore.isLoggedIn" class="grid grid-cols-3 gap-3 mb-4">
        <view class="text-center">
          <text class="text-lg font-bold text-gray-400 block">--</text>
          <text class="text-xs text-gray-500">活跃卡片</text>
        </view>
        <view class="text-center">
          <text class="text-lg font-bold text-gray-400 block">--</text>
          <text class="text-xs text-gray-500">可用额度</text>
        </view>
        <view class="text-center">
          <text class="text-lg font-bold text-gray-400 block">--</text>
          <text class="text-xs text-gray-500">免息天数</text>
        </view>
      </view>

      <!-- 已登录 - 快速统计 -->
      <view v-else-if="!isLoading && summary" class="grid grid-cols-3 gap-3 mb-4">
        <view class="text-center">
          <text class="text-lg font-bold text-blue-600 block">{{ summary.active_cards }}</text>
          <text class="text-xs text-gray-500">活跃卡片</text>
        </view>
        <view class="text-center">
          <text class="text-lg font-bold text-green-600 block">
            {{ formatMoney(summary.total_available_limit) }}
          </text>
          <text class="text-xs text-gray-500">可用额度</text>
        </view>
        <view class="text-center">
          <text class="text-lg font-bold text-orange-600 block">
            {{ summary.max_interest_free_days }}
          </text>
          <text class="text-xs text-gray-500">免息天数</text>
        </view>
      </view>

      <!-- 已登录 - 加载状态 -->
      <view v-else-if="userStore.isLoggedIn && isLoading" class="grid grid-cols-3 gap-3 mb-4">
        <view class="text-center">
          <text class="text-lg font-bold text-gray-400 block">--</text>
          <text class="text-xs text-gray-500">活跃卡片</text>
        </view>
        <view class="text-center">
          <text class="text-lg font-bold text-gray-400 block">--</text>
          <text class="text-xs text-gray-500">可用额度</text>
        </view>
        <view class="text-center">
          <text class="text-lg font-bold text-gray-400 block">--</text>
          <text class="text-xs text-gray-500">免息天数</text>
        </view>
      </view>

      <!-- 已登录 - 错误状态 -->
      <view v-else-if="userStore.isLoggedIn && isError && !isLoading" class="text-center py-4">
        <text class="text-sm text-gray-500">数据加载失败，请稍后重试</text>
      </view>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useUserStore } from '@/store/user'
import {
  getCardSummaryApiV1UserCardsSummaryOverviewGetQueryOptions,
  getUnreadRemindersCountApiV1UserRemindersUnreadCountGetQueryOptions,
} from '@/service/app/v1Yonghugongneng.vuequery'
import type * as API from '@/service/app/types'

// 移除props，组件自己获取数据

// 获取用户状态
const userStore = useUserStore()

// 使用Vue Query获取卡片摘要数据 - 只有在已登录时才启用
const {
  data: summaryResponse,
  isLoading,
  isError,
  refetch,
} = useQuery({
  ...getCardSummaryApiV1UserCardsSummaryOverviewGetQueryOptions({}),
  enabled: computed(() => userStore.isLoggedIn), // 只有在已登录时才启用查询
})

// 使用Vue Query获取未读提醒数量 - 只有在已登录时才启用
const {
  data: unreadCountResponse,
  isLoading: isUnreadCountLoading,
  isError: isUnreadCountError,
  refetch: refetchUnreadCount,
} = useQuery({
  ...getUnreadRemindersCountApiV1UserRemindersUnreadCountGetQueryOptions({}),
  enabled: computed(() => userStore.isLoggedIn), // 只有在已登录时才启用查询
})

// 监听用户登录状态变化，登录成功后自动刷新数据
watch(
  () => userStore.isLoggedIn,
  (newValue, oldValue) => {
    console.log('用户登录状态变化:', { oldValue, newValue })
    if (newValue && !oldValue) {
      // 从未登录变为已登录，刷新数据
      console.log('用户登录成功，刷新HeaderSection数据')
      setTimeout(() => {
        refetch()
        refetchUnreadCount()
      }, 100) // 稍微延迟确保token已设置
    }
  },
  { immediate: false },
)

// 计算属性 - 从API响应中提取摘要数据
const summary = computed(() => {
  console.log('summaryResponse', summaryResponse.value)

  return summaryResponse.value as any
})

// 计算属性 - 从API响应中提取未读通知数量
const unreadNotifications = computed(() => {
  console.log('unreadCountResponse', unreadCountResponse.value)
  if (!unreadCountResponse.value) {
    return 0
  }
  // 由于request.ts已经解包数据，直接访问total_unread字段
  return (unreadCountResponse.value as any)?.total_unread || 0
})

// 工具函数
const formatMoney = (amount: number) => {
  if (!amount || amount === 0) return '0.00'
  if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return amount.toLocaleString('zh-CN', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  })
}

// 事件处理
const handleNotificationClick = () => {
  console.log('Notification clicked')
  // 跳转到通知中心页面
  uni.navigateTo({
    url: '/pages/notifications/index',
  })
}

const handleSettingsClick = () => {
  console.log('Settings clicked')
  // 跳转到通知设置页面
  uni.navigateTo({
    url: '/pages/notifications/settings',
  })
}

// 暴露刷新方法供父组件调用
defineExpose({
  refetch,
  refetchUnreadCount,
})
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
