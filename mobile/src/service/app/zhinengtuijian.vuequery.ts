/* eslint-disable */
// @ts-ignore
import { queryOptions, useMutation } from '@tanstack/vue-query';
import type { DefaultError } from '@tanstack/vue-query';
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as apis from './zhinengtuijian';
import * as API from './types';

/** 获取信用卡推荐 获取信用卡推荐基于用户消费习惯和偏好，智能推荐最适合的信用卡产品。支持分页和模糊搜索功能。参数:- page: 页码，从1开始- page_size: 每页数量，默认20，最大100- keyword: 搜索关键词，支持银行名称、卡片类型模糊匹配 GET /api/recommendations/ */
export function getRecommendationsApiRecommendationsGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getRecommendationsApiRecommendationsGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getRecommendationsApiRecommendationsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getRecommendationsApiRecommendationsGet', options],
  });
}

/** 获取推荐详情 根据ID获取推荐详情获取指定推荐的详细信息，包括推荐理由、卡片特色等。 GET /api/recommendations/${param0} */
export function getRecommendationApiRecommendationsRecommendationIdGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getRecommendationApiRecommendationsRecommendationIdGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getRecommendationApiRecommendationsRecommendationIdGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getRecommendationApiRecommendationsRecommendationIdGet',
      options,
    ],
  });
}

/** 提交推荐反馈 提交推荐反馈用户对推荐结果进行反馈，用于优化推荐算法。 PUT /api/recommendations/${param0}/feedback */
export function useSubmitRecommendationFeedbackApiRecommendationsRecommendationIdFeedbackPutMutation(options?: {
  onSuccess?: (value?: API.ApiResponseNoneType_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn:
      apis.submitRecommendationFeedbackApiRecommendationsRecommendationIdFeedbackPut,
    onSuccess(data: API.ApiResponseNoneType_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 生成个性化推荐 生成个性化推荐基于用户的消费记录、偏好设置等生成个性化的信用卡推荐。 POST /api/recommendations/generate */
export function useGenerateRecommendationsApiRecommendationsGeneratePostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseListRecommendation_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.generateRecommendationsApiRecommendationsGeneratePost,
    onSuccess(data: API.ApiResponseListRecommendation_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}
