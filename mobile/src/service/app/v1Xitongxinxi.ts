/* eslint-disable */
// @ts-ignore
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as API from './types';

/** 健康检查 检查系统健康状态，包括服务状态、数据库连接等 GET /api/v1/public/system/health */
export async function healthCheckApiV1PublicSystemHealthGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<unknown>('/api/v1/public/system/health', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 服务状态 获取系统服务状态信息 GET /api/v1/public/system/status */
export async function getStatusApiV1PublicSystemStatusGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<unknown>('/api/v1/public/system/status', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 版本信息 获取系统版本信息 GET /api/v1/public/system/version */
export async function getVersionApiV1PublicSystemVersionGet({
  options,
}: {
  options?: CustomRequestOptions;
}) {
  return request<unknown>('/api/v1/public/system/version', {
    method: 'GET',
    ...(options || {}),
  });
}
