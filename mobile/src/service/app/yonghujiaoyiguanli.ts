/* eslint-disable */
// @ts-ignore
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as API from './types';

/** 删除交易记录 删除指定的交易记录 DELETE /api/v1/user/transactions/${param0}/delete */
export async function deleteTransactionApiV1UserTransactionsTransactionIdDeleteDelete({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.deleteTransactionApiV1UserTransactionsTransactionIdDeleteDeleteParams;
  options?: CustomRequestOptions;
}) {
  const { transaction_id: param0, ...queryParams } = params;

  return request<API.ApiResponseBool_>(
    `/api/v1/user/transactions/${param0}/delete`,
    {
      method: 'DELETE',
      params: { ...queryParams },
      ...(options || {}),
    }
  );
}

/** 获取交易记录详情 根据交易ID获取详细的交易记录信息 GET /api/v1/user/transactions/${param0}/details */
export async function getTransactionDetailsApiV1UserTransactionsTransactionIdDetailsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getTransactionDetailsApiV1UserTransactionsTransactionIdDetailsGetParams;
  options?: CustomRequestOptions;
}) {
  const { transaction_id: param0, ...queryParams } = params;

  return request<API.ApiResponseTransactionResponse_>(
    `/api/v1/user/transactions/${param0}/details`,
    {
      method: 'GET',
      params: { ...queryParams },
      ...(options || {}),
    }
  );
}

/** 更新交易记录 更新指定的交易记录信息 PUT /api/v1/user/transactions/${param0}/update */
export async function updateTransactionApiV1UserTransactionsTransactionIdUpdatePut({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.updateTransactionApiV1UserTransactionsTransactionIdUpdatePutParams;
  body: API.TransactionUpdate;
  options?: CustomRequestOptions;
}) {
  const { transaction_id: param0, ...queryParams } = params;

  return request<API.ApiResponseTransactionResponse_>(
    `/api/v1/user/transactions/${param0}/update`,
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

/** 获取交易分类列表 获取所有可用的交易分类，用于创建和编辑交易时选择 GET /api/v1/user/transactions/categories */
export async function getTransactionCategoriesApiV1UserTransactionsCategoriesGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseListTransactionCategoryResponse_>(
    '/api/v1/user/transactions/categories',
    {
      method: 'GET',
      ...(options || {}),
    }
  );
}

/** 创建交易记录 创建新的交易记录，支持消费、收入、退款等类型 POST /api/v1/user/transactions/create */
export async function createTransactionApiV1UserTransactionsCreatePost({
  body,
  options,
}: {
  body: API.TransactionCreate;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseTransactionResponse_>(
    '/api/v1/user/transactions/create',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      ...(options || {}),
    }
  );
}

/** 获取交易记录列表 获取当前用户的交易记录列表，支持分页、筛选和搜索 GET /api/v1/user/transactions/list */
export async function getTransactionsApiV1UserTransactionsListGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getTransactionsApiV1UserTransactionsListGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiPagedResponseTransactionResponse_>(
    '/api/v1/user/transactions/list',
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

/** 获取分类统计数据 获取指定时间范围内的交易分类统计，包括各分类的支出分布 GET /api/v1/user/transactions/statistics/categories */
export async function getCategoryStatisticsApiV1UserTransactionsStatisticsCategoriesGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getCategoryStatisticsApiV1UserTransactionsStatisticsCategoriesGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseCategoryStatisticsResponse_>(
    '/api/v1/user/transactions/statistics/categories',
    {
      method: 'GET',
      params: {
        ...params,
      },
      ...(options || {}),
    }
  );
}

/** 获取月度趋势分析 获取指定月数的月度交易趋势分析数据 GET /api/v1/user/transactions/statistics/monthly-trends */
export async function getMonthlyTrendsApiV1UserTransactionsStatisticsMonthlyTrendsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getMonthlyTrendsApiV1UserTransactionsStatisticsMonthlyTrendsGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseMonthlyTrendResponse_>(
    '/api/v1/user/transactions/statistics/monthly-trends',
    {
      method: 'GET',
      params: {
        // months has a default value: 12
        months: '12',
        ...params,
      },
      ...(options || {}),
    }
  );
}

/** 获取交易统计概览 获取指定时间范围内的交易统计数据，包括总额、笔数、积分等 GET /api/v1/user/transactions/statistics/overview */
export async function getTransactionStatisticsApiV1UserTransactionsStatisticsOverviewGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getTransactionStatisticsApiV1UserTransactionsStatisticsOverviewGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseTransactionStatisticsResponse_>(
    '/api/v1/user/transactions/statistics/overview',
    {
      method: 'GET',
      params: {
        ...params,
      },
      ...(options || {}),
    }
  );
}
