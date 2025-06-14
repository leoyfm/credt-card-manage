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

/** 注销账户 注销当前用户账户（软删除） DELETE /api/v1/user/profile/account */
export async function deleteAccountApiV1UserProfileAccountDelete({
  body,
  options,
}: {
  body: API.AccountDeletionRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseBool_>('/api/v1/user/profile/account', {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 修改密码 修改当前用户的登录密码 POST /api/v1/user/profile/change-password */
export async function changePasswordApiV1UserProfileChangePasswordPost({
  body,
  options,
}: {
  body: API.ChangePasswordRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseBool_>('/api/v1/user/profile/change-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 获取个人信息 获取当前用户的个人资料信息 GET /api/v1/user/profile/info */
export async function getUserInfoApiV1UserProfileInfoGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseUserProfileResponse_>(
    '/api/v1/user/profile/info',
    {
      method: 'GET',
      ...(options || {}),
    }
  );
}

/** 个人登录日志 获取当前用户的登录日志记录 GET /api/v1/user/profile/login-logs */
export async function getLoginLogsApiV1UserProfileLoginLogsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getLoginLogsApiV1UserProfileLoginLogsGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiPagedResponseLoginLogResponse_>(
    '/api/v1/user/profile/login-logs',
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

/** 退出登录 退出当前用户的登录状态 POST /api/v1/user/profile/logout */
export async function logoutApiV1UserProfileLogoutPost({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseBool_>('/api/v1/user/profile/logout', {
    method: 'POST',
    ...(options || {}),
  });
}

/** 个人统计信息 获取当前用户的统计信息（卡片、交易、积分等） GET /api/v1/user/profile/statistics */
export async function getUserStatisticsApiV1UserProfileStatisticsGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseUserStatisticsResponse_>(
    '/api/v1/user/profile/statistics',
    {
      method: 'GET',
      ...(options || {}),
    }
  );
}

/** 更新个人资料 更新当前用户的个人资料信息 PUT /api/v1/user/profile/update */
export async function updateUserProfileApiV1UserProfileUpdatePut({
  body,
  options,
}: {
  body: API.UserProfileUpdateRequest;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseUserProfileResponse_>(
    '/api/v1/user/profile/update',
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      data: body,
      ...(options || {}),
    }
  );
}

/** 微信绑定信息 获取当前用户的微信绑定信息 GET /api/v1/user/profile/wechat-bindings */
export async function getWechatBindingsApiV1UserProfileWechatBindingsGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseListWechatBindingResponse_>(
    '/api/v1/user/profile/wechat-bindings',
    {
      method: 'GET',
      ...(options || {}),
    }
  );
}

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

/** 生成自动提醒 为用户的信用卡自动生成提醒记录 POST /api/v1/user/reminders/generate-automatic */
export async function generateAutomaticRemindersApiV1UserRemindersGenerateAutomaticPost({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseDict_>(
    '/api/v1/user/reminders/generate-automatic',
    {
      method: 'POST',
      ...(options || {}),
    }
  );
}

/** 标记所有提醒为已读 将用户的所有未读提醒标记为已读状态 POST /api/v1/user/reminders/mark-all-read */
export async function markAllRemindersAsReadApiV1UserRemindersMarkAllReadPost({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseMarkAllReadResponse_>(
    '/api/v1/user/reminders/mark-all-read',
    {
      method: 'POST',
      ...(options || {}),
    }
  );
}

/** 获取最近的提醒 获取用户最近的提醒记录 GET /api/v1/user/reminders/recent */
export async function getRecentRemindersApiV1UserRemindersRecentGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getRecentRemindersApiV1UserRemindersRecentGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseListReminderRecordResponse_>(
    '/api/v1/user/reminders/recent',
    {
      method: 'GET',
      params: {
        // limit has a default value: 10
        limit: '10',
        ...params,
      },
      ...(options || {}),
    }
  );
}

/** 获取提醒记录列表 获取用户的提醒记录列表，支持按设置、状态、日期筛选和分页 GET /api/v1/user/reminders/records */
export async function getReminderRecordsApiV1UserRemindersRecordsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getReminderRecordsApiV1UserRemindersRecordsGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiPagedResponseReminderRecordResponse_>(
    '/api/v1/user/reminders/records',
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

/** 创建提醒记录 为用户创建新的提醒记录 POST /api/v1/user/reminders/records */
export async function createReminderRecordApiV1UserRemindersRecordsPost({
  body,
  options,
}: {
  body: API.ReminderRecordCreate;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseReminderRecordResponse_>(
    '/api/v1/user/reminders/records',
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

/** 获取提醒记录详情 获取指定提醒记录的详细信息 GET /api/v1/user/reminders/records/${param0} */
export async function getReminderRecordApiV1UserRemindersRecordsRecordIdGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getReminderRecordApiV1UserRemindersRecordsRecordIdGetParams;
  options?: CustomRequestOptions;
}) {
  const { record_id: param0, ...queryParams } = params;

  return request<API.ApiResponseReminderRecordResponse_>(
    `/api/v1/user/reminders/records/${param0}`,
    {
      method: 'GET',
      params: { ...queryParams },
      ...(options || {}),
    }
  );
}

/** 标记提醒为已读 将指定的提醒记录标记为已读状态 POST /api/v1/user/reminders/records/${param0}/read */
export async function markReminderAsReadApiV1UserRemindersRecordsRecordIdReadPost({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.markReminderAsReadApiV1UserRemindersRecordsRecordIdReadPostParams;
  options?: CustomRequestOptions;
}) {
  const { record_id: param0, ...queryParams } = params;

  return request<API.ApiResponseReminderRecordResponse_>(
    `/api/v1/user/reminders/records/${param0}/read`,
    {
      method: 'POST',
      params: { ...queryParams },
      ...(options || {}),
    }
  );
}

/** 获取提醒设置列表 获取用户的提醒设置列表，支持按信用卡、类型、状态筛选和分页 GET /api/v1/user/reminders/settings */
export async function getReminderSettingsApiV1UserRemindersSettingsGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getReminderSettingsApiV1UserRemindersSettingsGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiPagedResponseReminderSettingResponse_>(
    '/api/v1/user/reminders/settings',
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

/** 创建提醒设置 为用户创建新的提醒设置，可以是全局提醒或特定信用卡的提醒 POST /api/v1/user/reminders/settings */
export async function createReminderSettingApiV1UserRemindersSettingsPost({
  body,
  options,
}: {
  body: API.ReminderSettingCreate;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseReminderSettingResponse_>(
    '/api/v1/user/reminders/settings',
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

/** 获取提醒设置详情 获取指定提醒设置的详细信息 GET /api/v1/user/reminders/settings/${param0} */
export async function getReminderSettingApiV1UserRemindersSettingsSettingIdGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getReminderSettingApiV1UserRemindersSettingsSettingIdGetParams;
  options?: CustomRequestOptions;
}) {
  const { setting_id: param0, ...queryParams } = params;

  return request<API.ApiResponseReminderSettingResponse_>(
    `/api/v1/user/reminders/settings/${param0}`,
    {
      method: 'GET',
      params: { ...queryParams },
      ...(options || {}),
    }
  );
}

/** 更新提醒设置 更新指定的提醒设置信息 PUT /api/v1/user/reminders/settings/${param0} */
export async function updateReminderSettingApiV1UserRemindersSettingsSettingIdPut({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.updateReminderSettingApiV1UserRemindersSettingsSettingIdPutParams;
  body: API.ReminderSettingUpdate;
  options?: CustomRequestOptions;
}) {
  const { setting_id: param0, ...queryParams } = params;

  return request<API.ApiResponseReminderSettingResponse_>(
    `/api/v1/user/reminders/settings/${param0}`,
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

/** 删除提醒设置 删除指定的提醒设置及其关联的提醒记录 DELETE /api/v1/user/reminders/settings/${param0} */
export async function deleteReminderSettingApiV1UserRemindersSettingsSettingIdDelete({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.deleteReminderSettingApiV1UserRemindersSettingsSettingIdDeleteParams;
  options?: CustomRequestOptions;
}) {
  const { setting_id: param0, ...queryParams } = params;

  return request<API.ApiResponseBool_>(
    `/api/v1/user/reminders/settings/${param0}`,
    {
      method: 'DELETE',
      params: { ...queryParams },
      ...(options || {}),
    }
  );
}

/** 获取提醒统计 获取用户的提醒统计信息，包括设置数量、提醒数量、阅读率等 GET /api/v1/user/reminders/statistics */
export async function getReminderStatisticsApiV1UserRemindersStatisticsGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseReminderStatisticsResponse_>(
    '/api/v1/user/reminders/statistics',
    {
      method: 'GET',
      ...(options || {}),
    }
  );
}

/** 获取未读提醒个数 获取用户的未读提醒个数统计，包括总数、今日未读、高优先级未读等 GET /api/v1/user/reminders/unread-count */
export async function getUnreadRemindersCountApiV1UserRemindersUnreadCountGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseUnreadRemindersCountResponse_>(
    '/api/v1/user/reminders/unread-count',
    {
      method: 'GET',
      ...(options || {}),
    }
  );
}

/** 获取即将到来的提醒 获取指定天数内即将到来的提醒，按优先级分类 GET /api/v1/user/reminders/upcoming */
export async function getUpcomingRemindersApiV1UserRemindersUpcomingGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getUpcomingRemindersApiV1UserRemindersUpcomingGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseUpcomingRemindersResponse_>(
    '/api/v1/user/reminders/upcoming',
    {
      method: 'GET',
      params: {
        // days_ahead has a default value: 7
        days_ahead: '7',
        ...params,
      },
      ...(options || {}),
    }
  );
}
