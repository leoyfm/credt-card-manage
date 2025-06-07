<route lang="json5" type="page">
{
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '通知设置',
  },
}
</route>

<template>
  <view class="notification-settings bg-gray-50 min-h-screen">
    <!-- 顶部导航栏 -->
    <view class="top-nav bg-white border-b border-gray-100">
      <view class="px-4 py-4 flex items-center justify-between">
        <text class="text-lg font-semibold text-gray-900">通知设置</text>
        <view class="p-2" @click="handleClose">
          <text class="text-gray-600">关闭</text>
        </view>
      </view>
    </view>

    <!-- 通知设置内容 -->
    <view class="mx-4 mt-4">
      <!-- 通知设置标题区域 -->
      <view class="bg-white rounded-lg mb-4">
        <view class="px-4 py-4">
          <view class="flex items-center">
            <text class="text-lg mr-2">🔔</text>
            <text class="font-medium text-gray-800">通知设置</text>
          </view>
        </view>
      </view>

      <!-- 启用通知 -->
      <view class="bg-white rounded-lg mb-4">
        <view class="px-4 py-4">
          <text class="font-medium text-gray-900 block mb-1">启用通知</text>
          <text class="text-sm text-gray-500 mb-4">开启或关闭所有通知</text>
          
          <view class="flex items-center justify-between">
            <text class="text-gray-900">全部通知</text>
            <switch 
              :checked="settings.enableAllNotifications"
              @change="handleToggleAllNotifications"
              color="#007AFF"
            />
          </view>
        </view>
      </view>

      <!-- 还款提醒设置 -->
      <view class="bg-white rounded-lg mb-4">
        <view class="px-4 py-4">
          <text class="font-medium text-gray-900 block mb-4">还款提醒设置</text>
          
          <!-- 还款日提醒开关 -->
          <view class="flex items-center justify-between mb-4">
            <view class="flex items-center">
              <text class="text-lg mr-2">📅</text>
              <text class="text-gray-900">还款日提醒</text>
            </view>
            <switch 
              :checked="settings.paymentReminder"
              @change="handleTogglePaymentReminder"
              color="#007AFF"
            />
          </view>

          <!-- 提前天数设置 -->
          <view v-if="settings.paymentReminder" class="space-y-4">
            <view class="flex items-center justify-between">
              <text class="text-gray-900">提前天数</text>
              <picker 
                mode="selector" 
                :value="dayOptions.indexOf(settings.reminderDays)"
                :range="dayOptions"
                @change="handleDaysChange"
              >
                <view class="flex items-center text-gray-600">
                  <text>{{ settings.reminderDays }}</text>
                  <text class="text-gray-400 ml-1">▼</text>
                </view>
              </picker>
            </view>

            <!-- 提醒时间设置 -->
            <view class="flex items-center justify-between">
              <view class="flex items-center">
                <text class="text-lg mr-2">🕘</text>
                <text class="text-gray-900">提醒时间</text>
              </view>
              <picker 
                mode="time" 
                :value="settings.reminderTime"
                @change="handleTimeChange"
              >
                <view class="flex items-center text-gray-600">
                  <text>{{ settings.reminderTime }}</text>
                  <text class="text-gray-400 ml-1">🕘</text>
                </view>
              </picker>
            </view>
          </view>
        </view>
      </view>

      <!-- 其他通知 -->
      <view class="bg-white rounded-lg mb-4">
        <view class="px-4 py-4">
          <text class="font-medium text-gray-900 block mb-4">其他通知</text>
          
          <!-- 高使用率提醒 -->
          <view class="flex items-center justify-between mb-4">
            <view class="flex items-center">
              <text class="text-lg mr-2">⚠️</text>
              <text class="text-gray-900">高使用率提醒</text>
            </view>
            <switch 
              :checked="settings.highUsageAlert"
              @change="handleToggleHighUsageAlert"
              color="#007AFF"
            />
          </view>

          <!-- 付款确认通知 -->
          <view class="flex items-center justify-between">
            <view class="flex items-center">
              <text class="text-lg mr-2">✅</text>
              <text class="text-gray-900">付款确认通知</text>
            </view>
            <switch 
              :checked="settings.paymentConfirmation"
              @change="handleTogglePaymentConfirmation"
              color="#007AFF"
            />
          </view>
        </view>
      </view>

      <!-- 请求通知权限按钮 -->
      <view class="mt-6 mb-4">
        <view 
          class="bg-gray-900 text-white rounded-lg py-4 text-center"
          @click="handleRequestPermission"
        >
          <text class="text-white font-medium flex items-center justify-center">
            <text class="mr-2">🔔</text>
            <text>请求通知权限</text>
          </text>
        </view>
      </view>

      <!-- 底部说明 -->
      <view class="px-4 pb-8">
        <text class="text-xs text-gray-400 text-center block">您需要授予予设备通知权限才能接收到还款提醒</text>
      </view>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { ref, reactive, watch } from 'vue'

// 设置数据
const settings = reactive({
  enableAllNotifications: true,
  paymentReminder: true,
  reminderDays: '提前 3 天',
  reminderTime: '09:00',
  highUsageAlert: true,
  paymentConfirmation: true
})

// 天数选项
const dayOptions = ref([
  '提前 1 天',
  '提前 2 天', 
  '提前 3 天',
  '提前 5 天',
  '提前 7 天'
])

// 监听总开关变化
watch(() => settings.enableAllNotifications, (newValue) => {
  if (!newValue) {
    // 关闭总开关时，关闭所有子开关
    settings.paymentReminder = false
    settings.highUsageAlert = false
    settings.paymentConfirmation = false
  }
})

// 事件处理
const handleClose = () => {
  uni.navigateBack()
}

const handleToggleAllNotifications = (e: any) => {
  settings.enableAllNotifications = e.detail.value
  
  if (e.detail.value) {
    uni.showToast({
      title: '已开启所有通知',
      icon: 'success'
    })
  } else {
    uni.showToast({
      title: '已关闭所有通知',
      icon: 'none'
    })
  }
}

const handleTogglePaymentReminder = (e: any) => {
  if (!settings.enableAllNotifications && e.detail.value) {
    uni.showToast({
      title: '请先开启总通知开关',
      icon: 'none'
    })
    return
  }
  
  settings.paymentReminder = e.detail.value
  uni.showToast({
    title: e.detail.value ? '已开启还款提醒' : '已关闭还款提醒',
    icon: 'success'
  })
}

const handleDaysChange = (e: any) => {
  settings.reminderDays = dayOptions.value[e.detail.value]
  uni.showToast({
    title: `设置为${settings.reminderDays}`,
    icon: 'success'
  })
}

const handleTimeChange = (e: any) => {
  settings.reminderTime = e.detail.value
  uni.showToast({
    title: `提醒时间设置为${settings.reminderTime}`,
    icon: 'success'
  })
}

const handleToggleHighUsageAlert = (e: any) => {
  if (!settings.enableAllNotifications && e.detail.value) {
    uni.showToast({
      title: '请先开启总通知开关',
      icon: 'none'
    })
    return
  }
  
  settings.highUsageAlert = e.detail.value
  uni.showToast({
    title: e.detail.value ? '已开启高使用率提醒' : '已关闭高使用率提醒',
    icon: 'success'
  })
}

const handleTogglePaymentConfirmation = (e: any) => {
  if (!settings.enableAllNotifications && e.detail.value) {
    uni.showToast({
      title: '请先开启总通知开关',
      icon: 'none'
    })
    return
  }
  
  settings.paymentConfirmation = e.detail.value
  uni.showToast({
    title: e.detail.value ? '已开启付款确认通知' : '已关闭付款确认通知',
    icon: 'success'
  })
}

const handleRequestPermission = () => {
  uni.showModal({
    title: '请求通知权限',
    content: '应用需要获取通知权限以便为您发送还款提醒，是否前往系统设置开启权限？',
    confirmText: '去设置',
    cancelText: '取消',
    success: (res) => {
      if (res.confirm) {
        // 实际项目中这里应该跳转到系统设置
        uni.showToast({
          title: '请在系统设置中开启通知权限',
          icon: 'none',
          duration: 3000
        })
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.notification-settings {
  padding-top: env(safe-area-inset-top);
}

.top-nav {
  padding-top: env(safe-area-inset-top);
}

.space-y-4 > :not(:first-child) {
  margin-top: 1rem;
}

switch {
  transform: scale(0.8);
}

picker {
  cursor: pointer;
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

.justify-center {
  justify-content: center;
}

.text-center {
  text-align: center;
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
  
  .mb-4 {
    margin-bottom: 1rem;
  }
}
</style> 