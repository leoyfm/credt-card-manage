/* eslint-disable */
// @ts-ignore
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as API from './types';

/** 注销账户 注销当前用户账户（软删除） DELETE /api/v1/user/profile/account */
export async function deleteAccountApiV1UserProfileAccountDelete({
  body,
  options,
}: {
  body: API.AccountDeletionRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseBool_>('/api/v1/user/profile/account', {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 修改密码 修改当前用户的登录密码 POST /api/v1/user/profile/change-password */
export async function changePasswordApiV1UserProfileChangePasswordPost({
  body,
  options,
}: {
  body: API.ChangePasswordRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseBool_>('/api/v1/user/profile/change-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 获取个人信息 获取当前用户的个人资料信息 GET /api/v1/user/profile/info */
export async function getUserInfoApiV1UserProfileInfoGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseUserProfileResponse_>(
    '/api/v1/user/profile/info',
    {
      method: 'GET',
      ...(options || {}),
    }
  );
}

/** 个人登录日志 获取当前用户的登录日志记录 GET /api/v1/user/profile/login-logs */
export async function getLoginLogsApiV1UserProfileLoginLogsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getLoginLogsApiV1UserProfileLoginLogsGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiPagedResponseLoginLogResponse_>(
    '/api/v1/user/profile/login-logs',
    {
      method: 'GET',
      params: {
        // page has a default value: 1
        page: '1',
        // page_size has a default value: 20
        page_size: '20',
        ...params,
      },
      ...(options || {}),
    }
  );
}

/** 退出登录 退出当前用户的登录状态 POST /api/v1/user/profile/logout */
export async function logoutApiV1UserProfileLogoutPost({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseBool_>('/api/v1/user/profile/logout', {
    method: 'POST',
    ...(options || {}),
  });
}

/** 个人统计信息 获取当前用户的统计信息（卡片、交易、积分等） GET /api/v1/user/profile/statistics */
export async function getUserStatisticsApiV1UserProfileStatisticsGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseUserStatisticsResponse_>(
    '/api/v1/user/profile/statistics',
    {
      method: 'GET',
      ...(options || {}),
    }
  );
}

/** 更新个人资料 更新当前用户的个人资料信息 PUT /api/v1/user/profile/update */
export async function updateUserProfileApiV1UserProfileUpdatePut({
  body,
  options,
}: {
  body: API.UserProfileUpdateRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseUserProfileResponse_>(
    '/api/v1/user/profile/update',
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      ...(options || {}),
    }
  );
}

/** 微信绑定信息 获取当前用户的微信绑定信息 GET /api/v1/user/profile/wechat-bindings */
export async function getWechatBindingsApiV1UserProfileWechatBindingsGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseListWechatBindingResponse_>(
    '/api/v1/user/profile/wechat-bindings',
    {
      method: 'GET',
      ...(options || {}),
    }
  );
}
