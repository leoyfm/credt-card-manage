/* eslint-disable */
// @ts-ignore
import { queryOptions, useMutation } from '@tanstack/vue-query';
import type { DefaultError } from '@tanstack/vue-query';
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as apis from './xinyongka';
import * as API from './types';

/** 获取信用卡列表 获取信用卡列表（集成年费信息）支持分页和模糊搜索功能。返回信用卡基本信息以及年费相关信息。参数:- page: 页码，从1开始- page_size: 每页数量，默认20，最大100- keyword: 搜索关键词，支持银行名称、卡片名称模糊匹配 GET /api/cards/ */
export function getCardsApiCardsGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCardsApiCardsGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getCardsApiCardsGet(queryKey[1] as typeof options);
    },
    queryKey: ['getCardsApiCardsGet', options],
  });
}

/** 创建信用卡 创建新的信用卡（集成年费管理）添加新的信用卡到系统中，支持同时创建年费规则。如果启用年费管理，将同时创建对应的年费规则和记录。年费管理功能：- 支持多种年费类型：刚性年费、刷卡次数减免、刷卡金额减免、积分兑换减免- 自动创建年费记录- 支持自定义年费扣除日期 POST /api/cards/ */
export function useCreateCardApiCardsPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseCardWithAnnualFee_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.createCardApiCardsPost,
    onSuccess(data: API.ApiResponseCardWithAnnualFee_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取信用卡详情 根据ID获取信用卡详情（集成年费信息）获取指定信用卡的详细信息，包括基本信息、年费规则、当前年费状态等。 GET /api/cards/${param0} */
export function getCardApiCardsCardIdGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCardApiCardsCardIdGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getCardApiCardsCardIdGet(queryKey[1] as typeof options);
    },
    queryKey: ['getCardApiCardsCardIdGet', options],
  });
}

/** 更新信用卡信息 更新信用卡信息（集成年费管理）更新指定信用卡的信息，支持同时管理年费规则。年费管理功能：- 可以启用或禁用年费管理- 禁用年费管理时将删除现有年费规则和记录- 启用时将创建新的年费规则- 修改年费规则时会更新相关记录 PUT /api/cards/${param0} */
export function useUpdateCardApiCardsCardIdPutMutation(options?: {
  onSuccess?: (value?: API.ApiResponseCardWithAnnualFee_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.updateCardApiCardsCardIdPut,
    onSuccess(data: API.ApiResponseCardWithAnnualFee_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 删除信用卡 删除信用卡从系统中删除指定的信用卡记录。同时会删除相关的年费规则和记录。 DELETE /api/cards/${param0} */
export function useDeleteCardApiCardsCardIdDeleteMutation(options?: {
  onSuccess?: (value?: API.ApiResponseNoneType_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.deleteCardApiCardsCardIdDelete,
    onSuccess(data: API.ApiResponseNoneType_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}

/** 获取信用卡列表（基础版本） 获取信用卡列表（基础版本，不包含年费信息）支持分页和模糊搜索功能。可以根据银行名称、卡片名称等关键词进行搜索。 GET /api/cards/basic */
export function getCardsBasicApiCardsBasicGetQueryOptions(options: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCardsBasicApiCardsBasicGetParams;
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getCardsBasicApiCardsBasicGet(queryKey[1] as typeof options);
    },
    queryKey: ['getCardsBasicApiCardsBasicGet', options],
  });
}

/** 创建信用卡（基础版本） 创建新的信用卡（基础版本，不含年费管理）添加新的信用卡到系统中，包括基本信息、额度设置等。 POST /api/cards/basic */
export function useCreateCardBasicApiCardsBasicPostMutation(options?: {
  onSuccess?: (value?: API.ApiResponseCard_) => void;
  onError?: (error?: DefaultError) => void;
}) {
  const { onSuccess, onError } = options || {};

  const response = useMutation({
    mutationFn: apis.createCardBasicApiCardsBasicPost,
    onSuccess(data: API.ApiResponseCard_) {
      onSuccess?.(data);
    },
    onError(error) {
      onError?.(error);
    },
  });

  return response;
}
