import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ref, computed } from 'vue'

// Mock toast
const mockToast = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  info: vi.fn(),
}

vi.mock('@/utils/toast', () => ({
  toast: mockToast,
}))

// Mock user store
const mockUserStore = {
  register: vi.fn(),
  isLoggedIn: ref(false),
  userInfo: ref(null),
}

vi.mock('@/store/user', () => ({
  useUserStore: () => mockUserStore,
}))

// Mock wot-design-uni components
vi.mock('wot-design-uni', () => ({
  useToast: () => mockToast,
}))

// 创建一个简化的注册页面组件用于测试
const RegisterPageComponent = {
  template: `
    <view class="register-page">
      <view class="header">
        <view class="title">信用卡管家</view>
        <view class="subtitle">轻松管理你的信用卡</view>
      </view>
      
      <view class="form-container">
        <view class="welcome-text">创建账户</view>
        
        <!-- 步骤指示器 -->
        <view class="steps">
          <view 
            v-for="(step, index) in steps"
            :key="index"
            :class="['step-item', { active: currentStep >= index + 1, completed: currentStep > index + 1 }]"
          >
            <view class="step-number">{{ index + 1 }}</view>
            <view class="step-text">{{ step }}</view>
          </view>
        </view>

        <!-- 第一步：基本信息 -->
        <view v-if="currentStep === 1" class="step-content">
          <input 
            v-model="registerForm.username" 
            placeholder="请输入用户名"
            data-testid="username-input"
          />
          <input 
            v-model="registerForm.email" 
            placeholder="请输入邮箱地址"
            data-testid="email-input"
          />
          <input 
            v-model="registerForm.password" 
            type="password"
            placeholder="请输入密码"
            data-testid="password-input"
          />
          <input 
            v-model="confirmPassword" 
            type="password"
            placeholder="请确认密码"
            data-testid="confirm-password-input"
          />
          <button @click="nextStep" data-testid="next-btn">下一步</button>
        </view>

        <!-- 第二步：手机验证 -->
        <view v-if="currentStep === 2" class="step-content">
          <input 
            v-model="registerForm.phone" 
            placeholder="请输入手机号"
            data-testid="phone-input"
          />
          <view class="code-input-wrapper">
            <input 
              v-model="registerForm.verification_code" 
              placeholder="请输入验证码"
              data-testid="code-input"
            />
            <button 
              @click="sendCode" 
              :disabled="codeDisabled"
              data-testid="send-code-btn"
            >
              {{ codeText }}
            </button>
          </view>
          <view class="button-group">
            <button @click="prevStep" data-testid="prev-btn">上一步</button>
            <button @click="nextStep" data-testid="next-btn">下一步</button>
          </view>
        </view>

        <!-- 第三步：完善信息 -->
        <view v-if="currentStep === 3" class="step-content">
          <input 
            v-model="registerForm.nickname" 
            placeholder="请输入昵称（可选）"
            data-testid="nickname-input"
          />
          <select v-model="registerForm.gender" data-testid="gender-select">
            <option value="">请选择性别</option>
            <option value="male">男</option>
            <option value="female">女</option>
            <option value="unknown">保密</option>
          </select>
          
          <label>
            <input 
              type="checkbox" 
              v-model="agreePrivacy"
              data-testid="privacy-checkbox"
            />
            我已阅读并同意用户协议和隐私政策
          </label>
          
          <view class="button-group">
            <button @click="prevStep" data-testid="prev-btn">上一步</button>
            <button @click="handleRegister" :disabled="loading" data-testid="register-btn">
              {{ loading ? '注册中...' : '完成注册' }}
            </button>
          </view>
        </view>
      </view>
    </view>
  `,
  setup() {
    const steps = ['基本信息', '手机验证', '完善信息']
    const currentStep = ref(1)

    const registerForm = ref({
      username: '',
      email: '',
      password: '',
      phone: '',
      verification_code: '',
      nickname: '',
      gender: '',
    })

    const confirmPassword = ref('')
    const loading = ref(false)
    const codeSending = ref(false)
    const codeDisabled = ref(false)
    const codeCountdown = ref(0)
    const agreePrivacy = ref(false)

    const codeText = computed(() => {
      return codeCountdown.value > 0 ? `${codeCountdown.value}s后重发` : '获取验证码'
    })

    // 验证当前步骤
    const validateCurrentStep = () => {
      switch (currentStep.value) {
        case 1:
          if (!registerForm.value.username.trim()) {
            mockToast.error('请输入用户名')
            return false
          }
          if (registerForm.value.username.length < 3 || registerForm.value.username.length > 20) {
            mockToast.error('用户名长度应为3-20个字符')
            return false
          }
          if (!registerForm.value.email.trim()) {
            mockToast.error('请输入邮箱地址')
            return false
          }
          if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.value.email)) {
            mockToast.error('请输入正确的邮箱格式')
            return false
          }
          if (!registerForm.value.password.trim()) {
            mockToast.error('请输入密码')
            return false
          }
          if (registerForm.value.password.length < 8 || registerForm.value.password.length > 30) {
            mockToast.error('密码长度应为8-30个字符')
            return false
          }
          if (!confirmPassword.value.trim()) {
            mockToast.error('请确认密码')
            return false
          }
          if (registerForm.value.password !== confirmPassword.value) {
            mockToast.error('两次输入的密码不一致')
            return false
          }
          return true

        case 2:
          if (!registerForm.value.phone.trim()) {
            mockToast.error('请输入手机号')
            return false
          }
          if (!/^1[3-9]\d{9}$/.test(registerForm.value.phone)) {
            mockToast.error('请输入正确的手机号')
            return false
          }
          if (!registerForm.value.verification_code.trim()) {
            mockToast.error('请输入验证码')
            return false
          }
          return true

        case 3:
          if (!agreePrivacy.value) {
            mockToast.error('请先同意用户协议和隐私政策')
            return false
          }
          return true

        default:
          return true
      }
    }

    // 验证验证码
    const verifyCode = async () => {
      if (registerForm.value.verification_code.trim() === '123456') {
        return true
      } else {
        mockToast.error('验证码错误（测试模式请输入123456）')
        return false
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

    // 发送验证码
    const sendCode = async () => {
      if (!registerForm.value.phone.trim()) {
        mockToast.error('请输入手机号')
        return
      }

      if (!/^1[3-9]\d{9}$/.test(registerForm.value.phone)) {
        mockToast.error('请输入正确的手机号')
        return
      }

      try {
        codeSending.value = true
        mockToast.error('验证码功能正在开发中')

        // 暂时模拟发送成功
        setTimeout(() => {
          mockToast.success('验证码发送成功（模拟）')
          startCountdown()
        }, 1000)
      } catch (error) {
        mockToast.error('验证码发送失败，请稍后重试')
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

    // 注册
    const handleRegister = async () => {
      if (!validateCurrentStep()) {
        return
      }

      try {
        loading.value = true

        const registerData = {
          username: registerForm.value.username.trim(),
          email: registerForm.value.email.trim(),
          password: registerForm.value.password.trim(),
          nickname: registerForm.value.nickname.trim() || undefined,
        }

        const result = await mockUserStore.register(registerData)

        if (result.success) {
          setTimeout(() => {
            // uni.redirectTo({ url: '/pages/auth/login' })
          }, 1500)
        }
      } catch (error) {
        mockToast.error('注册失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }

    return {
      steps,
      currentStep,
      registerForm,
      confirmPassword,
      loading,
      codeSending,
      codeDisabled,
      codeCountdown,
      agreePrivacy,
      codeText,
      nextStep,
      prevStep,
      sendCode,
      handleRegister,
      validateCurrentStep,
      verifyCode,
    }
  },
}

describe('注册页面测试', () => {
  let wrapper: any
  let pinia: any

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    // 重置所有 mock
    vi.clearAllMocks()

    // 重置 userStore mock
    mockUserStore.register.mockResolvedValue({ success: true })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('页面渲染测试', () => {
    it('应该正确渲染注册页面', () => {
      wrapper = mount(RegisterPageComponent, {
        global: {
          plugins: [pinia],
        },
      })

      expect(wrapper.find('.register-page').exists()).toBe(true)
      expect(wrapper.find('.header .title').text()).toBe('信用卡管家')
      expect(wrapper.find('.welcome-text').text()).toBe('创建账户')
    })

    it('应该显示步骤指示器', () => {
      wrapper = mount(RegisterPageComponent, {
        global: {
          plugins: [pinia],
        },
      })

      const steps = wrapper.findAll('.step-item')
      expect(steps).toHaveLength(3)
      expect(steps[0].text()).toContain('基本信息')
      expect(steps[1].text()).toContain('手机验证')
      expect(steps[2].text()).toContain('完善信息')
    })

    it('应该默认显示第一步', () => {
      wrapper = mount(RegisterPageComponent, {
        global: {
          plugins: [pinia],
        },
      })

      expect(wrapper.find('[data-testid="username-input"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="email-input"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="password-input"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="confirm-password-input"]').exists()).toBe(true)
    })
  })

  describe('第一步：基本信息验证测试', () => {
    beforeEach(() => {
      wrapper = mount(RegisterPageComponent, {
        global: {
          plugins: [pinia],
        },
      })
    })

    it('应该验证用户名不能为空', async () => {
      const nextBtn = wrapper.find('[data-testid="next-btn"]')
      await nextBtn.trigger('click')

      expect(mockToast.error).toHaveBeenCalledWith('请输入用户名')
    })

    it('应该验证用户名长度', async () => {
      const usernameInput = wrapper.find('[data-testid="username-input"]')
      await usernameInput.setValue('ab') // 少于3个字符

      const nextBtn = wrapper.find('[data-testid="next-btn"]')
      await nextBtn.trigger('click')

      expect(mockToast.error).toHaveBeenCalledWith('用户名长度应为3-20个字符')
    })

    it('应该验证邮箱格式', async () => {
      const usernameInput = wrapper.find('[data-testid="username-input"]')
      const emailInput = wrapper.find('[data-testid="email-input"]')

      await usernameInput.setValue('testuser')
      await emailInput.setValue('invalid-email')

      const nextBtn = wrapper.find('[data-testid="next-btn"]')
      await nextBtn.trigger('click')

      expect(mockToast.error).toHaveBeenCalledWith('请输入正确的邮箱格式')
    })

    it('应该验证密码长度', async () => {
      const usernameInput = wrapper.find('[data-testid="username-input"]')
      const emailInput = wrapper.find('[data-testid="email-input"]')
      const passwordInput = wrapper.find('[data-testid="password-input"]')

      await usernameInput.setValue('testuser')
      await emailInput.setValue('test@example.com')
      await passwordInput.setValue('123') // 少于8个字符

      const nextBtn = wrapper.find('[data-testid="next-btn"]')
      await nextBtn.trigger('click')

      expect(mockToast.error).toHaveBeenCalledWith('密码长度应为8-30个字符')
    })

    it('应该验证密码确认', async () => {
      const usernameInput = wrapper.find('[data-testid="username-input"]')
      const emailInput = wrapper.find('[data-testid="email-input"]')
      const passwordInput = wrapper.find('[data-testid="password-input"]')
      const confirmPasswordInput = wrapper.find('[data-testid="confirm-password-input"]')

      await usernameInput.setValue('testuser')
      await emailInput.setValue('test@example.com')
      await passwordInput.setValue('password123')
      await confirmPasswordInput.setValue('password456') // 不匹配

      const nextBtn = wrapper.find('[data-testid="next-btn"]')
      await nextBtn.trigger('click')

      expect(mockToast.error).toHaveBeenCalledWith('两次输入的密码不一致')
    })

    it('应该在验证通过时进入第二步', async () => {
      const usernameInput = wrapper.find('[data-testid="username-input"]')
      const emailInput = wrapper.find('[data-testid="email-input"]')
      const passwordInput = wrapper.find('[data-testid="password-input"]')
      const confirmPasswordInput = wrapper.find('[data-testid="confirm-password-input"]')

      await usernameInput.setValue('testuser')
      await emailInput.setValue('test@example.com')
      await passwordInput.setValue('password123')
      await confirmPasswordInput.setValue('password123')

      const nextBtn = wrapper.find('[data-testid="next-btn"]')
      await nextBtn.trigger('click')

      await wrapper.vm.$nextTick()

      // 应该显示第二步的内容
      expect(wrapper.find('[data-testid="phone-input"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="code-input"]').exists()).toBe(true)
    })
  })

  describe('第二步：手机验证测试', () => {
    beforeEach(async () => {
      wrapper = mount(RegisterPageComponent, {
        global: {
          plugins: [pinia],
        },
      })

      // 先完成第一步
      const usernameInput = wrapper.find('[data-testid="username-input"]')
      const emailInput = wrapper.find('[data-testid="email-input"]')
      const passwordInput = wrapper.find('[data-testid="password-input"]')
      const confirmPasswordInput = wrapper.find('[data-testid="confirm-password-input"]')

      await usernameInput.setValue('testuser')
      await emailInput.setValue('test@example.com')
      await passwordInput.setValue('password123')
      await confirmPasswordInput.setValue('password123')

      const nextBtn = wrapper.find('[data-testid="next-btn"]')
      await nextBtn.trigger('click')
      await wrapper.vm.$nextTick()
    })

    it('应该验证手机号格式', async () => {
      const phoneInput = wrapper.find('[data-testid="phone-input"]')
      await phoneInput.setValue('123456789') // 无效手机号

      const nextBtn = wrapper.find('[data-testid="next-btn"]')
      await nextBtn.trigger('click')

      expect(mockToast.error).toHaveBeenCalledWith('请输入正确的手机号')
    })

    it('应该验证验证码不能为空', async () => {
      const phoneInput = wrapper.find('[data-testid="phone-input"]')
      await phoneInput.setValue('13812345678')

      const nextBtn = wrapper.find('[data-testid="next-btn"]')
      await nextBtn.trigger('click')

      expect(mockToast.error).toHaveBeenCalledWith('请输入验证码')
    })

    it('应该验证错误的验证码', async () => {
      const phoneInput = wrapper.find('[data-testid="phone-input"]')
      const codeInput = wrapper.find('[data-testid="code-input"]')

      await phoneInput.setValue('13812345678')
      await codeInput.setValue('000000') // 错误验证码

      const nextBtn = wrapper.find('[data-testid="next-btn"]')
      await nextBtn.trigger('click')

      expect(mockToast.error).toHaveBeenCalledWith('验证码错误（测试模式请输入123456）')
    })

    it('应该在验证码正确时进入第三步', async () => {
      const phoneInput = wrapper.find('[data-testid="phone-input"]')
      const codeInput = wrapper.find('[data-testid="code-input"]')

      await phoneInput.setValue('13812345678')
      await codeInput.setValue('123456') // 正确验证码

      const nextBtn = wrapper.find('[data-testid="next-btn"]')
      await nextBtn.trigger('click')

      await wrapper.vm.$nextTick()

      // 应该显示第三步的内容
      expect(wrapper.find('[data-testid="nickname-input"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="gender-select"]').exists()).toBe(true)
    })

    it('应该能够返回上一步', async () => {
      const prevBtn = wrapper.find('[data-testid="prev-btn"]')
      await prevBtn.trigger('click')

      await wrapper.vm.$nextTick()

      // 应该回到第一步
      expect(wrapper.find('[data-testid="username-input"]').exists()).toBe(true)
    })
  })

  describe('第三步：完善信息测试', () => {
    beforeEach(async () => {
      wrapper = mount(RegisterPageComponent, {
        global: {
          plugins: [pinia],
        },
      })

      // 完成前两步
      wrapper.vm.currentStep = 3
      await wrapper.vm.$nextTick()
    })

    it('应该验证隐私协议必须同意', async () => {
      const registerBtn = wrapper.find('[data-testid="register-btn"]')
      await registerBtn.trigger('click')

      expect(mockToast.error).toHaveBeenCalledWith('请先同意用户协议和隐私政策')
    })

    it('应该在同意协议后成功注册', async () => {
      const privacyCheckbox = wrapper.find('[data-testid="privacy-checkbox"]')
      await privacyCheckbox.setValue(true)

      const registerBtn = wrapper.find('[data-testid="register-btn"]')
      await registerBtn.trigger('click')

      expect(mockUserStore.register).toHaveBeenCalled()
    })

    it('应该处理可选字段', async () => {
      const nicknameInput = wrapper.find('[data-testid="nickname-input"]')
      const genderSelect = wrapper.find('[data-testid="gender-select"]')
      const privacyCheckbox = wrapper.find('[data-testid="privacy-checkbox"]')

      await nicknameInput.setValue('测试昵称')
      await genderSelect.setValue('male')
      await privacyCheckbox.setValue(true)

      const registerBtn = wrapper.find('[data-testid="register-btn"]')
      await registerBtn.trigger('click')

      expect(mockUserStore.register).toHaveBeenCalled()
    })
  })

  describe('验证码功能测试', () => {
    beforeEach(async () => {
      wrapper = mount(RegisterPageComponent, {
        global: {
          plugins: [pinia],
        },
      })

      // 进入第二步
      wrapper.vm.currentStep = 2
      await wrapper.vm.$nextTick()
    })

    it('应该验证手机号后才能发送验证码', async () => {
      const sendCodeBtn = wrapper.find('[data-testid="send-code-btn"]')
      await sendCodeBtn.trigger('click')

      expect(mockToast.error).toHaveBeenCalledWith('请输入手机号')
    })

    it('应该验证手机号格式后才能发送验证码', async () => {
      const phoneInput = wrapper.find('[data-testid="phone-input"]')
      await phoneInput.setValue('123456789')

      const sendCodeBtn = wrapper.find('[data-testid="send-code-btn"]')
      await sendCodeBtn.trigger('click')

      expect(mockToast.error).toHaveBeenCalledWith('请输入正确的手机号')
    })

    it('应该在有效手机号时发送验证码', async () => {
      const phoneInput = wrapper.find('[data-testid="phone-input"]')
      await phoneInput.setValue('13812345678')

      const sendCodeBtn = wrapper.find('[data-testid="send-code-btn"]')
      await sendCodeBtn.trigger('click')

      expect(mockToast.error).toHaveBeenCalledWith('验证码功能正在开发中')
    })
  })

  describe('步骤导航测试', () => {
    beforeEach(() => {
      wrapper = mount(RegisterPageComponent, {
        global: {
          plugins: [pinia],
        },
      })
    })

    it('应该正确显示当前步骤', async () => {
      expect(wrapper.vm.currentStep).toBe(1)

      const activeSteps = wrapper.findAll('.step-item.active')
      expect(activeSteps).toHaveLength(1)
    })

    it('应该能够在步骤间导航', async () => {
      // 手动设置到第二步
      wrapper.vm.currentStep = 2
      await wrapper.vm.$nextTick()

      expect(wrapper.find('[data-testid="phone-input"]').exists()).toBe(true)

      // 返回第一步
      const prevBtn = wrapper.find('[data-testid="prev-btn"]')
      await prevBtn.trigger('click')

      expect(wrapper.vm.currentStep).toBe(1)
      expect(wrapper.find('[data-testid="username-input"]').exists()).toBe(true)
    })
  })

  describe('表单数据验证测试', () => {
    beforeEach(() => {
      wrapper = mount(RegisterPageComponent, {
        global: {
          plugins: [pinia],
        },
      })
    })

    it('应该验证用户名长度边界值', async () => {
      const usernameInput = wrapper.find('[data-testid="username-input"]')

      // 测试最小长度
      await usernameInput.setValue('ab')
      const nextBtn = wrapper.find('[data-testid="next-btn"]')
      await nextBtn.trigger('click')
      expect(mockToast.error).toHaveBeenCalledWith('用户名长度应为3-20个字符')

      // 测试有效长度
      vi.clearAllMocks()
      await usernameInput.setValue('abc')
      const emailInput = wrapper.find('[data-testid="email-input"]')
      await emailInput.setValue('test@example.com')
      const passwordInput = wrapper.find('[data-testid="password-input"]')
      await passwordInput.setValue('password123')
      const confirmPasswordInput = wrapper.find('[data-testid="confirm-password-input"]')
      await confirmPasswordInput.setValue('password123')

      await nextBtn.trigger('click')
      expect(mockToast.error).not.toHaveBeenCalled()
    })

    it('应该验证邮箱格式的各种情况', async () => {
      const usernameInput = wrapper.find('[data-testid="username-input"]')
      const emailInput = wrapper.find('[data-testid="email-input"]')
      const nextBtn = wrapper.find('[data-testid="next-btn"]')

      await usernameInput.setValue('testuser')

      // 测试无效邮箱格式
      const invalidEmails = ['invalid', 'test@', '@example.com', 'test@.com', 'test.example.com']

      for (const email of invalidEmails) {
        vi.clearAllMocks()
        await emailInput.setValue(email)
        await nextBtn.trigger('click')
        expect(mockToast.error).toHaveBeenCalledWith('请输入正确的邮箱格式')
      }

      // 测试有效邮箱格式
      vi.clearAllMocks()
      await emailInput.setValue('test@example.com')
      const passwordInput = wrapper.find('[data-testid="password-input"]')
      await passwordInput.setValue('password123')
      const confirmPasswordInput = wrapper.find('[data-testid="confirm-password-input"]')
      await confirmPasswordInput.setValue('password123')

      await nextBtn.trigger('click')
      expect(mockToast.error).not.toHaveBeenCalled()
    })

    it('应该验证手机号格式', async () => {
      // 进入第二步
      wrapper.vm.currentStep = 2
      await wrapper.vm.$nextTick()

      const phoneInput = wrapper.find('[data-testid="phone-input"]')
      const nextBtn = wrapper.find('[data-testid="next-btn"]')

      // 测试无效手机号
      const invalidPhones = ['123456789', '12345678901', '12812345678', '10812345678']

      for (const phone of invalidPhones) {
        vi.clearAllMocks()
        await phoneInput.setValue(phone)
        await nextBtn.trigger('click')
        expect(mockToast.error).toHaveBeenCalledWith('请输入正确的手机号')
      }

      // 测试有效手机号
      vi.clearAllMocks()
      await phoneInput.setValue('13812345678')
      const codeInput = wrapper.find('[data-testid="code-input"]')
      await codeInput.setValue('123456')

      await nextBtn.trigger('click')
      expect(mockToast.error).not.toHaveBeenCalled()
    })
  })
})
