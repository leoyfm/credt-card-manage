<template>
  <view class="login-page">
    <!-- 背景装饰 -->
    <view class="bg-decoration">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
      <view class="circle circle-3"></view>
    </view>

    <!-- 顶部logo和标题 -->
    <view class="header">
      <view class="logo">
        <text class="logo-icon">💳</text>
      </view>
      <view class="title">信用卡管家</view>
      <view class="subtitle">轻松管理你的信用卡</view>
    </view>

    <!-- 登录表单 -->
    <view class="form-container">
      <view class="welcome-text">欢迎回来</view>

      <!-- 登录方式切换 -->
      <view class="login-tabs" style="display: none">
        <view
          :class="['tab-item', { active: loginType === 'username' }]"
          @click="switchLoginType('username')"
        >
          账号登录
        </view>
        <view
          :class="['tab-item', { active: loginType === 'phone' }]"
          @click="switchLoginType('phone')"
        >
          手机登录
        </view>
      </view>

      <!-- 账号密码登录 -->
      <view class="form-content">
        <view class="input-group">
          <wd-input
            v-model="usernameForm.username"
            prefix-icon="user"
            placeholder="请输入用户名/邮箱"
            clearable
            size="large"
            class="input-item"
          />

          <wd-input
            v-model="usernameForm.password"
            prefix-icon="lock-on"
            placeholder="请输入密码"
            show-password
            clearable
            size="large"
            class="input-item"
          />
        </view>

        <view class="forgot-password" @click="handleForgotPassword">忘记密码？</view>

        <wd-button
          type="primary"
          size="large"
          block
          :loading="usernameLoginMutation.isPending.value"
          @click="handleUsernameLogin"
          class="login-btn"
        >
          登录
        </wd-button>
      </view>
    </view>

    <!-- 底部注册链接 -->
    <view class="footer">
      <view class="register-link">
        还没有账号？
        <text class="link-text" @click="goToRegister">立即注册</text>
      </view>

      <!-- 隐私协议 -->
      <view class="privacy-agreement">
        <wd-checkbox v-model="agreePrivacy" size="small">
          我已阅读并同意
          <text class="link-text" @click="showAgreement('user')">《用户协议》</text>
          和
          <text class="link-text" @click="showAgreement('privacy')">《隐私政策》</text>
        </wd-checkbox>
      </view>
    </view>

    <!-- Toast -->
    <wd-toast />
  </view>
</template>

<script lang="ts" setup>
import { ref, reactive } from 'vue'
import { useToast } from 'wot-design-uni'
import { useUserStore } from '@/store/user'
import { useLoginUsernameApiV1PublicAuthLoginUsernamePostMutation } from '@/service/app/renzheng.vuequery'
import type * as API from '@/service/app/types'

const toast = useToast()
const userStore = useUserStore()

// 使用 Vue Query mutation 进行用户名登录
const usernameLoginMutation = useLoginUsernameApiV1PublicAuthLoginUsernamePostMutation({
  onSuccess: (data: API.AuthResponse) => {
    console.log('登录成功:', data)

    userStore.setAuthData(data)

    // 直接保存用户信息到 store，简化数据结构
    // userStore.userInfo = {
    //   id: data.user_id,
    //   username: data.username,
    //   email: data.email,
    //   nickname: data.nickname,
    //   phone: data.phone,
    //   avatar_url: data.avatar_url,
    //   is_active: data.is_active || false,
    //   is_verified: data.is_verified || false,
    //   timezone: data.timezone || 'Asia/Shanghai',
    //   language: data.language || 'zh-CN',
    //   currency: data.currency || 'CNY',
    //   last_login_at: data.last_login_at,
    //   email_verified_at: data.email_verified_at,
    //   created_at: data.created_at || new Date().toISOString(),
    // }

    // userStore.token = data.access_token
    // userStore.refreshToken = data.refresh_token
    // userStore.isLoggedIn = true

    // // 保存到本地存储
    // uni.setStorageSync('token', data.access_token)
    // uni.setStorageSync('userInfo', userStore.userInfo)
    // uni.setStorageSync('isLoggedIn', true)

    toast.success('登录成功')

    // 跳转到首页
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 1000)
  },
  onError: (error: any) => {
    console.error('登录失败:', error)
    let errorMsg = '登录失败，请稍后重试'

    if (error.response?.data?.message) {
      errorMsg = error.response.data.message
    } else if (error.message) {
      errorMsg = error.message
    }

    toast.error(errorMsg)
  },
})

// 登录类型
const loginType = ref<'username' | 'phone'>('username')

// 表单数据
const usernameForm = reactive({
  username: '',
  password: '',
})

// 状态控制
const agreePrivacy = ref(true)

// 切换登录方式
const switchLoginType = (type: 'username' | 'phone') => {
  loginType.value = type
}

// 账号密码登录 - 使用 Vue Query mutation
const handleUsernameLogin = async () => {
  if (!agreePrivacy.value) {
    toast.error('请先同意用户协议和隐私政策')
    return
  }

  if (!usernameForm.username.trim()) {
    toast.error('请输入用户名或邮箱')
    return
  }

  if (!usernameForm.password.trim()) {
    toast.error('请输入密码')
    return
  }

  // 调用 Vue Query mutation
  usernameLoginMutation.mutate({
    body: {
      username: usernameForm.username.trim(),
      password: usernameForm.password.trim(),
    },
  })
}

// 忘记密码
const handleForgotPassword = () => {
  uni.navigateTo({ url: '/pages/auth/forgot-password' })
}

// 去注册页面
const goToRegister = () => {
  uni.navigateTo({ url: '/pages/auth/register' })
}

// 显示协议
const showAgreement = (type: 'user' | 'privacy') => {
  const url = type === 'user' ? '/pages/agreement/user' : '/pages/agreement/privacy'
  uni.navigateTo({ url })
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
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
      width: 200px;
      height: 200px;
      top: -100px;
      right: -100px;
    }

    &.circle-2 {
      width: 150px;
      height: 150px;
      bottom: 100px;
      left: -75px;
    }

    &.circle-3 {
      width: 100px;
      height: 100px;
      top: 50%;
      right: 50px;
      transform: translateY(-50%);
    }
  }
}

.header {
  text-align: center;
  padding: 100px 32px 60px;

  .logo {
    margin-bottom: 16px;

    .logo-icon {
      font-size: 60px;
      color: white;
    }
  }

  .title {
    font-size: 28px;
    font-weight: bold;
    color: white;
    margin-bottom: 8px;
  }

  .subtitle {
    font-size: 16px;
    color: rgba(255, 255, 255, 0.8);
  }
}

.form-container {
  background: white;
  margin: 0 32px;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);

  .welcome-text {
    font-size: 24px;
    font-weight: bold;
    color: #333;
    text-align: center;
    margin-bottom: 32px;
  }
}

.login-tabs {
  display: flex;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 32px;

  .tab-item {
    flex: 1;
    text-align: center;
    padding: 12px;
    border-radius: 6px;
    color: #666;
    transition: all 0.3s;

    &.active {
      background: #4f46e5;
      color: white;
    }
  }
}

.form-content {
  .input-group {
    margin-bottom: 24px;

    .input-item {
      margin-bottom: 16px;
    }
  }

  .code-input-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;

    .code-input {
      flex: 1;
    }

    .send-code-btn {
      width: 100px;
      height: 44px;
    }
  }

  .forgot-password {
    text-align: right;
    color: #4f46e5;
    font-size: 14px;
    margin-bottom: 32px;
  }

  .login-btn {
    background: #4f46e5;
    border: none;
    height: 48px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: bold;
  }
}

.footer {
  padding: 32px;
  text-align: center;

  .register-link {
    color: white;
    margin-bottom: 24px;

    .link-text {
      color: #ffd700;
      font-weight: bold;
    }
  }

  .privacy-agreement {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.8);

    .link-text {
      color: #ffd700;
    }
  }
}
</style>
