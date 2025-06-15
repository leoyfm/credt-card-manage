<template>
  <view class="transaction-detail-page">
    <!-- 导航栏 -->
    <view class="navbar bg-white border-b border-gray-200 px-4 py-3">
      <view class="flex items-center justify-between">
        <view class="flex items-center">
          <text class="text-2xl mr-3" @click="goBack">‹</text>
          <text class="text-lg font-semibold text-gray-800">交易详情</text>
        </view>
        <view class="flex items-center space-x-3">
          <text class="text-blue-600 text-base" @click="editTransaction">编辑</text>
          <text class="text-red-600 text-base" @click="deleteTransaction">删除</text>
        </view>
      </view>
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading-container flex items-center justify-center py-20">
      <view class="text-center">
        <view class="loading-spinner mb-3"></view>
        <text class="text-gray-500">加载中...</text>
      </view>
    </view>

    <!-- 错误状态 -->
    <view v-else-if="error" class="error-container text-center py-20 px-4">
      <text class="text-4xl mb-4 block">😕</text>
      <text class="text-gray-500 text-base mb-4 block">加载失败</text>
      <button class="btn-primary" @click="loadTransactionDetail">重试</button>
    </view>

    <!-- 交易详情内容 -->
    <view v-else-if="transaction" class="detail-content">
      <!-- 交易金额卡片 -->
      <view
        class="amount-card bg-gradient-to-r from-blue-500 to-purple-600 mx-4 mt-4 rounded-xl p-6 text-white"
      >
        <view class="text-center">
          <text class="text-sm opacity-90 block mb-2">交易金额</text>
          <text class="text-3xl font-bold block mb-2">
            {{ transaction.transactionType === '退款' ? '+' : '-' }}¥{{
              formatMoney(transaction.amount)
            }}
          </text>
          <text class="text-sm opacity-90">{{ transaction.merchantName }}</text>
        </view>
      </view>

      <!-- 基本信息 -->
      <view class="info-section bg-white mx-4 mt-4 rounded-lg shadow-sm">
        <view class="section-header px-4 py-3 border-b border-gray-100">
          <text class="text-base font-semibold text-gray-800">基本信息</text>
        </view>

        <view class="info-list">
          <view
            class="info-item flex items-center justify-between px-4 py-3 border-b border-gray-50"
          >
            <view class="flex items-center">
              <view
                class="icon-container w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mr-3"
              >
                <text class="text-blue-600 text-sm">🏪</text>
              </view>
              <text class="text-gray-600">商户名称</text>
            </view>
            <text class="text-gray-900 font-medium">{{ transaction.merchantName }}</text>
          </view>

          <view
            class="info-item flex items-center justify-between px-4 py-3 border-b border-gray-50"
          >
            <view class="flex items-center">
              <view
                class="icon-container w-8 h-8 rounded-full bg-green-100 flex items-center justify-center mr-3"
              >
                <text class="text-green-600 text-sm">📂</text>
              </view>
              <text class="text-gray-600">交易分类</text>
            </view>
            <view class="flex items-center">
              <view
                class="category-dot w-3 h-3 rounded-full mr-2"
                :style="{ backgroundColor: getCategoryColor(transaction.category) }"
              ></view>
              <text class="text-gray-900 font-medium">{{ transaction.category }}</text>
            </view>
          </view>

          <view
            class="info-item flex items-center justify-between px-4 py-3 border-b border-gray-50"
          >
            <view class="flex items-center">
              <view
                class="icon-container w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center mr-3"
              >
                <text class="text-orange-600 text-sm">🔄</text>
              </view>
              <text class="text-gray-600">交易类型</text>
            </view>
            <view class="px-2 py-1 rounded" :class="getTypeClass(transaction.transactionType)">
              <text class="text-xs font-medium">{{ transaction.transactionType }}</text>
            </view>
          </view>

          <view
            class="info-item flex items-center justify-between px-4 py-3 border-b border-gray-50"
          >
            <view class="flex items-center">
              <view
                class="icon-container w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center mr-3"
              >
                <text class="text-purple-600 text-sm">📅</text>
              </view>
              <text class="text-gray-600">交易时间</text>
            </view>
            <view class="text-right">
              <text class="text-gray-900 font-medium block">
                {{ formatDate(transaction.transactionDate) }}
              </text>
              <text class="text-gray-500 text-sm">
                {{ formatTime(transaction.transactionDate) }}
              </text>
            </view>
          </view>

          <view
            v-if="transaction.installment > 0"
            class="info-item flex items-center justify-between px-4 py-3 border-b border-gray-50"
          >
            <view class="flex items-center">
              <view
                class="icon-container w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center mr-3"
              >
                <text class="text-yellow-600 text-sm">📊</text>
              </view>
              <text class="text-gray-600">分期信息</text>
            </view>
            <text class="text-gray-900 font-medium">{{ transaction.installment }}期分期</text>
          </view>

          <view class="info-item flex items-center justify-between px-4 py-3">
            <view class="flex items-center">
              <view
                class="icon-container w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center mr-3"
              >
                <text class="text-indigo-600 text-sm">💳</text>
              </view>
              <text class="text-gray-600">关联信用卡</text>
            </view>
            <text class="text-gray-900 font-medium">
              {{ transaction.cardName }}-{{ transaction.cardNumber.slice(-4) }}
            </text>
          </view>
        </view>
      </view>

      <!-- 备注信息 -->
      <view
        v-if="transaction.description"
        class="info-section bg-white mx-4 mt-4 rounded-lg shadow-sm"
      >
        <view class="section-header px-4 py-3 border-b border-gray-100">
          <text class="text-base font-semibold text-gray-800">备注信息</text>
        </view>
        <view class="px-4 py-3">
          <text class="text-gray-700 leading-relaxed">{{ transaction.description }}</text>
        </view>
      </view>

      <!-- 操作按钮 -->
      <view class="action-buttons mx-4 mt-6 mb-8">
        <view class="flex space-x-3">
          <button class="btn-secondary flex-1" @click="editTransaction">
            <text class="mr-2">✏️</text>
            编辑交易
          </button>
          <button class="btn-danger flex-1" @click="confirmDelete">
            <text class="mr-2">🗑️</text>
            删除交易
          </button>
        </view>
      </view>
    </view>

    <!-- 底部安全区域 -->
    <view class="h-8"></view>
  </view>
</template>

<script lang="ts" setup>
import { smartGoBack } from '@/utils'
import { getTransactionDetailsApiV1UserTransactionsTransactionIdDetailsGetQueryOptions } from '@/service/app/yonghujiaoyiguanli.vuequery'
import { useDeleteTransactionApiV1UserTransactionsTransactionIdDeleteDeleteMutation } from '@/service/app/yonghujiaoyiguanli.vuequery'
import { useQuery } from '@tanstack/vue-query'

defineOptions({
  name: 'TransactionDetailPage',
})

// 定义交易记录类型
interface Transaction {
  id: string
  merchantName: string
  amount: number
  category: string
  transactionType: string
  transactionDate: string
  installment: number
  cardId: string
  cardName: string
  cardNumber: string
  cardType: string
  cardBank: string
  description: string
}

// 响应式数据
const transaction = ref<Transaction | null>(null)
const transactionId = ref('')

// 页面加载时获取交易ID
onLoad((options: any) => {
  if (options.id) {
    transactionId.value = options.id
    console.log('transactionId', transactionId.value)
  }
})

// 使用Vue Query获取交易详情
const {
  data: transactionData,
  isLoading: loading,
  isError: error,
  refetch: refetchTransaction,
} = useQuery(
  computed(() => {
    console.log('=== Vue Query 查询参数 ===')
    console.log('transactionId.value:', transactionId.value)

    const queryOptions =
      getTransactionDetailsApiV1UserTransactionsTransactionIdDetailsGetQueryOptions({
        params: {
          transaction_id: transactionId.value,
        },
      })

    console.log('=== 生成的查询配置 ===')
    console.log('queryOptions:', queryOptions)

    return {
      ...queryOptions,
      enabled: !!transactionId.value,
    }
  }),
)

// 使用Vue Query删除交易
const deleteTransactionMutation =
  useDeleteTransactionApiV1UserTransactionsTransactionIdDeleteDeleteMutation({
    onSuccess: (data) => {
      console.log('=== 删除交易成功 ===')
      console.log('返回数据:', data)

      // 智能判断成功状态
      let isSuccess = false
      if (data) {
        // @ts-ignore
        if (data.success === true) {
          isSuccess = true
        }
        // @ts-ignore
        else if (data.success === undefined && !data.error && !data.message?.includes('失败')) {
          isSuccess = true
        }
      }

      if (isSuccess) {
        uni.showToast({
          title: '删除成功',
          icon: 'success',
        })

        setTimeout(() => {
          smartGoBack()
        }, 1500)
      } else {
        // @ts-ignore
        const errorMessage = data?.message || data?.error || '删除失败'
        uni.showToast({
          title: errorMessage,
          icon: 'error',
        })
      }
    },
    onError: (error) => {
      console.error('删除交易失败:', error)
      uni.showToast({
        title: '删除失败，请重试',
        icon: 'error',
      })
    },
  })

// 监听交易数据变化
watch(
  transactionData,
  (newData) => {
    console.log('=== 交易详情数据变化 ===')
    console.log('返回数据:', newData)

    if (newData) {
      // 智能检测API响应格式
      let data = newData
      // @ts-ignore
      if (newData.success && newData.data) {
        // @ts-ignore
        data = newData.data
      }

      // 处理交易数据
      if (data && typeof data === 'object') {
        // @ts-ignore
        const apiTransaction = data
        transaction.value = {
          // @ts-ignore
          id: apiTransaction.id || transactionId.value,
          // @ts-ignore
          merchantName: apiTransaction.merchant_name || apiTransaction.merchantName || '未知商户',
          // @ts-ignore
          amount: apiTransaction.amount || 0,
          // @ts-ignore
          category: apiTransaction.category || '其他',
          // @ts-ignore
          transactionType:
            apiTransaction.transaction_type || apiTransaction.transactionType || '消费',
          // @ts-ignore
          transactionDate:
            apiTransaction.transaction_date ||
            apiTransaction.transactionDate ||
            new Date().toISOString(),
          // @ts-ignore
          installment: apiTransaction.installment_months || apiTransaction.installment || 0,
          // @ts-ignore
          cardId: apiTransaction.card_id || apiTransaction.cardId || '',
          // @ts-ignore
          cardName: apiTransaction.card_name || apiTransaction.cardName || '',
          // @ts-ignore
          cardNumber: apiTransaction.card_number || apiTransaction.cardNumber || '',
          // @ts-ignore
          cardType: apiTransaction.card_type || apiTransaction.cardType || '',
          // @ts-ignore
          cardBank: apiTransaction.card_bank || apiTransaction.cardBank || '',
          // @ts-ignore
          // @ts-ignore
          description: apiTransaction.description || '',
        }

        console.log('处理后的交易数据:', transaction.value)
      }
    }
  },
  { immediate: true },
)

// 重新加载交易详情
const loadTransactionDetail = () => {
  refetchTransaction()
}

// 格式化金额
const formatMoney = (amount: number) => {
  return amount.toFixed(2)
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  })
}

// 格式化时间
const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 获取分类颜色
const getCategoryColor = (category: string) => {
  const colors: Record<string, string> = {
    餐饮美食: '#FF6B6B',
    购物消费: '#4ECDC4',
    交通出行: '#45B7D1',
    生活服务: '#96CEB4',
    娱乐休闲: '#FECA57',
    医疗健康: '#FF9FF3',
    教育培训: '#54A0FF',
    旅游度假: '#5F27CD',
    数码3C: '#00D2D3',
    服装配饰: '#FF9F43',
  }
  return colors[category] || '#A4B0BE'
}

// 获取交易类型样式
const getTypeClass = (type: string) => {
  const classes: Record<string, string> = {
    消费: 'bg-red-100 text-red-700',
    退款: 'bg-green-100 text-green-700',
    转账: 'bg-blue-100 text-blue-700',
    提现: 'bg-orange-100 text-orange-700',
  }
  return classes[type] || 'bg-gray-100 text-gray-700'
}

// 获取信用卡名称
const getCardName = (cardId: string) => {
  // TODO: 从信用卡列表中获取卡片名称
  const cardMap: Record<string, string> = {
    'card-001': '招商银行经典白金卡(1234)',
    'card-002': '建设银行龙卡(5678)',
    'card-003': '浦发银行AE白金卡(9012)',
  }
  return cardMap[cardId] || '未知卡片'
}

// 返回上一页
const goBack = () => {
  smartGoBack()
}

// 编辑交易
const editTransaction = () => {
  uni.navigateTo({
    url: `/pages/transactions/edit?id=${transactionId.value}`,
  })
}

// 确认删除
const confirmDelete = () => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除这笔"${transaction.value?.merchantName}"的交易记录吗？`,
    confirmText: '删除',
    confirmColor: '#ff3b30',
    success: (res) => {
      if (res.confirm) {
        deleteTransaction()
      }
    },
  })
}

// 删除交易
const deleteTransaction = async () => {
  console.log('=== 开始删除交易 ===')
  console.log('交易ID:', transactionId.value)

  try {
    // 调用删除API
    deleteTransactionMutation.mutate({
      params: {
        transaction_id: transactionId.value,
      },
    })
  } catch (err) {
    console.error('删除交易失败:', err)
    uni.showToast({
      title: '删除失败',
      icon: 'error',
    })
  }
}
</script>

<style lang="scss" scoped>
.transaction-detail-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
}

.amount-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.info-section {
  border: 1px solid #f0f0f0;
}

.section-header {
  background: #fafafa;
}

.info-item:last-child {
  border-bottom: none !important;
}

.icon-container {
  flex-shrink: 0;
}

.category-dot {
  flex-shrink: 0;
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

.btn-danger {
  background: #ff3b30;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.98);
    background: #e6342a;
  }
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
