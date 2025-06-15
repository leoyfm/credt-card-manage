<route lang="json5" type="page">
{
  style: {
    navigationBarTitleText: '注册',
    navigationStyle: 'custom',
  },
}
</route>

<template>
  <view class="register-page">
    <!-- 返回按钮 -->
    <wd-navbar
      title="创建账户"
      left-arrow
      fixed
      placeholder
      safe-area-inset-top
      @click-left="handleBack"
    />

    <!-- 背景装饰 -->
    <view class="bg-decoration">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
    </view>

    <!-- 注册表单 -->
    <view class="form-container">
      <view class="header">
        <view class="title">欢迎加入信用卡管家</view>
        <view class="subtitle">请完善您的基本信息</view>
      </view>

      <!-- 步骤指示器 -->
      <view class="steps">
        <view
          v-for="(step, index) in steps"
          :key="index"
          :class="[
            'step-item',
            { active: currentStep >= index + 1, completed: currentStep > index + 1 },
          ]"
        >
          <view class="step-number">{{ index + 1 }}</view>
          <view class="step-text">{{ step }}</view>
        </view>
      </view>

      <!-- 第一步：基本信息 -->
      <view v-if="currentStep === 1" class="step-content">
        <view class="form-group">
          <wd-input
            v-model="registerForm.username"
            label="用户名"
            placeholder="请输入用户名（3-20个字符）"
            clearable
            required
            :rules="[{ required: true, message: '请输入用户名' }]"
          />

          <wd-input
            v-model="registerForm.email"
            label="邮箱"
            placeholder="请输入邮箱地址"
            clearable
            required
            :rules="[{ required: true, message: '请输入邮箱地址' }]"
          />

          <wd-input
            v-model="registerForm.password"
            label="密码"
            placeholder="请输入密码（8-30个字符）"
            show-password
            clearable
            required
            :rules="[{ required: true, message: '请输入密码' }]"
          />

          <wd-input
            v-model="confirmPassword"
            label="确认密码"
            placeholder="请再次输入密码"
            show-password
            clearable
            required
            :rules="[{ required: true, message: '请确认密码' }]"
          />
        </view>

        <wd-button type="primary" size="large" block @click="nextStep" class="next-btn">
          下一步
        </wd-button>
      </view>

      <!-- 第二步：手机验证 -->
      <view v-if="currentStep === 2" class="step-content">
        <view class="form-group">
          <wd-input
            v-model="registerForm.phone"
            label="手机号"
            placeholder="请输入手机号"
            clearable
            required
            :rules="[{ required: true, message: '请输入手机号' }]"
          />

          <view class="code-input-wrapper">
            <wd-input
              v-model="registerForm.verification_code"
              label="验证码"
              placeholder="请输入验证码"
              clearable
              required
              class="code-input"
              :rules="[{ required: true, message: '请输入验证码' }]"
            />
            <wd-button
              :disabled="codeDisabled"
              :loading="codeSending"
              @click="sendCode"
              class="send-code-btn"
              size="small"
            >
              {{ codeText }}
            </wd-button>
          </view>
        </view>

        <view class="button-group">
          <wd-button type="info" size="large" @click="prevStep" class="prev-btn">上一步</wd-button>

          <wd-button type="primary" size="large" @click="nextStep" class="next-btn">
            下一步
          </wd-button>
        </view>
      </view>

      <!-- 第三步：完善信息 -->
      <view v-if="currentStep === 3" class="step-content">
        <view class="form-group">
          <wd-input
            v-model="registerForm.nickname"
            label="昵称"
            placeholder="请输入昵称（可选）"
            clearable
          />

          <wd-select-picker
            label="性别"
            v-model="registerForm.gender"
            :columns="genderOptions"
            placeholder="请选择性别（可选）"
          />
        </view>

        <!-- 提示信息 -->
        <view class="tip-info">
          <view class="tip-text">性别信息可在注册后的个人资料中设置</view>
        </view>

        <!-- 隐私协议 -->
        <view class="privacy-agreement">
          <wd-checkbox v-model="agreePrivacy" required>
            我已阅读并同意
            <text class="link-text" @click="showAgreement('user')">《用户协议》</text>
            和
            <text class="link-text" @click="showAgreement('privacy')">《隐私政策》</text>
          </wd-checkbox>
        </view>

        <view class="button-group">
          <wd-button type="info" size="large" @click="prevStep" class="prev-btn">上一步</wd-button>

          <wd-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleRegister"
            class="register-btn"
          >
            完成注册
          </wd-button>
        </view>
      </view>
    </view>

    <!-- 登录链接 -->
    <view class="footer">
      <view class="login-link">
        已有账号？
        <text class="link-text" @click="goToLogin">立即登录</text>
      </view>
    </view>

    <!-- Toast -->
    <wd-toast />
  </view>
</template>

<script lang="ts" setup>
import { ref, reactive, computed } from 'vue'
import { useToast } from 'wot-design-uni'
import { useUserStore } from '@/store/user'
// 暂时注释掉旧的API引用，等待新的验证码API
// import {
//   sendVerificationCodeApiAuthCodeSendPost,
//   verifyVerificationCodeApiAuthCodeVerifyPost
// } from '@/service/app/yonghurenzheng'
// import { CodeType, Gender } from '@/service/app/types'
import type * as API from '@/service/app/types'

const toast = useToast()
const userStore = useUserStore()

// 步骤
const steps = ['基本信息', '手机验证', '完善信息']
const currentStep = ref(1)

// 表单数据
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  phone: '',
  verification_code: '',
  nickname: '',
  gender: '',
})

const confirmPassword = ref('')

// 状态控制
const loading = ref(false)
const codeSending = ref(false)
const codeDisabled = ref(false)
const codeCountdown = ref(0)
const agreePrivacy = ref(false)

// 性别选项
const genderOptions = [
  { value: 'male', label: '男' },
  { value: 'female', label: '女' },
  { value: 'unknown', label: '保密' },
]

// 验证码按钮文字
const codeText = computed(() => {
  return codeCountdown.value > 0 ? `${codeCountdown.value}s后重发` : '获取验证码'
})

// 返回
const handleBack = () => {
  if (currentStep.value > 1) {
    prevStep()
  } else {
    uni.navigateBack()
  }
}

// 下一步
const nextStep = async () => {
  if (!validateCurrentStep()) {
    return
  }

  // 第二步需要验证验证码
  if (currentStep.value === 2) {
    const isCodeValid = await verifyCode()
    if (!isCodeValid) {
      return
    }
  }

  if (currentStep.value < 3) {
    currentStep.value++
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

// 验证当前步骤
const validateCurrentStep = () => {
  switch (currentStep.value) {
    case 1:
      if (!registerForm.username.trim()) {
        toast.error('请输入用户名')
        return false
      }
      if (registerForm.username.length < 3 || registerForm.username.length > 20) {
        toast.error('用户名长度应为3-20个字符')
        return false
      }
      if (!registerForm.email.trim()) {
        toast.error('请输入邮箱地址')
        return false
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email)) {
        toast.error('请输入正确的邮箱格式')
        return false
      }
      if (!registerForm.password.trim()) {
        toast.error('请输入密码')
        return false
      }
      if (registerForm.password.length < 8 || registerForm.password.length > 30) {
        toast.error('密码长度应为8-30个字符')
        return false
      }
      if (!confirmPassword.value.trim()) {
        toast.error('请确认密码')
        return false
      }
      if (registerForm.password !== confirmPassword.value) {
        toast.error('两次输入的密码不一致')
        return false
      }
      return true

    case 2:
      if (!registerForm.phone.trim()) {
        toast.error('请输入手机号')
        return false
      }
      if (!/^1[3-9]\d{9}$/.test(registerForm.phone)) {
        toast.error('请输入正确的手机号')
        return false
      }
      if (!registerForm.verification_code.trim()) {
        toast.error('请输入验证码')
        return false
      }
      return true

    case 3:
      if (!agreePrivacy.value) {
        toast.error('请先同意用户协议和隐私政策')
        return false
      }
      return true

    default:
      return true
  }
}

// 发送验证码
const sendCode = async () => {
  if (!registerForm.phone.trim()) {
    toast.error('请输入手机号')
    return
  }

  if (!/^1[3-9]\d{9}$/.test(registerForm.phone)) {
    toast.error('请输入正确的手机号')
    return
  }

  try {
    codeSending.value = true

    // TODO: 等待新的验证码API
    toast.error('验证码功能正在开发中')

    // 暂时模拟发送成功
    setTimeout(() => {
      toast.success('验证码发送成功（模拟）')
      startCountdown()
    }, 1000)
  } catch (error: any) {
    console.error('验证码发送失败:', error)
    toast.error('验证码发送失败，请稍后重试')
  } finally {
    codeSending.value = false
  }
}

// 开始倒计时
const startCountdown = () => {
  codeDisabled.value = true
  codeCountdown.value = 60

  const timer = setInterval(() => {
    codeCountdown.value--
    if (codeCountdown.value <= 0) {
      clearInterval(timer)
      codeDisabled.value = false
    }
  }, 1000)
}

// 验证验证码
const verifyCode = async () => {
  try {
    // TODO: 等待新的验证码验证API
    if (registerForm.verification_code.trim() === '123456') {
      return true
    } else {
      toast.error('验证码错误（测试模式请输入123456）')
      return false
    }
  } catch (error: any) {
    console.error('验证验证码失败:', error)
    toast.error('验证码验证失败，请稍后重试')
    return false
  }
}

// 注册
const handleRegister = async () => {
  if (!validateCurrentStep()) {
    return
  }

  try {
    loading.value = true

    // 构建注册请求数据
    const registerData: API.RegisterRequest = {
      username: registerForm.username.trim(),
      email: registerForm.email.trim(),
      password: registerForm.password.trim(),
      nickname: registerForm.nickname.trim() || undefined,
    }

    // 使用用户store进行注册
    const result = await userStore.register(registerData)

    if (result.success) {
      // 注册成功，跳转到登录页面
      setTimeout(() => {
        uni.redirectTo({ url: '/pages/auth/login' })
      }, 1500)
    }
    // 错误信息已经在store中通过toast显示了
  } catch (error: any) {
    console.error('注册失败:', error)
    toast.error('注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 去登录页面
const goToLogin = () => {
  uni.navigateTo({ url: '/pages/auth/login' })
}

// 显示协议
const showAgreement = (type: 'user' | 'privacy') => {
  const url = type === 'user' ? '/pages/agreement/user' : '/pages/agreement/privacy'
  uni.navigateTo({ url })
}
</script>

<style lang="scss" scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;

  .circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);

    &.circle-1 {
      width: 150px;
      height: 150px;
      top: 20%;
      right: -75px;
    }

    &.circle-2 {
      width: 100px;
      height: 100px;
      bottom: 30%;
      left: -50px;
    }
  }
}

.form-container {
  background: white;
  margin: 20px;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  min-height: calc(100vh - 200px);
}

.header {
  text-align: center;
  margin-bottom: 32px;

  .title {
    font-size: 24px;
    font-weight: bold;
    color: #333;
    margin-bottom: 8px;
  }

  .subtitle {
    font-size: 14px;
    color: #666;
  }
}

.steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 40px;

  .step-item {
    flex: 1;
    text-align: center;
    position: relative;

    &:not(:last-child)::after {
      content: '';
      position: absolute;
      top: 16px;
      right: -50%;
      width: 100%;
      height: 2px;
      background: #e5e5e5;
      z-index: 1;
    }

    &.active::after,
    &.completed::after {
      background: #4f46e5;
    }

    .step-number {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #e5e5e5;
      color: #999;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 8px;
      position: relative;
      z-index: 2;
      font-weight: bold;
      transition: all 0.3s;
    }

    &.active .step-number {
      background: #4f46e5;
      color: white;
    }

    &.completed .step-number {
      background: #10b981;
      color: white;
    }

    .step-text {
      font-size: 12px;
      color: #666;
    }

    &.active .step-text {
      color: #4f46e5;
      font-weight: bold;
    }
  }
}

.step-content {
  .form-group {
    margin-bottom: 32px;

    .code-input-wrapper {
      display: flex;
      align-items: end;
      gap: 12px;

      .code-input {
        flex: 1;
      }

      .send-code-btn {
        width: 100px;
        height: 44px;
        margin-bottom: 8px;
      }
    }
  }

  .tip-info {
    margin-bottom: 16px;

    .tip-text {
      font-size: 12px;
      color: #999;
      text-align: center;
    }
  }

  .privacy-agreement {
    margin-bottom: 32px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;

    .link-text {
      color: #4f46e5;
      font-weight: bold;
    }
  }

  .button-group {
    display: flex;
    gap: 16px;

    .prev-btn {
      flex: 1;
      height: 48px;
    }

    .next-btn,
    .register-btn {
      flex: 2;
      height: 48px;
      background: #4f46e5;
      border: none;
    }
  }

  .next-btn {
    height: 48px;
    background: #4f46e5;
    border: none;
  }
}

.footer {
  text-align: center;
  padding: 32px;

  .login-link {
    color: white;

    .link-text {
      color: #ffd700;
      font-weight: bold;
    }
  }
}
</style>
