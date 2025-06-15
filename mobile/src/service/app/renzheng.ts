/* eslint-disable */
// @ts-ignore
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as API from './types';

/** 用户名登录 用户名密码登录接口 POST /api/v1/public/auth/login/username */
export async function loginUsernameApiV1PublicAuthLoginUsernamePost({
  body,
  options,
}: {
  body: API.LoginRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.AuthResponse>('/api/v1/public/auth/login/username', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 刷新令牌 刷新JWT访问令牌接口 POST /api/v1/public/auth/refresh-token */
export async function refreshTokenApiV1PublicAuthRefreshTokenPost({
  body,
  options,
}: {
  body: API.RefreshTokenRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.TokenResponse>('/api/v1/public/auth/refresh-token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 用户注册 用户注册接口 POST /api/v1/public/auth/register */
export async function registerApiV1PublicAuthRegisterPost({
  body,
  options,
}: {
  body: API.RegisterRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.AuthResponse>('/api/v1/public/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}
