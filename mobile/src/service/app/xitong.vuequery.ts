/* eslint-disable */
// @ts-ignore
import { queryOptions, useMutation } from '@tanstack/vue-query';
import type { DefaultError } from '@tanstack/vue-query';
import request from '@/utils/request';
import { CustomRequestOptions } from '@/interceptors/request';

import * as apis from './xitong';
import * as API from './types';

/** 服务状态检查 获取服务运行状态返回API服务的基本运行状态信息，用于确认服务是否正常启动。 GET / */
export function rootGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.rootGet(queryKey[1] as typeof options);
    },
    queryKey: ['rootGet', options],
  });
}

/** 健康检查 系统健康检查检查系统各组件的运行状态，包括数据库连接、缓存服务等。返回详细的健康状态信息。 GET /health */
export function healthCheckHealthGetQueryOptions(options: {
  options?: CustomRequestOptions;
}) {
  return queryOptions({
    queryFn: async ({ queryKey }) => {
      return apis.healthCheckHealthGet(queryKey[1] as typeof options);
    },
    queryKey: ['healthCheckHealthGet', options],
  });
}
