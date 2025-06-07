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
    <view v-if="!notificationEnabled" class="mx-4 mt-4">
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
    <view class="mx-4 mt-4 mb-8">
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
                  <text class="text-gray-900 font-medium text-sm block mb-1">{{ notification.title }}</text>
                  <text class="text-gray-600 text-sm leading-relaxed">{{ notification.content }}</text>
                  
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

    <!-- 底部提示 -->
    <view class="px-4 pb-8">
      <text class="text-xs text-gray-400 text-center block">系统会在还款日前3天发送提醒通知</text>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'

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

// 通知开启状态
const notificationEnabled = ref(false)

// 模拟通知数据
const notifications = ref<Notification[]>([
  {
    id: '1',
    type: 'warning',
    title: '中国银行长城环球通信用卡',
    content: '使用率已达85%，建议及时还款以维持良好信用记录为已逾',
    time: '6/7 14:15',
    priority: 'high',
    isRead: false,
    actions: [
      { text: '标记为已读', type: 'secondary', action: 'mark_read' }
    ]
  },
  {
    id: '2',
    type: 'reminder',
    title: '工商银行宇宙星座信用卡',
    content: '将在3天后(12月8日)到期，请及时还款 8,500 元',
    time: '6/7 10:15',
    priority: 'medium',
    isRead: false,
    actions: [
      { text: '标记为已读', type: 'secondary', action: 'mark_read' }
    ]
  },
  {
    id: '3',
    type: 'info',
    title: '招商银行全币种国际信用卡',
    content: '年费 ¥300 将在30天后到期，请注意查看减免条件',
    time: '6/7 08:15',
    priority: 'medium',
    isRead: false,
    actions: [
      { text: '标记为已读', type: 'secondary', action: 'mark_read' }
    ]
  },
  {
    id: '4',
    type: 'success',
    title: '交通银行Y-POWER信用卡',
    content: '成功还款 3,200 元，当前余额为 0 元',
    time: '6/6 16:15',
    priority: 'low',
    isRead: true
  },
  {
    id: '5',
    type: 'info',
    title: '平安银行车主信用卡',
    content: '检测到异常消费 ¥150，已成功冻结卡片续费 ¥15.75',
    time: '6/5 16:15',
    priority: 'medium',
    isRead: false,
    actions: [
      { text: '标记为已读', type: 'secondary', action: 'mark_read' }
    ]
  },
  {
    id: '6',
    type: 'info',
    title: '工商银行宇宙星座信用卡',
    content: '积分即将过期，请及时使用',
    time: '6/2 16:16',
    priority: 'low',
    isRead: false,
    actions: [
      { text: '标记为已读', type: 'secondary', action: 'mark_read' }
    ]
  },
  {
    id: '7',
    type: 'info',
    title: '中国银行长城环球通信用卡',
    content: '账单已生成，请查看详情',
    time: '6/5 16:16',
    priority: 'low',
    isRead: false,
    actions: [
      { text: '标记为已读', type: 'secondary', action: 'mark_read' }
    ]
  },
  {
    id: '8',
    type: 'info',
    title: '民生银行女人花信用卡',
    content: '积分通知买已到账',
    time: '5/14 16:16',
    priority: 'low',
    isRead: false,
    actions: [
      { text: '标记为已读', type: 'secondary', action: 'mark_read' }
    ]
  }
])

// 计算未读数量
const unreadCount = computed(() => 
  notifications.value.filter(n => !n.isRead).length
)

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
    url: '/pages/notifications/settings'
  })
}

const handleClearAll = () => {
  uni.showModal({
    title: '确认清空',
    content: '确定要清空所有通知吗？',
    success: (res) => {
      if (res.confirm) {
        notifications.value = []
        uni.showToast({
          title: '已清空所有通知',
          icon: 'success'
        })
      }
    }
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
          icon: 'success'
        })
      }
    }
  })
}

const handleNotificationClick = (notification: Notification) => {
  console.log('Notification clicked:', notification)
  
  // 标记为已读
  if (!notification.isRead) {
    notification.isRead = true
  }
  
  // 可以根据通知类型跳转到不同页面
  switch (notification.type) {
    case 'warning':
    case 'reminder':
      uni.navigateTo({
        url: '/pages/cards/index'
      })
      break
    case 'info':
      uni.showToast({
        title: '查看通知详情',
        icon: 'none'
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
      notification.isRead = true
      uni.showToast({
        title: '已标记为已读',
        icon: 'success'
      })
      break
    default:
      break
  }
}
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