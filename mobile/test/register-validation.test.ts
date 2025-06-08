import { describe, it, expect } from 'vitest'

/**
 * 注册页面核心验证逻辑测试
 * 测试各种输入验证函数的正确性
 */

describe('📱 注册页面验证逻辑测试', () => {
  // 用户名验证函数
  const validateUsername = (username: string): boolean => {
    if (!username || username.trim().length === 0) return false
    if (username.length < 3 || username.length > 20) return false
    return true
  }

  // 邮箱验证函数
  const validateEmail = (email: string): boolean => {
    if (!email || email.trim().length === 0) return false
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  // 密码验证函数
  const validatePassword = (password: string): boolean => {
    if (!password || password.trim().length === 0) return false
    if (password.length < 8 || password.length > 30) return false
    return true
  }

  // 手机号验证函数
  const validatePhone = (phone: string): boolean => {
    if (!phone || phone.trim().length === 0) return false
    const phoneRegex = /^1[3-9]\d{9}$/
    return phoneRegex.test(phone)
  }

  // 验证码验证函数
  const validateVerificationCode = (code: string): boolean => {
    if (!code || code.trim().length === 0) return false
    const codeRegex = /^\d{6}$/
    return codeRegex.test(code)
  }

  describe('🔍 用户名验证', () => {
    it('空用户名应该验证失败', () => {
      expect(validateUsername('')).toBe(false)
      expect(validateUsername('   ')).toBe(false)
    })

    it('用户名长度不足应该验证失败', () => {
      expect(validateUsername('ab')).toBe(false)
      expect(validateUsername('a')).toBe(false)
    })

    it('用户名长度超限应该验证失败', () => {
      expect(validateUsername('a'.repeat(21))).toBe(false)
      expect(validateUsername('verylongusernamethatexceedslimit')).toBe(false)
    })

    it('有效用户名应该验证通过', () => {
      expect(validateUsername('testuser')).toBe(true)
      expect(validateUsername('user123')).toBe(true)
      expect(validateUsername('test_user_2024')).toBe(true)
    })
  })

  describe('📧 邮箱验证', () => {
    it('空邮箱应该验证失败', () => {
      expect(validateEmail('')).toBe(false)
      expect(validateEmail('   ')).toBe(false)
    })

    it('无效邮箱格式应该验证失败', () => {
      expect(validateEmail('invalid-email')).toBe(false)
      expect(validateEmail('test@')).toBe(false)
      expect(validateEmail('@example.com')).toBe(false)
      expect(validateEmail('test@.com')).toBe(false)
      expect(validateEmail('test@example')).toBe(false)
    })

    it('有效邮箱应该验证通过', () => {
      expect(validateEmail('test@example.com')).toBe(true)
      expect(validateEmail('user.name@domain.org')).toBe(true)
      expect(validateEmail('test+tag@example.co.uk')).toBe(true)
    })
  })

  describe('🔐 密码验证', () => {
    it('空密码应该验证失败', () => {
      expect(validatePassword('')).toBe(false)
      expect(validatePassword('   ')).toBe(false)
    })

    it('密码长度不足应该验证失败', () => {
      expect(validatePassword('1234567')).toBe(false)
      expect(validatePassword('short')).toBe(false)
    })

    it('密码长度超限应该验证失败', () => {
      expect(validatePassword('a'.repeat(31))).toBe(false)
    })

    it('有效密码应该验证通过', () => {
      expect(validatePassword('password123')).toBe(true)
      expect(validatePassword('TestPass123')).toBe(true)
      expect(validatePassword('MySecurePassword2024!')).toBe(true)
    })
  })

  describe('📱 手机号验证', () => {
    it('空手机号应该验证失败', () => {
      expect(validatePhone('')).toBe(false)
      expect(validatePhone('   ')).toBe(false)
    })

    it('无效手机号格式应该验证失败', () => {
      expect(validatePhone('1234567890')).toBe(false)
      expect(validatePhone('12345678901')).toBe(false)
      expect(validatePhone('abcdefghijk')).toBe(false)
      expect(validatePhone('12812345678')).toBe(false) // 不是1[3-9]开头
      expect(validatePhone('10812345678')).toBe(false) // 以10开头
    })

    it('有效手机号应该验证通过', () => {
      expect(validatePhone('13812345678')).toBe(true)
      expect(validatePhone('15987654321')).toBe(true)
      expect(validatePhone('18900000000')).toBe(true)
      expect(validatePhone('17612345678')).toBe(true)
      expect(validatePhone('19912345678')).toBe(true)
    })
  })

  describe('🔢 验证码验证', () => {
    it('空验证码应该验证失败', () => {
      expect(validateVerificationCode('')).toBe(false)
      expect(validateVerificationCode('   ')).toBe(false)
    })

    it('验证码位数不正确应该验证失败', () => {
      expect(validateVerificationCode('12345')).toBe(false) // 5位
      expect(validateVerificationCode('1234567')).toBe(false) // 7位
      expect(validateVerificationCode('1234')).toBe(false) // 4位
    })

    it('非数字验证码应该验证失败', () => {
      expect(validateVerificationCode('abcdef')).toBe(false)
      expect(validateVerificationCode('12345a')).toBe(false)
      expect(validateVerificationCode('a12345')).toBe(false)
    })

    it('有效验证码应该验证通过', () => {
      expect(validateVerificationCode('123456')).toBe(true)
      expect(validateVerificationCode('000000')).toBe(true)
      expect(validateVerificationCode('999999')).toBe(true)
    })
  })

  describe('🔗 综合验证场景', () => {
    it('完整的第一步验证逻辑', () => {
      const validateStep1 = (data: {
        username: string
        email: string
        password: string
        confirmPassword: string
      }) => {
        if (!validateUsername(data.username)) return { valid: false, error: '用户名格式不正确' }
        if (!validateEmail(data.email)) return { valid: false, error: '邮箱格式不正确' }
        if (!validatePassword(data.password)) return { valid: false, error: '密码格式不正确' }
        if (data.password !== data.confirmPassword) return { valid: false, error: '两次密码不一致' }
        return { valid: true }
      }

      // 测试无效数据
      expect(
        validateStep1({
          username: 'ab',
          email: 'test@example.com',
          password: 'TestPass123',
          confirmPassword: 'TestPass123',
        }),
      ).toEqual({ valid: false, error: '用户名格式不正确' })

      // 测试密码不一致
      expect(
        validateStep1({
          username: 'testuser',
          email: 'test@example.com',
          password: 'TestPass123',
          confirmPassword: 'DifferentPass',
        }),
      ).toEqual({ valid: false, error: '两次密码不一致' })

      // 测试有效数据
      expect(
        validateStep1({
          username: 'testuser123',
          email: 'test@example.com',
          password: 'TestPass123',
          confirmPassword: 'TestPass123',
        }),
      ).toEqual({ valid: true })
    })

    it('完整的第二步验证逻辑', () => {
      const validateStep2 = (data: { phone: string; verificationCode: string }) => {
        if (!validatePhone(data.phone)) return { valid: false, error: '手机号格式不正确' }
        if (!validateVerificationCode(data.verificationCode))
          return { valid: false, error: '验证码格式不正确' }
        return { valid: true }
      }

      // 测试无效手机号
      expect(
        validateStep2({
          phone: '1234567890',
          verificationCode: '123456',
        }),
      ).toEqual({ valid: false, error: '手机号格式不正确' })

      // 测试无效验证码
      expect(
        validateStep2({
          phone: '13812345678',
          verificationCode: '12345',
        }),
      ).toEqual({ valid: false, error: '验证码格式不正确' })

      // 测试有效数据
      expect(
        validateStep2({
          phone: '13812345678',
          verificationCode: '123456',
        }),
      ).toEqual({ valid: true })
    })

    it('完整的第三步验证逻辑', () => {
      const validateStep3 = (data: {
        nickname?: string
        gender?: string
        agreePrivacy: boolean
      }) => {
        if (!data.agreePrivacy) return { valid: false, error: '请同意隐私协议' }
        // 昵称和性别是可选的，所以不需要验证
        return { valid: true }
      }

      // 测试未同意协议
      expect(
        validateStep3({
          nickname: 'Test User',
          gender: 'male',
          agreePrivacy: false,
        }),
      ).toEqual({ valid: false, error: '请同意隐私协议' })

      // 测试有效数据
      expect(
        validateStep3({
          nickname: 'Test User',
          gender: 'male',
          agreePrivacy: true,
        }),
      ).toEqual({ valid: true })

      // 测试最少数据（只同意协议）
      expect(
        validateStep3({
          agreePrivacy: true,
        }),
      ).toEqual({ valid: true })
    })
  })

  describe('⏱️ 验证码倒计时逻辑', () => {
    it('倒计时状态管理', () => {
      let codeDisabled = false
      let codeCountdown = 0

      const startCountdown = () => {
        codeDisabled = true
        codeCountdown = 60
      }

      const decrementCountdown = () => {
        if (codeCountdown > 0) {
          codeCountdown--
        }
        if (codeCountdown === 0) {
          codeDisabled = false
        }
      }

      // 初始状态
      expect(codeDisabled).toBe(false)
      expect(codeCountdown).toBe(0)

      // 开始倒计时
      startCountdown()
      expect(codeDisabled).toBe(true)
      expect(codeCountdown).toBe(60)

      // 模拟倒计时
      for (let i = 60; i > 0; i--) {
        expect(codeCountdown).toBe(i)
        decrementCountdown()
      }

      // 倒计时结束
      expect(codeDisabled).toBe(false)
      expect(codeCountdown).toBe(0)
    })
  })

  describe('🎯 性别选项验证', () => {
    const genderOptions = [
      { value: 'male', label: '男' },
      { value: 'female', label: '女' },
      { value: 'unknown', label: '保密' },
    ]

    it('性别选项应该包含正确的值', () => {
      expect(genderOptions).toHaveLength(3)
      expect(genderOptions.map((option) => option.value)).toEqual(['male', 'female', 'unknown'])
      expect(genderOptions.map((option) => option.label)).toEqual(['男', '女', '保密'])
    })

    it('有效性别值验证', () => {
      const validateGender = (gender: string) => {
        const validGenders = ['', 'male', 'female', 'unknown']
        return validGenders.includes(gender)
      }

      expect(validateGender('')).toBe(true) // 可选
      expect(validateGender('male')).toBe(true)
      expect(validateGender('female')).toBe(true)
      expect(validateGender('unknown')).toBe(true)
      expect(validateGender('invalid')).toBe(false)
    })
  })
})
