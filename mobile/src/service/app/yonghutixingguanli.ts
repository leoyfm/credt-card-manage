/* eslint-disable */
// @ts-ignore
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as API from './types';

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
