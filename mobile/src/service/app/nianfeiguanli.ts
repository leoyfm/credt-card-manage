/* eslint-disable */
// @ts-ignore
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as API from './types';

/** 批量检查年费减免 批量检查多张信用卡的年费减免条件 POST /api/annual-fees/batch/check-waivers */
export async function batchCheckAnnualFeeWaiversApiAnnualFeesBatchCheckWaiversPost({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.batchCheckAnnualFeeWaiversApiAnnualFeesBatchCheckWaiversPostParams;
  body: string[];
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseListAnnualFeeWaiverCheck_>(
    '/api/annual-fees/batch/check-waivers',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      params: {
        ...params,
      },
      data: body,
      ...(options || {}),
    }
  );
}

/** 批量创建年费记录 为多张信用卡批量创建年费记录 POST /api/annual-fees/batch/create-records */
export async function batchCreateAnnualFeeRecordsApiAnnualFeesBatchCreateRecordsPost({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.batchCreateAnnualFeeRecordsApiAnnualFeesBatchCreateRecordsPostParams;
  body: string[];
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseDict_>(
    '/api/annual-fees/batch/create-records',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      params: {
        ...params,
      },
      data: body,
      ...(options || {}),
    }
  );
}

/** 获取年费记录列表 获取年费记录列表获取年费记录信息，支持多种筛选条件和模糊搜索。可以按照信用卡、年份、减免状态等进行过滤。参数:- page: 页码，从1开始- page_size: 每页数量，默认20，最大100- keyword: 搜索关键词，支持卡片名称、银行名称模糊匹配- card_id: 信用卡ID，筛选指定卡片的年费记录- fee_year: 年费年份，筛选指定年份的记录- waiver_status: 减免状态，可选值：pending、waived、paid、overdue GET /api/annual-fees/records */
export async function getAnnualFeeRecordsApiAnnualFeesRecordsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getAnnualFeeRecordsApiAnnualFeesRecordsGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiPagedResponseAnnualFeeRecord_>(
    '/api/annual-fees/records',
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

/** 创建年费记录 创建年费记录 POST /api/annual-fees/records */
export async function createAnnualFeeRecordApiAnnualFeesRecordsPost({
  body,
  options,
}: {
  body: API.AnnualFeeRecordCreate;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseAnnualFeeRecord_>('/api/annual-fees/records', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 获取年费记录详情 根据ID获取年费记录详情 GET /api/annual-fees/records/${param0} */
export async function getAnnualFeeRecordApiAnnualFeesRecordsRecordIdGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getAnnualFeeRecordApiAnnualFeesRecordsRecordIdGetParams;
  options?: CustomRequestOptions;
}) {
  const { record_id: param0, ...queryParams } = params;

  return request<API.ApiResponseAnnualFeeRecord_>(
    `/api/annual-fees/records/${param0}`,
    {
      method: 'GET',
      params: { ...queryParams },
      ...(options || {}),
    }
  );
}

/** 更新年费记录 更新年费记录 PUT /api/annual-fees/records/${param0} */
export async function updateAnnualFeeRecordApiAnnualFeesRecordsRecordIdPut({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.updateAnnualFeeRecordApiAnnualFeesRecordsRecordIdPutParams;
  body: API.AnnualFeeRecordUpdate;
  options?: CustomRequestOptions;
}) {
  const { record_id: param0, ...queryParams } = params;

  return request<API.ApiResponseAnnualFeeRecord_>(
    `/api/annual-fees/records/${param0}`,
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

/** 自动创建年费记录 使用数据库函数自动创建年费记录 POST /api/annual-fees/records/auto */
export async function createAnnualFeeRecordAutoApiAnnualFeesRecordsAutoPost({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.createAnnualFeeRecordAutoApiAnnualFeesRecordsAutoPostParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseDict_>('/api/annual-fees/records/auto', {
    method: 'POST',
    params: {
      ...params,
    },
    ...(options || {}),
  });
}

/** 获取年费规则列表 获取年费规则列表获取系统中所有的年费规则，支持分页、模糊搜索和类型过滤。参数:- page: 页码，从1开始- page_size: 每页数量，默认20，最大100- keyword: 搜索关键词，支持规则名称、描述模糊匹配- fee_type: 年费类型过滤，可选值：rigid、transaction_count、transaction_amount、points_exchange GET /api/annual-fees/rules */
export async function getAnnualFeeRulesApiAnnualFeesRulesGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getAnnualFeeRulesApiAnnualFeesRulesGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiPagedResponseAnnualFeeRule_>('/api/annual-fees/rules', {
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

/** 创建年费规则 创建新的年费规则创建新的年费减免规则，支持多种年费类型：- rigid: 刚性年费，不可减免- transaction_count: 刷卡次数减免- transaction_amount: 刷卡金额减免- points_exchange: 积分兑换减免参数:- rule_data: 年费规则创建数据 POST /api/annual-fees/rules */
export async function createAnnualFeeRuleApiAnnualFeesRulesPost({
  body,
  options,
}: {
  body: API.AnnualFeeRuleCreate;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseAnnualFeeRule_>('/api/annual-fees/rules', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 获取年费规则详情 根据ID获取年费规则详情获取指定年费规则的详细信息，包括规则名称、年费类型、减免条件、考核周期等完整信息。参数:- rule_id: 年费规则的UUID GET /api/annual-fees/rules/${param0} */
export async function getAnnualFeeRuleApiAnnualFeesRulesRuleIdGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getAnnualFeeRuleApiAnnualFeesRulesRuleIdGetParams;
  options?: CustomRequestOptions;
}) {
  const { rule_id: param0, ...queryParams } = params;

  return request<API.ApiResponseAnnualFeeRule_>(
    `/api/annual-fees/rules/${param0}`,
    {
      method: 'GET',
      params: { ...queryParams },
      ...(options || {}),
    }
  );
}

/** 更新年费规则 更新年费规则 PUT /api/annual-fees/rules/${param0} */
export async function updateAnnualFeeRuleApiAnnualFeesRulesRuleIdPut({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.updateAnnualFeeRuleApiAnnualFeesRulesRuleIdPutParams;
  body: API.AnnualFeeRuleUpdate;
  options?: CustomRequestOptions;
}) {
  const { rule_id: param0, ...queryParams } = params;

  return request<API.ApiResponseAnnualFeeRule_>(
    `/api/annual-fees/rules/${param0}`,
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

/** 删除年费规则 删除年费规则 DELETE /api/annual-fees/rules/${param0} */
export async function deleteAnnualFeeRuleApiAnnualFeesRulesRuleIdDelete({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.deleteAnnualFeeRuleApiAnnualFeesRulesRuleIdDeleteParams;
  options?: CustomRequestOptions;
}) {
  const { rule_id: param0, ...queryParams } = params;

  return request<API.ApiResponseNoneType_>(`/api/annual-fees/rules/${param0}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  });
}

/** 获取年费统计信息 获取用户的年费统计信息 GET /api/annual-fees/statistics/${param0} */
export async function getAnnualFeeStatisticsApiAnnualFeesStatisticsUserIdGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getAnnualFeeStatisticsApiAnnualFeesStatisticsUserIdGetParams;
  options?: CustomRequestOptions;
}) {
  const { user_id: param0, ...queryParams } = params;

  return request<API.ApiResponseAnnualFeeStatistics_>(
    `/api/annual-fees/statistics/${param0}`,
    {
      method: 'GET',
      params: {
        ...queryParams,
      },
      ...(options || {}),
    }
  );
}

/** 检查年费减免条件 检查指定信用卡的年费减免条件 GET /api/annual-fees/waiver-check/${param0}/${param1} */
export async function checkAnnualFeeWaiverApiAnnualFeesWaiverCheckCardIdFeeYearGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.checkAnnualFeeWaiverApiAnnualFeesWaiverCheckCardIdFeeYearGetParams;
  options?: CustomRequestOptions;
}) {
  const { card_id: param0, fee_year: param1, ...queryParams } = params;

  return request<API.ApiResponseAnnualFeeWaiverCheck_>(
    `/api/annual-fees/waiver-check/${param0}/${param1}`,
    {
      method: 'GET',
      params: { ...queryParams },
      ...(options || {}),
    }
  );
}

/** 检查用户所有卡的年费减免条件 检查用户所有信用卡的年费减免条件 GET /api/annual-fees/waiver-check/user/${param0} */
export async function checkAllAnnualFeeWaiversApiAnnualFeesWaiverCheckUserUserIdGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.checkAllAnnualFeeWaiversApiAnnualFeesWaiverCheckUserUserIdGetParams;
  options?: CustomRequestOptions;
}) {
  const { user_id: param0, ...queryParams } = params;

  return request<API.ApiResponseListAnnualFeeWaiverCheck_>(
    `/api/annual-fees/waiver-check/user/${param0}`,
    {
      method: 'GET',
      params: {
        ...queryParams,
      },
      ...(options || {}),
    }
  );
}
