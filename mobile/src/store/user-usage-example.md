# 用户Store使用示例

优化后的用户store已经完全适配新的登录API，并提供了完整的用户认证功能。

## 主要功能

### 1. 登录功能
- 账号密码登录：`loginWithUsername()`
- 手机验证码登录：`loginWithPhoneCode()`
- 发送验证码：`sendVerificationCode()`

### 2. 用户管理
- 获取用户信息：`getCurrentUser()`
- 更新用户信息：`setUserInfo()`
- 检查登录状态：`checkLoginStatus()`

### 3. 认证管理
- 刷新token：`refreshAccessToken()`
- 用户登出：`logout()`
- 清除用户信息：`clearUserInfo()`

### 4. 数据持久化
- 自动保存到本地存储
- 应用启动时自动恢复用户状态

## 使用示例

### 在登录页面中使用

```vue
<script lang="ts" setup>
import { useUserStore } from '@/store/user'
import { CodeType } from '@/service/app/types'

const userStore = useUserStore()

// 账号密码登录
const handleLogin = async () => {
  const result = await userStore.loginWithUsername({
    username: 'testuser2024',
    password: 'TestPass123456',
    remember_me: true
  })
  
  if (result.success) {
    // 登录成功，跳转到首页
    uni.switchTab({ url: '/pages/index/index' })
  }
}

// 手机验证码登录
const handlePhoneLogin = async () => {
  const result = await userStore.loginWithPhoneCode({
    phone: '13800138000',
    verification_code: '123456'
  })
  
  if (result.success) {
    uni.switchTab({ url: '/pages/index/index' })
  }
}

// 发送验证码
const sendCode = async () => {
  const result = await userStore.sendVerificationCode({
    phone_or_email: '13800138000',
    code_type: CodeType.login
  })
  
  if (result.success) {
    // 开始倒计时
    startCountdown()
  }
}
</script>
```

### 在其他页面中检查登录状态

```vue
<script lang="ts" setup>
import { useUserStore } from '@/store/user'
import { onMounted } from 'vue'

const userStore = useUserStore()

onMounted(() => {
  // 检查登录状态
  if (!userStore.checkLoginStatus()) {
    // 未登录，跳转到登录页
    uni.navigateTo({ url: '/pages/auth/login' })
    return
  }
  
  // 已登录，获取用户信息
  console.log('当前用户:', userStore.userInfo)
})
</script>
```

### 用户登出

```vue
<script lang="ts" setup>
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

const handleLogout = async () => {
  const result = await userStore.logout(false) // false表示只登出当前设备
  
  if (result.success) {
    // 自动跳转到登录页，store中已处理
  }
}

// 登出所有设备
const handleLogoutAll = async () => {
  await userStore.logout(true)
}
</script>
```

### 获取和更新用户信息

```vue
<script lang="ts" setup>
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

// 刷新用户信息
const refreshUserInfo = async () => {
  const result = await userStore.getCurrentUser()
  
  if (result.success) {
    console.log('用户信息已更新:', result.data)
  }
}

// 检查用户状态
const checkUser = () => {
  console.log('是否已登录:', userStore.isLoggedIn)
  console.log('用户信息:', userStore.userInfo)
  console.log('访问令牌:', userStore.token)
}
</script>
```

### 在请求拦截器中使用Token

请求拦截器已经自动配置好，会自动添加token到请求头：

```ts
// mobile/src/interceptors/request.ts
const userStore = useUserStore()
const token = userStore.token
if (token) {
  options.header.Authorization = `Bearer ${token}`
}
```

## 注意事项

1. **自动状态恢复**：应用启动时会自动从本地存储恢复用户状态
2. **错误处理**：所有方法都有完整的错误处理，会通过toast显示错误信息
3. **Token管理**：Token会自动保存到本地存储，并在请求时自动添加到请求头
4. **状态同步**：用户状态在store中统一管理，各页面共享

## 与旧版本的区别

1. **API接口**：使用新的认证API，支持JWT token
2. **数据结构**：用户信息使用新的`UserProfile`类型
3. **错误处理**：统一的错误处理和提示机制
4. **状态管理**：更完善的登录状态管理
5. **类型安全**：完整的TypeScript类型支持 