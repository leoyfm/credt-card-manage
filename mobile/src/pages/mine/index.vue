<route lang="json5">
{
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '我的',
  },
}
</route>

<template>
  <view class="mine-page">
    <!-- 状态栏占位 -->
    <view
      :style="{ height: safeAreaInsets?.top + 'px' }"
      class="bg-gradient-to-r from-indigo-500 to-purple-600"
    ></view>

    <!-- 未登录状态 -->
    <view
      v-if="!userStore.isLoggedIn"
      class="login-prompt bg-gradient-to-r from-indigo-500 to-purple-600 text-white pb-8"
    >
      <view class="flex flex-col items-center px-4 py-8">
        <view
          class="w-20 h-20 bg-white bg-opacity-20 rounded-full flex items-center justify-center mb-4"
        >
          <text class="text-3xl">👤</text>
        </view>
        <text class="text-lg font-bold mb-2">欢迎使用信用卡管家</text>
        <text class="text-sm opacity-80 mb-6">登录后查看您的信用卡管理数据</text>
        <view class="bg-white bg-opacity-20 px-6 py-3 rounded-full" @click="goToLogin">
          <text class="text-white font-medium">立即登录</text>
        </view>
      </view>
    </view>

    <!-- 已登录状态 -->
    <view v-else>
      <!-- 用户信息头部 -->
      <view class="user-header bg-gradient-to-r from-indigo-500 to-purple-600 text-white pb-8">
        <!-- 加载状态 -->
        <view v-if="isUserInfoLoading" class="flex items-center px-4 py-3">
          <view
            class="user-avatar w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-4"
          >
            <text class="text-2xl">⏳</text>
          </view>
          <view class="flex-1">
            <text class="text-lg font-bold block">加载中...</text>
            <text class="text-sm opacity-80 block">正在获取用户信息</text>
          </view>
        </view>

        <!-- 用户信息 -->
        <view v-else class="flex items-center px-4 py-3">
          <view
            class="user-avatar w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-4"
            @click="goToProfile"
          >
            <image v-if="userInfo.avatar" :src="userInfo.avatar" class="w-14 h-14 rounded-full" />
            <text v-else class="text-2xl">👤</text>
          </view>
          <view class="flex-1">
            <text class="text-lg font-bold block">{{ userInfo.nickname || '未设置昵称' }}</text>
            <text class="text-sm opacity-80 block">{{ userInfo.phone || '未绑定手机' }}</text>
            <view class="flex items-center mt-2">
              <text class="text-xs bg-white bg-opacity-20 px-2 py-1 rounded">
                {{ getUserLevelText(userInfo.level) }}
              </text>
              <text class="text-xs opacity-70 ml-2">{{ userInfo.memberDays }}天会员</text>
            </view>
          </view>
          <view class="text-right">
            <text class="iconfont icon-edit text-xl opacity-80" @click="goToProfile">⚙️</text>
          </view>
        </view>

        <!-- 统计数据 -->
        <view class="stats-grid px-4 mt-4">
          <view class="bg-white bg-opacity-15 rounded-xl p-4">
            <!-- 加载状态 -->
            <view v-if="isStatisticsLoading" class="flex justify-center py-4">
              <text class="text-white opacity-80">统计数据加载中...</text>
            </view>
            <!-- 统计数据 -->
            <view v-else class="flex justify-around">
              <view class="text-center" @click="goToCardList">
                <text class="text-xl font-bold block">{{ statistics.totalCards }}</text>
                <text class="text-xs opacity-80">信用卡</text>
              </view>
              <view class="text-center" @click="goToTransactions">
                <text class="text-xl font-bold block">{{ statistics.totalTransactions }}</text>
                <text class="text-xs opacity-80">消费笔数</text>
              </view>
              <view class="text-center" @click="goToFees">
                <text class="text-xl font-bold block">
                  ¥{{ formatMoney(statistics.totalSavings) }}
                </text>
                <text class="text-xs opacity-80">节省费用</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 功能菜单 -->
      <view class="menu-section bg-white -mt-4 mx-4 rounded-xl shadow-lg mb-4">
        <!-- 第一组菜单 -->
        <view class="menu-group border-b border-gray-100 last:border-b-0">
          <view
            v-for="(item, index) in primaryMenus"
            :key="item.key"
            class="menu-item flex items-center px-4 py-4 transition-all"
            :class="{ 'border-t border-gray-100': index > 0 }"
            @click="handleMenuClick(item.key)"
          >
            <view
              class="menu-icon w-10 h-10 rounded-full flex items-center justify-center mr-3"
              :style="{ backgroundColor: item.bgColor }"
            >
              <text class="text-white text-lg">{{ item.icon }}</text>
            </view>
            <view class="flex-1">
              <text class="text-gray-800 font-medium">{{ item.title }}</text>
              <text v-if="item.subtitle" class="text-xs text-gray-500 block">
                {{ item.subtitle }}
              </text>
            </view>
            <view class="flex items-center">
              <text
                v-if="item.badge"
                class="text-xs bg-red-500 text-white px-2 py-0.5 rounded-full mr-2"
              >
                {{ item.badge }}
              </text>
              <text class="text-gray-400">›</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 工具菜单 -->
      <view class="menu-section bg-white mx-4 rounded-xl shadow-sm mb-4">
        <view class="menu-header px-4 py-3 border-b border-gray-100">
          <text class="text-gray-600 font-medium">实用工具</text>
        </view>
        <view class="menu-group">
          <view
            v-for="(item, index) in toolMenus"
            :key="item.key"
            class="menu-item flex items-center px-4 py-4 transition-all"
            :class="{ 'border-t border-gray-100': index > 0 }"
            @click="handleMenuClick(item.key)"
          >
            <view
              class="menu-icon w-8 h-8 rounded-lg flex items-center justify-center mr-3"
              :style="{ backgroundColor: item.bgColor }"
            >
              <text class="text-white text-sm">{{ item.icon }}</text>
            </view>
            <view class="flex-1">
              <text class="text-gray-800">{{ item.title }}</text>
            </view>
            <text class="text-gray-400 text-sm">›</text>
          </view>
        </view>
      </view>

      <!-- 设置菜单 -->
      <view class="menu-section bg-white mx-4 rounded-xl shadow-sm mb-4">
        <view class="menu-header px-4 py-3 border-b border-gray-100">
          <text class="text-gray-600 font-medium">设置</text>
        </view>
        <view class="menu-group">
          <view
            v-for="(item, index) in settingMenus"
            :key="item.key"
            class="menu-item flex items-center px-4 py-4 transition-all"
            :class="{ 'border-t border-gray-100': index > 0 }"
            @click="handleMenuClick(item.key)"
          >
            <view
              class="menu-icon w-8 h-8 rounded-lg flex items-center justify-center mr-3"
              :style="{ backgroundColor: item.bgColor }"
            >
              <text class="text-white text-sm">{{ item.icon }}</text>
            </view>
            <view class="flex-1">
              <text class="text-gray-800">{{ item.title }}</text>
            </view>
            <text class="text-gray-400 text-sm">›</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 版本信息 -->
    <view class="version-info text-center px-4 py-6">
      <text class="text-gray-400 text-sm block">信用卡管家 v1.0.0</text>
      <text class="text-gray-400 text-xs mt-1">智能管理，省心理财</text>
    </view>

    <!-- 底部安全区域 -->
    <view class="h-20"></view>
  </view>
</template>

<script lang="ts" setup>
import { useQuery } from '@tanstack/vue-query'
import { useUserStore } from '@/store/user'
import {
  getUserInfoApiV1UserProfileInfoGetQueryOptions,
  getUserStatisticsApiV1UserProfileStatisticsGetQueryOptions,
  getUnreadRemindersCountApiV1UserRemindersUnreadCountGetQueryOptions,
} from '@/service/app/v1Yonghugongneng.vuequery'
import type * as API from '@/service/app/types'

defineOptions({
  name: 'MinePage',
})

// 获取屏幕边界到安全区域距离
let safeAreaInsets: any = null
try {
  const systemInfo = uni.getSystemInfoSync()
  safeAreaInsets = systemInfo.safeAreaInsets
} catch (e) {
  console.warn('获取安全区域失败', e)
}

// 获取用户状态
const userStore = useUserStore()

// 使用Vue Query获取用户信息
const {
  data: userInfoResponse,
  isLoading: isUserInfoLoading,
  isError: isUserInfoError,
  refetch: refetchUserInfo,
} = useQuery({
  ...getUserInfoApiV1UserProfileInfoGetQueryOptions({}),
  enabled: computed(() => userStore.isLoggedIn),
})

// 使用Vue Query获取用户统计数据
const {
  data: statisticsResponse,
  isLoading: isStatisticsLoading,
  isError: isStatisticsError,
  refetch: refetchStatistics,
} = useQuery({
  ...getUserStatisticsApiV1UserProfileStatisticsGetQueryOptions({}),
  enabled: computed(() => userStore.isLoggedIn),
})

// 使用Vue Query获取未读通知数量
const {
  data: unreadCountResponse,
  isLoading: isUnreadCountLoading,
  isError: isUnreadCountError,
  refetch: refetchUnreadCount,
} = useQuery({
  ...getUnreadRemindersCountApiV1UserRemindersUnreadCountGetQueryOptions({}),
  enabled: computed(() => userStore.isLoggedIn),
})

// 监听用户登录状态变化，登录成功后自动刷新数据
watch(
  () => userStore.isLoggedIn,
  (newValue, oldValue) => {
    console.log('用户登录状态变化:', { oldValue, newValue })
    if (newValue && !oldValue) {
      // 从未登录变为已登录，刷新数据
      console.log('用户登录成功，刷新个人中心数据')
      setTimeout(() => {
        refetchUserInfo()
        refetchStatistics()
        refetchUnreadCount()
      }, 100) // 稍微延迟确保token已设置
    }
  },
  { immediate: false },
)

// 计算属性 - 用户信息
const userInfo = computed(() => {
  console.log('userInfoResponse:', userInfoResponse.value)

  if (!userInfoResponse.value) {
    return {
      nickname: '信用卡用户',
      phone: '',
      avatar: '',
      level: 'gold',
      memberDays: 365,
    }
  }

  // 智能处理API响应数据结构
  let userData: any = userInfoResponse.value
  if (userData.data) {
    userData = userData.data
  }

  return {
    nickname: userData.nickname || userData.display_name || '信用卡用户',
    phone: userData.phone || userData.mobile || '',
    avatar: userData.avatar || userData.avatar_url || '',
    level: userData.level || userData.user_level || 'gold',
    memberDays: userData.member_days || userData.memberDays || 365,
  }
})

// 计算属性 - 统计数据
const statistics = computed(() => {
  console.log('statisticsResponse:', statisticsResponse.value)

  if (!statisticsResponse.value) {
    return {
      totalCards: 0,
      totalTransactions: 0,
      totalSavings: 0,
    }
  }

  // 智能处理API响应数据结构
  let statsData: any = statisticsResponse.value
  if (statsData.data) {
    statsData = statsData.data
  }

  return {
    totalCards: statsData.total_cards || statsData.totalCards || 0,
    totalTransactions: statsData.total_transactions || statsData.totalTransactions || 0,
    totalSavings: statsData.total_savings || statsData.totalSavings || 0,
  }
})

// 计算属性 - 未读通知数量
const notificationCount = computed(() => {
  console.log('unreadCountResponse:', unreadCountResponse.value)

  if (!unreadCountResponse.value) {
    return 0
  }

  // 智能处理API响应数据结构
  let countData: any = unreadCountResponse.value
  if (countData.data) {
    countData = countData.data
  }

  return countData.total_unread || countData.totalUnread || countData.unreadCount || 0
})

// 页面生命周期
onLoad(async () => {
  console.log('个人中心页面加载，用户登录状态:', userStore.isLoggedIn)
  // Vue Query会自动处理数据加载，这里不需要手动调用
})

onShow(() => {
  console.log('个人中心页面显示，刷新未读通知数量')
  // 每次显示页面时刷新通知数量
  if (userStore.isLoggedIn) {
    refetchUnreadCount()
  }
})

// 菜单配置
const primaryMenus = computed(() => [
  {
    key: 'notifications',
    title: '消息通知',
    subtitle: '账单提醒、还款通知',
    icon: '🔔',
    bgColor: '#FF6B6B',
    badge: notificationCount.value > 0 ? notificationCount.value : null,
  },
  {
    key: 'payment-reminders',
    title: '还款提醒',
    subtitle: '智能提醒，不错过还款日',
    icon: '⏰',
    bgColor: '#4ECDC4',
    badge: null,
  },
  {
    key: 'bill-analysis',
    title: '账单分析',
    subtitle: '消费趋势，理财建议',
    icon: '📊',
    bgColor: '#45B7D1',
    badge: null,
  },
  {
    key: 'security-center',
    title: '安全中心',
    subtitle: '账户保护，隐私设置',
    icon: '🛡️',
    bgColor: '#96CEB4',
    badge: null,
  },
])

const toolMenus = [
  { key: 'rate-calculator', title: '费率计算器', icon: '🧮', bgColor: '#FECA57' },
  { key: 'installment-calculator', title: '分期计算器', icon: '💰', bgColor: '#FF9FF3' },
  { key: 'optimal-card', title: '最优卡片推荐', icon: '🎯', bgColor: '#54A0FF' },
  { key: 'data-export', title: '数据导出', icon: '📤', bgColor: '#5F27CD' },
]

const settingMenus = [
  { key: 'account-settings', title: '账户设置', icon: '👤', bgColor: '#778CA3' },
  { key: 'privacy-settings', title: '隐私设置', icon: '🔒', bgColor: '#4B6584' },
  { key: 'notification-settings', title: '通知设置', icon: '🔔', bgColor: '#A4B0BE' },
  { key: 'data-backup', title: '数据备份', icon: '☁️', bgColor: '#57606F' },
  { key: 'feedback', title: '意见反馈', icon: '💬', bgColor: '#2F3542' },
  { key: 'about', title: '关于我们', icon: 'ℹ️', bgColor: '#40407A' },
]

// 工具函数
const formatMoney = (amount: number) => {
  if (!amount) return '0'
  if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return amount.toLocaleString()
}

const getUserLevelText = (level: string) => {
  const levels = {
    bronze: '铜牌会员',
    silver: '银牌会员',
    gold: '金牌会员',
    platinum: '白金会员',
    diamond: '钻石会员',
  }
  return levels[level] || '普通会员'
}

// 菜单点击处理
const handleMenuClick = (key: string) => {
  switch (key) {
    case 'notifications':
      uni.navigateTo({ url: '/pages/notifications/index' })
      break
    case 'payment-reminders':
      uni.navigateTo({ url: '/pages/reminders/index' })
      break
    case 'bill-analysis':
      uni.navigateTo({ url: '/pages/analysis/index' })
      break
    case 'security-center':
      uni.navigateTo({ url: '/pages/security/index' })
      break
    case 'rate-calculator':
      uni.navigateTo({ url: '/pages/tools/rate-calculator' })
      break
    case 'installment-calculator':
      uni.navigateTo({ url: '/pages/tools/installment-calculator' })
      break
    case 'optimal-card':
      uni.navigateTo({ url: '/pages/tools/optimal-card' })
      break
    case 'data-export':
      uni.navigateTo({ url: '/pages/tools/data-export' })
      break
    case 'account-settings':
      uni.navigateTo({ url: '/pages/mine/profile' })
      break
    case 'privacy-settings':
      uni.navigateTo({ url: '/pages/mine/privacy' })
      break
    case 'notification-settings':
      uni.navigateTo({ url: '/pages/mine/notification-settings' })
      break
    case 'data-backup':
      uni.navigateTo({ url: '/pages/mine/backup' })
      break
    case 'feedback':
      uni.navigateTo({ url: '/pages/mine/feedback' })
      break
    case 'about':
      uni.navigateTo({ url: '/pages/mine/about' })
      break
    default:
      uni.showToast({
        title: '功能开发中',
        icon: 'none',
      })
  }
}

// 导航函数
const goToLogin = () => {
  uni.navigateTo({ url: '/pages/auth/login' })
}

const goToProfile = () => {
  uni.navigateTo({ url: '/pages/mine/profile' })
}

const goToCardList = () => {
  uni.switchTab({ url: '/pages/cards/index' })
}

const goToTransactions = () => {
  uni.switchTab({ url: '/pages/transactions/index' })
}

const goToFees = () => {
  uni.switchTab({ url: '/pages/fees/index' })
}
</script>

<style lang="scss">
.mine-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.user-avatar {
  cursor: pointer;
  transition: transform 0.2s ease;

  &:active {
    transform: scale(0.95);
  }
}

.menu-item {
  cursor: pointer;

  &:active {
    background: #f8f9fa;
  }
}

.stats-grid {
  cursor: pointer;

  &:active {
    transform: scale(0.98);
  }
}

// 渐变背景兼容性
.bg-gradient-to-r {
  background: linear-gradient(to right, var(--tw-gradient-stops, #6366f1, #8b5cf6));
}

.from-indigo-500 {
  --tw-gradient-from: #6366f1;
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgba(99, 102, 241, 0));
}

.to-purple-600 {
  --tw-gradient-to: #9333ea;
}
</style>
