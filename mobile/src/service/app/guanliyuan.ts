/* eslint-disable */
// @ts-ignore
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as API from './types';

/** 获取年费管理概览 管理员获取系统年费管理统计概览 GET /api/v1/admin/cards/annual-fee-summary */
export async function getAnnualFeeSummaryApiV1AdminCardsAnnualFeeSummaryGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getAnnualFeeSummaryApiV1AdminCardsAnnualFeeSummaryGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/annual-fee-summary', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  });
}

/** 获取银行分布统计 管理员获取各银行信用卡分布情况 GET /api/v1/admin/cards/bank-distribution */
export async function getBankDistributionApiV1AdminCardsBankDistributionGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/bank-distribution', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 获取卡片类型分布 管理员获取信用卡类型、等级分布统计 GET /api/v1/admin/cards/card-types */
export async function getCardTypesDistributionApiV1AdminCardsCardTypesGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/card-types', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 获取即将到期卡片统计 管理员获取即将到期信用卡的统计信息 GET /api/v1/admin/cards/expiry-alerts */
export async function getExpiryAlertsApiV1AdminCardsExpiryAlertsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getExpiryAlertsApiV1AdminCardsExpiryAlertsGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/expiry-alerts', {
    method: 'GET',
    params: {
      // months_ahead has a default value: 3
      months_ahead: '3',
      ...params,
    },
    ...(options || {}),
  });
}

/** 获取信用卡健康状况 管理员获取系统信用卡健康状况分析 GET /api/v1/admin/cards/health-status */
export async function getCardHealthStatusApiV1AdminCardsHealthStatusGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/health-status', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 获取信用卡系统统计 管理员获取系统级信用卡统计数据（脱敏） GET /api/v1/admin/cards/statistics */
export async function getCardStatisticsApiV1AdminCardsStatisticsGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/statistics', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 获取信用卡趋势分析 管理员获取信用卡增长趋势和使用情况分析 GET /api/v1/admin/cards/trends */
export async function getCardTrendsApiV1AdminCardsTrendsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCardTrendsApiV1AdminCardsTrendsGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/trends', {
    method: 'GET',
    params: {
      // months has a default value: 6
      months: '6',
      ...params,
    },
    ...(options || {}),
  });
}

/** 获取信用额度利用率分析 管理员获取系统信用额度利用率分布和风险分析 GET /api/v1/admin/cards/utilization-analysis */
export async function getUtilizationAnalysisApiV1AdminCardsUtilizationAnalysisGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/utilization-analysis', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 删除用户 管理员删除指定用户（谨慎操作） DELETE /api/v1/admin/users/${param0}/delete */
export async function deleteUserApiV1AdminUsersUserIdDeleteDelete({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.deleteUserApiV1AdminUsersUserIdDeleteDeleteParams;
  body: API.UserDeletionRequest;
  options?: CustomRequestOptions;
}) {
  const { user_id: param0, ...queryParams } = params;

  return request<API.ApiResponse>(`/api/v1/admin/users/${param0}/delete`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  });
}

/** 获取用户详情 管理员获取指定用户的详细信息 GET /api/v1/admin/users/${param0}/details */
export async function getUserDetailsApiV1AdminUsersUserIdDetailsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getUserDetailsApiV1AdminUsersUserIdDetailsGetParams;
  options?: CustomRequestOptions;
}) {
  const { user_id: param0, ...queryParams } = params;

  return request<API.ApiResponse>(`/api/v1/admin/users/${param0}/details`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  });
}

/** 获取用户登录日志 管理员获取指定用户的登录日志 GET /api/v1/admin/users/${param0}/login-logs */
export async function getUserLoginLogsApiV1AdminUsersUserIdLoginLogsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getUserLoginLogsApiV1AdminUsersUserIdLoginLogsGetParams;
  options?: CustomRequestOptions;
}) {
  const { user_id: param0, ...queryParams } = params;

  return request<API.ApiPagedResponse>(
    `/api/v1/admin/users/${param0}/login-logs`,
    {
      method: 'GET',
      params: {
        // page has a default value: 1
        page: '1',
        // page_size has a default value: 20
        page_size: '20',
        ...queryParams,
      },
      ...(options || {}),
    }
  );
}

/** 更新用户权限 管理员更新用户的权限（管理员权限、验证状态） PUT /api/v1/admin/users/${param0}/permissions */
export async function updateUserPermissionsApiV1AdminUsersUserIdPermissionsPut({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.updateUserPermissionsApiV1AdminUsersUserIdPermissionsPutParams;
  body: API.UserPermissionsUpdateRequest;
  options?: CustomRequestOptions;
}) {
  const { user_id: param0, ...queryParams } = params;

  return request<API.ApiResponse>(`/api/v1/admin/users/${param0}/permissions`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  });
}

/** 更新用户状态 管理员更新用户的激活状态 PUT /api/v1/admin/users/${param0}/status */
export async function updateUserStatusApiV1AdminUsersUserIdStatusPut({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.updateUserStatusApiV1AdminUsersUserIdStatusPutParams;
  body: API.UserStatusUpdateRequest;
  options?: CustomRequestOptions;
}) {
  const { user_id: param0, ...queryParams } = params;

  return request<API.ApiResponse>(`/api/v1/admin/users/${param0}/status`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  });
}

/** 获取用户列表 管理员获取系统用户列表，支持搜索和筛选 GET /api/v1/admin/users/list */
export async function getUsersListApiV1AdminUsersListGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getUsersListApiV1AdminUsersListGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiPagedResponse>('/api/v1/admin/users/list', {
    method: 'GET',
    params: {
      // page has a default value: 1
      page: '1',
      // page_size has a default value: 20
      page_size: '20',

      ...params,
    },
    ...(options || {}),
  });
}

/** 获取用户统计 管理员获取系统用户统计信息 GET /api/v1/admin/users/statistics */
export async function getUserStatisticsApiV1AdminUsersStatisticsGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/users/statistics', {
    method: 'GET',
    ...(options || {}),
  });
}
