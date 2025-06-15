<route lang="json5" type="page">
{
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '通知中心',
  },
}
</route>

<template>
  <view class="notification-center bg-gray-50 min-h-screen">
    <!-- 顶部导航栏 -->
    <view class="top-nav bg-white border-b border-gray-100">
      <view class="px-4 py-4 flex items-center justify-between">
        <text class="text-lg font-semibold text-gray-900">通知中心</text>
        <view class="p-2" @click="handleClose">
          <text class="text-gray-600">关闭</text>
        </view>
      </view>
    </view>

    <!-- 未登录状态 -->
    <view
      v-if="!userStore.isLoggedIn"
      class="login-prompt bg-white mx-4 mt-4 rounded-lg p-8 text-center"
    >
      <view
        class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4"
      >
        <text class="text-3xl">🔔</text>
      </view>
      <text class="text-lg font-bold mb-2 block text-gray-800">通知中心需要登录</text>
      <text class="text-sm text-gray-600 mb-6 block">登录后查看您的提醒和通知</text>
      <view class="bg-blue-500 px-6 py-3 rounded-full inline-block" @click="goToLogin">
        <text class="text-white font-medium">立即登录</text>
      </view>
    </view>

    <!-- 已登录状态 -->
    <template v-else>
      <!-- 通知中心标题区域 -->
      <view class="notification-header bg-white mx-4 mt-4 rounded-lg">
        <view class="px-4 py-3 flex items-center justify-between">
          <view class="flex items-center">
            <text class="text-lg">🔔</text>
            <text class="ml-2 font-medium text-gray-800">通知中心</text>
            <view
              v-if="unreadCount > 0"
              class="ml-2 px-2 py-1 bg-red-500 rounded-full min-w-[20px] h-5 flex items-center justify-center"
            >
              <text class="text-white text-xs font-medium">{{ unreadCount }}</text>
            </view>
          </view>
          <view class="flex items-center gap-4">
            <view class="flex items-center" @click="handleSettings">
              <text class="text-lg mr-1">⚙️</text>
              <text class="text-gray-600">设置</text>
            </view>
            <view class="flex items-center" @click="handleClearAll">
              <text class="text-lg mr-1">🗑️</text>
              <text class="text-gray-600">清空</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 开启通知提示 -->
      <view v-if="!notificationEnabled && !loading && !isRemindersError" class="mx-4 mt-4">
        <view class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <view class="flex items-start">
            <text class="text-yellow-500 text-lg mr-2">⚠️</text>
            <view class="flex-1">
              <text class="text-yellow-800 text-sm">您尚未开启通知权限，将无法收到还款提醒</text>
              <view class="mt-3">
                <view
                  class="bg-gray-800 px-4 py-2 rounded-md inline-block"
                  @click="handleEnableNotification"
                >
                  <text class="text-white text-sm font-medium">开启通知</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 通知列表 -->
      <view v-if="!loading && !isRemindersError && notifications.length > 0" class="mx-4 mt-4 mb-8">
        <view class="bg-white rounded-lg overflow-hidden">
          <view
            v-for="(notification, index) in notifications"
            :key="notification.id"
            class="notification-item border-b border-gray-100 last:border-b-0"
            @click="handleNotificationClick(notification)"
          >
            <view class="px-4 py-4 flex items-start">
              <!-- 左侧图标 -->
              <view class="flex-shrink-0 mr-3 mt-1">
                <view
                  :class="getIconClass(notification.type)"
                  class="w-6 h-6 rounded-full flex items-center justify-center"
                >
                  <text class="text-sm">{{ getIconText(notification.type) }}</text>
                </view>
              </view>

              <!-- 通知内容 -->
              <view class="flex-1 min-w-0">
                <view class="flex items-start justify-between">
                  <view class="flex-1">
                    <text class="text-gray-900 font-medium text-sm block mb-1">
                      {{ notification.title }}
                    </text>
                    <text class="text-gray-600 text-sm leading-relaxed">
                      {{ notification.content }}
                    </text>

                    <!-- 操作按钮 -->
                    <view v-if="notification.actions && notification.actions.length" class="mt-2">
                      <view
                        v-for="action in notification.actions"
                        :key="action.text"
                        class="inline-block mr-2 px-3 py-1 bg-gray-100 rounded text-xs text-gray-700"
                        @click.stop="handleActionClick(action, notification)"
                      >
                        <text>{{ action.text }}</text>
                      </view>
                    </view>
                  </view>

                  <!-- 右侧时间和优先级 -->
                  <view class="flex-shrink-0 ml-3 flex items-center">
                    <view class="text-right">
                      <text class="text-xs text-gray-400 block">{{ notification.time }}</text>
                      <!-- 优先级指示器 -->
                      <view
                        v-if="notification.priority === 'high'"
                        class="w-1 h-8 bg-red-400 rounded-full mt-1 ml-auto"
                      ></view>
                      <view
                        v-else-if="notification.priority === 'medium'"
                        class="w-1 h-6 bg-orange-400 rounded-full mt-1 ml-auto"
                      ></view>
                      <view
                        v-else-if="notification.priority === 'low'"
                        class="w-1 h-4 bg-gray-400 rounded-full mt-1 ml-auto"
                      ></view>
                    </view>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 加载状态 -->
      <view v-if="loading" class="mx-4 mt-4">
        <view class="bg-white rounded-lg p-4">
          <view class="flex items-center justify-center py-8">
            <text class="text-gray-500">加载中...</text>
          </view>
        </view>
      </view>

      <!-- 错误状态 -->
      <view v-else-if="isRemindersError || isUnreadCountError" class="mx-4 mt-4">
        <view class="bg-white rounded-lg p-4 text-center">
          <text class="text-lg mb-2 block">😕</text>
          <text class="text-gray-500 text-sm mb-4 block">加载失败，请重试</text>
          <view class="bg-blue-500 px-4 py-2 rounded-md inline-block" @click="handleRetry">
            <text class="text-white text-sm font-medium">重新加载</text>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view v-else-if="notifications.length === 0" class="mx-4 mt-4">
        <view class="bg-white rounded-lg p-8 text-center">
          <text class="text-4xl mb-4 block">🔕</text>
          <text class="text-gray-500 text-base mb-2 block">暂无通知</text>
          <text class="text-gray-400 text-sm">您的通知将在这里显示</text>
        </view>
      </view>

      <!-- 底部提示 -->
      <view v-else class="px-4 pb-8">
        <text class="text-xs text-gray-400 text-center block">系统会在还款日前3天发送提醒通知</text>
      </view>
    </template>
  </view>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { useQuery, useMutation } from '@tanstack/vue-query'
import { useUserStore } from '@/store/user'
import {
  getReminderRecordsApiV1UserRemindersRecordsGetQueryOptions,
  getUnreadRemindersCountApiV1UserRemindersUnreadCountGetQueryOptions,
  useMarkReminderAsReadApiV1UserRemindersRecordsRecordIdReadPostMutation,
  useMarkAllRemindersAsReadApiV1UserRemindersMarkAllReadPostMutation,
} from '@/service/app/v1Yonghugongneng.vuequery'
import type * as API from '@/service/app/types'

interface NotificationAction {
  text: string
  type: 'primary' | 'secondary'
  action: string
}

interface Notification {
  id: string
  type: 'warning' | 'reminder' | 'info' | 'success'
  title: string
  content: string
  time: string
  priority: 'high' | 'medium' | 'low'
  isRead: boolean
  actions?: NotificationAction[]
}

// 获取用户状态
const userStore = useUserStore()

// 通知开启状态
const notificationEnabled = ref(true)

// 使用Vue Query获取提醒记录列表
const {
  data: remindersResponse,
  isLoading: isRemindersLoading,
  isError: isRemindersError,
  refetch: refetchReminders,
} = useQuery({
  ...getReminderRecordsApiV1UserRemindersRecordsGetQueryOptions({
    params: {
      page: 1,
      page_size: 50, // 获取最近50条提醒
    },
    options: undefined,
  }),
  enabled: computed(() => userStore.isLoggedIn),
})

// 使用Vue Query获取未读提醒数量
const {
  data: unreadCountResponse,
  isLoading: isUnreadCountLoading,
  isError: isUnreadCountError,
  refetch: refetchUnreadCount,
} = useQuery({
  ...getUnreadRemindersCountApiV1UserRemindersUnreadCountGetQueryOptions({
    options: undefined,
  }),
  enabled: computed(() => userStore.isLoggedIn),
})

// 标记单个提醒为已读
const markAsReadMutation = useMarkReminderAsReadApiV1UserRemindersRecordsRecordIdReadPostMutation({
  onSuccess: () => {
    uni.showToast({
      title: '已标记为已读',
      icon: 'success',
    })
    // 刷新数据
    refetchReminders()
    refetchUnreadCount()
  },
  onError: (error) => {
    console.error('标记已读失败:', error)
    uni.showToast({
      title: '操作失败',
      icon: 'error',
    })
  },
})

// 标记所有提醒为已读
const markAllAsReadMutation = useMarkAllRemindersAsReadApiV1UserRemindersMarkAllReadPostMutation({
  onSuccess: (data) => {
    const markedCount = data?.data?.marked_count || 0
    uni.showToast({
      title: `已标记${markedCount}条为已读`,
      icon: 'success',
    })
    // 刷新数据
    refetchReminders()
    refetchUnreadCount()
  },
  onError: (error) => {
    console.error('批量标记已读失败:', error)
    uni.showToast({
      title: '操作失败',
      icon: 'error',
    })
  },
})

// 智能处理API响应数据
const reminderRecords = computed(() => {
  const rawData = remindersResponse.value
  if (!rawData) return []

  // 智能解包API响应
  const data = rawData.data || rawData
  return Array.isArray(data) ? data : []
})

// 获取未读数量
const unreadCount = computed(() => {
  const rawData = unreadCountResponse.value
  if (!rawData) return 0

  // 智能解包API响应
  const data = rawData.data || rawData
  // @ts-ignore - API类型定义问题
  return data?.total_unread || 0
})

// 转换API数据为前端格式
const notifications = computed<Notification[]>(() => {
  return reminderRecords.value.map((record: any) => {
    // 根据提醒类型确定通知类型和优先级
    const getNotificationType = (reminderType: string) => {
      switch (reminderType) {
        case 'payment':
          return { type: 'warning' as const, priority: 'high' as const }
        case 'annual_fee':
          return { type: 'reminder' as const, priority: 'medium' as const }
        case 'card_expiry':
          return { type: 'warning' as const, priority: 'high' as const }
        default:
          return { type: 'info' as const, priority: 'low' as const }
      }
    }

    const { type, priority } = getNotificationType(record.reminder_type || 'info')

    // 格式化时间
    const formatTime = (dateStr: string) => {
      try {
        const date = new Date(dateStr)
        const now = new Date()
        const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))

        if (diffDays === 0) {
          return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
        } else if (diffDays < 7) {
          return `${diffDays}天前`
        } else {
          return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' })
        }
      } catch {
        return '刚刚'
      }
    }

    return {
      id: record.id || Math.random().toString(),
      type,
      title: record.title || '系统提醒',
      content: record.content || '暂无内容',
      time: formatTime(record.created_at || record.scheduled_at || new Date().toISOString()),
      priority,
      isRead: record.status === 'read',
      actions:
        record.status !== 'read'
          ? [{ text: '标记为已读', type: 'secondary' as const, action: 'mark_read' }]
          : undefined,
    }
  })
})

// 加载状态
const loading = computed(() => isRemindersLoading.value || isUnreadCountLoading.value)

// 获取图标样式类
const getIconClass = (type: string) => {
  switch (type) {
    case 'warning':
      return 'bg-red-100'
    case 'reminder':
      return 'bg-orange-100'
    case 'info':
      return 'bg-blue-100'
    case 'success':
      return 'bg-green-100'
    default:
      return 'bg-gray-100'
  }
}

// 获取图标文本
const getIconText = (type: string) => {
  switch (type) {
    case 'warning':
      return '⚠️'
    case 'reminder':
      return '📅'
    case 'info':
      return '🔔'
    case 'success':
      return '✅'
    default:
      return '📋'
  }
}

// 事件处理
const handleClose = () => {
  uni.navigateBack()
}

const handleSettings = () => {
  uni.navigateTo({
    url: '/pages/notifications/settings',
  })
}

const handleClearAll = () => {
  if (unreadCount.value === 0) {
    uni.showToast({
      title: '暂无未读通知',
      icon: 'none',
    })
    return
  }

  uni.showModal({
    title: '确认操作',
    content: `确定要将所有${unreadCount.value}条未读通知标记为已读吗？`,
    success: (res) => {
      if (res.confirm) {
        markAllAsReadMutation.mutate({
          options: undefined,
        })
      }
    },
  })
}

const handleEnableNotification = () => {
  uni.showModal({
    title: '开启通知',
    content: '是否前往设置开启通知权限？',
    success: (res) => {
      if (res.confirm) {
        notificationEnabled.value = true
        uni.showToast({
          title: '通知权限已开启',
          icon: 'success',
        })
      }
    },
  })
}

const handleNotificationClick = (notification: Notification) => {
  console.log('Notification clicked:', notification)

  // 如果未读，标记为已读
  if (!notification.isRead) {
    markAsReadMutation.mutate({
      params: { record_id: notification.id },
      options: undefined,
    })
  }

  // 可以根据通知类型跳转到不同页面
  switch (notification.type) {
    case 'warning':
    case 'reminder':
      uni.switchTab({
        url: '/pages/cards/index',
      })
      break
    case 'info':
      uni.showToast({
        title: '查看通知详情',
        icon: 'none',
      })
      break
    default:
      break
  }
}

const handleActionClick = (action: NotificationAction, notification: Notification) => {
  console.log('Action clicked:', action, notification)

  switch (action.action) {
    case 'mark_read':
      markAsReadMutation.mutate({
        params: { record_id: notification.id },
        options: undefined,
      })
      break
    default:
      break
  }
}

const handleRetry = async () => {
  await Promise.all([refetchReminders(), refetchUnreadCount()])
}

const goToLogin = () => {
  uni.navigateTo({ url: '/pages/auth/login' })
}

// 页面生命周期
onMounted(() => {
  if (userStore.isLoggedIn) {
    refetchReminders()
    refetchUnreadCount()
  }
})

// 使用uni-app的onShow生命周期
uni.addInterceptor('navigateBack', {
  success() {
    if (userStore.isLoggedIn) {
      refetchUnreadCount()
    }
  },
})
</script>

<style lang="scss" scoped>
.notification-center {
  padding-top: env(safe-area-inset-top);
}

.top-nav {
  padding-top: env(safe-area-inset-top);
}

.notification-item {
  transition: background-color 0.2s ease;

  &:active {
    background-color: #f9fafb;
  }
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

.min-w-0 {
  min-width: 0;
}

.leading-relaxed {
  line-height: 1.625;
}

@media (max-width: 640px) {
  .px-4 {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .py-4 {
    padding-top: 1rem;
    padding-bottom: 1rem;
  }

  .mx-4 {
    margin-left: 1rem;
    margin-right: 1rem;
  }

  .mt-4 {
    margin-top: 1rem;
  }
}
</style>
