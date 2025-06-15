/* eslint-disable */
// @ts-ignore
import { queryOptions, useMutation } from '@tanstack/vue-query';
import type { DefaultError } from '@tanstack/vue-query';
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as apis from './guanliyuanyonghuguanli';
import * as API from './types';

/** 删除用户 管理员删除指定用户（谨慎操作） DELETE /api/v1/admin/users/${param0}/delete */
export function useDeleteUserApiV1AdminUsersUserIdDeleteDeleteMutation(options?: {
  onSuccess?: (value?: API.ApiResponse) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.deleteUserApiV1AdminUsersUserIdDeleteDelete,
    onSuccess(data: API.ApiResponse) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取用户详情 管理员获取指定用户的详细信息 GET /api/v1/admin/users/${param0}/details */
export function getUserDetailsApiV1AdminUsersUserIdDetailsGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getUserDetailsApiV1AdminUsersUserIdDetailsGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getUserDetailsApiV1AdminUsersUserIdDetailsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getUserDetailsApiV1AdminUsersUserIdDetailsGet', options],
  });
}

/** 获取用户登录日志 管理员获取指定用户的登录日志 GET /api/v1/admin/users/${param0}/login-logs */
export function getUserLoginLogsApiV1AdminUsersUserIdLoginLogsGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getUserLoginLogsApiV1AdminUsersUserIdLoginLogsGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getUserLoginLogsApiV1AdminUsersUserIdLoginLogsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getUserLoginLogsApiV1AdminUsersUserIdLoginLogsGet', options],
  });
}

/** 更新用户权限 管理员更新用户的权限（管理员权限、验证状态） PUT /api/v1/admin/users/${param0}/permissions */
export function useUpdateUserPermissionsApiV1AdminUsersUserIdPermissionsPutMutation(options?: {
  onSuccess?: (value?: API.ApiResponse) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.updateUserPermissionsApiV1AdminUsersUserIdPermissionsPut,
    onSuccess(data: API.ApiResponse) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 更新用户状态 管理员更新用户的激活状态 PUT /api/v1/admin/users/${param0}/status */
export function useUpdateUserStatusApiV1AdminUsersUserIdStatusPutMutation(options?: {
  onSuccess?: (value?: API.ApiResponse) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.updateUserStatusApiV1AdminUsersUserIdStatusPut,
    onSuccess(data: API.ApiResponse) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取用户列表 管理员获取系统用户列表，支持搜索和筛选 GET /api/v1/admin/users/list */
export function getUsersListApiV1AdminUsersListGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getUsersListApiV1AdminUsersListGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getUsersListApiV1AdminUsersListGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getUsersListApiV1AdminUsersListGet', options],
  });
}

/** 获取用户统计 管理员获取系统用户统计信息 GET /api/v1/admin/users/statistics */
export function getUserStatisticsApiV1AdminUsersStatisticsGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getUserStatisticsApiV1AdminUsersStatisticsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getUserStatisticsApiV1AdminUsersStatisticsGet', options],
  });
}
