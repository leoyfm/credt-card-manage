<!-- 信用卡列表页面 -->
<route lang="json5">
{
  style: {
    navigationBarTitleText: '我的卡片',
    enablePullDownRefresh: true,
  },
}
</route>

<template>
  <view class="cards-page">
    <!-- 搜索栏 -->
    <view class="search-bar bg-white px-4 py-3 sticky top-0 z-10">
      <view class="flex items-center bg-gray-100 rounded-full px-4 py-2">
        <text class="iconfont icon-search text-gray-400 mr-2">🔍</text>
        <input
          v-model="searchKeyword"
          placeholder="搜索银行或卡片名称"
          class="flex-1 text-sm"
          @input="handleSearch"
        />
        <text v-if="searchKeyword" class="text-gray-400 ml-2" @click="clearSearch">✕</text>
      </view>
    </view>

    <!-- 筛选栏 -->
    <view class="filter-bar bg-white px-4 py-3 border-b border-gray-100">
      <view class="flex space-x-3">
        <view
          v-for="filter in filterOptions"
          :key="filter.key"
          class="filter-item px-3 py-1 rounded-full text-sm transition-all"
          :class="
            activeFilter === filter.key ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600'
          "
          @click="setFilter(filter.key)"
        >
          {{ filter.label }}
        </view>
      </view>
    </view>

    <!-- 统计信息 -->
    <view class="stats-bar bg-blue-50 px-4 py-3">
      <view class="flex justify-between text-sm">
        <text class="text-gray-600">共 {{ filteredCards.length }} 张卡片</text>
        <text class="text-blue-600">总额度 ¥{{ formatMoney(totalCreditLimit) }}</text>
      </view>
    </view>

    <!-- 卡片列表 -->
    <view class="card-list px-4 py-2">
      <view
        v-for="card in filteredCards"
        :key="card.id"
        class="card-item bg-white rounded-xl p-4 mb-4 shadow-sm"
        @click="goToCardDetail(card.id)"
      >
        <!-- 银行头部 -->
        <view class="flex items-center justify-between mb-4">
          <view class="flex items-center">
            <view
              class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold mr-3"
              :style="{ backgroundColor: card.bankColor }"
            >
              {{ card.bankCode }}
            </view>
            <view>
              <text class="font-semibold text-gray-800 text-base">{{ card.bankName }}</text>
              <view class="flex items-center mt-1">
                <text class="text-sm text-gray-600">{{ card.cardName }}</text>
                <text class="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded ml-2">
                  {{ card.cardLevel }}
                </text>
              </view>
            </view>
          </view>
          <view class="flex items-center space-x-2">
            <view
              class="edit-btn w-8 h-8 bg-blue-50 rounded-full flex items-center justify-center"
              @click.stop="editCard(card.id)"
            >
              <text class="text-blue-500 text-sm">✏️</text>
            </view>
            <view class="text-right">
              <view class="flex items-center">
                <text class="text-sm font-semibold" :class="getCardStatusClass(card.isActive)">
                  {{ card.isActive ? '正常' : '停用' }}
                </text>
                <text class="text-gray-400 ml-2">›</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 卡号信息 -->
        <view class="bg-gray-50 rounded-lg p-3 mb-4">
          <view class="flex items-center justify-between">
            <text class="text-gray-600 text-sm">卡号</text>
            <text class="text-gray-800 font-mono">**** **** **** {{ card.cardNumberLast4 }}</text>
          </view>
          <view class="flex items-center justify-between mt-2">
            <text class="text-gray-600 text-sm">有效期</text>
            <text class="text-gray-800">{{ formatDate(card.expiryDate, 'MM/YY') }}</text>
          </view>
        </view>

        <!-- 额度信息 -->
        <view class="mb-4">
          <view class="flex justify-between items-center mb-2">
            <text class="text-sm text-gray-600">信用额度</text>
            <text class="text-lg font-bold text-gray-800">
              ¥{{ formatMoney(card.creditLimit) }}
            </text>
          </view>

          <!-- 额度使用进度条 -->
          <view class="mb-2">
            <view class="bg-gray-200 rounded-full h-3 relative overflow-hidden">
              <view
                class="h-3 rounded-full transition-all duration-500"
                :class="getUsageColorClass(card.usedAmount / card.creditLimit)"
                :style="{ width: (card.usedAmount / card.creditLimit) * 100 + '%' }"
              ></view>
              <text
                class="absolute inset-0 text-xs text-white flex items-center justify-center font-medium"
              >
                {{ Math.round((card.usedAmount / card.creditLimit) * 100) }}%
              </text>
            </view>
          </view>

          <view class="flex justify-between text-sm">
            <text class="text-green-600">可用 ¥{{ formatMoney(card.availableAmount) }}</text>
            <text class="text-red-600">已用 ¥{{ formatMoney(card.usedAmount) }}</text>
          </view>
        </view>

        <!-- 还款信息 -->
        <view class="flex justify-between items-center py-2 border-t border-gray-100">
          <view class="flex-1">
            <text class="text-sm text-gray-600">账单日</text>
            <text class="text-sm text-gray-800 ml-2">每月{{ card.billingDay }}日</text>
          </view>
          <view class="flex-1">
            <text class="text-sm text-gray-600">还款日</text>
            <text class="text-sm text-gray-800 ml-2">每月{{ card.dueDay }}日</text>
          </view>
          <view class="flex-1 text-right">
            <text class="text-sm text-gray-600">下次账单</text>
            <text class="text-sm text-blue-600 ml-2">
              {{ formatDate(card.nextBillingDate, 'MM-DD') }}
            </text>
          </view>
        </view>

        <!-- 年费信息 -->
        <view class="flex items-center justify-between pt-3 border-t border-gray-100">
          <view class="flex items-center">
            <text class="text-sm text-gray-600">年费</text>
            <text class="text-sm text-gray-800 ml-2">¥{{ card.annualFee }}</text>
            <text class="text-xs ml-2" :class="getFeeStatusClass(card.annualFeeStatus)">
              {{ getFeeStatusText(card.annualFeeStatus) }}
            </text>
          </view>
          <view v-if="card.feeType !== 'rigid'" class="text-right">
            <text class="text-xs text-gray-500">{{ card.waiverCondition }}</text>
            <view class="flex items-center mt-1">
              <view class="w-16 bg-gray-200 rounded-full h-1 mr-2">
                <view
                  class="bg-blue-500 h-1 rounded-full transition-all duration-300"
                  :style="{ width: card.waiverProgress + '%' }"
                ></view>
              </view>
              <text class="text-xs text-blue-600">{{ card.waiverProgress }}%</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view v-if="filteredCards.length === 0" class="empty-state text-center py-16">
      <text class="text-4xl mb-4 block">💳</text>
      <text class="text-gray-500 text-base mb-4 block">
        {{
          searchKeyword || activeFilter !== 'all' ? '没有找到符合条件的卡片' : '还没有添加信用卡'
        }}
      </text>
      <button v-if="!searchKeyword && activeFilter === 'all'" class="btn-primary" @click="addCard">
        添加第一张信用卡
      </button>
    </view>

    <!-- 底部操作栏 -->
    <view
      class="bottom-actions fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-3 safe-area-inset-bottom"
    >
      <view class="flex space-x-3">
        <button class="btn-secondary flex-1" @click="importCards">批量导入</button>
        <button class="btn-primary flex-1" @click="addCard">添加卡片</button>
      </view>
    </view>

    <!-- 底部安全区域 -->
    <view class="h-20"></view>
  </view>
</template>

<script lang="ts" setup>
import { cardApi } from '@/service/api'
// import '@/mock' // 暂时注释掉Mock数据引用

defineOptions({
  name: 'CardsPage',
})

// 响应式数据
const cardList = ref([])
const searchKeyword = ref('')
const activeFilter = ref('all')
const loading = ref(false)

// 筛选选项
const filterOptions = [
  { key: 'all', label: '全部' },
  { key: 'active', label: '正常' },
  { key: 'inactive', label: '停用' },
  { key: 'high_limit', label: '高额度' },
  { key: 'fee_due', label: '年费待缴' },
]

// 计算属性
const filteredCards = computed(() => {
  let filtered = cardList.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(
      (card) =>
        card.bankName.toLowerCase().includes(keyword) ||
        card.cardName.toLowerCase().includes(keyword) ||
        card.cardNumberLast4.includes(keyword),
    )
  }

  // 状态过滤
  switch (activeFilter.value) {
    case 'active':
      filtered = filtered.filter((card) => card.isActive)
      break
    case 'inactive':
      filtered = filtered.filter((card) => !card.isActive)
      break
    case 'high_limit':
      filtered = filtered.filter((card) => card.creditLimit >= 100000)
      break
    case 'fee_due':
      filtered = filtered.filter((card) => card.annualFeeStatus === 'pending')
      break
  }

  return filtered
})

const totalCreditLimit = computed(() => {
  return filteredCards.value.reduce((sum, card) => sum + card.creditLimit, 0)
})

// 页面生命周期
onLoad(async () => {
  await loadCards()
})

onPullDownRefresh(async () => {
  await loadCards()
  uni.stopPullDownRefresh()
})

// 数据加载
const loadCards = async () => {
  try {
    loading.value = true
    const res = await cardApi.getCards()
    if (res.code === 200) {
      cardList.value = res.data.list
    }
  } catch (error) {
    console.error('加载卡片失败:', error)
    uni.showToast({
      title: '加载失败',
      icon: 'none',
    })
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  // 实时搜索，已通过计算属性实现
}

const clearSearch = () => {
  searchKeyword.value = ''
}

// 筛选处理
const setFilter = (filterKey: string) => {
  activeFilter.value = filterKey
}

// 工具函数
const formatMoney = (amount: number) => {
  if (!amount) return '0'
  if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return amount.toLocaleString()
}

const formatDate = (dateStr: string, format: string = 'YYYY-MM-DD') => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  if (format === 'MM/YY') {
    return `${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getFullYear()).slice(2)}`
  } else if (format === 'MM-DD') {
    return `${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  }
  return dateStr
}

const getCardStatusClass = (isActive: boolean) => {
  return isActive ? 'text-green-600' : 'text-red-600'
}

const getUsageColorClass = (ratio: number) => {
  if (ratio >= 0.9) return 'bg-red-500'
  if (ratio >= 0.7) return 'bg-orange-500'
  if (ratio >= 0.5) return 'bg-yellow-500'
  return 'bg-green-500'
}

const getFeeStatusClass = (status: string) => {
  const classes = {
    pending: 'text-orange-600 bg-orange-50',
    waived: 'text-green-600 bg-green-50',
    paid: 'text-blue-600 bg-blue-50',
    overdue: 'text-red-600 bg-red-50',
  }
  return `px-2 py-0.5 rounded text-xs ${classes[status] || 'text-gray-600 bg-gray-50'}`
}

const getFeeStatusText = (status: string) => {
  const texts = {
    pending: '待缴费',
    waived: '已减免',
    paid: '已缴费',
    overdue: '已逾期',
  }
  return texts[status] || '未知'
}

// 导航函数
const goToCardDetail = (cardId: string) => {
  uni.navigateTo({ url: `/pages/cards/detail?id=${cardId}` })
}

const addCard = () => {
  uni.navigateTo({ url: '/pages/cards/add' })
}

const importCards = () => {
  uni.showToast({
    title: '功能开发中',
    icon: 'none',
  })
}

const editCard = (cardId: string) => {
  uni.navigateTo({ url: `/pages/cards/edit?id=${cardId}` })
}
</script>

<style lang="scss">
.cards-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.filter-item {
  cursor: pointer;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.95);
  }
}

.card-item {
  transition: transform 0.2s ease;

  &:active {
    transform: scale(0.98);
  }
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.98);
  }
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 1px solid #667eea;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.98);
    background: #f8f9ff;
  }
}

.empty-state {
  margin-top: 10vh;
}
</style>
