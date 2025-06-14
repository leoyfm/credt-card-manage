/* eslint-disable */
// @ts-ignore
import { queryOptions, useMutation } from '@tanstack/vue-query';
import type { DefaultError } from '@tanstack/vue-query';
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as apis from './v1Xitongxinxi';
import * as API from './types';

/** 健康检查 检查系统健康状态，包括服务状态、数据库连接等 GET /api/v1/public/system/health */
export function healthCheckApiV1PublicSystemHealthGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.healthCheckApiV1PublicSystemHealthGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['healthCheckApiV1PublicSystemHealthGet', options],
  });
}

/** 服务状态 获取系统服务状态信息 GET /api/v1/public/system/status */
export function getStatusApiV1PublicSystemStatusGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getStatusApiV1PublicSystemStatusGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getStatusApiV1PublicSystemStatusGet', options],
  });
}

/** 版本信息 获取系统版本信息 GET /api/v1/public/system/version */
export function getVersionApiV1PublicSystemVersionGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.getVersionApiV1PublicSystemVersionGet(
        queryKey[1] as typeof options
      );
    },
    queryKey: ['getVersionApiV1PublicSystemVersionGet', options],
  });
}
