/* eslint-disable */
// @ts-ignore
import { queryOptions, useMutation } from '@tanstack/vue-query';
import type { DefaultError } from '@tanstack/vue-query';
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as apis from './v1Yonghugongneng';
import * as API from './types';

/** 获取信用卡列表 获取用户的信用卡列表支持多种筛选条件：- 关键词搜索（卡片名称、银行名称）- 状态筛选- 银行筛选- 卡片类型筛选- 主卡筛选- 即将过期筛选 GET /api/v1/user/cards */
export function getCreditCardsApiV1UserCardsGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCreditCardsApiV1UserCardsGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getCreditCardsApiV1UserCardsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getCreditCardsApiV1UserCardsGet', options],
  });
}

/** 创建信用卡 创建新的信用卡- **card_name**: 卡片名称- **card_number**: 卡号（会进行加密存储）- **credit_limit**: 信用额度- **expiry_month**: 有效期月份- **expiry_year**: 有效期年份- **bank_id**: 银行ID（可选）- **bank_name**: 银行名称（如果不提供bank_id） POST /api/v1/user/cards */
export function useCreateCreditCardApiV1UserCardsPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponse) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.createCreditCardApiV1UserCardsPost,
    onSuccess(data: API.ApiResponse) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取信用卡详情 获取指定信用卡的详细信息 GET /api/v1/user/cards/${param0} */
export function getCreditCardApiV1UserCardsCardIdGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCreditCardApiV1UserCardsCardIdGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getCreditCardApiV1UserCardsCardIdGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getCreditCardApiV1UserCardsCardIdGet', options],
  });
}

/** 更新信用卡 更新信用卡信息可更新的字段包括：- 卡片名称- 信用额度- 有效期- 账单日和还款日- 年费信息- 特色功能- 备注等 PUT /api/v1/user/cards/${param0} */
export function useUpdateCreditCardApiV1UserCardsCardIdPutMutation(options?: {
  onSuccess?: (value?: API.ApiResponse) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.updateCreditCardApiV1UserCardsCardIdPut,
    onSuccess(data: API.ApiResponse) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 删除信用卡 删除信用卡注意：删除信用卡会同时删除相关的交易记录和年费记录 DELETE /api/v1/user/cards/${param0} */
export function useDeleteCreditCardApiV1UserCardsCardIdDeleteMutation(options?: {
  onSuccess?: (value?: API.ApiResponse) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.deleteCreditCardApiV1UserCardsCardIdDelete,
    onSuccess(data: API.ApiResponse) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 更新信用卡状态 更新信用卡状态支持的状态：- active: 激活- frozen: 冻结- closed: 关闭 PATCH /api/v1/user/cards/${param0}/status */
export function useUpdateCardStatusApiV1UserCardsCardIdStatusPatchMutation(options?: {
  onSuccess?: (value?: API.ApiResponse) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.updateCardStatusApiV1UserCardsCardIdStatusPatch,
    onSuccess(data: API.ApiResponse) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取银行列表 获取银行列表用于创建信用卡时选择银行 GET /api/v1/user/cards/banks/list */
export function getBanksApiV1UserCardsBanksListGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getBanksApiV1UserCardsBanksListGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getBanksApiV1UserCardsBanksListGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getBanksApiV1UserCardsBanksListGet', options],
  });
}

/** 获取信用卡详细统计 获取信用卡详细统计包括：- 摘要信息- 按银行统计- 按状态统计- 按卡片等级统计- 使用率分布 GET /api/v1/user/cards/statistics/detailed */
export function getCardStatisticsApiV1UserCardsStatisticsDetailedGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getCardStatisticsApiV1UserCardsStatisticsDetailedGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getCardStatisticsApiV1UserCardsStatisticsDetailedGet', options],
  });
}

/** 获取信用卡摘要统计 获取信用卡摘要统计包括：- 信用卡总数- 激活卡片数- 总信用额度- 总已用额度- 总可用额度- 平均使用率- 即将过期卡片数 GET /api/v1/user/cards/summary/overview */
export function getCardSummaryApiV1UserCardsSummaryOverviewGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getCardSummaryApiV1UserCardsSummaryOverviewGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getCardSummaryApiV1UserCardsSummaryOverviewGet', options],
  });
}

/** 注销账户 注销当前用户账户（软删除） DELETE /api/v1/user/profile/account */
export function useDeleteAccountApiV1UserProfileAccountDeleteMutation(options?: {
  onSuccess?: (value?: API.ApiResponseBool_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.deleteAccountApiV1UserProfileAccountDelete,
    onSuccess(data: API.ApiResponseBool_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 修改密码 修改当前用户的登录密码 POST /api/v1/user/profile/change-password */
export function useChangePasswordApiV1UserProfileChangePasswordPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseBool_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.changePasswordApiV1UserProfileChangePasswordPost,
    onSuccess(data: API.ApiResponseBool_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取个人信息 获取当前用户的个人资料信息 GET /api/v1/user/profile/info */
export function getUserInfoApiV1UserProfileInfoGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getUserInfoApiV1UserProfileInfoGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getUserInfoApiV1UserProfileInfoGet', options],
  });
}

/** 个人登录日志 获取当前用户的登录日志记录 GET /api/v1/user/profile/login-logs */
export function getLoginLogsApiV1UserProfileLoginLogsGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getLoginLogsApiV1UserProfileLoginLogsGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getLoginLogsApiV1UserProfileLoginLogsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getLoginLogsApiV1UserProfileLoginLogsGet', options],
  });
}

/** 退出登录 退出当前用户的登录状态 POST /api/v1/user/profile/logout */
export function useLogoutApiV1UserProfileLogoutPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseBool_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.logoutApiV1UserProfileLogoutPost,
    onSuccess(data: API.ApiResponseBool_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 个人统计信息 获取当前用户的统计信息（卡片、交易、积分等） GET /api/v1/user/profile/statistics */
export function getUserStatisticsApiV1UserProfileStatisticsGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getUserStatisticsApiV1UserProfileStatisticsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getUserStatisticsApiV1UserProfileStatisticsGet', options],
  });
}

/** 更新个人资料 更新当前用户的个人资料信息 PUT /api/v1/user/profile/update */
export function useUpdateUserProfileApiV1UserProfileUpdatePutMutation(options?: {
  onSuccess?: (value?: API.ApiResponseUserProfileResponse_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.updateUserProfileApiV1UserProfileUpdatePut,
    onSuccess(data: API.ApiResponseUserProfileResponse_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 微信绑定信息 获取当前用户的微信绑定信息 GET /api/v1/user/profile/wechat-bindings */
export function getWechatBindingsApiV1UserProfileWechatBindingsGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getWechatBindingsApiV1UserProfileWechatBindingsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getWechatBindingsApiV1UserProfileWechatBindingsGet', options],
  });
}

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
