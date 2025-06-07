<route lang="json5">
{
  style: {
    navigationBarTitleText: 'Mock 测试页面',
  },
}
</route>

<template>
  <view class="test-page">
    <view class="header">
      <text class="title">Mock 数据测试</text>
    </view>
    
    <view class="test-section">
      <button @click="testCards" class="test-button">测试信用卡数据</button>
      <button @click="testTransactions" class="test-button">测试交易数据</button>
      <button @click="testNotifications" class="test-button">测试通知数据</button>
      <button @click="testStatistics" class="test-button">测试统计数据</button>
    </view>
    
    <view class="result-section">
      <text class="result-title">测试结果:</text>
      <view class="result-content">
        <text>{{ resultText }}</text>
      </view>
      <view v-if="resultData" class="result-data">
        <text class="data-title">数据内容:</text>
        <text class="data-content">{{ JSON.stringify(resultData, null, 2) }}</text>
      </view>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { cardApi, transactionApi, notificationApi, statisticsApi } from '@/service/api'
import '@/mock' // 引入Mock数据

defineOptions({
  name: 'TestMockPage',
})

const resultText = ref('等待测试...')
const resultData = ref(null)

const testCards = async () => {
  try {
    resultText.value = '正在测试信用卡数据...'
    resultData.value = null
    
    const response = await cardApi.getCards()
    console.log('Cards API Response:', response)
    
    if (response && response.code === 200) {
      resultText.value = '✅ 信用卡数据获取成功!'
      resultData.value = response.data
    } else {
      resultText.value = '❌ 信用卡数据获取失败: ' + (response?.msg || '未知错误')
    }
  } catch (error: any) {
    console.error('Cards API Error:', error)
    resultText.value = '❌ 信用卡数据请求异常: ' + error.message
  }
}

const testTransactions = async () => {
  try {
    resultText.value = '正在测试交易数据...'
    resultData.value = null
    
    const response = await transactionApi.getTransactions()
    console.log('Transactions API Response:', response)
    
    if (response && response.code === 200) {
      resultText.value = '✅ 交易数据获取成功!'
      resultData.value = response.data
    } else {
      resultText.value = '❌ 交易数据获取失败: ' + (response?.msg || '未知错误')
    }
  } catch (error: any) {
    console.error('Transactions API Error:', error)
    resultText.value = '❌ 交易数据请求异常: ' + error.message
  }
}

const testNotifications = async () => {
  try {
    resultText.value = '正在测试通知数据...'
    resultData.value = null
    
    const response = await notificationApi.getNotifications()
    console.log('Notifications API Response:', response)
    
    if (response && response.code === 200) {
      resultText.value = '✅ 通知数据获取成功!'
      resultData.value = response.data
    } else {
      resultText.value = '❌ 通知数据获取失败: ' + (response?.msg || '未知错误')
    }
  } catch (error: any) {
    console.error('Notifications API Error:', error)
    resultText.value = '❌ 通知数据请求异常: ' + error.message
  }
}

const testStatistics = async () => {
  try {
    resultText.value = '正在测试统计数据...'
    resultData.value = null
    
    const response = await statisticsApi.getOverview()
    console.log('Statistics API Response:', response)
    
    if (response && response.code === 200) {
      resultText.value = '✅ 统计数据获取成功!'
      resultData.value = response.data
    } else {
      resultText.value = '❌ 统计数据获取失败: ' + (response?.msg || '未知错误')
    }
  } catch (error: any) {
    console.error('Statistics API Error:', error)
    resultText.value = '❌ 统计数据请求异常: ' + error.message
  }
}

// 页面加载时自动测试一个接口
onLoad(() => {
  console.log('Mock 测试页面加载完成')
  console.log('检查是否加载了 Mock.js:', typeof window !== 'undefined' && (window as any).Mock ? '✅ 已加载' : '❌ 未加载')
})
</script>

<style lang="scss" scoped>
.test-page {
  padding: 20px;
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.test-section {
  margin-bottom: 30px;
}

.test-button {
  display: block;
  width: 100%;
  margin-bottom: 15px;
  padding: 15px;
  background: #007aff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
}

.result-section {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.result-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
  display: block;
}

.result-content {
  background: #f0f0f0;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 15px;
}

.result-data {
  margin-top: 15px;
}

.data-title {
  font-size: 16px;
  font-weight: bold;
  color: #666;
  margin-bottom: 10px;
  display: block;
}

.data-content {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 5px;
  font-family: monospace;
  font-size: 12px;
  color: #333;
  word-wrap: break-word;
  white-space: pre-wrap;
  display: block;
}
</style> 