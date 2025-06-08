/* eslint-disable */
// @ts-ignore
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as API from './types';

/** 发送验证码 发送验证码接口支持向手机号或邮箱发送验证码：- phone_or_email: 手机号或邮箱地址- code_type: 验证码类型（注册、登录、重置密码、绑定手机）限制：同一手机号/邮箱每分钟只能发送一次验证码。 POST /api/auth/code/send */
export async function sendVerificationCodeApiAuthCodeSendPost({
  body,
  options,
}: {
  body: API.SendCodeRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseDictStr_str_>('/api/auth/code/send', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 验证验证码 验证验证码接口验证手机号或邮箱的验证码是否正确：- phone_or_email: 手机号或邮箱地址- code: 验证码- code_type: 验证码类型验证成功后验证码将标记为已使用。 POST /api/auth/code/verify */
export async function verifyVerificationCodeApiAuthCodeVerifyPost({
  body,
  options,
}: {
  body: API.VerifyCodeRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseDictStr_bool_>('/api/auth/code/verify', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 手机号密码登录 手机号密码登录接口使用手机号和密码进行登录：- phone: 手机号码，支持中国大陆手机号格式- password: 用户密码- remember_me: 是否记住登录状态（可选） POST /api/auth/login/phone */
export async function loginWithPhonePasswordApiAuthLoginPhonePost({
  body,
  options,
}: {
  body: API.PhonePasswordLogin;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseLoginResponse_>('/api/auth/login/phone', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 手机号验证码登录 手机号验证码登录接口使用手机号和验证码进行登录，支持自动注册：- phone: 手机号码- verification_code: 6位数字验证码如果手机号未注册，将自动创建新用户。 POST /api/auth/login/phone-code */
export async function loginWithPhoneCodeApiAuthLoginPhoneCodePost({
  body,
  options,
}: {
  body: API.PhoneCodeLogin;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseLoginResponse_>('/api/auth/login/phone-code', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 用户名密码登录 用户名密码登录接口支持用户名或邮箱登录：- username: 用户名或邮箱地址- password: 用户密码- remember_me: 是否记住登录状态（可选）登录成功返回JWT访问令牌，有效期24小时。 POST /api/auth/login/username */
export async function loginWithUsernamePasswordApiAuthLoginUsernamePost({
  body,
  options,
}: {
  body: API.UsernamePasswordLogin;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseLoginResponse_>('/api/auth/login/username', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 微信登录 微信登录接口使用微信授权码进行登录：- code: 微信授权码，由微信客户端获取- user_info: 可选的用户补充信息首次登录会自动创建账户并绑定微信。 POST /api/auth/login/wechat */
export async function loginWithWechatApiAuthLoginWechatPost({
  body,
  options,
}: {
  body: API.WechatLoginRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseLoginResponse_>('/api/auth/login/wechat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 用户登出 用户登出接口用户主动登出，可选择：- all_devices: 是否登出所有设备登出后客户端应清除本地存储的令牌。 POST /api/auth/logout */
export async function logoutApiAuthLogoutPost({
  body,
  options,
}: {
  body: API.LogoutRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseDictStr_str_>('/api/auth/logout', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 修改密码 修改密码接口用户在已登录状态下修改密码：- old_password: 当前密码- new_password: 新密码修改成功后建议用户重新登录。 POST /api/auth/password/change */
export async function changePasswordApiAuthPasswordChangePost({
  body,
  options,
}: {
  body: API.ChangePasswordRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseDictStr_str_>('/api/auth/password/change', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 重置密码 重置密码接口通过验证码重置密码，用于忘记密码场景：- phone_or_email: 手机号或邮箱- verification_code: 验证码- new_password: 新密码需要先调用发送验证码接口获取验证码。 POST /api/auth/password/reset */
export async function resetPasswordApiAuthPasswordResetPost({
  body,
  options,
}: {
  body: API.ResetPasswordRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseDictStr_str_>('/api/auth/password/reset', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 获取用户资料 获取用户资料接口返回当前登录用户的详细信息，包括：- 基本信息：用户名、昵称、邮箱、手机号- 状态信息：注册时间、最后登录时间、登录次数- 认证信息：是否已验证、是否激活 GET /api/auth/profile */
export async function getUserProfileApiAuthProfileGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseUserProfile_>('/api/auth/profile', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 更新用户资料 更新用户资料接口支持更新以下字段：- nickname: 昵称- avatar_url: 头像URL- gender: 性别- birthday: 生日- bio: 个人简介 PUT /api/auth/profile */
export async function updateUserProfileApiAuthProfilePut({
  body,
  options,
}: {
  body: API.UserUpdateRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseUserProfile_>('/api/auth/profile', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 用户注册 用户注册接口支持用户名、邮箱注册，可选手机号验证。- 用户名：3-20位字符，支持字母、数字、下划线- 邮箱：标准邮箱格式- 密码：8-30位字符，包含字母和数字- 手机号：可选，需要验证码验证- 昵称：可选，默认使用用户名 POST /api/auth/register */
export async function registerApiAuthRegisterPost({
  body,
  options,
}: {
  body: API.UserRegisterRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseUserProfile_>('/api/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 检查认证状态 检查认证状态接口返回当前用户的认证状态信息：- 是否已登录- 令牌剩余有效时间- 用户基本信息 GET /api/auth/status */
export async function checkAuthStatusApiAuthStatusGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseDictStr_Any_>('/api/auth/status', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 刷新访问令牌 刷新访问令牌接口使用刷新令牌获取新的访问令牌：- refresh_token: 刷新令牌当访问令牌即将过期时使用此接口获取新令牌。 POST /api/auth/token/refresh */
export async function refreshAccessTokenApiAuthTokenRefreshPost({
  body,
  options,
}: {
  body: API.RefreshTokenRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseLoginResponse_>('/api/auth/token/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}
