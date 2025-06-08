/* eslint-disable */
// @ts-ignore
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as API from './types';

/** 获取信用卡列表 获取信用卡列表（集成年费信息）支持分页和模糊搜索功能。返回信用卡基本信息以及年费相关信息。参数:- page: 页码，从1开始- page_size: 每页数量，默认20，最大100- keyword: 搜索关键词，支持银行名称、卡片名称模糊匹配 GET /api/cards/ */
export async function getCardsApiCardsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCardsApiCardsGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiPagedResponseCardSummaryWithAnnualFee_>('/api/cards/', {
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

/** 创建信用卡 创建新的信用卡（集成年费管理）添加新的信用卡到系统中，支持同时创建年费规则。如果启用年费管理，将同时创建对应的年费规则和记录。年费管理功能：- 支持多种年费类型：刚性年费、刷卡次数减免、刷卡金额减免、积分兑换减免- 自动创建年费记录- 支持自定义年费扣除日期 POST /api/cards/ */
export async function createCardApiCardsPost({
  body,
  options,
}: {
  body: API.CardWithAnnualFeeCreate;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseCardWithAnnualFee_>('/api/cards/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 获取信用卡详情 根据ID获取信用卡详情（集成年费信息）获取指定信用卡的详细信息，包括基本信息、年费规则、当前年费状态等。 GET /api/cards/${param0} */
export async function getCardApiCardsCardIdGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCardApiCardsCardIdGetParams;
  options?: CustomRequestOptions;
}) {
  const { card_id: param0, ...queryParams } = params;

  return request<API.ApiResponseCardWithAnnualFee_>(`/api/cards/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  });
}

/** 更新信用卡信息 更新信用卡信息（集成年费管理）更新指定信用卡的信息，支持同时管理年费规则。年费管理功能：- 可以启用或禁用年费管理- 禁用年费管理时将删除现有年费规则和记录- 启用时将创建新的年费规则- 修改年费规则时会更新相关记录 PUT /api/cards/${param0} */
export async function updateCardApiCardsCardIdPut({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.updateCardApiCardsCardIdPutParams;
  body: API.CardWithAnnualFeeUpdate;
  options?: CustomRequestOptions;
}) {
  const { card_id: param0, ...queryParams } = params;

  return request<API.ApiResponseCardWithAnnualFee_>(`/api/cards/${param0}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  });
}

/** 删除信用卡 删除信用卡从系统中删除指定的信用卡记录。同时会删除相关的年费规则和记录。 DELETE /api/cards/${param0} */
export async function deleteCardApiCardsCardIdDelete({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.deleteCardApiCardsCardIdDeleteParams;
  options?: CustomRequestOptions;
}) {
  const { card_id: param0, ...queryParams } = params;

  return request<API.ApiResponseNoneType_>(`/api/cards/${param0}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  });
}

/** 获取信用卡列表（基础版本） 获取信用卡列表（基础版本，不包含年费信息）支持分页和模糊搜索功能。可以根据银行名称、卡片名称等关键词进行搜索。 GET /api/cards/basic */
export async function getCardsBasicApiCardsBasicGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCardsBasicApiCardsBasicGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiPagedResponseCard_>('/api/cards/basic', {
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

/** 创建信用卡（基础版本） 创建新的信用卡（基础版本，不含年费管理）添加新的信用卡到系统中，包括基本信息、额度设置等。 POST /api/cards/basic */
export async function createCardBasicApiCardsBasicPost({
  body,
  options,
}: {
  body: API.CardCreate;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseCard_>('/api/cards/basic', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}
