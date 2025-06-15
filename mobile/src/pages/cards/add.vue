<route lang="json5" type="page">
{
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '添加信用卡',
  },
}
</route>

<template>
  <view class="add-card-page">
    <!-- 顶部导航栏 -->
    <wd-navbar
      title="添加信用卡"
      left-text="返回"
      left-arrow
      right-text="保存"
      fixed
      placeholder
      safe-area-inset-top
      custom-style="height: 60px; line-height: 60px;"
      @click-left="handleBack"
      @click-right="handleSave"
    />

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
          placeholder="请选择发卡银行"
          prop="selectedBankId"
          :rules="[{ required: true, message: '请选择发卡银行' }]"
          @change="onBankChange"
        />

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
  </view>

  <!-- Toast 组件 -->
  <wd-toast />
</template>

<script lang="ts" setup>
import { ref, reactive, computed, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useToast } from 'wot-design-uni'
import { smartGoBack } from '@/utils'
import { getBanksApiV1UserCardsBanksListGetQueryOptions } from '@/service/app/v1Yonghugongneng.vuequery'
import type { CreditCard } from '@/types/card'
import type * as API from '@/service/app/types'

const toast = useToast()

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
        // 构建信用卡对象
        const newCard: Partial<CreditCard> = {
          id: Date.now().toString(),
          bankName: formData.bankName,
          cardName: formData.cardName,
          cardType: formData.cardType as any,
          cardNumberLast4: formData.cardNumber.slice(-4),
          creditLimit: formData.creditLimit,
          usedAmount: formData.usedAmount,
          availableAmount: formData.creditLimit - formData.usedAmount,
          isActive: formData.isEnabled,
          annualFeeStatus: 'pending',
          feeType: 'waivable',
          waiverProgress: 0,
          annualFee: formData.annualFee,
          dueDate: formData.dueDate,
          bankColor: formData.bankColor,
          bankCode: formData.bankName.charAt(0),
        }

        console.log('Saving card:', newCard)

        toast.success('保存成功')

        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
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
</script>

<style lang="scss" scoped>
page {
  height: 100%;
}

.add-card-page {
  min-height: 100vh;
  background-color: #f8fafc;
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
  //   background: #f8fafc;
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

.text-orange-500 {
  color: #f97316;
}

.text-blue-500 {
  color: #3b82f6;
}

.text-green-500 {
  color: #10b981;
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
