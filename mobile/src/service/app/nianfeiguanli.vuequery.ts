/* eslint-disable */
// @ts-ignore
import { queryOptions, useMutation } from '@tanstack/vue-query';
import type { DefaultError } from '@tanstack/vue-query';
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as apis from './nianfeiguanli';
import * as API from './types';

/** 批量检查年费减免 批量检查多张信用卡的年费减免条件 POST /api/annual-fees/batch/check-waivers */
export function useBatchCheckAnnualFeeWaiversApiAnnualFeesBatchCheckWaiversPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseListAnnualFeeWaiverCheck_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn:
      apis.batchCheckAnnualFeeWaiversApiAnnualFeesBatchCheckWaiversPost,
    onSuccess(data: API.ApiResponseListAnnualFeeWaiverCheck_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 批量创建年费记录 为多张信用卡批量创建年费记录 POST /api/annual-fees/batch/create-records */
export function useBatchCreateAnnualFeeRecordsApiAnnualFeesBatchCreateRecordsPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseDict_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn:
      apis.batchCreateAnnualFeeRecordsApiAnnualFeesBatchCreateRecordsPost,
    onSuccess(data: API.ApiResponseDict_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取年费记录列表 获取年费记录列表获取年费记录信息，支持多种筛选条件和模糊搜索。可以按照信用卡、年份、减免状态等进行过滤。参数:- page: 页码，从1开始- page_size: 每页数量，默认20，最大100- keyword: 搜索关键词，支持卡片名称、银行名称模糊匹配- card_id: 信用卡ID，筛选指定卡片的年费记录- fee_year: 年费年份，筛选指定年份的记录- waiver_status: 减免状态，可选值：pending、waived、paid、overdue GET /api/annual-fees/records */
export function getAnnualFeeRecordsApiAnnualFeesRecordsGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getAnnualFeeRecordsApiAnnualFeesRecordsGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getAnnualFeeRecordsApiAnnualFeesRecordsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getAnnualFeeRecordsApiAnnualFeesRecordsGet', options],
  });
}

/** 创建年费记录 创建年费记录 POST /api/annual-fees/records */
export function useCreateAnnualFeeRecordApiAnnualFeesRecordsPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseAnnualFeeRecord_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.createAnnualFeeRecordApiAnnualFeesRecordsPost,
    onSuccess(data: API.ApiResponseAnnualFeeRecord_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取年费记录详情 根据ID获取年费记录详情 GET /api/annual-fees/records/${param0} */
export function getAnnualFeeRecordApiAnnualFeesRecordsRecordIdGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getAnnualFeeRecordApiAnnualFeesRecordsRecordIdGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getAnnualFeeRecordApiAnnualFeesRecordsRecordIdGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getAnnualFeeRecordApiAnnualFeesRecordsRecordIdGet', options],
  });
}

/** 更新年费记录 更新年费记录 PUT /api/annual-fees/records/${param0} */
export function useUpdateAnnualFeeRecordApiAnnualFeesRecordsRecordIdPutMutation(options?: {
  onSuccess?: (value?: API.ApiResponseAnnualFeeRecord_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.updateAnnualFeeRecordApiAnnualFeesRecordsRecordIdPut,
    onSuccess(data: API.ApiResponseAnnualFeeRecord_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 自动创建年费记录 使用数据库函数自动创建年费记录 POST /api/annual-fees/records/auto */
export function useCreateAnnualFeeRecordAutoApiAnnualFeesRecordsAutoPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseDict_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.createAnnualFeeRecordAutoApiAnnualFeesRecordsAutoPost,
    onSuccess(data: API.ApiResponseDict_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取年费规则列表 获取年费规则列表获取系统中所有的年费规则，支持分页、模糊搜索和类型过滤。参数:- page: 页码，从1开始- page_size: 每页数量，默认20，最大100- keyword: 搜索关键词，支持规则名称、描述模糊匹配- fee_type: 年费类型过滤，可选值：rigid、transaction_count、transaction_amount、points_exchange GET /api/annual-fees/rules */
export function getAnnualFeeRulesApiAnnualFeesRulesGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getAnnualFeeRulesApiAnnualFeesRulesGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getAnnualFeeRulesApiAnnualFeesRulesGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getAnnualFeeRulesApiAnnualFeesRulesGet', options],
  });
}

/** 创建年费规则 创建新的年费规则创建新的年费减免规则，支持多种年费类型：- rigid: 刚性年费，不可减免- transaction_count: 刷卡次数减免- transaction_amount: 刷卡金额减免- points_exchange: 积分兑换减免参数:- rule_data: 年费规则创建数据 POST /api/annual-fees/rules */
export function useCreateAnnualFeeRuleApiAnnualFeesRulesPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseAnnualFeeRule_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.createAnnualFeeRuleApiAnnualFeesRulesPost,
    onSuccess(data: API.ApiResponseAnnualFeeRule_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取年费规则详情 根据ID获取年费规则详情获取指定年费规则的详细信息，包括规则名称、年费类型、减免条件、考核周期等完整信息。参数:- rule_id: 年费规则的UUID GET /api/annual-fees/rules/${param0} */
export function getAnnualFeeRuleApiAnnualFeesRulesRuleIdGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getAnnualFeeRuleApiAnnualFeesRulesRuleIdGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getAnnualFeeRuleApiAnnualFeesRulesRuleIdGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getAnnualFeeRuleApiAnnualFeesRulesRuleIdGet', options],
  });
}

/** 更新年费规则 更新年费规则 PUT /api/annual-fees/rules/${param0} */
export function useUpdateAnnualFeeRuleApiAnnualFeesRulesRuleIdPutMutation(options?: {
  onSuccess?: (value?: API.ApiResponseAnnualFeeRule_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.updateAnnualFeeRuleApiAnnualFeesRulesRuleIdPut,
    onSuccess(data: API.ApiResponseAnnualFeeRule_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 删除年费规则 删除年费规则 DELETE /api/annual-fees/rules/${param0} */
export function useDeleteAnnualFeeRuleApiAnnualFeesRulesRuleIdDeleteMutation(options?: {
  onSuccess?: (value?: API.ApiResponseNoneType_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.deleteAnnualFeeRuleApiAnnualFeesRulesRuleIdDelete,
    onSuccess(data: API.ApiResponseNoneType_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取年费统计信息 获取用户的年费统计信息 GET /api/annual-fees/statistics/${param0} */
export function getAnnualFeeStatisticsApiAnnualFeesStatisticsUserIdGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getAnnualFeeStatisticsApiAnnualFeesStatisticsUserIdGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getAnnualFeeStatisticsApiAnnualFeesStatisticsUserIdGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getAnnualFeeStatisticsApiAnnualFeesStatisticsUserIdGet',
      options,
    ],
  });
}

/** 检查年费减免条件 检查指定信用卡的年费减免条件 GET /api/annual-fees/waiver-check/${param0}/${param1} */
export function checkAnnualFeeWaiverApiAnnualFeesWaiverCheckCardIdFeeYearGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.checkAnnualFeeWaiverApiAnnualFeesWaiverCheckCardIdFeeYearGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.checkAnnualFeeWaiverApiAnnualFeesWaiverCheckCardIdFeeYearGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'checkAnnualFeeWaiverApiAnnualFeesWaiverCheckCardIdFeeYearGet',
      options,
    ],
  });
}

/** 检查用户所有卡的年费减免条件 检查用户所有信用卡的年费减免条件 GET /api/annual-fees/waiver-check/user/${param0} */
export function checkAllAnnualFeeWaiversApiAnnualFeesWaiverCheckUserUserIdGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.checkAllAnnualFeeWaiversApiAnnualFeesWaiverCheckUserUserIdGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.checkAllAnnualFeeWaiversApiAnnualFeesWaiverCheckUserUserIdGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'checkAllAnnualFeeWaiversApiAnnualFeesWaiverCheckUserUserIdGet',
      options,
    ],
  });
}
