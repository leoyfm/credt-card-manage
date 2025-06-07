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
  <view class="home-page">
    <!-- 状态栏占位 -->
    <view :style="{ height: safeAreaInsets?.top + 'px' }" class="bg-gradient-to-r from-blue-500 to-purple-600"></view>
    
    <!-- 顶部导航栏 -->
    <view class="navbar bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-3">
      <view class="flex items-center justify-between">
        <view class="flex items-center">
          <text class="text-lg font-bold">信用卡管家</text>
          <text class="text-sm ml-2 opacity-80">智能管理您的信用卡</text>
        </view>
        <view class="flex items-center space-x-3">
          <view class="relative" @click="goToNotifications">
            <text class="iconfont icon-notification text-xl"></text>
            <view v-if="notificationCount > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
              {{ notificationCount > 9 ? '9+' : notificationCount }}
            </view>
          </view>
          <text class="iconfont icon-setting text-xl" @click="goToSettings"></text>
        </view>
      </view>
    </view>

    <!-- 统计卡片 -->
    <view class="stats-section px-4 -mt-6 mb-4">
      <view class="bg-white rounded-xl shadow-lg p-4">
        <view class="flex justify-around">
          <view class="text-center">
            <text class="text-2xl font-bold text-blue-600">{{ summary.activeCards }}</text>
            <text class="text-xs text-gray-500 block mt-1">活跃卡片</text>
          </view>
          <view class="text-center">
            <text class="text-2xl font-bold text-green-600">¥{{ formatMoney(summary.totalAvailableAmount) }}</text>
            <text class="text-xs text-gray-500 block mt-1">可用额度</text>
          </view>
          <view class="text-center">
            <text class="text-2xl font-bold text-orange-600">{{ summary.freeDays }}</text>
            <text class="text-xs text-gray-500 block mt-1">免息天数</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="function-menu px-4 mb-6">
      <view class="flex justify-around bg-white rounded-xl py-4 shadow-sm">
        <view class="text-center" @click="addCard">
          <view class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <text class="iconfont icon-add text-blue-600 text-xl"></text>
          </view>
          <text class="text-xs text-gray-600">添加卡片</text>
        </view>
        <view class="text-center" @click="goToTransactions">
          <view class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <text class="iconfont icon-transaction text-green-600 text-xl"></text>
          </view>
          <text class="text-xs text-gray-600">添加消费</text>
        </view>
        <view class="text-center" @click="goToStatistics">
          <view class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <text class="iconfont icon-chart text-purple-600 text-xl"></text>
          </view>
          <text class="text-xs text-gray-600">统计分析</text>
        </view>
        <view class="text-center" @click="goToReminders">
          <view class="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <text class="iconfont icon-remind text-orange-600 text-xl"></text>
          </view>
          <text class="text-xs text-gray-600">还款提醒</text>
        </view>
      </view>
    </view>

    <!-- 信用卡列表 -->
    <view class="card-list px-4">
      <view class="flex items-center justify-between mb-4">
        <text class="text-lg font-semibold text-gray-800">我的信用卡</text>
        <text class="text-sm text-gray-500" @click="goToCardList">查看全部</text>
      </view>
      
      <view class="space-y-4">
        <view 
          v-for="card in displayCards" 
          :key="card.id" 
          class="card-item bg-white rounded-xl p-4 shadow-sm"
          @click="goToCardDetail(card.id)"
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
      </view>

      <!-- 查看更多 -->
      <view v-if="cardList.length > 3" class="text-center mt-4">
        <text class="text-sm text-blue-600" @click="goToCardList">查看全部 {{ cardList.length }} 张卡片</text>
      </view>
    </view>

    <!-- 底部安全区域 -->
    <view class="h-20"></view>
  </view>
</template>

<script lang="ts" setup>
import { cardApi, notificationApi } from '@/service/api'
import '@/service/mock' // 引入Mock数据

defineOptions({
  name: 'HomePage',
})

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

// 响应式数据
const cardList = ref([])
const summary = ref({
  activeCards: 0,
  totalAvailableAmount: 0,
  freeDays: 0
})
const notificationCount = ref(0)
const loading = ref(false)

// 计算属性
const displayCards = computed(() => cardList.value.slice(0, 3))

// 页面加载时获取数据
onLoad(async () => {
  await loadData()
})

// 下拉刷新
onPullDownRefresh(async () => {
  await loadData()
  uni.stopPullDownRefresh()
})

// 数据加载函数
const loadData = async () => {
  try {
    loading.value = true
    
    // 并行请求数据
    const [cardsRes, notificationsRes] = await Promise.all([
      cardApi.getCards(),
      notificationApi.getNotifications()
    ])

    if (cardsRes.code === 200) {
      cardList.value = cardsRes.data.list
      summary.value = cardsRes.data.summary
    }

    if (notificationsRes.code === 200) {
      notificationCount.value = notificationsRes.data.unreadCount
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    uni.showToast({
      title: '数据加载失败',
      icon: 'none'
    })
  } finally {
    loading.value = false
  }
}

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

// 导航函数
const goToCardList = () => {
  uni.navigateTo({ url: '/pages/cards/index' })
}

const goToCardDetail = (cardId: string) => {
  uni.navigateTo({ url: `/pages/cards/detail?id=${cardId}` })
}

const goToTransactions = () => {
  uni.navigateTo({ url: '/pages/transactions/index' })
}

const goToNotifications = () => {
  uni.navigateTo({ url: '/pages/notifications/index' })
}

const goToSettings = () => {
  uni.navigateTo({ url: '/pages/mine/index' })
}

const goToStatistics = () => {
  uni.navigateTo({ url: '/pages/statistics/index' })
}

const goToReminders = () => {
  uni.navigateTo({ url: '/pages/reminders/index' })
}

const addCard = () => {
  uni.navigateTo({ url: '/pages/cards/add' })
}
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
