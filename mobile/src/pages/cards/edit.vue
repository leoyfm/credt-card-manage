<route lang="json5" type="page">
{
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '编辑信用卡',
  },
}
</route>

<template>
  <view class="edit-card-page">
    <!-- 顶部导航栏 -->
    <wd-navbar
      title="编辑信用卡"
      left-text="返回"
      left-arrow
      :right-text="updateCardMutation.isPending.value ? '保存中...' : '保存'"
      fixed
      placeholder
      safe-area-inset-top
      custom-style="height: 60px; line-height: 60px;"
      @click-left="handleBack"
      @click-right="handleSave"
      :right-disabled="updateCardMutation.isPending.value || isLoading"
    />

    <!-- 加载状态 -->
    <view v-if="isLoading" class="loading-container">
      <wd-loading />
      <text class="loading-text">加载信用卡信息中...</text>
    </view>

    <!-- 错误状态 -->
    <view v-else-if="isError" class="error-container">
      <text class="error-text">加载失败，请重试</text>
      <wd-button type="primary" @click="refetch">重新加载</wd-button>
    </view>

    <!-- 编辑表单 -->
    <view v-else class="form-container">
      <!-- 信用卡预览 -->
      <view class="mx-4 mt-4 mb-6">
        <view
          class="card-preview relative rounded-xl p-6 text-white"
          :style="{ background: getCardGradient(formData.bankColor) }"
        >
          <view class="flex justify-between items-start mb-4">
            <view>
              <text class="text-lg font-medium">{{ formData.bankName || '招商银行' }}</text>
              <text class="text-sm opacity-90 block mt-1">
                {{ formData.cardName || '全币种国际卡' }}
              </text>
            </view>
            <view class="bg-white bg-opacity-20 px-3 py-1 rounded">
              <text class="text-white text-sm" @click="handleEditCard">编辑</text>
            </view>
          </view>

          <view class="mb-4">
            <text class="text-base tracking-wider">
              **** **** **** {{ formData.cardNumber.slice(-4) || '0000' }}
            </text>
          </view>

          <view class="flex justify-between items-end">
            <view>
              <text class="text-xs opacity-75">有效期至</text>
              <text class="text-sm block">{{ formData.expiryDate || '12/25' }}</text>
            </view>
            <view>
              <text class="text-xs opacity-75">年费扣款</text>
              <text class="text-sm block">{{ annualFeeDateDisplay }}</text>
            </view>
            <view class="w-8 h-8 bg-white bg-opacity-20 rounded flex items-center justify-center">
              <text class="text-white text-xs">{{ getCardTypeIcon(formData.cardType) }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 表单内容 -->
      <wd-form ref="form" :model="formData">
        <!-- 个性化设置 -->
        <view class="form-section">
          <view class="section-title">
            <text>个性化设置</text>
          </view>

          <wd-cell title="卡片颜色" custom>
            <view class="color-grid">
              <view
                v-for="(color, index) in cardColors"
                :key="index"
                :class="['color-item', formData.bankColor === color ? 'selected' : '']"
                :style="{ backgroundColor: color }"
                @click="selectColor(color)"
              ></view>
            </view>
          </wd-cell>

          <wd-cell title="启用此卡片">
            <wd-switch v-model="formData.isEnabled" size="small" />
          </wd-cell>
        </view>

        <!-- 基本信息 -->
        <view class="form-section">
          <view class="section-title">
            <text>基本信息</text>
          </view>

          <wd-select-picker
            label="发卡银行"
            v-model="formData.selectedBankId"
            :columns="bankColumns"
            type="radio"
            required
            :placeholder="isBanksLoading ? '加载银行列表中...' : '请选择发卡银行'"
            prop="selectedBankId"
            :rules="[{ required: true, message: '请选择发卡银行' }]"
            :disabled="isBanksLoading || isBanksError"
            @change="onBankChange"
          />

          <!-- 银行列表加载错误提示 -->
          <wd-cell v-if="isBanksError" custom>
            <view class="text-red-500 text-sm">
              <text>银行列表加载失败，请检查网络连接</text>
            </view>
          </wd-cell>

          <wd-input
            label="卡片名称"
            v-model="formData.cardName"
            placeholder="请输入卡片名称"
            required
            clearable
            prop="cardName"
            :rules="[{ required: true, message: '请输入卡片名称' }]"
          />

          <wd-input
            label="卡号"
            v-model="formData.cardNumber"
            placeholder="请输入卡号后四位"
            clearable
            :maxlength="4"
            prop="cardNumber"
            :rules="[{ required: true, message: '请输入卡号' }]"
          />

          <wd-input
            label="有效期"
            v-model="formData.expiryDate"
            placeholder="请输入有效期 (如: 06/24)"
            required
            clearable
            :maxlength="5"
            prop="expiryDate"
            :rules="expiryDateRules"
          >
            <template #suffix>
              <text class="text-xs text-gray-500">MM/YY</text>
            </template>
          </wd-input>

          <wd-select-picker
            label="卡片类型"
            v-model="formData.cardType"
            :columns="cardTypeColumns"
            type="radio"
            required
            prop="cardType"
            :rules="[{ required: true, message: '请选择卡片类型' }]"
            @change="onCardTypeChange"
          />
        </view>

        <!-- 额度信息 -->
        <view class="form-section">
          <view class="section-title">
            <text>额度信息</text>
          </view>

          <wd-input
            label="授信额度 (¥)"
            v-model.number="formData.creditLimit"
            placeholder="0"
            type="number"
            prop="creditLimit"
          />

          <wd-input
            label="已用额度 (¥)"
            v-model.number="formData.usedAmount"
            placeholder="0"
            type="number"
            prop="usedAmount"
          />
        </view>

        <!-- 账单设置 -->
        <view class="form-section">
          <view class="section-title">
            <text>账单设置</text>
          </view>

          <wd-select-picker
            label="账单日"
            v-model="formData.billDay"
            :columns="billDayColumns"
            type="radio"
            prop="billDay"
            @change="onBillDayChange"
          />

          <wd-select-picker
            label="还款日"
            v-model="formData.dueDate"
            :columns="dueDayColumns"
            type="radio"
            prop="dueDate"
            @change="onDueDayChange"
          />
        </view>

        <!-- 年费信息 -->
        <view class="form-section">
          <view class="section-title">
            <text>年费信息</text>
          </view>

          <wd-input
            label="年费金额 (¥)"
            v-model.number="formData.annualFee"
            placeholder="0"
            type="number"
            prop="annualFee"
          >
            <template #suffix>
              <text class="text-sm text-gray-500">免首年年费</text>
            </template>
          </wd-input>

          <wd-select-picker
            label="年费类型"
            v-model="formData.annualFeeType"
            :columns="annualFeeTypeColumns"
            type="radio"
            prop="annualFeeType"
            @change="onAnnualFeeTypeChange"
          />

          <!-- 条件字段根据年费类型显示 -->
          <wd-input
            v-if="formData.annualFeeType === '刷卡次数达标'"
            label="所需刷卡次数"
            v-model.number="formData.requiredSwipeCount"
            placeholder="请输入所需刷卡次数"
            type="number"
            prop="requiredSwipeCount"
          />

          <wd-input
            v-if="formData.annualFeeType === '刷卡金额达标'"
            label="所需刷卡金额 (¥)"
            v-model.number="formData.requiredSwipeAmount"
            placeholder="请输入所需刷卡金额"
            type="number"
            prop="requiredSwipeAmount"
          />

          <wd-input
            v-if="formData.annualFeeType === '积分兑换'"
            label="所需积分"
            v-model.number="formData.requiredPoints"
            placeholder="请输入所需积分"
            type="number"
            prop="requiredPoints"
          />

          <wd-cell v-if="formData.annualFeeType === '积分兑换'" title="积分兑换比率" custom>
            <view class="flex items-center gap-2">
              <text class="text-sm text-gray-600">1元 =</text>
              <wd-input
                v-model.number="formData.pointsPerYuan"
                placeholder="1"
                type="number"
                style="width: 80px"
                no-border
                prop="pointsPerYuan"
              />
              <text class="text-sm text-gray-600">积分</text>
            </view>
          </wd-cell>

          <wd-cell v-if="formData.annualFeeType === '积分兑换'" title="积分价值" custom>
            <view class="flex items-center gap-2">
              <text class="text-sm text-gray-600">1积分 =</text>
              <wd-input
                v-model.number="formData.yuanPerPoint"
                placeholder="1"
                type="number"
                style="width: 80px"
                no-border
                prop="yuanPerPoint"
              />
              <text class="text-sm text-gray-600">元</text>
            </view>
          </wd-cell>

          <wd-picker
            label="年费扣款时间"
            v-model="formData.annualFeeDate"
            :columns="annualFeeDateColumns"
            placeholder="请选择年费扣款时间"
            prop="annualFeeDate"
            @change="onAnnualFeeDateChange"
          />
        </view>

        <!-- 底部间距 -->
        <view class="h-20"></view>
      </wd-form>

      <!-- 删除按钮 -->
      <view class="delete-section mx-4 mb-6">
        <wd-button
          type="error"
          block
          :loading="deleteCardMutation.isPending.value"
          @click="handleDelete"
        >
          {{ deleteCardMutation.isPending.value ? '删除中...' : '删除信用卡' }}
        </wd-button>
      </view>
    </view>

    <!-- Toast 组件 -->
    <wd-toast />
  </view>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useToast } from 'wot-design-uni'
import { smartGoBack } from '@/utils'
import {
  getBanksApiV1UserCardsBanksListGetQueryOptions,
  getCreditCardApiV1UserCardsCardIdGetQueryOptions,
  useUpdateCreditCardApiV1UserCardsCardIdPutMutation,
  useDeleteCreditCardApiV1UserCardsCardIdDeleteMutation,
} from '@/service/app/v1Yonghugongneng.vuequery'
import type { CreditCard } from '@/types/card'
import type * as API from '@/service/app/types'

const toast = useToast()

// 获取路由参数
const pages = getCurrentPages()
const currentPage = pages[pages.length - 1]
const cardId = (currentPage as any).options?.id || ''

if (!cardId) {
  toast.error('缺少信用卡ID参数')
  smartGoBack()
}

// 表单引用
const form = ref()

// 表单数据
const formData = reactive({
  selectedBankId: '', // 选中的银行ID
  bankName: '招商银行',
  cardName: '全币种国际卡',
  cardNumber: '',
  cardType: 'visa',
  expiryDate: '', // 有效期 MM/YY 格式
  creditLimit: 0,
  usedAmount: 0,
  billDay: 1,
  dueDate: 1,
  annualFee: 0,
  annualFeeType: '刚性年费',
  annualFeeDate: [1, 1], // 年费扣款时间（月日）- 默认1月1日
  // 年费达标条件
  requiredSwipeCount: 0,
  requiredSwipeAmount: 0,
  requiredPoints: 0,
  // 积分兑换比率
  pointsPerYuan: 1, // 每元对应积分数
  yuanPerPoint: 1, // 每积分对应金额
  bankColor: '#3B82F6',
  isEnabled: true,
})

// 获取信用卡详情
const {
  data: cardResponse,
  isLoading,
  isError,
  refetch,
} = useQuery({
  ...getCreditCardApiV1UserCardsCardIdGetQueryOptions({
    params: {
      card_id: cardId,
    },
  }),
  enabled: !!cardId,
})

// 使用Vue Query获取银行列表
const {
  data: banksResponse,
  isLoading: isBanksLoading,
  isError: isBanksError,
} = useQuery({
  ...getBanksApiV1UserCardsBanksListGetQueryOptions({
    params: {
      active_only: true, // 只获取激活的银行
    },
  }),
})

// 更新信用卡的mutation
const updateCardMutation = useUpdateCreditCardApiV1UserCardsCardIdPutMutation({
  onSuccess: (response) => {
    console.log('更新信用卡成功:', response)
    toast.success('信用卡更新成功！')

    // 延迟返回上一页，让用户看到成功提示
    setTimeout(() => {
      smartGoBack()
    }, 1500)
  },
  onError: (error) => {
    console.error('更新信用卡失败:', error)
    toast.error('更新信用卡失败，请重试')
  },
})

// 删除信用卡的mutation
const deleteCardMutation = useDeleteCreditCardApiV1UserCardsCardIdDeleteMutation({
  onSuccess: () => {
    console.log('删除信用卡成功')
    toast.success('信用卡删除成功！')

    // 延迟返回上一页，让用户看到成功提示
    setTimeout(() => {
      smartGoBack()
    }, 1500)
  },
  onError: (error) => {
    console.error('删除信用卡失败:', error)
    toast.error('删除信用卡失败，请重试')
  },
})

// 银行数据处理
const banksData = computed(() => {
  if (!banksResponse.value) {
    return []
  }

  // 检查响应数据结构
  let banks = null
  if (banksResponse.value.data && Array.isArray(banksResponse.value.data)) {
    banks = banksResponse.value.data
  } else if (Array.isArray(banksResponse.value)) {
    banks = banksResponse.value
  }

  return banks || []
})

// 银行选择器数据
const bankColumns = computed(() => {
  return banksData.value.map((bank: any) => ({
    value: bank.id,
    label: bank.bank_name,
  }))
})

// 年费扣款时间显示格式
const annualFeeDateDisplay = computed(() => {
  if (Array.isArray(formData.annualFeeDate) && formData.annualFeeDate.length === 2) {
    const [month, day] = formData.annualFeeDate
    return `${month}月${day}日`
  }
  return '请选择'
})

// 卡片颜色选项
const cardColors = ref([
  '#3B82F6',
  '#EF4444',
  '#10B981',
  '#F59E0B',
  '#8B5CF6',
  '#EC4899',
  '#06B6D4',
  '#84CC16',
])

// 卡片类型值映射函数 - 将API返回的值映射到选择器的值
const mapCardTypeValue = (apiValue: string): string => {
  // API可能返回的值映射到选择器的值
  const mapping: Record<string, string> = {
    VISA: 'visa',
    visa: 'visa',
    Visa: 'visa',
    MASTERCARD: 'mastercard',
    mastercard: 'mastercard',
    MasterCard: 'mastercard',
    UNIONPAY: 'unionpay',
    unionpay: 'unionpay',
    银联: 'unionpay',
    AMERICAN_EXPRESS: 'americanexpress',
    americanexpress: 'americanexpress',
    'American Express': 'americanexpress',
    AMEX: 'americanexpress',
  }

  const mappedValue = mapping[apiValue] || apiValue.toLowerCase()
  console.log('卡片类型值映射:', apiValue, '->', mappedValue)
  return mappedValue
}

// 选择器数据 - 正确的格式
const cardTypeColumns = ref([
  { value: 'visa', label: 'Visa' },
  { value: 'mastercard', label: 'MasterCard' },
  { value: 'unionpay', label: '银联' },
  { value: 'americanexpress', label: 'American Express' },
])

const billDayColumns = ref(
  Array.from({ length: 31 }, (_, i) => ({
    value: i + 1,
    label: `${i + 1}日`,
  })),
)

const dueDayColumns = ref(
  Array.from({ length: 31 }, (_, i) => ({
    value: i + 1,
    label: `${i + 1}日`,
  })),
)

const annualFeeTypeColumns = ref([
  { value: '刚性年费', label: '刚性年费' },
  { value: '刷卡次数达标', label: '刷卡次数达标' },
  { value: '刷卡金额达标', label: '刷卡金额达标' },
  { value: '积分兑换', label: '积分兑换' },
])

// 年费扣款时间选择器数据 - 月日选择
const annualFeeDateColumns = ref([
  // 月份列
  Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: `${i + 1}月`,
  })),
  // 日期列
  Array.from({ length: 31 }, (_, i) => ({
    value: i + 1,
    label: `${i + 1}日`,
  })),
])

// 获取卡片类型图标
const getCardTypeIcon = (type: string) => {
  switch (type) {
    case 'visa':
      return 'V'
    case 'mastercard':
      return 'M'
    case 'unionpay':
      return 'U'
    case 'americanexpress':
      return 'A'
    default:
      return 'C'
  }
}

// 获取卡片渐变背景
const getCardGradient = (color: string) => {
  const baseColor = color
  const darkerColor = darkenColor(color, 20)
  return `linear-gradient(135deg, ${baseColor} 0%, ${darkerColor} 100%)`
}

// 颜色加深函数
const darkenColor = (color: string, percent: number) => {
  const hex = color.replace('#', '')
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)

  const newR = Math.max(0, Math.floor((r * (100 - percent)) / 100))
  const newG = Math.max(0, Math.floor((g * (100 - percent)) / 100))
  const newB = Math.max(0, Math.floor((b * (100 - percent)) / 100))

  return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`
}

// 事件处理
const handleBack = () => {
  smartGoBack()
}

const handleSave = () => {
  // 使用表单校验
  form.value
    .validate()
    .then(({ valid, errors }) => {
      if (valid) {
        // 解析有效期 MM/YY 格式
        const [monthStr, yearStr] = formData.expiryDate.split('/')
        const expiryMonth = parseInt(monthStr, 10)
        const expiryYear = parseInt(yearStr, 10)

        // 将YY转换为完整年份
        const currentYear = new Date().getFullYear()
        const currentCentury = Math.floor(currentYear / 100) * 100
        let fullYear = currentCentury + expiryYear
        if (expiryYear < currentYear % 100) {
          fullYear += 100
        }

        // 构建API请求数据
        const cardData: API.CreditCardUpdate = {
          card_name: formData.cardName,
          card_type: formData.cardType,
          bank_color: formData.bankColor,
          credit_limit: formData.creditLimit,
          used_limit: formData.usedAmount,
          expiry_month: expiryMonth,
          expiry_year: fullYear,
          billing_date: formData.billDay,
          due_date: formData.dueDate,
          annual_fee: formData.annualFee,
          fee_waivable: formData.annualFeeType !== '刚性年费',
          fee_auto_deduct: true,
          fee_due_month: Array.isArray(formData.annualFeeDate) ? formData.annualFeeDate[0] : 1,
          features: [], // 可以根据需要添加特色功能
          points_rate: formData.pointsPerYuan,
          cashback_rate: 0, // 可以根据需要设置
          is_primary: true, // 默认为主卡
          notes: `年费类型: ${formData.annualFeeType}${
            formData.annualFeeType === '刷卡次数达标'
              ? `，需刷卡${formData.requiredSwipeCount}次`
              : formData.annualFeeType === '刷卡金额达标'
                ? `，需刷卡${formData.requiredSwipeAmount}元`
                : formData.annualFeeType === '积分兑换'
                  ? `，需${formData.requiredPoints}积分`
                  : ''
          }`,
          status: formData.isEnabled ? 'active' : 'frozen',
        }

        console.log('准备更新信用卡:', cardData)

        // 调用API更新信用卡
        updateCardMutation.mutate({
          params: {
            card_id: cardId,
          },
          body: cardData,
        })
      } else {
        console.log('表单校验失败:', errors)
        // 显示第一个错误信息
        if (errors && errors.length > 0) {
          toast.error(errors[0].message)
        }
      }
    })
    .catch((error) => {
      console.log('表单校验异常:', error)
      toast.error('表单校验失败')
    })
}

const handleEditCard = () => {
  toast.show('编辑卡片样式')
}

// 有效期校验函数
const validateExpiryDate = (value: string): string => {
  console.log('开始校验有效期:', value)

  if (!value) {
    return '请输入有效期'
  }

  // 检查格式是否为 MM/YY
  const formatRegex = /^\d{2}\/\d{2}$/
  if (!formatRegex.test(value)) {
    console.log('格式不正确:', value)
    return '请输入正确的有效期格式 (MM/YY)'
  }

  const [monthStr, yearStr] = value.split('/')
  const month = parseInt(monthStr, 10)
  const yearNum = parseInt(yearStr, 10)

  console.log('解析结果:', { monthStr, yearStr, month, yearNum })

  // 检查月份是否有效
  if (month < 1 || month > 12) {
    console.log('月份无效:', month)
    return '月份必须在01-12之间'
  }

  // 检查年份是否有效（00-99）
  if (yearNum < 0 || yearNum > 99) {
    console.log('年份格式无效:', yearNum)
    return '年份必须在00-99之间'
  }

  // 将YY转换为完整年份（智能判断世纪）
  const currentYear = new Date().getFullYear()
  const currentCentury = Math.floor(currentYear / 100) * 100
  let fullYear = currentCentury + yearNum

  // 如果年份小于当前年份的后两位，认为是下个世纪
  if (yearNum < currentYear % 100) {
    fullYear += 100
  }

  console.log('完整年份:', fullYear)

  // 检查是否已过期
  const currentMonth = new Date().getMonth() + 1 // getMonth() 返回0-11

  if (fullYear < currentYear || (fullYear === currentYear && month < currentMonth)) {
    console.log('已过期')
    return '信用卡已过期'
  }

  // 检查年份是否过于久远
  if (fullYear > currentYear + 20) {
    console.log('年份过于久远:', fullYear)
    return '有效期年份不能超过20年'
  }

  console.log('校验通过')
  return '' // 校验通过
}

// 监听有效期输入变化，自动格式化
let isFormatting = false // 防止循环更新
watch(
  () => formData.expiryDate,
  (newValue, oldValue) => {
    if (isFormatting) return // 如果正在格式化，跳过

    console.log('有效期值变化:', { oldValue, newValue })

    if (typeof newValue === 'string') {
      isFormatting = true

      // 自动格式化输入为 MM/YY 格式
      let formatted = newValue.replace(/\D/g, '') // 只保留数字

      if (formatted.length >= 2) {
        formatted = formatted.substring(0, 2) + '/' + formatted.substring(2, 4)
      }

      // 只有当格式化后的值与当前值不同时才更新
      if (formatted !== newValue) {
        formData.expiryDate = formatted
        console.log('自动格式化为:', formatted)
      }

      isFormatting = false
    }
  },
)

// 选择器事件处理
const onBankChange = ({ value }: any) => {
  formData.selectedBankId = value
  // 根据选中的银行更新银行名称和颜色
  const selectedBank = banksData.value.find((bank: any) => bank.id === value)
  if (selectedBank) {
    formData.bankName = selectedBank.bank_name
    // 可以根据银行设置默认颜色，或者保持用户选择的颜色
    // formData.bankColor = selectedBank.bank_color || formData.bankColor
  }
}

const onCardTypeChange = ({ value }: any) => {
  formData.cardType = value
}

const onBillDayChange = ({ value }: any) => {
  formData.billDay = typeof value === 'number' ? value : parseInt(value)
}

const onDueDayChange = ({ value }: any) => {
  formData.dueDate = typeof value === 'number' ? value : parseInt(value)
}

const onAnnualFeeTypeChange = ({ value }: any) => {
  formData.annualFeeType = value
}

const onAnnualFeeDateChange = ({ value }: any) => {
  // value 是一个数组 [月份, 日期]
  if (Array.isArray(value) && value.length === 2) {
    formData.annualFeeDate = value
    console.log('年费扣款时间:', `${value[0]}月${value[1]}日`)
  }
}

// 颜色选择
const selectColor = (color: string) => {
  formData.bankColor = color
}

// 有效期校验规则
const expiryDateRules = [
  { required: true, message: '请输入有效期' },
  {
    required: false,
    validator: (value: any) => {
      const errorMessage = validateExpiryDate(value)
      return errorMessage === ''
    },
    message: '请输入正确的有效期格式 (MM/YY)',
  },
]

// 监听银行数据变化，确保银行选择器正确显示
watch(
  () => banksData.value,
  (newBanks) => {
    console.log('银行数据变化:', newBanks)

    // 如果已经有选中的银行ID，但银行数据刚加载完成，重新验证
    if (formData.selectedBankId && newBanks.length > 0) {
      const bankExists = newBanks.find((bank: any) => bank.id === formData.selectedBankId)
      if (bankExists) {
        console.log('银行数据加载完成，银行ID验证通过:', bankExists)
        // 强制触发选择器更新
        formData.selectedBankId = formData.selectedBankId
      } else {
        console.log('警告：银行ID在新加载的列表中未找到')
      }
    }
  },
  { immediate: true },
)

// 监听信用卡数据变化，填充表单
watch(
  () => cardResponse.value,
  (newResponse) => {
    console.log('API响应数据变化:', newResponse)

    if (newResponse) {
      // 处理可能的数据包装格式
      let cardData = null

      if (newResponse.data) {
        cardData = newResponse.data
        console.log('从data字段获取卡片数据:', cardData)
      } else if (newResponse.success && newResponse.data) {
        cardData = newResponse.data
        console.log('从包装格式获取卡片数据:', cardData)
      } else {
        cardData = newResponse
        console.log('直接使用响应数据:', cardData)
      }

      if (cardData) {
        fillFormData(cardData)
      } else {
        console.log('未找到有效的卡片数据')
      }
    }
  },
  { immediate: true },
)

// 删除信用卡
const handleDelete = () => {
  // 显示删除确认对话框
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
            card_id: cardId,
          },
        })
      }
    },
  })
}

// 填充表单数据
const fillFormData = (cardData: any) => {
  if (!cardData) {
    console.log('没有卡片数据，跳过填充')
    return
  }

  console.log('开始填充表单数据:', cardData)

  try {
    // 基本信息
    if (cardData.card_name) {
      formData.cardName = cardData.card_name
      console.log('设置卡片名称:', cardData.card_name)
    }

    if (cardData.card_number) {
      formData.cardNumber = cardData.card_number
      console.log('设置卡号:', cardData.card_number)
    }

    if (cardData.card_network) {
      formData.cardType = mapCardTypeValue(cardData.card_network)
      console.log('设置卡片类型:', cardData.card_network, '->', formData.cardType)
    }

    if (cardData.bank_color) {
      formData.bankColor = cardData.bank_color
      console.log('设置银行颜色:', cardData.bank_color)
    }

    if (cardData.credit_limit !== undefined) {
      formData.creditLimit = Number(cardData.credit_limit) || 0
      console.log('设置授信额度:', formData.creditLimit)
    }

    if (cardData.used_limit !== undefined) {
      formData.usedAmount = Number(cardData.used_limit) || 0
      console.log('设置已用额度:', formData.usedAmount)
    }

    if (cardData.billing_date !== undefined) {
      formData.billDay = Number(cardData.billing_date) || 1
      console.log('设置账单日:', formData.billDay)
    }

    if (cardData.due_date !== undefined) {
      formData.dueDate = Number(cardData.due_date) || 1
      console.log('设置还款日:', formData.dueDate)
    }

    if (cardData.annual_fee !== undefined) {
      formData.annualFee = Number(cardData.annual_fee) || 0
      console.log('设置年费:', formData.annualFee)
    }

    if (cardData.points_rate !== undefined) {
      formData.pointsPerYuan = Number(cardData.points_rate) || 1
      console.log('设置积分比率:', formData.pointsPerYuan)
    }

    if (cardData.status) {
      formData.isEnabled = cardData.status === 'active'
      console.log('设置启用状态:', formData.isEnabled)
    }

    // 银行信息
    if (cardData.bank_id) {
      formData.selectedBankId = cardData.bank_id
      console.log('设置银行ID:', cardData.bank_id)

      // 检查银行ID是否在银行列表中存在
      const bankExists = banksData.value.find((bank: any) => bank.id === cardData.bank_id)
      if (bankExists) {
        console.log('银行ID在列表中找到:', bankExists)
      } else {
        console.log('警告：银行ID在列表中未找到，当前银行列表:', banksData.value)
      }
    }

    // 处理银行名称 - 可能在不同的字段中
    if (cardData.bank_name) {
      formData.bankName = cardData.bank_name
      console.log('设置银行名称:', cardData.bank_name)
    } else if (cardData.bank && cardData.bank.bank_name) {
      formData.bankName = cardData.bank.bank_name
      console.log('从嵌套对象设置银行名称:', cardData.bank.bank_name)
    }

    // 有效期处理
    if (cardData.expiry_month && cardData.expiry_year) {
      const month = String(cardData.expiry_month).padStart(2, '0')
      const year = String(cardData.expiry_year).slice(-2)
      formData.expiryDate = `${month}/${year}`
      console.log('设置有效期:', formData.expiryDate)
    }

    // 年费信息
    if (cardData.fee_due_month) {
      formData.annualFeeDate = [Number(cardData.fee_due_month), 1]
      console.log('设置年费扣款时间:', formData.annualFeeDate)
    }

    // 年费类型从备注中解析
    if (cardData.notes && cardData.notes.includes('年费类型:')) {
      const notesParts = cardData.notes.split('年费类型:')[1]
      if (notesParts) {
        const feeType = notesParts.split('，')[0].trim()
        formData.annualFeeType = feeType || '刚性年费'
        console.log('从备注解析年费类型:', formData.annualFeeType)

        // 解析年费条件
        if (notesParts.includes('需刷卡') && notesParts.includes('次')) {
          const match = notesParts.match(/需刷卡(\d+)次/)
          if (match) {
            formData.requiredSwipeCount = parseInt(match[1])
            console.log('解析刷卡次数:', formData.requiredSwipeCount)
          }
        } else if (notesParts.includes('需刷卡') && notesParts.includes('元')) {
          const match = notesParts.match(/需刷卡(\d+)元/)
          if (match) {
            formData.requiredSwipeAmount = parseInt(match[1])
            console.log('解析刷卡金额:', formData.requiredSwipeAmount)
          }
        } else if (notesParts.includes('需') && notesParts.includes('积分')) {
          const match = notesParts.match(/需(\d+)积分/)
          if (match) {
            formData.requiredPoints = parseInt(match[1])
            console.log('解析所需积分:', formData.requiredPoints)
          }
        }
      }
    } else {
      formData.annualFeeType = cardData.fee_waivable ? '刷卡金额达标' : '刚性年费'
      console.log('根据fee_waivable设置年费类型:', formData.annualFeeType)
    }

    console.log('表单数据填充完成:', formData)
  } catch (error) {
    console.error('填充表单数据时出错:', error)
    toast.error('数据加载异常，请重试')
  }
}
</script>

<style lang="scss" scoped>
page {
  height: 100%;
}

.edit-card-page {
  min-height: 100vh;
  background-color: #f8fafc;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 50vh;
  gap: 1rem;
}

.loading-text {
  color: #6b7280;
  font-size: 14px;
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 50vh;
  gap: 1rem;
  padding: 2rem;
}

.error-text {
  color: #ef4444;
  font-size: 16px;
  text-align: center;
}

.form-container {
  min-height: 100vh;
}

.card-preview {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.form-content {
  padding-bottom: env(safe-area-inset-bottom);
}

.form-section {
  margin: 0 1rem 1rem;
  background: white;
  border-radius: 0.75rem;
  overflow: hidden;
}

.section-title {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;

  text {
    font-weight: 600;
    color: #374151;
  }
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  padding: 0.5rem 0;
}

.color-item {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: transform 0.2s ease;

  &:active {
    transform: scale(0.95);
  }

  &.selected::after {
    content: '✓';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 20px;
    font-weight: bold;
  }
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.gap-2 {
  gap: 0.5rem;
}

.h-20 {
  height: 5rem;
}

.text-gray-600 {
  color: #4b5563;
}

.text-gray-500 {
  color: #6b7280;
}

.text-red-500 {
  color: #ef4444;
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

  .mb-6 {
    margin-bottom: 1.5rem;
  }
}
</style>
