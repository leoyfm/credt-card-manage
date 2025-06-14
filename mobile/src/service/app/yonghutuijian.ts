/* eslint-disable */
// @ts-ignore
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as API from './types';

/** 获取推荐详情 获取指定推荐的详细信息 GET /api/v1/user/recommendations/${param0} */
export async function getRecommendationDetailApiV1UserRecommendationsRecommendationIdGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getRecommendationDetailApiV1UserRecommendationsRecommendationIdGetParams;
  options?: CustomRequestOptions;
}) {
  const { recommendation_id: param0, ...queryParams } = params;

  return request<API.ApiResponseRecommendationRecordResponse_>(
    `/api/v1/user/recommendations/${param0}`,
    {
      method: 'GET',
      params: { ...queryParams },
      ...(options || {}),
    }
  );
}

/** 更新推荐记录 更新推荐记录的状态或用户行动 PUT /api/v1/user/recommendations/${param0} */
export async function updateRecommendationApiV1UserRecommendationsRecommendationIdPut({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.updateRecommendationApiV1UserRecommendationsRecommendationIdPutParams;
  body: API.RecommendationRecordUpdate;
  options?: CustomRequestOptions;
}) {
  const { recommendation_id: param0, ...queryParams } = params;

  return request<API.ApiResponseRecommendationRecordResponse_>(
    `/api/v1/user/recommendations/${param0}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      params: { ...queryParams },
      data: body,
      ...(options || {}),
    }
  );
}

/** 提交推荐反馈 对推荐提交用户反馈和行动 POST /api/v1/user/recommendations/${param0}/feedback */
export async function submitRecommendationFeedbackApiV1UserRecommendationsRecommendationIdFeedbackPost({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.submitRecommendationFeedbackApiV1UserRecommendationsRecommendationIdFeedbackPostParams;
  body: API.RecommendationFeedback;
  options?: CustomRequestOptions;
}) {
  const { recommendation_id: param0, ...queryParams } = params;

  return request<API.ApiResponseRecommendationRecordResponse_>(
    `/api/v1/user/recommendations/${param0}/feedback`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      params: { ...queryParams },
      data: body,
      ...(options || {}),
    }
  );
}

/** 获取可用用户行动 获取用户可以对推荐执行的行动类型 GET /api/v1/user/recommendations/actions/available */
export async function getAvailableUserActionsApiV1UserRecommendationsActionsAvailableGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseListStr_>(
    '/api/v1/user/recommendations/actions/available',
    {
      method: 'GET',
      ...(options || {}),
    }
  );
}

/** 评估推荐规则 基于系统规则为用户生成推荐 POST /api/v1/user/recommendations/evaluate-rules */
export async function evaluateRecommendationRulesApiV1UserRecommendationsEvaluateRulesPost({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseListRecommendationRecordResponse_>(
    '/api/v1/user/recommendations/evaluate-rules',
    {
      method: 'POST',
      ...(options || {}),
    }
  );
}

/** 获取推荐历史 获取用户的推荐历史记录，支持筛选和分页 GET /api/v1/user/recommendations/history */
export async function getRecommendationHistoryApiV1UserRecommendationsHistoryGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getRecommendationHistoryApiV1UserRecommendationsHistoryGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiPagedResponseRecommendationRecordResponse_>(
    '/api/v1/user/recommendations/history',
    {
      method: 'GET',
      params: {
        // page has a default value: 1
        page: '1',
        // page_size has a default value: 20
        page_size: '20',
        ...params,
      },
      ...(options || {}),
    }
  );
}

/** 获取智能推荐 基于用户数据生成个性化推荐 GET /api/v1/user/recommendations/smart */
export async function getSmartRecommendationsApiV1UserRecommendationsSmartGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getSmartRecommendationsApiV1UserRecommendationsSmartGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseListRecommendationRecordResponse_>(
    '/api/v1/user/recommendations/smart',
    {
      method: 'GET',
      params: {
        // limit has a default value: 5
        limit: '5',
        ...params,
      },
      ...(options || {}),
    }
  );
}

/** 获取推荐统计 获取用户推荐的统计信息 GET /api/v1/user/recommendations/stats/overview */
export async function getRecommendationStatsApiV1UserRecommendationsStatsOverviewGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseRecommendationStats_>(
    '/api/v1/user/recommendations/stats/overview',
    {
      method: 'GET',
      ...(options || {}),
    }
  );
}

/** 获取可用推荐类型 获取系统支持的推荐类型列表 GET /api/v1/user/recommendations/types/available */
export async function getAvailableRecommendationTypesApiV1UserRecommendationsTypesAvailableGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseListStr_>(
    '/api/v1/user/recommendations/types/available',
    {
      method: 'GET',
      ...(options || {}),
    }
  );
}
