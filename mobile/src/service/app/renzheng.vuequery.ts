/* eslint-disable */
// @ts-ignore
import { queryOptions, useMutation } from '@tanstack/vue-query';
import type { DefaultError } from '@tanstack/vue-query';
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as apis from './renzheng';
import * as API from './types';

/** 用户名登录 用户名密码登录接口 POST /api/v1/public/auth/login/username */
export function useLoginUsernameApiV1PublicAuthLoginUsernamePostMutation(options?: {
  onSuccess?: (value?: API.AuthResponse) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.loginUsernameApiV1PublicAuthLoginUsernamePost,
    onSuccess(data: API.AuthResponse) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 刷新令牌 刷新JWT访问令牌接口 POST /api/v1/public/auth/refresh-token */
export function useRefreshTokenApiV1PublicAuthRefreshTokenPostMutation(options?: {
  onSuccess?: (value?: API.TokenResponse) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.refreshTokenApiV1PublicAuthRefreshTokenPost,
    onSuccess(data: API.TokenResponse) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 用户注册 用户注册接口 POST /api/v1/public/auth/register */
export function useRegisterApiV1PublicAuthRegisterPostMutation(options?: {
  onSuccess?: (value?: API.AuthResponse) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.registerApiV1PublicAuthRegisterPost,
    onSuccess(data: API.AuthResponse) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}
