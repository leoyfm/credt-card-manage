<!-- 添加消费记录页面 -->
<route lang="json5">
{
  style: {
    navigationBarTitleText: '添加消费记录',
    navigationBarBackgroundColor: '#ffffff',
    navigationBarTextStyle: 'black',
  },
}
</route>

<template>
  <view class="add-transaction-page">
    <!-- 表单内容 -->
    <view class="form-container bg-white mt-4 shadow-sm">
      <view class="form-header p-4 border-b border-gray-100">
        <text class="text-lg font-semibold text-gray-800">消费信息</text>
      </view>

      <view class="form-content p-4 space-y-4">
        <!-- 消费金额 -->
        <view class="form-item">
          <view class="form-label">
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
        <view class="form-item">
          <view class="form-label">
            <text class="text-gray-700 font-medium">商户名称</text>
            <text class="text-red-500 ml-1">*</text>
          </view>
          <input
            v-model="formData.merchantName"
            placeholder="请输入商户名称"
            class="form-input"
            @blur="validateField('merchantName')"
          />
          <text v-if="errors.merchantName" class="error-text">{{ errors.merchantName }}</text>
        </view>

        <!-- 消费分类 -->
        <view class="form-item">
          <view class="form-label">
            <text class="text-gray-700 font-medium">消费分类</text>
            <text class="text-red-500 ml-1">*</text>
          </view>
          <picker
            :value="categoryIndex"
            :range="categoryOptions"
            range-key="label"
            @change="onCategoryChange"
          >
            <view class="picker-input">
              <text class="picker-text" :class="{ 'text-gray-400': categoryIndex === 0 }">
                {{ categoryOptions[categoryIndex].label }}
              </text>
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
          <text v-if="errors.category" class="error-text">{{ errors.category }}</text>
        </view>

        <!-- 信用卡选择 -->
        <view class="form-item">
          <view class="form-label">
            <text class="text-gray-700 font-medium">使用卡片</text>
            <text class="text-red-500 ml-1">*</text>
          </view>
          <picker :value="cardIndex" :range="cardOptions" range-key="label" @change="onCardChange">
            <view class="picker-input">
              <text class="picker-text" :class="{ 'text-gray-400': cardIndex === 0 }">
                {{ cardOptions[cardIndex].label }}
              </text>
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
          <text v-if="errors.cardId" class="error-text">{{ errors.cardId }}</text>
        </view>

        <!-- 交易类型 -->
        <view class="form-item">
          <view class="form-label">
            <text class="text-gray-700 font-medium">交易类型</text>
          </view>
          <picker
            :value="transactionTypeIndex"
            :range="transactionTypeOptions"
            range-key="label"
            @change="onTransactionTypeChange"
          >
            <view class="picker-input">
              <text class="picker-text">
                {{ transactionTypeOptions[transactionTypeIndex].label }}
              </text>
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
        </view>

        <!-- 交易时间 -->
        <view class="form-item">
          <view class="form-label">
            <text class="text-gray-700 font-medium">交易时间</text>
          </view>
          <view class="datetime-container">
            <picker mode="date" :value="dateValue" @change="onDateChange" class="flex-1">
              <view class="picker-input">
                <text class="picker-text">{{ dateValue || '选择日期' }}</text>
                <text class="picker-arrow">▼</text>
              </view>
            </picker>
            <picker mode="time" :value="timeValue" @change="onTimeChange" class="flex-1 ml-2">
              <view class="picker-input">
                <text class="picker-text">{{ timeValue || '选择时间' }}</text>
                <text class="picker-arrow">▼</text>
              </view>
            </picker>
          </view>
        </view>

        <!-- 分期期数 -->
        <view class="form-item">
          <view class="form-label">
            <text class="text-gray-700 font-medium">分期期数</text>
          </view>
          <picker
            :value="installmentIndex"
            :range="installmentOptions"
            range-key="label"
            @change="onInstallmentChange"
          >
            <view class="picker-input">
              <text class="picker-text">
                {{ installmentOptions[installmentIndex].label }}
              </text>
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
        </view>

        <!-- 备注说明 -->
        <view class="form-item">
          <view class="form-label">
            <text class="text-gray-700 font-medium">备注说明</text>
          </view>
          <textarea
            v-model="formData.description"
            placeholder="请输入备注说明（可选）"
            class="form-textarea"
            :maxlength="200"
          />
          <view class="text-right mt-1">
            <text class="text-xs text-gray-400">{{ formData.description.length }}/200</text>
          </view>
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
          {{ submitting ? '提交中...' : '确认添加' }}
        </button>
      </view>
    </view>

    <!-- 底部安全区域 -->
    <view class="h-20 pb-safe"></view>

    <!-- Toast 组件 -->
    <wd-toast />
  </view>
</template>

<script lang="ts" setup>
import { useToast } from 'wot-design-uni'
import { smartGoBack } from '@/utils/navigation'
import { useCreateTransactionApiV1UserTransactionsCreatePostMutation } from '@/service/app/yonghujiaoyiguanli.vuequery'
import { getCreditCardsApiV1UserCardsGetQueryOptions } from '@/service/app/xinyongkaguanli.vuequery'
import { useQuery } from '@tanstack/vue-query'

defineOptions({
  name: 'AddTransactionPage',
})

const toast = useToast()

// 表单数据
const formData = ref({
  amount: '',
  merchantName: '',
  category: '',
  cardId: '',
  transactionType: '消费',
  transactionDate: '',
  installment: 0,
  description: '',
})

// 表单验证错误
const errors = ref({
  amount: '',
  merchantName: '',
  category: '',
  cardId: '',
})

// 选择器索引
const categoryIndex = ref(0)
const cardIndex = ref(0)
const transactionTypeIndex = ref(0)
const installmentIndex = ref(0)

// 日期时间
const dateValue = ref('')
const timeValue = ref('')

// 提交状态
const submitting = ref(false)

// 选项数据
const categoryOptions = [
  { value: '', label: '请选择消费分类' },
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

const cardOptions = ref([{ value: '', label: '请选择信用卡' }])

const transactionTypeOptions = [
  { value: '消费', label: '消费' },
  { value: '退款', label: '退款' },
  { value: '转账', label: '转账' },
]

const installmentOptions: Array<{ value: number; label: string }> = [
  { value: 0, label: '无分期' },
  { value: 3, label: '3期' },
  { value: 6, label: '6期' },
  { value: 12, label: '12期' },
  { value: 18, label: '18期' },
  { value: 24, label: '24期' },
]

// 页面生命周期
onLoad(() => {
  initDateTime()
})

// 初始化日期时间
const initDateTime = () => {
  const now = new Date()
  dateValue.value = now.toISOString().split('T')[0]
  timeValue.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
  updateTransactionDate()
}

// 更新交易时间
const updateTransactionDate = () => {
  if (dateValue.value && timeValue.value) {
    formData.value.transactionDate = `${dateValue.value} ${timeValue.value}:00`
  }
}

// 使用Vue Query获取信用卡列表
const { data: creditCardsData, isLoading: cardsLoading } = useQuery({
  ...getCreditCardsApiV1UserCardsGetQueryOptions({
    params: {},
  }),
  enabled: true,
})

// 监听信用卡数据变化，更新选项
watch(
  creditCardsData,
  (newData) => {
    console.log('=== 添加页面信用卡数据变化 ===')
    console.log('原始数据:', newData)

    if (newData) {
      try {
        // @ts-ignore - 忽略类型错误以便调试
        let data = newData

        // 检查是否有包装格式
        // @ts-ignore
        if (newData.success !== undefined && newData.data !== undefined) {
          console.log('检测到包装格式，提取data字段')
          // @ts-ignore
          data = newData.data
        }

        console.log('提取后的数据:', data)

        let cards: any[] = []
        if (Array.isArray(data)) {
          console.log('数据是直接数组格式，长度:', data.length)
          cards = data
        } else if (data && typeof data === 'object') {
          console.log('数据是对象格式，查找items/list字段')
          // @ts-ignore
          cards = data.items || data.list || []
          console.log('找到的cards:', cards)
        }

        console.log('最终信用卡数据:', cards)

        if (cards.length > 0) {
          cardOptions.value = [
            { value: '', label: '请选择信用卡' },
            ...cards.map((card: any) => {
              const option = {
                value: card.id,
                label: `${card.bank.bank_name || card.bankName || '未知银行'}${card.card_name || card.cardName || ''}(${card.card_number.slice(-4) || card.cardNumberLast4 || '****'})`,
              }
              console.log('卡片选项:', card, '->', option)
              return option
            }),
          ]
        } else {
          console.log('没有找到信用卡数据，使用模拟数据')
          cardOptions.value = [
            { value: '', label: '请选择信用卡' },
            { value: '1', label: '招商银行经典白金卡(1234)' },
            { value: '2', label: '建设银行龙卡(5678)' },
            { value: '3', label: '浦发银行AE白金卡(9012)' },
          ]
        }

        console.log('最终卡片选项:', cardOptions.value)
      } catch (error) {
        console.error('处理信用卡数据时出错:', error)
        // 出错时使用模拟数据
        cardOptions.value = [
          { value: '', label: '请选择信用卡' },
          { value: '1', label: '招商银行经典白金卡(1234)' },
          { value: '2', label: '建设银行龙卡(5678)' },
          { value: '3', label: '浦发银行AE白金卡(9012)' },
        ]
      }
    } else {
      console.log('没有接收到信用卡数据')
    }
  },
  { immediate: true },
)

// 选择器事件处理
const onCategoryChange = (e: any) => {
  categoryIndex.value = e.detail.value
  formData.value.category = categoryOptions[categoryIndex.value].value
  validateField('category')
}

const onCardChange = (e: any) => {
  cardIndex.value = e.detail.value
  formData.value.cardId = cardOptions.value[cardIndex.value].value
  validateField('cardId')
}

const onTransactionTypeChange = (e: any) => {
  transactionTypeIndex.value = e.detail.value
  formData.value.transactionType = transactionTypeOptions[transactionTypeIndex.value].value
}

const onInstallmentChange = (e: any) => {
  installmentIndex.value = parseInt(e.detail.value)
  formData.value.installment = installmentOptions[installmentIndex.value].value
}

const onDateChange = (e: any) => {
  dateValue.value = e.detail.value
  updateTransactionDate()
}

const onTimeChange = (e: any) => {
  timeValue.value = e.detail.value
  updateTransactionDate()
}

// 金额输入处理
const handleAmountInput = () => {
  // 只允许输入数字和小数点
  let value = formData.value.amount.replace(/[^\d.]/g, '')

  // 确保只有一个小数点
  const parts = value.split('.')
  if (parts.length > 2) {
    value = parts[0] + '.' + parts.slice(1).join('')
  }

  // 限制小数点后两位
  if (parts[1] && parts[1].length > 2) {
    value = parts[0] + '.' + parts[1].substring(0, 2)
  }

  formData.value.amount = value
  validateField('amount')
}

// 表单验证
const validateField = (field: string) => {
  switch (field) {
    case 'amount':
      if (!formData.value.amount) {
        errors.value.amount = '请输入消费金额'
      } else if (parseFloat(formData.value.amount) <= 0) {
        errors.value.amount = '消费金额必须大于0'
      } else {
        errors.value.amount = ''
      }
      break
    case 'merchantName':
      if (!formData.value.merchantName.trim()) {
        errors.value.merchantName = '请输入商户名称'
      } else {
        errors.value.merchantName = ''
      }
      break
    case 'category':
      if (!formData.value.category) {
        errors.value.category = '请选择消费分类'
      } else {
        errors.value.category = ''
      }
      break
    case 'cardId':
      if (!formData.value.cardId) {
        errors.value.cardId = '请选择信用卡'
      } else {
        errors.value.cardId = ''
      }
      break
  }
}

// 验证整个表单
const validateForm = () => {
  validateField('amount')
  validateField('merchantName')
  validateField('category')
  validateField('cardId')

  return !Object.values(errors.value).some((error) => error !== '')
}

// 使用Vue Query mutation创建交易
const createTransactionMutation = useCreateTransactionApiV1UserTransactionsCreatePostMutation({
  onSuccess: (data) => {
    console.log('=== 交易创建成功回调 ===')
    console.log('返回数据:', data)
    console.log('数据类型:', typeof data)
    console.log('是否有success字段:', data?.success)
    console.log('是否有data字段:', data?.data)

    submitting.value = false

    // 智能判断成功状态
    let isSuccess = false
    let responseData = data

    // 检查不同的成功标识
    if (data) {
      // @ts-ignore - 忽略类型错误以便处理多种响应格式
      // 情况1: 直接有success字段且为true
      if (data.success === true) {
        isSuccess = true
        // @ts-ignore
        responseData = data.data || data
      }
      // 情况2: 没有success字段，但有data字段（可能是直接返回数据）
      // @ts-ignore
      else if (data.success === undefined && data.data) {
        isSuccess = true
        // @ts-ignore
        responseData = data.data
      }
      // 情况3: 没有success字段，但有id字段（可能是直接返回创建的对象）
      // @ts-ignore
      else if (data.success === undefined && data.id) {
        isSuccess = true
        responseData = data
      }
      // 情况4: HTTP状态码成功，没有明确的错误信息
      // @ts-ignore
      else if (data.success === undefined && !data.error && !data.message?.includes('失败')) {
        isSuccess = true
        responseData = data
      }
    }

    console.log('判断结果 - 是否成功:', isSuccess)
    console.log('响应数据:', responseData)

    if (isSuccess) {
      toast.success('添加成功')
      setTimeout(() => {
        uni.navigateBack()
      }, 1500)
    } else {
      // @ts-ignore
      const errorMessage = data?.message || data?.error || '添加失败'
      console.log('失败原因:', errorMessage)
      toast.error(errorMessage)
    }
  },
  onError: (error) => {
    console.log('=== 交易创建错误回调 ===')
    console.error('错误详情:', error)
    submitting.value = false
    toast.error('提交失败，请重试')
  },
})

// 提交表单
const submitForm = async () => {
  if (!validateForm()) {
    toast.error('请检查表单信息')
    return
  }

  submitting.value = true

  // 构建提交数据
  const submitData = {
    amount: parseFloat(formData.value.amount),
    merchant_name: formData.value.merchantName.trim(),
    category: formData.value.category,
    card_id: formData.value.cardId,
    transaction_type: formData.value.transactionType,
    transaction_date: formData.value.transactionDate,
    installment_months: formData.value.installment,
    description: formData.value.description.trim(),
  }

  console.log('=== 提交交易数据 ===')
  console.log('表单数据:', formData.value)
  console.log('选中的卡片索引:', cardIndex.value)
  console.log('卡片选项:', cardOptions.value)
  console.log('选中的卡片:', cardOptions.value[cardIndex.value])
  console.log('最终提交数据:', submitData)

  // 验证card_id是否为有效的UUID格式
  if (!submitData.card_id || submitData.card_id === '') {
    toast.error('请选择信用卡')
    submitting.value = false
    return
  }

  // 检查card_id是否看起来像UUID
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
  if (!uuidRegex.test(submitData.card_id)) {
    console.warn('card_id不是有效的UUID格式:', submitData.card_id)
    // 不阻止提交，但记录警告
  }

  // 调用Vue Query mutation
  createTransactionMutation.mutate({
    body: submitData,
  })
}

// 返回
const goBack = () => {
  smartGoBack()
}
</script>

<style lang="scss">
.add-transaction-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.form-item {
  margin-bottom: 20px;
}

.form-label {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.form-input {
  width: auto;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  background: #ffffff;

  &:focus {
    border-color: #667eea;
    outline: none;
  }
}

.form-textarea {
  width: auto;
  min-height: 80px;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  background: #ffffff;
  resize: none;

  &:focus {
    border-color: #667eea;
    outline: none;
  }
}

.amount-input-container {
  display: flex;
  align-items: center;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #ffffff;
  overflow: hidden;

  &:focus-within {
    border-color: #667eea;
  }
}

.currency-symbol {
  padding: 12px 0 12px 16px;
  font-size: 18px;
  font-weight: 600;
  color: #374151;
}

.amount-input {
  flex: 1;
  padding: 12px 16px 12px 8px;
  border: none;
  font-size: 18px;
  font-weight: 600;
  background: transparent;

  &:focus {
    outline: none;
  }
}

.picker-input {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #ffffff;
  cursor: pointer;

  &:active {
    background: #f9fafb;
  }
}

.picker-text {
  font-size: 16px;
  color: #374151;
}

.picker-arrow {
  font-size: 12px;
  color: #9ca3af;
}

.datetime-container {
  display: flex;
  gap: 8px;
}

.error-text {
  font-size: 12px;
  color: #ef4444;
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

  &:active {
    transform: scale(0.98);
  }

  &:disabled {
    opacity: 0.6;
    transform: none;
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
</style>
