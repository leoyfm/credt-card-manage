/* eslint-disable */
// @ts-ignore
import { queryOptions, useMutation } from '@tanstack/vue-query';
import type { DefaultError } from '@tanstack/vue-query';
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as apis from './yonghutuijian';
import * as API from './types';

/** 获取推荐详情 获取指定推荐的详细信息 GET /api/v1/user/recommendations/${param0} */
export function getRecommendationDetailApiV1UserRecommendationsRecommendationIdGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getRecommendationDetailApiV1UserRecommendationsRecommendationIdGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getRecommendationDetailApiV1UserRecommendationsRecommendationIdGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getRecommendationDetailApiV1UserRecommendationsRecommendationIdGet',
      options,
    ],
  });
}

/** 更新推荐记录 更新推荐记录的状态或用户行动 PUT /api/v1/user/recommendations/${param0} */
export function useUpdateRecommendationApiV1UserRecommendationsRecommendationIdPutMutation(options?: {
  onSuccess?: (value?: API.ApiResponseRecommendationRecordResponse_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn:
      apis.updateRecommendationApiV1UserRecommendationsRecommendationIdPut,
    onSuccess(data: API.ApiResponseRecommendationRecordResponse_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 提交推荐反馈 对推荐提交用户反馈和行动 POST /api/v1/user/recommendations/${param0}/feedback */
export function useSubmitRecommendationFeedbackApiV1UserRecommendationsRecommendationIdFeedbackPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseRecommendationRecordResponse_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn:
      apis.submitRecommendationFeedbackApiV1UserRecommendationsRecommendationIdFeedbackPost,
    onSuccess(data: API.ApiResponseRecommendationRecordResponse_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取可用用户行动 获取用户可以对推荐执行的行动类型 GET /api/v1/user/recommendations/actions/available */
export function getAvailableUserActionsApiV1UserRecommendationsActionsAvailableGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getAvailableUserActionsApiV1UserRecommendationsActionsAvailableGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getAvailableUserActionsApiV1UserRecommendationsActionsAvailableGet',
      options,
    ],
  });
}

/** 评估推荐规则 基于系统规则为用户生成推荐 POST /api/v1/user/recommendations/evaluate-rules */
export function useEvaluateRecommendationRulesApiV1UserRecommendationsEvaluateRulesPostMutation(options?: {
  onSuccess?: (
    value?: API.ApiResponseListRecommendationRecordResponse_
  ) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn:
      apis.evaluateRecommendationRulesApiV1UserRecommendationsEvaluateRulesPost,
    onSuccess(data: API.ApiResponseListRecommendationRecordResponse_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取推荐历史 获取用户的推荐历史记录，支持筛选和分页 GET /api/v1/user/recommendations/history */
export function getRecommendationHistoryApiV1UserRecommendationsHistoryGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getRecommendationHistoryApiV1UserRecommendationsHistoryGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getRecommendationHistoryApiV1UserRecommendationsHistoryGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getRecommendationHistoryApiV1UserRecommendationsHistoryGet',
      options,
    ],
  });
}

/** 获取智能推荐 基于用户数据生成个性化推荐 GET /api/v1/user/recommendations/smart */
export function getSmartRecommendationsApiV1UserRecommendationsSmartGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getSmartRecommendationsApiV1UserRecommendationsSmartGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getSmartRecommendationsApiV1UserRecommendationsSmartGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getSmartRecommendationsApiV1UserRecommendationsSmartGet',
      options,
    ],
  });
}

/** 获取推荐统计 获取用户推荐的统计信息 GET /api/v1/user/recommendations/stats/overview */
export function getRecommendationStatsApiV1UserRecommendationsStatsOverviewGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getRecommendationStatsApiV1UserRecommendationsStatsOverviewGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getRecommendationStatsApiV1UserRecommendationsStatsOverviewGet',
      options,
    ],
  });
}

/** 获取可用推荐类型 获取系统支持的推荐类型列表 GET /api/v1/user/recommendations/types/available */
export function getAvailableRecommendationTypesApiV1UserRecommendationsTypesAvailableGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getAvailableRecommendationTypesApiV1UserRecommendationsTypesAvailableGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getAvailableRecommendationTypesApiV1UserRecommendationsTypesAvailableGet',
      options,
    ],
  });
}
