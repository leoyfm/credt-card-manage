/* eslint-disable */
// @ts-ignore
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as API from './types';

/** 获取还款提醒列表 获取还款提醒列表获取用户的还款提醒信息，支持分页和模糊搜索。包括还款日期、金额、状态等信息。参数:- page: 页码，从1开始- page_size: 每页数量，默认20，最大100- keyword: 搜索关键词，支持卡片名称、银行名称模糊匹配 GET /api/reminders/ */
export async function getRemindersApiRemindersGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getRemindersApiRemindersGetParams;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiPagedResponseReminder_>('/api/reminders/', {
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

/** 创建还款提醒 创建新的还款提醒为指定信用卡创建还款提醒，包括提醒时间、金额等信息。 POST /api/reminders/ */
export async function createReminderApiRemindersPost({
  body,
  options,
}: {
  body: API.ReminderCreate;
  options?: CustomRequestOptions;
}) {
  return request<API.ApiResponseReminder_>('/api/reminders/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 获取还款提醒详情 根据ID获取还款提醒详情获取指定还款提醒的详细信息。 GET /api/reminders/${param0} */
export async function getReminderApiRemindersReminderIdGet({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.getReminderApiRemindersReminderIdGetParams;
  options?: CustomRequestOptions;
}) {
  const { reminder_id: param0, ...queryParams } = params;

  return request<API.ApiResponseReminder_>(`/api/reminders/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  });
}

/** 更新还款提醒 更新还款提醒信息更新指定还款提醒的信息，如提醒时间、金额等。 PUT /api/reminders/${param0} */
export async function updateReminderApiRemindersReminderIdPut({
  params,
  body,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.updateReminderApiRemindersReminderIdPutParams;
  body: API.ReminderUpdate;
  options?: CustomRequestOptions;
}) {
  const { reminder_id: param0, ...queryParams } = params;

  return request<API.ApiResponseReminder_>(`/api/reminders/${param0}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  });
}

/** 删除还款提醒 删除还款提醒从系统中删除指定的还款提醒记录。 DELETE /api/reminders/${param0} */
export async function deleteReminderApiRemindersReminderIdDelete({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.deleteReminderApiRemindersReminderIdDeleteParams;
  options?: CustomRequestOptions;
}) {
  const { reminder_id: param0, ...queryParams } = params;

  return request<API.ApiResponseNoneType_>(`/api/reminders/${param0}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  });
}

/** 标记提醒已读 标记还款提醒为已读状态将指定的还款提醒标记为已读，避免重复提醒。 PUT /api/reminders/${param0}/mark-read */
export async function markReminderReadApiRemindersReminderIdMarkReadPut({
  params,
  options,
}: {
  // 叠加生成的Param类型 (非body参数openapi默认没有生成对象)
  params: API.markReminderReadApiRemindersReminderIdMarkReadPutParams;
  options?: CustomRequestOptions;
}) {
  const { reminder_id: param0, ...queryParams } = params;

  return request<API.ApiResponseNoneType_>(
    `/api/reminders/${param0}/mark-read`,
    {
      method: 'PUT',
      params: { ...queryParams },
      ...(options || {}),
    }
  );
}
