/* eslint-disable */
// @ts-ignore
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as API from './types';

/** 获取信用卡列表 获取用户的信用卡列表支持多种筛选条件：- 关键词搜索（卡片名称、银行名称）- 状态筛选- 银行筛选- 卡片类型筛选- 主卡筛选- 即将过期筛选 GET /api/v1/user/cards */
export async function getCreditCardsApiV1UserCardsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCreditCardsApiV1UserCardsGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiPagedResponse>('/api/v1/user/cards', {
    method: 'GET',
    params: {
      // page has a default value: 1
      page: '1',
      // page_size has a default value: 20
      page_size: '20',
      ...params,
    },
    ...(options || {}),
  });
}

/** 创建信用卡 创建新的信用卡- **card_name**: 卡片名称- **card_number**: 卡号（会进行加密存储）- **credit_limit**: 信用额度- **expiry_month**: 有效期月份- **expiry_year**: 有效期年份- **bank_id**: 银行ID（可选）- **bank_name**: 银行名称（如果不提供bank_id） POST /api/v1/user/cards */
export async function createCreditCardApiV1UserCardsPost({
  body,
  options,
}: {
  body: API.CreditCardCreate;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/user/cards', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 获取信用卡详情 获取指定信用卡的详细信息 GET /api/v1/user/cards/${param0} */
export async function getCreditCardApiV1UserCardsCardIdGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCreditCardApiV1UserCardsCardIdGetParams;
  options?: CustomRequestOptions;
}) {
  const { card_id: param0, ...queryParams } = params;

  return request<API.ApiResponse>(`/api/v1/user/cards/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  });
}

/** 更新信用卡 更新信用卡信息可更新的字段包括：- 卡片名称- 信用额度- 有效期- 账单日和还款日- 年费信息- 特色功能- 备注等 PUT /api/v1/user/cards/${param0} */
export async function updateCreditCardApiV1UserCardsCardIdPut({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.updateCreditCardApiV1UserCardsCardIdPutParams;
  body: API.CreditCardUpdate;
  options?: CustomRequestOptions;
}) {
  const { card_id: param0, ...queryParams } = params;

  return request<API.ApiResponse>(`/api/v1/user/cards/${param0}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  });
}

/** 删除信用卡 删除信用卡注意：删除信用卡会同时删除相关的交易记录和年费记录 DELETE /api/v1/user/cards/${param0} */
export async function deleteCreditCardApiV1UserCardsCardIdDelete({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.deleteCreditCardApiV1UserCardsCardIdDeleteParams;
  options?: CustomRequestOptions;
}) {
  const { card_id: param0, ...queryParams } = params;

  return request<API.ApiResponse>(`/api/v1/user/cards/${param0}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  });
}

/** 更新信用卡状态 更新信用卡状态支持的状态：- active: 激活- frozen: 冻结- closed: 关闭 PATCH /api/v1/user/cards/${param0}/status */
export async function updateCardStatusApiV1UserCardsCardIdStatusPatch({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.updateCardStatusApiV1UserCardsCardIdStatusPatchParams;
  body: API.CreditCardStatusUpdate;
  options?: CustomRequestOptions;
}) {
  const { card_id: param0, ...queryParams } = params;

  return request<API.ApiResponse>(`/api/v1/user/cards/${param0}/status`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  });
}

/** 获取银行列表 获取银行列表用于创建信用卡时选择银行 GET /api/v1/user/cards/banks/list */
export async function getBanksApiV1UserCardsBanksListGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getBanksApiV1UserCardsBanksListGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/user/cards/banks/list', {
    method: 'GET',
    params: {
      // active_only has a default value: true
      active_only: 'true',
      ...params,
    },
    ...(options || {}),
  });
}

/** 获取信用卡详细统计 获取信用卡详细统计包括：- 摘要信息- 按银行统计- 按状态统计- 按卡片等级统计- 使用率分布 GET /api/v1/user/cards/statistics/detailed */
export async function getCardStatisticsApiV1UserCardsStatisticsDetailedGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/user/cards/statistics/detailed', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 获取信用卡摘要统计 获取信用卡摘要统计包括：- 信用卡总数- 激活卡片数- 总信用额度- 总已用额度- 总可用额度- 平均使用率- 即将过期卡片数 GET /api/v1/user/cards/summary/overview */
export async function getCardSummaryApiV1UserCardsSummaryOverviewGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponse>('/api/v1/user/cards/summary/overview', {
    method: 'GET',
    ...(options || {}),
  });
}
