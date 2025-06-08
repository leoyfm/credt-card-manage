 # 注册功能测试指南

优化后的注册页面已经集成了真实的API，支持完整的三步注册流程。

## 功能特性

### ✅ 已实现功能
1. **三步注册流程**：
   - 第一步：基本信息（用户名、邮箱、密码）
   - 第二步：手机验证（手机号、验证码）
   - 第三步：完善信息（昵称、同意协议）

2. **真实API集成**：
   - 发送验证码：`sendVerificationCodeApiAuthCodeSendPost`
   - 验证验证码：`verifyVerificationCodeApiAuthCodeVerifyPost`
   - 用户注册：使用 `userStore.register()`

3. **智能验证**：
   - 第二步前进时自动验证验证码
   - 完整的表单验证和错误提示
   - 倒计时防重复发送

4. **用户体验优化**：
   - 统一使用用户store管理状态
   - 自动保存用户信息和token
   - 注册成功后自动跳转登录页

## 测试流程

### 第一步测试：基本信息
```typescript
// 测试数据
const testData = {
  username: 'testuser' + Math.random().toString(36).substr(2, 6),
  email: 'test' + Math.random().toString(36).substr(2, 6) + '@example.com',
  password: 'TestPass123456',
  confirmPassword: 'TestPass123456'
}
```

**验证点**：
- 用户名长度3-20位
- 邮箱格式正确
- 密码长度8-30位
- 确认密码一致

### 第二步测试：手机验证
```typescript
// 测试数据
const phoneData = {
  phone: '13800138000', // 测试手机号
  verification_code: '123456' // 从短信/邮箱获取
}
```

**验证点**：
- 手机号格式验证
- 验证码发送成功
- 验证码验证通过
- 倒计时功能正常

### 第三步测试：完善信息
```typescript
// 测试数据
const profileData = {
  nickname: '测试用户昵称',
  agreePrivacy: true
}
```

**验证点**：
- 昵称可选填写
- 必须同意协议才能注册
- 注册成功跳转

## API调用流程

### 1. 发送验证码
```typescript
userStore.sendVerificationCode({
  phone_or_email: '13800138000',
  code_type: CodeType.register
})
```

### 2. 验证验证码（第二步前进时）
```typescript
verifyVerificationCodeApiAuthCodeVerifyPost({
  body: {
    phone_or_email: '13800138000',
    code: '123456',
    code_type: CodeType.register
  }
})
```

### 3. 用户注册
```typescript
userStore.register({
  username: 'testuser123',
  email: 'test@example.com', 
  password: 'TestPass123456',
  phone: '13800138000',
  nickname: '测试用户',
  verification_code: '123456'
})
```

## 错误处理

### 常见错误场景
1. **验证码相关**：
   - 验证码已过期
   - 验证码错误
   - 发送频率限制

2. **注册相关**：
   - 用户名已存在
   - 邮箱已被注册
   - 手机号已绑定

3. **网络相关**：
   - 请求超时
   - 服务器错误
   - 网络连接失败

### 错误显示方式
- 使用 toast 显示错误信息
- 表单验证错误直接在字段下显示
- 网络错误提供重试选项

## 与后端联调

### 测试环境配置
1. 确保后端服务正常运行
2. 验证API端点配置正确
3. 检查认证接口返回格式

### 验证点
1. ✅ 验证码发送成功
2. ✅ 验证码验证通过
3. ✅ 注册接口调用成功
4. ✅ 用户信息正确保存
5. ✅ JWT token正确生成

## 后续改进

### 可选优化
1. **性别信息**：注册后在个人资料页面设置
2. **图片验证码**：增加机器人防护
3. **邮箱验证**：支持邮箱验证码注册
4. **社交登录**：微信、QQ等第三方注册

### 数据持久化
- 用户信息自动保存到 localStorage
- JWT token自动设置到请求头
- 登录状态自动恢复

现在注册功能已经完全集成真实API，可以进行完整的端到端测试。