<route lang="json5" type="page">
    {
      style: {
        navigationStyle: 'custom',
        navigationBarTitleText: '添加信用卡',
      },
    }
    </route>
    
    <template>
      <view class="add-card-page bg-gray-50 min-h-screen">
        <!-- 顶部导航栏 -->
        <view class="top-nav bg-white">
          <view class="px-4 py-4 flex items-center justify-between">
            <view class="flex items-center" @click="handleBack">
              <text class="text-lg mr-2">←</text>
              <text class="text-lg font-semibold text-gray-900">添加信用卡</text>
            </view>
            <wd-button type="primary" size="small" @click="handleSave">保存</wd-button>
          </view>
        </view>
    
        <!-- 信用卡预览 -->
        <view class="mx-4 mt-4 mb-6">
          <view 
            class="card-preview relative rounded-xl p-6 text-white"
            :style="{ background: getCardGradient(formData.bankColor) }"
          >
            <view class="flex justify-between items-start mb-4">
              <view>
                <text class="text-lg font-medium">{{ formData.bankName || '招商银行' }}</text>
                <text class="text-sm opacity-90 block mt-1">{{ formData.cardName || '全币种国际卡' }}</text>
              </view>
              <view class="bg-white bg-opacity-20 px-3 py-1 rounded">
                <text class="text-white text-sm" @click="handleEditCard">编辑</text>
              </view>
            </view>
            
            <view class="mb-4">
              <text class="text-base tracking-wider">**** **** **** {{ formData.cardNumber.slice(-4) || '0000' }}</text>
            </view>
            
            <view class="flex justify-between items-end">
              <view>
                <text class="text-xs opacity-75">有效期至</text>
                <text class="text-sm block">{{ formData.expiryDate || '12/25' }}</text>
              </view>
              <view class="w-8 h-8 bg-white bg-opacity-20 rounded flex items-center justify-center">
                <text class="text-white text-xs">{{ getCardTypeIcon(formData.cardType) }}</text>
              </view>
            </view>
          </view>
        </view>
    
        <scroll-view scroll-y class="flex-1">

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
              <wd-switch 
                v-model="formData.isEnabled"
                size="small"
              />
            </wd-cell>
          </view>

          <!-- 基本信息 -->
          <view class="form-section">
            <view class="section-title">
              <text>基本信息</text>
            </view>
            
            <wd-input
              label="卡片名称"
              v-model="formData.cardName"
              placeholder="请输入卡片名称"
              required
              clearable
            />
            
            <wd-input
              label="卡号"
              v-model="formData.cardNumber"
              placeholder="请输入完整卡号"
              clearable
              :maxlength="19"
            />
            
            <wd-datetime-picker
              label="有效期至"
              v-model="formData.expiryDate"
              placeholder="请选择有效期"
              type="date"
            />
            
            <wd-select-picker
              label="卡片类型"
              v-model="formData.cardType"
              :columns="cardTypeColumns"
              type="radio"
              required
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
            />
            
            <wd-input
              label="已用额度 (¥)"
              v-model.number="formData.usedAmount"
              placeholder="0"
              type="number"
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
              @change="onBillDayChange"
            />
            
            <wd-select-picker
              label="还款日"
              v-model="formData.dueDate"
              :columns="dueDayColumns"
              type="radio"
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
              @change="onAnnualFeeTypeChange"
            />

            <!-- 条件字段根据年费类型显示 -->
            <wd-input
              v-if="formData.annualFeeType === '刷卡次数达标'"
              label="所需刷卡次数"
              v-model.number="formData.requiredSwipeCount"
              placeholder="请输入所需刷卡次数"
              type="number"
            />

            <wd-input
              v-if="formData.annualFeeType === '刷卡金额达标'"
              label="所需刷卡金额 (¥)"
              v-model.number="formData.requiredSwipeAmount"
              placeholder="请输入所需刷卡金额"
              type="number"
            />

            <wd-input
              v-if="formData.annualFeeType === '积分兑换'"
              label="所需积分"
              v-model.number="formData.requiredPoints"
              placeholder="请输入所需积分"
              type="number"
            />

            <wd-cell 
              v-if="formData.annualFeeType === '积分兑换'"
              title="积分兑换比率"
              custom
            >
              <view class="flex items-center gap-2">
                <text class="text-sm text-gray-600">1元 = </text>
                <wd-input
                  v-model.number="formData.pointsPerYuan"
                  placeholder="1"
                  type="number"
                  style="width: 80px;"
                  no-border
                />
                <text class="text-sm text-gray-600">积分</text>
              </view>
            </wd-cell>

            <wd-cell 
              v-if="formData.annualFeeType === '积分兑换'"
              title="积分价值"
              custom
            >
              <view class="flex items-center gap-2">
                <text class="text-sm text-gray-600">1积分 = </text>
                <wd-input
                  v-model.number="formData.yuanPerPoint"
                  placeholder="1"
                  type="number"
                  style="width: 80px;"
                  no-border
                />
                <text class="text-sm text-gray-600">元</text>
              </view>
            </wd-cell>

            <wd-datetime-picker
              label="年费开始时间"
              v-model="formData.annualFeeStartDate"
              placeholder="请选择年费开始时间"
              type="date"
            />

            <wd-datetime-picker
              label="年费结束时间"
              v-model="formData.annualFeeEndDate"
              placeholder="请选择年费结束时间"
              type="date"
            />
          </view>
    
                  <!-- 底部间距 -->
        <view class="h-20"></view>
      </scroll-view>
    </view>
    
    <!-- Toast 组件 -->
    <wd-toast />
  </template>
    
    <script lang="ts" setup>
    import { ref, reactive } from 'vue'
    import { useToast } from 'wot-design-uni'
    import type { CreditCard } from '@/types/card'
    
    const toast = useToast()
    
    // 表单数据
    const formData = reactive({
      bankName: '招商银行',
      cardName: '全币种国际卡',
      cardNumber: '',
      cardType: 'visa',
      expiryDate: '',
      creditLimit: 0,
      usedAmount: 0,
      billDay: 1,
      dueDate: 1,
      annualFee: 0,
      annualFeeType: '刚性年费',
      annualFeeStartDate: '',
      annualFeeEndDate: '',
      // 年费达标条件
      requiredSwipeCount: 0,
      requiredSwipeAmount: 0,
      requiredPoints: 0,
      // 积分兑换比率
      pointsPerYuan: 1,        // 每元对应积分数
      yuanPerPoint: 1,         // 每积分对应金额
      bankColor: '#3B82F6',
      isEnabled: true
    })
    
    // 卡片颜色选项
    const cardColors = ref([
      '#3B82F6', '#EF4444', '#10B981', '#F59E0B',
      '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
    ])
    
    // 选择器数据 - 正确的格式
    const cardTypeColumns = ref([
      { value: 'visa', label: 'Visa' },
      { value: 'mastercard', label: 'MasterCard' },
      { value: 'unionpay', label: '银联' },
      { value: 'americanexpress', label: 'American Express' }
    ])
    
    const billDayColumns = ref(
      Array.from({length: 31}, (_, i) => ({
        value: i + 1,
        label: `${i + 1}日`
      }))
    )
    
    const dueDayColumns = ref(
      Array.from({length: 31}, (_, i) => ({
        value: i + 1,
        label: `${i + 1}日`
      }))
    )
    
    const annualFeeTypeColumns = ref([
      { value: '刚性年费', label: '刚性年费' },
      { value: '刷卡次数达标', label: '刷卡次数达标' },
      { value: '刷卡金额达标', label: '刷卡金额达标' },
      { value: '积分兑换', label: '积分兑换' }
    ])
    
    // 获取卡片类型图标
    const getCardTypeIcon = (type: string) => {
      switch (type) {
        case 'visa': return 'V'
        case 'mastercard': return 'M'
        case 'unionpay': return 'U'
        case 'americanexpress': return 'A'
        default: return 'C'
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
      
      const newR = Math.max(0, Math.floor(r * (100 - percent) / 100))
      const newG = Math.max(0, Math.floor(g * (100 - percent) / 100))
      const newB = Math.max(0, Math.floor(b * (100 - percent) / 100))
      
      return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`
    }
    
    // 事件处理
    const handleBack = () => {
      uni.navigateBack()
    }
    
    const handleSave = () => {
      // 验证必填字段
      if (!formData.cardName) {
        toast.error('请填写卡片名称')
        return
      }
      
      if (!formData.cardNumber) {
        toast.error('请填写卡号')
        return
      }
      
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
        bankCode: formData.bankName.charAt(0)
      }
      
      console.log('Saving card:', newCard)
      
      toast.success('保存成功')
      
      setTimeout(() => {
        uni.navigateBack()
      }, 1500)
    }
    
    const handleEditCard = () => {
      toast.show('编辑卡片样式')
    }
    
    // 选择器事件处理
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
    
    // 颜色选择
    const selectColor = (color: string) => {
      formData.bankColor = color
    }
    </script>
    
    <style lang="scss" scoped>
    .add-card-page {
      padding-top: env(safe-area-inset-top);
    }
    
    .top-nav {
      padding-top: env(safe-area-inset-top);
    }
    
    .card-preview {
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
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

// form-section 的 overflow: hidden 和 border-radius 会自动处理所有子元素的圆角
    
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