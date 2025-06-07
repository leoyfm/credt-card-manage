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
            
            <view class="form-item">
              <text class="label">卡片颜色</text>
              <view class="color-picker">
                <view class="color-grid">
                  <view 
                    v-for="(color, index) in cardColors" 
                    :key="index"
                    :class="['color-item', formData.bankColor === color ? 'selected' : '']"
                    :style="{ backgroundColor: color }"
                    @click="selectColor(color)"
                  ></view>
                </view>
                <view class="mt-3 flex items-center">
                  <text class="text-sm text-gray-600 mr-2">启用此卡片</text>
                  <switch 
                    :checked="formData.isEnabled"
                    @change="onIsEnabledChange"
                    color="#007AFF"
                  />
                </view>
              </view>
            </view>
          </view>

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
                :maxlength="19"
              />
            </view>
            
            <view class="form-item">
              <text class="label">有效期至</text>
              <picker mode="date" :value="formData.expiryDate" @change="onExpiryDateChange">
                <view class="picker-view">
                  <text>{{ formData.expiryDate || '请选择' }}</text>
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
          </view>
    
          <!-- 账单设置 -->
          <view class="form-section">
            <view class="section-title">
              <text>账单设置</text>
            </view>
            
            <view class="form-item">
              <text class="label">账单日</text>
              <picker mode="selector" :range="billDays" :value="billDayIndex" @change="onBillDayChange">
                <view class="picker-view">
                  <text>{{ billDays[billDayIndex] }}</text>
                  <text class="arrow">></text>
                </view>
              </picker>
            </view>
            
            <view class="form-item">
              <text class="label">还款日</text>
              <picker mode="selector" :range="dueDays" :value="dueDayIndex" @change="onDueDayChange">
                <view class="picker-view">
                  <text>{{ dueDays[dueDayIndex] }}</text>
                  <text class="arrow">></text>
                </view>
              </picker>
            </view>
        
          </view>
    
                    <!-- 年费信息 -->
          <view class="form-section">
            <view class="section-title">
              <text>年费信息</text>
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
              <text class="label">年费类型</text>
              <picker mode="selector" :range="annualFeeTypes" :value="annualFeeTypeIndex" @change="onAnnualFeeTypeChange">
                <view class="picker-view">
                  <text>{{ annualFeeTypes[annualFeeTypeIndex] }}</text>
                  <text class="arrow">></text>
                </view>
              </picker>
            </view>

            <!-- 条件字段根据年费类型显示 -->
            <view v-if="formData.annualFeeType === '刷卡次数达标'" class="form-item">
              <text class="label">所需刷卡次数</text>
              <input 
                class="input"
                v-model.number="formData.requiredSwipeCount"
                placeholder="请输入所需刷卡次数"
                type="number"
              />
            </view>

            <view v-if="formData.annualFeeType === '刷卡金额达标'" class="form-item">
              <text class="label">所需刷卡金额 (¥)</text>
              <input 
                class="input"
                v-model.number="formData.requiredSwipeAmount"
                placeholder="请输入所需刷卡金额"
                type="number"
              />
            </view>

            <view v-if="formData.annualFeeType === '积分兑换'" class="form-item">
              <text class="label">所需积分</text>
              <input 
                class="input"
                v-model.number="formData.requiredPoints"
                placeholder="请输入所需积分"
                type="number"
              />
            </view>

            <view v-if="formData.annualFeeType === '积分兑换'" class="form-item">
              <text class="label">积分兑换比率</text>
              <view class="flex items-center gap-2">
                <text class="text-sm text-gray-600">1元 = </text>
                <input 
                  class="input"
                  style="flex: 0 0 80px;"
                  v-model.number="formData.pointsPerYuan"
                  placeholder="1"
                  type="number"
                />
                <text class="text-sm text-gray-600">积分</text>
              </view>
            </view>

            <view v-if="formData.annualFeeType === '积分兑换'" class="form-item">
              <text class="label">积分价值</text>
              <view class="flex items-center gap-2">
                <text class="text-sm text-gray-600">1积分 = </text>
                <input 
                  class="input"
                  style="flex: 0 0 80px;"
                  v-model.number="formData.yuanPerPoint"
                  placeholder="1"
                  type="number"
                  step="0.01"
                />
                <text class="text-sm text-gray-600">元</text>
              </view>
            </view>

            <view class="form-item">
              <text class="label">年费开始时间</text>
              <picker mode="date" :value="formData.annualFeeStartDate" @change="onAnnualFeeStartDateChange">
                <view class="picker-view">
                  <text>{{ formData.annualFeeStartDate || '请选择' }}</text>
                  <text class="arrow">></text>
                </view>
              </picker>
            </view>

            <view class="form-item">
                <text class="label">年费结束时间</text>
                <picker mode="date" :value="formData.annualFeeEndDate" @change="onAnnualFeeEndDateChange">
                    <view class="picker-view">
                        <text>{{ formData.annualFeeEndDate || '请选择' }}</text>
                        <text class="arrow">></text>
                    </view>
                </picker>
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
      expiryDate: '12/25',
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
    
    // 选择器数据
    const cardTypes = ref(['Visa', 'MasterCard', '银联', 'American Express'])
    const cardTypeIndex = ref(0)
    
    const billDays = ref(Array.from({length: 31}, (_, i) => `${i + 1}日`))
    const billDayIndex = ref(0)
    
    const dueDays = ref(Array.from({length: 31}, (_, i) => `${i + 1}日`))
    const dueDayIndex = ref(0)
    
    const annualFeeTypes = ref(['刚性年费', '刷卡次数达标', '刷卡金额达标', '积分兑换'])
    const annualFeeTypeIndex = ref(0)
    
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
    
    // 获取卡片渐变背景
    const getCardGradient = (color: string) => {
      // 创建渐变效果，从选择的颜色到稍深的版本
      const baseColor = color
      const darkerColor = darkenColor(color, 20)
      return `linear-gradient(135deg, ${baseColor} 0%, ${darkerColor} 100%)`
    }
    
    // 颜色加深函数
    const darkenColor = (color: string, percent: number) => {
      // 将十六进制颜色转换为RGB
      const hex = color.replace('#', '')
      const r = parseInt(hex.substr(0, 2), 16)
      const g = parseInt(hex.substr(2, 2), 16)
      const b = parseInt(hex.substr(4, 2), 16)
      
      // 减少亮度
      const newR = Math.max(0, Math.floor(r * (100 - percent) / 100))
      const newG = Math.max(0, Math.floor(g * (100 - percent) / 100))
      const newB = Math.max(0, Math.floor(b * (100 - percent) / 100))
      
      // 转换回十六进制
      return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`
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
        isActive: formData.isEnabled,
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
    const onExpiryDateChange = (e: any) => {
      formData.expiryDate = e.detail.value
    }
    
    const onCardTypeChange = (e: any) => {
      cardTypeIndex.value = e.detail.value
      formData.cardType = cardTypes.value[e.detail.value].toLowerCase()
    }
    
    const onBillDayChange = (e: any) => {
      billDayIndex.value = e.detail.value
      formData.billDay = e.detail.value + 1
    }
    
    const onDueDayChange = (e: any) => {
      dueDayIndex.value = e.detail.value
      formData.dueDate = e.detail.value + 1
    }
    
    const onAnnualFeeTypeChange = (e: any) => {
      annualFeeTypeIndex.value = e.detail.value
      formData.annualFeeType = annualFeeTypes.value[e.detail.value]
    }
    
    const onAnnualFeeStartDateChange = (e: any) => {
      formData.annualFeeStartDate = e.detail.value
    }
    
    const onAnnualFeeEndDateChange = (e: any) => {
      formData.annualFeeEndDate = e.detail.value
    }
    
    const onIsEnabledChange = (e: any) => {
      formData.isEnabled = e.detail.value
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
    
    .color-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
      margin-top: 0.5rem;
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
    
    .gap-2 {
      gap: 0.5rem;
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
    
    .text-gray-600 {
      color: #4b5563;
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