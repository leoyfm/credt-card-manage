/* eslint-disable */
// @ts-ignore
import { queryOptions, useMutation } from '@tanstack/vue-query';
import type { DefaultError } from '@tanstack/vue-query';
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as apis from './guanliyuanxinyongkaguanli';
import * as API from './types';

/** 获取年费管理概览 管理员获取系统年费管理统计概览 GET /api/v1/admin/cards/annual-fee-summary */
export function getAnnualFeeSummaryApiV1AdminCardsAnnualFeeSummaryGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getAnnualFeeSummaryApiV1AdminCardsAnnualFeeSummaryGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getAnnualFeeSummaryApiV1AdminCardsAnnualFeeSummaryGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getAnnualFeeSummaryApiV1AdminCardsAnnualFeeSummaryGet',
      options,
    ],
  });
}

/** 获取银行分布统计 管理员获取各银行信用卡分布情况 GET /api/v1/admin/cards/bank-distribution */
export function getBankDistributionApiV1AdminCardsBankDistributionGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getBankDistributionApiV1AdminCardsBankDistributionGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getBankDistributionApiV1AdminCardsBankDistributionGet',
      options,
    ],
  });
}

/** 获取卡片类型分布 管理员获取信用卡类型、等级分布统计 GET /api/v1/admin/cards/card-types */
export function getCardTypesDistributionApiV1AdminCardsCardTypesGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getCardTypesDistributionApiV1AdminCardsCardTypesGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getCardTypesDistributionApiV1AdminCardsCardTypesGet', options],
  });
}

/** 获取即将到期卡片统计 管理员获取即将到期信用卡的统计信息 GET /api/v1/admin/cards/expiry-alerts */
export function getExpiryAlertsApiV1AdminCardsExpiryAlertsGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getExpiryAlertsApiV1AdminCardsExpiryAlertsGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getExpiryAlertsApiV1AdminCardsExpiryAlertsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getExpiryAlertsApiV1AdminCardsExpiryAlertsGet', options],
  });
}

/** 获取信用卡健康状况 管理员获取系统信用卡健康状况分析 GET /api/v1/admin/cards/health-status */
export function getCardHealthStatusApiV1AdminCardsHealthStatusGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getCardHealthStatusApiV1AdminCardsHealthStatusGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getCardHealthStatusApiV1AdminCardsHealthStatusGet', options],
  });
}

/** 获取信用卡系统统计 管理员获取系统级信用卡统计数据（脱敏） GET /api/v1/admin/cards/statistics */
export function getCardStatisticsApiV1AdminCardsStatisticsGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getCardStatisticsApiV1AdminCardsStatisticsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getCardStatisticsApiV1AdminCardsStatisticsGet', options],
  });
}

/** 获取信用卡趋势分析 管理员获取信用卡增长趋势和使用情况分析 GET /api/v1/admin/cards/trends */
export function getCardTrendsApiV1AdminCardsTrendsGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCardTrendsApiV1AdminCardsTrendsGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getCardTrendsApiV1AdminCardsTrendsGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getCardTrendsApiV1AdminCardsTrendsGet', options],
  });
}

/** 获取信用额度利用率分析 管理员获取系统信用额度利用率分布和风险分析 GET /api/v1/admin/cards/utilization-analysis */
export function getUtilizationAnalysisApiV1AdminCardsUtilizationAnalysisGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getUtilizationAnalysisApiV1AdminCardsUtilizationAnalysisGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: [
      'getUtilizationAnalysisApiV1AdminCardsUtilizationAnalysisGet',
      options,
    ],
  });
}
