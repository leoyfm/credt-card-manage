/* eslint-disable */
// @ts-ignore
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as API from './types';

/** 获取年费管理概览 管理员获取系统年费管理统计概览 GET /api/v1/admin/cards/annual-fee-summary */
export async function getAnnualFeeSummaryApiV1AdminCardsAnnualFeeSummaryGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getAnnualFeeSummaryApiV1AdminCardsAnnualFeeSummaryGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/annual-fee-summary', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  });
}

/** 获取银行分布统计 管理员获取各银行信用卡分布情况 GET /api/v1/admin/cards/bank-distribution */
export async function getBankDistributionApiV1AdminCardsBankDistributionGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/bank-distribution', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 获取卡片类型分布 管理员获取信用卡类型、等级分布统计 GET /api/v1/admin/cards/card-types */
export async function getCardTypesDistributionApiV1AdminCardsCardTypesGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/card-types', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 获取即将到期卡片统计 管理员获取即将到期信用卡的统计信息 GET /api/v1/admin/cards/expiry-alerts */
export async function getExpiryAlertsApiV1AdminCardsExpiryAlertsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getExpiryAlertsApiV1AdminCardsExpiryAlertsGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/expiry-alerts', {
    method: 'GET',
    params: {
      // months_ahead has a default value: 3
      months_ahead: '3',
      ...params,
    },
    ...(options || {}),
  });
}

/** 获取信用卡健康状况 管理员获取系统信用卡健康状况分析 GET /api/v1/admin/cards/health-status */
export async function getCardHealthStatusApiV1AdminCardsHealthStatusGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/health-status', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 获取信用卡系统统计 管理员获取系统级信用卡统计数据（脱敏） GET /api/v1/admin/cards/statistics */
export async function getCardStatisticsApiV1AdminCardsStatisticsGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/statistics', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 获取信用卡趋势分析 管理员获取信用卡增长趋势和使用情况分析 GET /api/v1/admin/cards/trends */
export async function getCardTrendsApiV1AdminCardsTrendsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCardTrendsApiV1AdminCardsTrendsGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/trends', {
    method: 'GET',
    params: {
      // months has a default value: 6
      months: '6',
      ...params,
    },
    ...(options || {}),
  });
}

/** 获取信用额度利用率分析 管理员获取系统信用额度利用率分布和风险分析 GET /api/v1/admin/cards/utilization-analysis */
export async function getUtilizationAnalysisApiV1AdminCardsUtilizationAnalysisGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/admin/cards/utilization-analysis', {
    method: 'GET',
    ...(options || {}),
  });
}
