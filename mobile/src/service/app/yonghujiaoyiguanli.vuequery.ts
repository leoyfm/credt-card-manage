/* eslint-disable */
// @ts-ignore
import { queryOptions, useMutation } from '@tanstack/vue-query';
import type { DefaultError } from '@tanstack/vue-query';
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as apis from './yonghujiaoyiguanli';
import * as API from './types';

/** 删除交易记录 删除指定的交易记录 DELETE /api/v1/user/transactions/${param0}/delete */
export function useDeleteTransactionApiV1UserTransactionsTransactionIdDeleteDeleteMutation(options?: {
  onSuccess?: (value?: API.ApiResponseBool_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn:
      apis.deleteTransactionApiV1UserTransactionsTransactionIdDeleteDelete,
    onSuccess(data: API.ApiResponseBool_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取交易记录详情 根据交易ID获取详细的交易记录信息 GET /api/v1/user/transactions/${param0}/details */
export function getTransactionDetailsApiV1UserTransactionsTransactionIdDetailsGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getTransactionDetailsApiV1UserTransactionsTransactionIdDetailsGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getTransactionDetailsApiV1UserTransactionsTransactionIdDetailsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getTransactionDetailsApiV1UserTransactionsTransactionIdDetailsGet',
      options,
    ],
  });
}

/** 更新交易记录 更新指定的交易记录信息 PUT /api/v1/user/transactions/${param0}/update */
export function useUpdateTransactionApiV1UserTransactionsTransactionIdUpdatePutMutation(options?: {
  onSuccess?: (value?: API.ApiResponseTransactionResponse_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn:
      apis.updateTransactionApiV1UserTransactionsTransactionIdUpdatePut,
    onSuccess(data: API.ApiResponseTransactionResponse_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取交易分类列表 获取所有可用的交易分类，用于创建和编辑交易时选择 GET /api/v1/user/transactions/categories */
export function getTransactionCategoriesApiV1UserTransactionsCategoriesGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getTransactionCategoriesApiV1UserTransactionsCategoriesGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getTransactionCategoriesApiV1UserTransactionsCategoriesGet',
      options,
    ],
  });
}

/** 创建交易记录 创建新的交易记录，支持消费、收入、退款等类型 POST /api/v1/user/transactions/create */
export function useCreateTransactionApiV1UserTransactionsCreatePostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseTransactionResponse_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.createTransactionApiV1UserTransactionsCreatePost,
    onSuccess(data: API.ApiResponseTransactionResponse_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取交易记录列表 获取当前用户的交易记录列表，支持分页、筛选和搜索 GET /api/v1/user/transactions/list */
export function getTransactionsApiV1UserTransactionsListGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getTransactionsApiV1UserTransactionsListGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getTransactionsApiV1UserTransactionsListGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getTransactionsApiV1UserTransactionsListGet', options],
  });
}

/** 获取分类统计数据 获取指定时间范围内的交易分类统计，包括各分类的支出分布 GET /api/v1/user/transactions/statistics/categories */
export function getCategoryStatisticsApiV1UserTransactionsStatisticsCategoriesGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCategoryStatisticsApiV1UserTransactionsStatisticsCategoriesGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getCategoryStatisticsApiV1UserTransactionsStatisticsCategoriesGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getCategoryStatisticsApiV1UserTransactionsStatisticsCategoriesGet',
      options,
    ],
  });
}

/** 获取月度趋势分析 获取指定月数的月度交易趋势分析数据 GET /api/v1/user/transactions/statistics/monthly-trends */
export function getMonthlyTrendsApiV1UserTransactionsStatisticsMonthlyTrendsGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getMonthlyTrendsApiV1UserTransactionsStatisticsMonthlyTrendsGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getMonthlyTrendsApiV1UserTransactionsStatisticsMonthlyTrendsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getMonthlyTrendsApiV1UserTransactionsStatisticsMonthlyTrendsGet',
      options,
    ],
  });
}

/** 获取交易统计概览 获取指定时间范围内的交易统计数据，包括总额、笔数、积分等 GET /api/v1/user/transactions/statistics/overview */
export function getTransactionStatisticsApiV1UserTransactionsStatisticsOverviewGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getTransactionStatisticsApiV1UserTransactionsStatisticsOverviewGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getTransactionStatisticsApiV1UserTransactionsStatisticsOverviewGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getTransactionStatisticsApiV1UserTransactionsStatisticsOverviewGet',
      options,
    ],
  });
}
