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
            <view class="p-2" @click="handleSave">
              <text class="text-blue-600 font-medium">保存</text>
            </view>
          </view>
        </view>
    
        <!-- 信用卡预览 -->
        <view class="mx-4 mt-4 mb-6">
          <view class="card-preview relative bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-6 text-white">
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
          <!-- 基本信息 -->
          <view class="form-section">
            <view class="section-title">
              <text>基本信息</text>
            </view>
            
            <view class="form-item">
              <text class="label">卡片名称</text>
              <input 
                class="input"
                v-model="formData.cardName"
                placeholder="请输入卡片名称"
              />
              <text class="required">*</text>
            </view>
            
            <view class="form-item">
              <text class="label">卡号</text>
              <input 
                class="input"
                v-model="formData.cardNumber"
                placeholder="请输入完整卡号"
                maxlength="19"
              />
            </view>
            
            <view class="form-item">
              <text class="label">生效期限</text>
              <picker mode="date" :value="formData.effectiveDate" @change="onEffectiveDateChange">
                <view class="picker-view">
                  <text>{{ formData.effectiveDate || '请选择' }}</text>
                  <text class="arrow">></text>
                </view>
              </picker>
            </view>
            
            <view class="form-item">
              <text class="label">卡片类型</text>
              <picker mode="selector" :range="cardTypes" :value="cardTypeIndex" @change="onCardTypeChange">
                <view class="picker-view">
                  <text>{{ cardTypes[cardTypeIndex] }}</text>
                  <text class="arrow">></text>
                </view>
              </picker>
              <text class="required">*</text>
            </view>
          </view>
    
          <!-- 额度信息 -->
          <view class="form-section">
            <view class="section-title">
              <text>额度信息</text>
            </view>
            
            <view class="form-item">
              <text class="label">授信额度 (¥)</text>
              <input 
                class="input"
                v-model.number="formData.creditLimit"
                placeholder="0"
                type="number"
              />
            </view>
            
            <view class="form-item">
              <text class="label">已用额度 (¥)</text>
              <input 
                class="input"
                v-model.number="formData.usedAmount"
                placeholder="0"
                type="number"
              />
            </view>
            
            <view class="form-item">
              <text class="label">最低还款额度 (¥)</text>
              <input 
                class="input"
                v-model.number="formData.minimumPayment"
                placeholder="0"
                type="number"
              />
            </view>
          </view>
    
          <!-- 还款信息 -->
          <view class="form-section">
            <view class="section-title">
              <text>还款信息</text>
            </view>
            
            <view class="form-item">
              <text class="label">主体类型 (期数)</text>
              <picker mode="selector" :range="repaymentTerms" :value="repaymentTermIndex" @change="onRepaymentTermChange">
                <view class="picker-view">
                  <text>{{ repaymentTerms[repaymentTermIndex] }}</text>
                  <text class="arrow">></text>
                </view>
              </picker>
            </view>
            
            <view class="form-item">
              <text class="label">还款日 (%)</text>
              <input 
                class="input"
                v-model.number="formData.dueDate"
                placeholder="0"
                type="number"
              />
            </view>
            
            <view class="form-item">
              <text class="label">上次还款日</text>
              <picker mode="date" :value="formData.lastPaymentDate" @change="onLastPaymentDateChange">
                <view class="picker-view">
                  <text>{{ formData.lastPaymentDate || '2024/06/07' }}</text>
                  <text class="arrow">></text>
                </view>
              </picker>
            </view>
          </view>
    
          <!-- 费用信息 -->
          <view class="form-section">
            <view class="section-title">
              <text>费用信息</text>
            </view>
            
            <view class="form-item">
              <text class="label">免费期 (期数)</text>
              <picker mode="selector" :range="gracePeriods" :value="gracePeriodIndex" @change="onGracePeriodChange">
                <view class="picker-view">
                  <text>{{ gracePeriods[gracePeriodIndex] }}</text>
                  <text class="arrow">></text>
                </view>
              </picker>
            </view>
            
            <view class="form-item">
              <text class="label">年费金额 (¥)</text>
              <view class="flex justify-between items-center">
                <input 
                  class="input flex-1"
                  v-model.number="formData.annualFee"
                  placeholder="0"
                  type="number"
                />
                <text class="text-sm text-gray-500 ml-2">免首年年费</text>
              </view>
            </view>
            
            <view class="form-item">
              <text class="label">还款方式</text>
              <picker mode="selector" :range="paymentMethods" :value="paymentMethodIndex" @change="onPaymentMethodChange">
                <view class="picker-view">
                  <text>{{ paymentMethods[paymentMethodIndex] }}</text>
                  <text class="arrow">></text>
                </view>
              </picker>
            </view>
            
            <view class="form-item">
              <text class="label">所属机构</text>
              <input 
                class="input"
                v-model="formData.institution"
                placeholder="请输入所属机构"
              />
            </view>
          </view>
    
          <!-- 手续设置 -->
          <view class="form-section">
            <view class="section-title">
              <text>手续设置</text>
            </view>
            
            <view class="form-item">
              <text class="label">手续费 (¥)</text>
              <input 
                class="input"
                v-model.number="formData.serviceFee"
                placeholder="0"
                type="number"
              />
            </view>
            
            <view class="form-item">
              <text class="label">手续费类别</text>
              <picker mode="selector" :range="feeCategories" :value="feeCategoryIndex" @change="onFeeCategoryChange">
                <view class="picker-view">
                  <text>{{ feeCategories[feeCategoryIndex] }}</text>
                  <text class="arrow">></text>
                </view>
              </picker>
            </view>
            
            <view class="form-item">
              <text class="label">收费方式</text>
              <input 
                class="input"
                v-model="formData.chargeMethod"
                placeholder="请输入收费方式"
              />
            </view>
            
            <view class="form-item">
              <text class="label">上次手续费日期</text>
              <view class="flex gap-4">
                <picker mode="date" :value="formData.lastFeeDate1" @change="onLastFeeDate1Change">
                  <view class="picker-view flex-1">
                    <text>{{ formData.lastFeeDate1 || 'yyyy/mm/dd' }}</text>
                    <text class="arrow">></text>
                  </view>
                </picker>
                <picker mode="date" :value="formData.lastFeeDate2" @change="onLastFeeDate2Change">
                  <view class="picker-view flex-1">
                    <text>{{ formData.lastFeeDate2 || 'yyyy/mm/dd' }}</text>
                    <text class="arrow">></text>
                  </view>
                </picker>
              </view>
            </view>
          </view>
    
          <!-- 手费设置 -->
          <view class="form-section">
            <view class="section-title">
              <text>手费设置</text>
            </view>
            
            <view class="form-item">
              <text class="label">手续费收费费率 (%)</text>
              <view class="flex gap-4">
                <input 
                  class="input flex-1"
                  v-model.number="formData.feeRate1"
                  placeholder="1"
                  type="number"
                />
                <input 
                  class="input flex-1"
                  v-model.number="formData.feeRate2"
                  placeholder="0"
                  type="number"
                />
              </view>
            </view>
            
            <view class="form-item">
              <text class="label">手续费条件费率 (%)</text>
              <view class="flex gap-4">
                <input 
                  class="input flex-1"
                  v-model.number="formData.conditionalRate1"
                  placeholder="1"
                  type="number"
                />
                <input 
                  class="input flex-1"
                  v-model.number="formData.conditionalRate2"
                  placeholder="0"
                  type="number"
                />
              </view>
            </view>
            
            <view class="form-item">
              <text class="label">逾期费 (¥)</text>
              <view class="flex gap-4">
                <input 
                  class="input flex-1"
                  v-model.number="formData.lateFee1"
                  placeholder="0"
                  type="number"
                />
                <input 
                  class="input flex-1"
                  v-model.number="formData.lateFee2"
                  placeholder="60"
                  type="number"
                />
              </view>
            </view>
            
            <view class="form-item">
              <text class="label">违约费 (¥)</text>
              <view class="flex gap-4">
                <input 
                  class="input flex-1"
                  v-model.number="formData.penaltyFee1"
                  placeholder="60"
                  type="number"
                />
                <input 
                  class="input flex-1"
                  v-model.number="formData.penaltyFee2"
                  placeholder="3"
                  type="number"
                />
              </view>
            </view>
            
            <view class="form-item">
              <text class="label">年费 (¥)</text>
              <view class="flex gap-4">
                <input 
                  class="input flex-1"
                  v-model.number="formData.annualFeeAmount1"
                  placeholder="90"
                  type="number"
                />
                <input 
                  class="input flex-1"
                  v-model.number="formData.annualFeeAmount2"
                  placeholder="90"
                  type="number"
                />
              </view>
            </view>
          </view>
    
          <!-- 其他设置 -->
          <view class="form-section">
            <view class="section-title">
              <text>其他设置</text>
            </view>
            
            <view class="form-item">
              <text class="label">卡片颜色</text>
              <view class="color-picker">
                <view class="flex flex-wrap gap-3 mt-2">
                  <view 
                    v-for="(color, index) in cardColors" 
                    :key="index"
                    :class="['color-item', formData.bankColor === color ? 'selected' : '']"
                    :style="{ backgroundColor: color }"
                    @click="selectColor(color)"
                  ></view>
                </view>
                <view class="mt-3 flex items-center">
                  <text class="text-sm text-gray-600 mr-2">按标准方式</text>
                  <switch 
                    :checked="formData.useStandardStyle"
                    @change="onUseStandardStyleChange"
                    color="#007AFF"
                  />
                </view>
              </view>
            </view>
          </view>
    
          <!-- 底部间距 -->
          <view class="h-20"></view>
        </scroll-view>
      </view>
    </template>
    
    <script lang="ts" setup>
    import { ref, reactive } from 'vue'
    import type { CreditCard } from '@/types/card'
    
    // 表单数据
    const formData = reactive({
      bankName: '招商银行',
      cardName: '全币种国际卡',
      cardNumber: '',
      cardType: 'visa',
      effectiveDate: '',
      expiryDate: '12/25',
      creditLimit: 0,
      usedAmount: 0,
      minimumPayment: 0,
      dueDate: 0,
      lastPaymentDate: '',
      annualFee: 0,
      institution: '',
      serviceFee: 0,
      chargeMethod: '',
      lastFeeDate1: '',
      lastFeeDate2: '',
      feeRate1: 1,
      feeRate2: 0,
      conditionalRate1: 1,
      conditionalRate2: 0,
      lateFee1: 0,
      lateFee2: 60,
      penaltyFee1: 60,
      penaltyFee2: 3,
      annualFeeAmount1: 90,
      annualFeeAmount2: 90,
      bankColor: '#3B82F6',
      useStandardStyle: true
    })
    
    // 选择器数据
    const cardTypes = ref(['Visa', 'MasterCard', 'UnionPay', 'American Express'])
    const cardTypeIndex = ref(0)
    
    const repaymentTerms = ref(['1期', '3期', '6期', '12期', '24期'])
    const repaymentTermIndex = ref(0)
    
    const gracePeriods = ref(['20天', '25天', '50天', '56天'])
    const gracePeriodIndex = ref(0)
    
    const paymentMethods = ref(['自动扣款', '主动还款', '银行转账'])
    const paymentMethodIndex = ref(0)
    
    const feeCategories = ref(['取现手续费', '分期手续费', '其他费用'])
    const feeCategoryIndex = ref(0)
    
    // 卡片颜色选项
    const cardColors = ref([
      '#3B82F6', '#EF4444', '#10B981', '#F59E0B',
      '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
    ])
    
    // 获取卡片类型图标
    const getCardTypeIcon = (type: string) => {
      switch (type) {
        case 'visa': return 'V'
        case 'mastercard': return 'M'
        case 'unionpay': return 'U'
        default: return 'C'
      }
    }
    
    // 事件处理
    const handleBack = () => {
      uni.navigateBack()
    }
    
    const handleSave = () => {
      // 验证必填字段
      if (!formData.cardName || !formData.cardNumber) {
        uni.showToast({
          title: '请填写必填信息',
          icon: 'none'
        })
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
        isActive: true,
        annualFeeStatus: 'pending',
        feeType: 'waivable',
        waiverProgress: 0,
        annualFee: formData.annualFee,
        dueDate: formData.dueDate,
        bankColor: formData.bankColor,
        bankCode: formData.bankName.charAt(0)
      }
      
      // 这里应该调用API保存数据
      console.log('Saving card:', newCard)
      
      uni.showToast({
        title: '保存成功',
        icon: 'success'
      })
      
      setTimeout(() => {
        uni.navigateBack()
      }, 1500)
    }
    
    const handleEditCard = () => {
      uni.showToast({
        title: '编辑卡片样式',
        icon: 'none'
      })
    }
    
    // 选择器变化事件
    const onEffectiveDateChange = (e: any) => {
      formData.effectiveDate = e.detail.value
    }
    
    const onCardTypeChange = (e: any) => {
      cardTypeIndex.value = e.detail.value
      formData.cardType = cardTypes.value[e.detail.value].toLowerCase()
    }
    
    const onRepaymentTermChange = (e: any) => {
      repaymentTermIndex.value = e.detail.value
    }
    
    const onLastPaymentDateChange = (e: any) => {
      formData.lastPaymentDate = e.detail.value
    }
    
    const onGracePeriodChange = (e: any) => {
      gracePeriodIndex.value = e.detail.value
    }
    
    const onPaymentMethodChange = (e: any) => {
      paymentMethodIndex.value = e.detail.value
    }
    
    const onFeeCategoryChange = (e: any) => {
      feeCategoryIndex.value = e.detail.value
    }
    
    const onLastFeeDate1Change = (e: any) => {
      formData.lastFeeDate1 = e.detail.value
    }
    
    const onLastFeeDate2Change = (e: any) => {
      formData.lastFeeDate2 = e.detail.value
    }
    
    const onUseStandardStyleChange = (e: any) => {
      formData.useStandardStyle = e.detail.value
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
      background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
      box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
    }
    
    .form-section {
      margin: 0 1rem 1rem;
      background: white;
      border-radius: 0.75rem;
      overflow: hidden;
    }
    
    .section-title {
      padding: 1rem;
      background: #f8fafc;
      border-bottom: 1px solid #e2e8f0;
      
      text {
        font-weight: 600;
        color: #374151;
      }
    }
    
    .form-item {
      display: flex;
      align-items: center;
      padding: 1rem;
      border-bottom: 1px solid #f1f5f9;
      
      &:last-child {
        border-bottom: none;
      }
    }
    
    .label {
      width: 120px;
      color: #374151;
      font-size: 14px;
      flex-shrink: 0;
    }
    
    .input {
      flex: 1;
      padding: 0.5rem 0;
      font-size: 14px;
      color: #111827;
      
      &::placeholder {
        color: #9ca3af;
      }
    }
    
    .picker-view {
      flex: 1;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.5rem 0;
      color: #374151;
      
      .arrow {
        color: #9ca3af;
        font-size: 12px;
      }
    }
    
    .required {
      color: #ef4444;
      margin-left: 4px;
    }
    
    .color-picker {
      flex: 1;
    }
    
    .color-item {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      position: relative;
      
      &.selected::after {
        content: '✓';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 16px;
        font-weight: bold;
      }
    }
    
    .flex {
      display: flex;
    }
    
    .flex-1 {
      flex: 1;
    }
    
    .flex-wrap {
      flex-wrap: wrap;
    }
    
    .items-center {
      align-items: center;
    }
    
    .justify-between {
      justify-content: space-between;
    }
    
    .gap-3 {
      gap: 0.75rem;
    }
    
    .gap-4 {
      gap: 1rem;
    }
    
    .mt-2 {
      margin-top: 0.5rem;
    }
    
    .mt-3 {
      margin-top: 0.75rem;
    }
    
    .ml-2 {
      margin-left: 0.5rem;
    }
    
    .mr-2 {
      margin-right: 0.5rem;
    }
    
    .h-20 {
      height: 5rem;
    }
    
    switch {
      transform: scale(0.8);
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