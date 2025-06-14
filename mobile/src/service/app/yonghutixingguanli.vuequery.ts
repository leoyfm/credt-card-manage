/* eslint-disable */
// @ts-ignore
import { queryOptions, useMutation } from '@tanstack/vue-query';
import type { DefaultError } from '@tanstack/vue-query';
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as apis from './yonghutixingguanli';
import * as API from './types';

/** 生成自动提醒 为用户的信用卡自动生成提醒记录 POST /api/v1/user/reminders/generate-automatic */
export function useGenerateAutomaticRemindersApiV1UserRemindersGenerateAutomaticPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseDict_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn:
      apis.generateAutomaticRemindersApiV1UserRemindersGenerateAutomaticPost,
    onSuccess(data: API.ApiResponseDict_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 标记所有提醒为已读 将用户的所有未读提醒标记为已读状态 POST /api/v1/user/reminders/mark-all-read */
export function useMarkAllRemindersAsReadApiV1UserRemindersMarkAllReadPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseMarkAllReadResponse_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.markAllRemindersAsReadApiV1UserRemindersMarkAllReadPost,
    onSuccess(data: API.ApiResponseMarkAllReadResponse_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取最近的提醒 获取用户最近的提醒记录 GET /api/v1/user/reminders/recent */
export function getRecentRemindersApiV1UserRemindersRecentGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getRecentRemindersApiV1UserRemindersRecentGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getRecentRemindersApiV1UserRemindersRecentGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getRecentRemindersApiV1UserRemindersRecentGet', options],
  });
}

/** 获取提醒记录列表 获取用户的提醒记录列表，支持按设置、状态、日期筛选和分页 GET /api/v1/user/reminders/records */
export function getReminderRecordsApiV1UserRemindersRecordsGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getReminderRecordsApiV1UserRemindersRecordsGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getReminderRecordsApiV1UserRemindersRecordsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getReminderRecordsApiV1UserRemindersRecordsGet', options],
  });
}

/** 创建提醒记录 为用户创建新的提醒记录 POST /api/v1/user/reminders/records */
export function useCreateReminderRecordApiV1UserRemindersRecordsPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseReminderRecordResponse_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.createReminderRecordApiV1UserRemindersRecordsPost,
    onSuccess(data: API.ApiResponseReminderRecordResponse_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取提醒记录详情 获取指定提醒记录的详细信息 GET /api/v1/user/reminders/records/${param0} */
export function getReminderRecordApiV1UserRemindersRecordsRecordIdGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getReminderRecordApiV1UserRemindersRecordsRecordIdGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getReminderRecordApiV1UserRemindersRecordsRecordIdGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getReminderRecordApiV1UserRemindersRecordsRecordIdGet',
      options,
    ],
  });
}

/** 标记提醒为已读 将指定的提醒记录标记为已读状态 POST /api/v1/user/reminders/records/${param0}/read */
export function useMarkReminderAsReadApiV1UserRemindersRecordsRecordIdReadPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseReminderRecordResponse_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn:
      apis.markReminderAsReadApiV1UserRemindersRecordsRecordIdReadPost,
    onSuccess(data: API.ApiResponseReminderRecordResponse_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取提醒设置列表 获取用户的提醒设置列表，支持按信用卡、类型、状态筛选和分页 GET /api/v1/user/reminders/settings */
export function getReminderSettingsApiV1UserRemindersSettingsGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getReminderSettingsApiV1UserRemindersSettingsGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getReminderSettingsApiV1UserRemindersSettingsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getReminderSettingsApiV1UserRemindersSettingsGet', options],
  });
}

/** 创建提醒设置 为用户创建新的提醒设置，可以是全局提醒或特定信用卡的提醒 POST /api/v1/user/reminders/settings */
export function useCreateReminderSettingApiV1UserRemindersSettingsPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseReminderSettingResponse_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.createReminderSettingApiV1UserRemindersSettingsPost,
    onSuccess(data: API.ApiResponseReminderSettingResponse_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取提醒设置详情 获取指定提醒设置的详细信息 GET /api/v1/user/reminders/settings/${param0} */
export function getReminderSettingApiV1UserRemindersSettingsSettingIdGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getReminderSettingApiV1UserRemindersSettingsSettingIdGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getReminderSettingApiV1UserRemindersSettingsSettingIdGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getReminderSettingApiV1UserRemindersSettingsSettingIdGet',
      options,
    ],
  });
}

/** 更新提醒设置 更新指定的提醒设置信息 PUT /api/v1/user/reminders/settings/${param0} */
export function useUpdateReminderSettingApiV1UserRemindersSettingsSettingIdPutMutation(options?: {
  onSuccess?: (value?: API.ApiResponseReminderSettingResponse_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn:
      apis.updateReminderSettingApiV1UserRemindersSettingsSettingIdPut,
    onSuccess(data: API.ApiResponseReminderSettingResponse_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 删除提醒设置 删除指定的提醒设置及其关联的提醒记录 DELETE /api/v1/user/reminders/settings/${param0} */
export function useDeleteReminderSettingApiV1UserRemindersSettingsSettingIdDeleteMutation(options?: {
  onSuccess?: (value?: API.ApiResponseBool_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn:
      apis.deleteReminderSettingApiV1UserRemindersSettingsSettingIdDelete,
    onSuccess(data: API.ApiResponseBool_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取提醒统计 获取用户的提醒统计信息，包括设置数量、提醒数量、阅读率等 GET /api/v1/user/reminders/statistics */
export function getReminderStatisticsApiV1UserRemindersStatisticsGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getReminderStatisticsApiV1UserRemindersStatisticsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getReminderStatisticsApiV1UserRemindersStatisticsGet', options],
  });
}

/** 获取未读提醒个数 获取用户的未读提醒个数统计，包括总数、今日未读、高优先级未读等 GET /api/v1/user/reminders/unread-count */
export function getUnreadRemindersCountApiV1UserRemindersUnreadCountGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getUnreadRemindersCountApiV1UserRemindersUnreadCountGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getUnreadRemindersCountApiV1UserRemindersUnreadCountGet',
      options,
    ],
  });
}

/** 获取即将到来的提醒 获取指定天数内即将到来的提醒，按优先级分类 GET /api/v1/user/reminders/upcoming */
export function getUpcomingRemindersApiV1UserRemindersUpcomingGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getUpcomingRemindersApiV1UserRemindersUpcomingGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getUpcomingRemindersApiV1UserRemindersUpcomingGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getUpcomingRemindersApiV1UserRemindersUpcomingGet', options],
  });
}
