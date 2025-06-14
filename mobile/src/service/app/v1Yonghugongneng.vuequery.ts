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
