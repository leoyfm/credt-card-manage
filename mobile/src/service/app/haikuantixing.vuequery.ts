/* eslint-disable */
// @ts-ignore
import { queryOptions, useMutation } from '@tanstack/vue-query';
import type { DefaultError } from '@tanstack/vue-query';
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as apis from './haikuantixing';
import * as API from './types';

/** 获取还款提醒列表 获取还款提醒列表获取用户的还款提醒信息，支持分页和模糊搜索。包括还款日期、金额、状态等信息。参数:- page: 页码，从1开始- page_size: 每页数量，默认20，最大100- keyword: 搜索关键词，支持卡片名称、银行名称模糊匹配 GET /api/reminders/ */
export function getRemindersApiRemindersGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getRemindersApiRemindersGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getRemindersApiRemindersGet(queryKey[1] as typeof options);
    },
    queryKey: ['getRemindersApiRemindersGet', options],
  });
}

/** 创建还款提醒 创建新的还款提醒为指定信用卡创建还款提醒，包括提醒时间、金额等信息。 POST /api/reminders/ */
export function useCreateReminderApiRemindersPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseReminder_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.createReminderApiRemindersPost,
    onSuccess(data: API.ApiResponseReminder_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取还款提醒详情 根据ID获取还款提醒详情获取指定还款提醒的详细信息。 GET /api/reminders/${param0} */
export function getReminderApiRemindersReminderIdGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getReminderApiRemindersReminderIdGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getReminderApiRemindersReminderIdGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getReminderApiRemindersReminderIdGet', options],
  });
}

/** 更新还款提醒 更新还款提醒信息更新指定还款提醒的信息，如提醒时间、金额等。 PUT /api/reminders/${param0} */
export function useUpdateReminderApiRemindersReminderIdPutMutation(options?: {
  onSuccess?: (value?: API.ApiResponseReminder_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.updateReminderApiRemindersReminderIdPut,
    onSuccess(data: API.ApiResponseReminder_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 删除还款提醒 删除还款提醒从系统中删除指定的还款提醒记录。 DELETE /api/reminders/${param0} */
export function useDeleteReminderApiRemindersReminderIdDeleteMutation(options?: {
  onSuccess?: (value?: API.ApiResponseNoneType_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.deleteReminderApiRemindersReminderIdDelete,
    onSuccess(data: API.ApiResponseNoneType_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 标记提醒已读 标记还款提醒为已读状态将指定的还款提醒标记为已读，避免重复提醒。 PUT /api/reminders/${param0}/mark-read */
export function useMarkReminderReadApiRemindersReminderIdMarkReadPutMutation(options?: {
  onSuccess?: (value?: API.ApiResponseNoneType_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.markReminderReadApiRemindersReminderIdMarkReadPut,
    onSuccess(data: API.ApiResponseNoneType_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}
