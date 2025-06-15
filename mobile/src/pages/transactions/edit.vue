<template>
  <view class="edit-transaction-page">
    <!-- 导航栏 -->
    <view class="navbar bg-white border-b border-gray-200 px-4 py-3">
      <view class="flex items-center justify-between">
        <view class="flex items-center">
          <text class="text-2xl mr-3" @click="goBack">‹</text>
          <text class="text-lg font-semibold text-gray-800">编辑交易</text>
        </view>
        <text class="text-blue-600 text-base" @click="submitForm">保存</text>
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
      <button class="btn-primary" @click="loadTransactionData">重试</button>
    </view>

    <!-- 编辑表单 -->
    <view v-else class="form-container">
      <!-- 消费信息 -->
      <view class="form-section bg-white mx-4 mt-4 rounded-lg shadow-sm">
        <view class="section-header px-4 py-3 border-b border-gray-100">
          <text class="text-lg font-semibold text-gray-800">消费信息</text>
        </view>

        <!-- 金额输入 -->
        <view class="form-item px-4 py-4 border-b border-gray-100">
          <view class="form-label mb-2">
            <text class="text-gray-700 font-medium">消费金额</text>
            <text class="text-red-500 ml-1">*</text>
          </view>
          <view class="amount-input-container">
            <text class="currency-symbol">¥</text>
            <input
              v-model="formData.amount"
              type="digit"
              placeholder="0.00"
              class="amount-input"
              @input="handleAmountInput"
            />
          </view>
          <text v-if="errors.amount" class="error-text">{{ errors.amount }}</text>
        </view>

        <!-- 商户名称 -->
        <view class="form-item px-4 py-4 border-b border-gray-100">
          <view class="form-label mb-2">
            <text class="text-gray-700 font-medium">商户名称</text>
            <text class="text-red-500 ml-1">*</text>
          </view>
          <input
            v-model="formData.merchantName"
            type="text"
            placeholder="请输入商户名称"
            class="form-input"
            :maxlength="50"
          />
          <text v-if="errors.merchantName" class="error-text">{{ errors.merchantName }}</text>
        </view>

        <!-- 消费分类 -->
        <view class="form-item px-4 py-4 border-b border-gray-100">
          <view class="form-label mb-2">
            <text class="text-gray-700 font-medium">消费分类</text>
            <text class="text-red-500 ml-1">*</text>
          </view>
          <picker
            :value="categoryIndex"
            :range="categoryOptions"
            range-key="label"
            @change="onCategoryChange"
          >
            <view class="picker-display">
              <text class="picker-text">{{ categoryOptions[categoryIndex].label }}</text>
              <text class="picker-arrow">›</text>
            </view>
          </picker>
          <text v-if="errors.category" class="error-text">{{ errors.category }}</text>
        </view>

        <!-- 关联信用卡 -->
        <view class="form-item px-4 py-4">
          <view class="form-label mb-2">
            <text class="text-gray-700 font-medium">关联信用卡</text>
            <text class="text-red-500 ml-1">*</text>
          </view>
          <picker :value="cardIndex" :range="cardOptions" range-key="label" @change="onCardChange">
            <view class="picker-display">
              <text class="picker-text">{{ cardOptions[cardIndex].label }}</text>
              <text class="picker-arrow">›</text>
            </view>
          </picker>
          <text v-if="errors.cardId" class="error-text">{{ errors.cardId }}</text>
        </view>
      </view>

      <!-- 交易详情 -->
      <view class="form-section bg-white mx-4 mt-4 rounded-lg shadow-sm">
        <view class="section-header px-4 py-3 border-b border-gray-100">
          <text class="text-lg font-semibold text-gray-800">交易详情</text>
        </view>

        <!-- 交易类型 -->
        <view class="form-item px-4 py-4 border-b border-gray-100">
          <view class="form-label mb-2">
            <text class="text-gray-700 font-medium">交易类型</text>
          </view>
          <picker
            :value="transactionTypeIndex"
            :range="transactionTypeOptions"
            range-key="label"
            @change="onTransactionTypeChange"
          >
            <view class="picker-display">
              <text class="picker-text">
                {{ transactionTypeOptions[transactionTypeIndex].label }}
              </text>
              <text class="picker-arrow">›</text>
            </view>
          </picker>
        </view>

        <!-- 交易时间 -->
        <view class="form-item px-4 py-4 border-b border-gray-100">
          <view class="form-label mb-2">
            <text class="text-gray-700 font-medium">交易时间</text>
          </view>
          <view class="datetime-container">
            <picker
              mode="date"
              :value="formData.transactionDate.split('T')[0]"
              @change="onDateChange"
            >
              <view class="datetime-picker">
                <text class="datetime-text">{{ formatDisplayDate(formData.transactionDate) }}</text>
                <text class="picker-arrow">›</text>
              </view>
            </picker>
            <picker mode="time" :value="formData.transactionTime" @change="onTimeChange">
              <view class="datetime-picker">
                <text class="datetime-text">{{ formData.transactionTime }}</text>
                <text class="picker-arrow">›</text>
              </view>
            </picker>
          </view>
        </view>

        <!-- 分期期数 -->
        <view class="form-item px-4 py-4">
          <view class="form-label mb-2">
            <text class="text-gray-700 font-medium">分期期数</text>
          </view>
          <picker
            :value="installmentIndex"
            :range="installmentOptions"
            range-key="label"
            @change="onInstallmentChange"
          >
            <view class="picker-display">
              <text class="picker-text">{{ installmentOptions[installmentIndex].label }}</text>
              <text class="picker-arrow">›</text>
            </view>
          </picker>
        </view>
      </view>

      <!-- 备注信息 -->
      <view class="form-section bg-white mx-4 mt-4 rounded-lg shadow-sm">
        <view class="section-header px-4 py-3 border-b border-gray-100">
          <text class="text-lg font-semibold text-gray-800">备注信息</text>
        </view>

        <view class="form-item px-4 py-4">
          <view class="form-label mb-2">
            <text class="text-gray-700 font-medium">备注说明</text>
            <text class="text-gray-500 text-sm ml-2">(可选)</text>
          </view>
          <textarea
            v-model="formData.description"
            placeholder="请输入备注说明（可选）"
            class="form-textarea"
            :maxlength="200"
          />
          <view class="text-right mt-1">
            <text class="text-gray-400 text-xs">{{ formData.description.length }}/200</text>
          </view>
        </view>
      </view>

      <!-- 底部操作栏 -->
      <view
        class="bottom-actions fixed left-0 right-0 bg-white border-t border-gray-200 px-4 py-3 safe-area-inset-bottom z-10"
      >
        <view class="flex space-x-3">
          <button class="btn-secondary flex-1" @click="goBack">取消</button>
          <button class="btn-primary flex-1" @click="submitForm" :disabled="submitting">
            {{ submitting ? '保存中...' : '保存修改' }}
          </button>
        </view>
      </view>

      <!-- 底部安全区域 -->
      <view class="h-20 pb-safe"></view>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { smartGoBack } from '@/utils'
import { getTransactionDetailsApiV1UserTransactionsTransactionIdDetailsGetQueryOptions } from '@/service/app/yonghujiaoyiguanli.vuequery'
import { useUpdateTransactionApiV1UserTransactionsTransactionIdUpdatePutMutation } from '@/service/app/yonghujiaoyiguanli.vuequery'
import { getCreditCardsApiV1UserCardsGetQueryOptions } from '@/service/app/xinyongkaguanli.vuequery'
import { useQuery } from '@tanstack/vue-query'

defineOptions({
  name: 'EditTransactionPage',
})

// 表单数据类型
interface FormData {
  amount: string
  merchantName: string
  category: string
  cardId: string
  transactionType: string
  transactionDate: string
  transactionTime: string
  installment: number
  description: string
}

// 响应式数据
const submitting = ref(false)
const transactionId = ref('')

const formData = ref<FormData>({
  amount: '',
  merchantName: '',
  category: '',
  cardId: '',
  transactionType: '消费',
  transactionDate: '',
  transactionTime: '',
  installment: 0,
  description: '',
})

const errors = ref<Record<string, string>>({})

// 选择器选项
const categoryOptions = [
  { value: '餐饮美食', label: '餐饮美食' },
  { value: '购物消费', label: '购物消费' },
  { value: '交通出行', label: '交通出行' },
  { value: '生活服务', label: '生活服务' },
  { value: '娱乐休闲', label: '娱乐休闲' },
  { value: '医疗健康', label: '医疗健康' },
  { value: '教育培训', label: '教育培训' },
  { value: '旅游度假', label: '旅游度假' },
  { value: '数码3C', label: '数码3C' },
  { value: '服装配饰', label: '服装配饰' },
]

const cardOptions = ref([
  { value: '', label: '请选择信用卡' },
  { value: 'card-001', label: '招商银行经典白金卡(1234)' },
  { value: 'card-002', label: '建设银行龙卡(5678)' },
  { value: 'card-003', label: '浦发银行AE白金卡(9012)' },
])

const transactionTypeOptions = [
  { value: '消费', label: '消费' },
  { value: '退款', label: '退款' },
  { value: '转账', label: '转账' },
  { value: '提现', label: '提现' },
]

const installmentOptions = [
  { value: 0, label: '无分期' },
  { value: 3, label: '3期' },
  { value: 6, label: '6期' },
  { value: 9, label: '9期' },
  { value: 12, label: '12期' },
  { value: 18, label: '18期' },
  { value: 24, label: '24期' },
]

// 选择器索引
const categoryIndex = ref(0)
const cardIndex = ref(0)
const transactionTypeIndex = ref(0)
const installmentIndex = ref(0)

// 页面加载时获取交易ID
onLoad((options: any) => {
  if (options.id) {
    transactionId.value = options.id
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
    console.log('=== 编辑页面 Vue Query 查询参数 ===')
    console.log('transactionId.value:', transactionId.value)

    const queryOptions =
      getTransactionDetailsApiV1UserTransactionsTransactionIdDetailsGetQueryOptions({
        params: {
          transaction_id: transactionId.value,
        },
      })

    console.log('=== 编辑页面生成的查询配置 ===')
    console.log('queryOptions:', queryOptions)

    return {
      ...queryOptions,
      enabled: !!transactionId.value,
    }
  }),
)

// 使用Vue Query获取信用卡列表
const { data: creditCardsData, isLoading: cardsLoading } = useQuery({
  ...getCreditCardsApiV1UserCardsGetQueryOptions({
    params: {},
  }),
  enabled: true,
})

// 使用Vue Query更新交易
const updateTransactionMutation =
  useUpdateTransactionApiV1UserTransactionsTransactionIdUpdatePutMutation({
    onSuccess: (data) => {
      console.log('=== 交易更新成功 ===')
      console.log('返回数据:', data)

      submitting.value = false

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
          title: '修改成功',
          icon: 'success',
        })

        setTimeout(() => {
          smartGoBack()
        }, 1500)
      } else {
        // @ts-ignore
        const errorMessage = data?.message || data?.error || '修改失败'
        uni.showToast({
          title: errorMessage,
          icon: 'error',
        })
      }
    },
    onError: (error) => {
      submitting.value = false
      console.error('修改交易失败:', error)
      uni.showToast({
        title: '修改失败，请重试',
        icon: 'error',
      })
    },
  })

// 监听交易数据变化，填充表单
watch(
  transactionData,
  (newData) => {
    console.log('=== 交易数据变化 ===')
    console.log('返回数据:', newData)

    if (newData) {
      // 智能检测API响应格式
      let data = newData
      // @ts-ignore
      if (newData.success && newData.data) {
        // @ts-ignore
        data = newData.data
      }

      // 处理交易数据并填充表单
      if (data && typeof data === 'object') {
        // @ts-ignore
        const apiTransaction = data

        // 填充表单数据
        // @ts-ignore
        const transactionDate =
          apiTransaction.transaction_date ||
          apiTransaction.transactionDate ||
          new Date().toISOString()
        const date = new Date(transactionDate)

        formData.value = {
          // @ts-ignore
          amount: (apiTransaction.amount || 0).toString(),
          // @ts-ignore
          merchantName: apiTransaction.merchant_name || apiTransaction.merchantName || '',
          // @ts-ignore
          category: apiTransaction.category || '餐饮美食',
          // @ts-ignore
          cardId: apiTransaction.card_id || apiTransaction.cardId || '',
          // @ts-ignore
          transactionType:
            apiTransaction.transaction_type || apiTransaction.transactionType || '消费',
          transactionDate: transactionDate,
          transactionTime: date.toTimeString().slice(0, 5),
          // @ts-ignore
          installment: apiTransaction.installment_months || apiTransaction.installment || 0,
          // @ts-ignore
          description: apiTransaction.description || '',
        }

        // 设置选择器索引
        // @ts-ignore
        categoryIndex.value = categoryOptions.findIndex(
          (item) => item.value === (apiTransaction.category || '餐饮美食'),
        )
        // @ts-ignore
        cardIndex.value = cardOptions.value.findIndex(
          (item) => item.value === (apiTransaction.card_id || apiTransaction.cardId || ''),
        )
        // @ts-ignore
        transactionTypeIndex.value = transactionTypeOptions.findIndex(
          (item) =>
            item.value ===
            (apiTransaction.transaction_type || apiTransaction.transactionType || '消费'),
        )
        // @ts-ignore
        installmentIndex.value = installmentOptions.findIndex(
          (item) =>
            item.value === (apiTransaction.installment_months || apiTransaction.installment || 0),
        )

        console.log('填充后的表单数据:', formData.value)
        console.log('选择器索引:', {
          categoryIndex: categoryIndex.value,
          cardIndex: cardIndex.value,
          transactionTypeIndex: transactionTypeIndex.value,
          installmentIndex: installmentIndex.value,
        })
      }
    }
  },
  { immediate: true },
)

// 监听信用卡数据变化，更新选项
watch(
  creditCardsData,
  (newData) => {
    console.log('=== 信用卡数据变化 ===')
    console.log('返回数据:', newData)

    if (newData) {
      // 智能检测API响应格式
      let data = newData
      // @ts-ignore
      if (newData.success && newData.data) {
        // @ts-ignore
        data = newData.data
      }

      let cards: any[] = []
      if (Array.isArray(data)) {
        cards = data
      } else if (data && typeof data === 'object') {
        // @ts-ignore
        cards = data.items || data.list || []
      }

      cardOptions.value = [
        { value: '', label: '请选择信用卡' },
        ...cards.map((card: any) => ({
          value: card.id,
          label: `${card.bank?.bank_name || card.bank_name || '未知银行'}${card.card_name || ''}(${card.card_number_last4 || '****'})`,
        })),
      ]

      console.log('处理后的卡片选项:', cardOptions.value)
    }
  },
  { immediate: true },
)

// 重新加载交易数据
const loadTransactionData = () => {
  refetchTransaction()
}

// 金额输入处理
const handleAmountInput = (e: any) => {
  let value = e.detail.value
  // 只允许数字和小数点
  value = value.replace(/[^\d.]/g, '')
  // 确保只有一个小数点
  const parts = value.split('.')
  if (parts.length > 2) {
    value = parts[0] + '.' + parts.slice(1).join('')
  }
  // 限制小数位数为2位
  if (parts[1] && parts[1].length > 2) {
    value = parts[0] + '.' + parts[1].slice(0, 2)
  }
  formData.value.amount = value

  // 清除金额错误
  if (errors.value.amount) {
    delete errors.value.amount
  }
}

// 选择器变化处理
const onCategoryChange = (e: any) => {
  categoryIndex.value = e.detail.value
  formData.value.category = categoryOptions[e.detail.value].value
}

const onCardChange = (e: any) => {
  cardIndex.value = e.detail.value
  formData.value.cardId = cardOptions.value[e.detail.value].value

  // 清除卡片错误
  if (errors.value.cardId) {
    delete errors.value.cardId
  }
}

const onTransactionTypeChange = (e: any) => {
  transactionTypeIndex.value = e.detail.value
  formData.value.transactionType = transactionTypeOptions[e.detail.value].value
}

const onInstallmentChange = (e: any) => {
  installmentIndex.value = e.detail.value
  formData.value.installment = installmentOptions[e.detail.value].value
}

const onDateChange = (e: any) => {
  const selectedDate = e.detail.value
  const currentTime = formData.value.transactionTime || '12:00'
  formData.value.transactionDate = `${selectedDate}T${currentTime}:00.000Z`
}

const onTimeChange = (e: any) => {
  formData.value.transactionTime = e.detail.value
  const currentDate = formData.value.transactionDate.split('T')[0]
  formData.value.transactionDate = `${currentDate}T${e.detail.value}:00.000Z`
}

// 格式化显示日期
const formatDisplayDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

// 表单验证
const validateForm = () => {
  errors.value = {}

  if (!formData.value.amount || parseFloat(formData.value.amount) <= 0) {
    errors.value.amount = '请输入有效的金额'
  }

  if (!formData.value.merchantName.trim()) {
    errors.value.merchantName = '请输入商户名称'
  }

  if (!formData.value.category) {
    errors.value.category = '请选择消费分类'
  }

  if (!formData.value.cardId) {
    errors.value.cardId = '请选择关联信用卡'
  }

  return Object.keys(errors.value).length === 0
}

// 提交表单
const submitForm = async () => {
  if (!validateForm()) {
    uni.showToast({
      title: '请检查表单信息',
      icon: 'none',
    })
    return
  }

  submitting.value = true

  console.log('=== 开始保存交易 ===')
  console.log('交易ID:', transactionId.value)
  console.log('表单数据:', formData.value)

  try {
    // 构建更新数据
    const updateData = {
      amount: parseFloat(formData.value.amount),
      merchant_name: formData.value.merchantName.trim(),
      category: formData.value.category,
      card_id: formData.value.cardId,
      transaction_type: formData.value.transactionType,
      transaction_date: formData.value.transactionDate,
      installment_months: formData.value.installment,
      description: formData.value.description.trim(),
    }

    console.log('构建的更新数据:', updateData)

    // 调用更新API
    updateTransactionMutation.mutate({
      params: {
        transaction_id: transactionId.value,
      },
      data: updateData,
    })
  } catch (err) {
    submitting.value = false
    console.error('保存交易失败:', err)
    uni.showToast({
      title: '修改失败，请重试',
      icon: 'error',
    })
  }
}

// 返回上一页
const goBack = () => {
  smartGoBack()
}
</script>

<style lang="scss" scoped>
.edit-transaction-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
}

.form-section {
  border: 1px solid #f0f0f0;
}

.section-header {
  background: #fafafa;
}

.form-item:last-child {
  border-bottom: none !important;
}

.form-label {
  display: flex;
  align-items: center;
}

.amount-input-container {
  display: flex;
  align-items: center;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 0 12px;
  height: 48px;
}

.currency-symbol {
  color: #6c757d;
  font-size: 18px;
  font-weight: 600;
  margin-right: 8px;
}

.amount-input {
  flex: 1;
  background: transparent;
  border: none;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.form-input {
  width: 100%;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 12px;
  font-size: 16px;
  color: #333;
}

.form-textarea {
  width: 100%;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 12px;
  font-size: 16px;
  color: #333;
  min-height: 80px;
  resize: none;
}

.picker-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 12px;
  min-height: 48px;
}

.picker-text {
  flex: 1;
  font-size: 16px;
  color: #333;
}

.picker-arrow {
  color: #6c757d;
  font-size: 18px;
  margin-left: 8px;
}

.datetime-container {
  display: flex;
  gap: 12px;
}

.datetime-picker {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 12px;
  min-height: 48px;
}

.datetime-text {
  font-size: 16px;
  color: #333;
}

.error-text {
  color: #dc3545;
  font-size: 12px;
  margin-top: 4px;
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

  &:disabled {
    opacity: 0.6;
    transform: none;
  }

  &:active:not(:disabled) {
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

.bottom-actions {
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  bottom: var(--window-bottom);
}

.pb-safe {
  padding-bottom: env(safe-area-inset-bottom);
  height: calc(80px + var(--window-bottom));
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
